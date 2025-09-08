use pyo3::prelude::*;
use rayon::prelude::*;
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};

/// Work-stealing scheduler for load balancing
#[pyclass]
pub struct WorkStealingScheduler {
    workers: usize,
    work_queues: Arc<Mutex<Vec<VecDeque<Arc<Py<PyAny>>>>>>,
}

#[pymethods]
impl WorkStealingScheduler {
    #[new]
    #[pyo3(signature = (workers = None))]
    pub fn new(workers: Option<usize>) -> Self {
        let num_workers = workers.unwrap_or_else(|| num_cpus::get());
        let work_queues = Arc::new(Mutex::new(vec![VecDeque::new(); num_workers]));

        Self {
            workers: num_workers,
            work_queues,
        }
    }

    /// Execute tasks with work-stealing scheduling
    pub fn execute(&self, py: Python, tasks: Vec<Bound<PyAny>>) -> PyResult<Vec<Py<PyAny>>> {
        if tasks.is_empty() {
            return Ok(Vec::new());
        }

        let task_objects: Vec<Arc<Py<PyAny>>> =
            tasks.into_iter().map(|t| Arc::new(t.into())).collect();

        // Distribute tasks among work queues
        {
            let mut queues = self.work_queues.lock().unwrap();
            for (i, task) in task_objects.iter().enumerate() {
                let queue_idx = i % self.workers;
                queues[queue_idx].push_back(task.clone());
            }
        }

        // Execute tasks using rayon's work-stealing
        let results: PyResult<Vec<Py<PyAny>>> = py.detach(|| {
            task_objects
                .par_iter()
                .map(|task| {
                    Python::attach(|py| {
                        let bound_task = task.bind(py);
                        bound_task.call0().map(|r| r.into())
                    })
                })
                .collect()
        });

        results
    }

    /// Execute tasks with custom work distribution
    pub fn execute_with_distribution(
        &self,
        py: Python,
        tasks: Vec<Bound<PyAny>>,
        chunk_size: Option<usize>,
    ) -> PyResult<Vec<Py<PyAny>>> {
        if tasks.is_empty() {
            return Ok(Vec::new());
        }

        let chunk_size = chunk_size.unwrap_or(tasks.len() / self.workers.max(1));
        let task_objects: Vec<Arc<Py<PyAny>>> =
            tasks.into_iter().map(|t| Arc::new(t.into())).collect();

        // Process in chunks with work-stealing
        let results: PyResult<Vec<Py<PyAny>>> = py.detach(|| {
            task_objects
                .par_chunks(chunk_size)
                .flat_map(|chunk| {
                    chunk.par_iter().map(|task| {
                        Python::attach(|py| {
                            let bound_task = task.bind(py);
                            bound_task.call0().map(|r| r.into())
                        })
                    })
                })
                .collect()
        });

        results
    }

    /// Get number of workers
    #[getter]
    pub fn workers(&self) -> usize {
        self.workers
    }

    /// Get work queue lengths (for debugging)
    pub fn queue_lengths(&self) -> PyResult<Vec<usize>> {
        let queues = self.work_queues.lock().unwrap();
        Ok(queues.iter().map(|q| q.len()).collect())
    }
}

/// Round-robin scheduler for even task distribution
#[pyclass]
pub struct RoundRobinScheduler {
    workers: usize,
    current_worker: Arc<Mutex<usize>>,
}

#[pymethods]
impl RoundRobinScheduler {
    #[new]
    #[pyo3(signature = (workers = None))]
    pub fn new(workers: Option<usize>) -> Self {
        let num_workers = workers.unwrap_or_else(|| num_cpus::get());

        Self {
            workers: num_workers,
            current_worker: Arc::new(Mutex::new(0)),
        }
    }

    /// Execute tasks in round-robin fashion
    pub fn execute(&self, py: Python, tasks: Vec<Bound<PyAny>>) -> PyResult<Vec<Py<PyAny>>> {
        if tasks.is_empty() {
            return Ok(Vec::new());
        }

        let task_objects: Vec<Arc<Py<PyAny>>> =
            tasks.into_iter().map(|t| Arc::new(t.into())).collect();

        // Group tasks by worker assignment
        let mut worker_tasks: Vec<Vec<Arc<Py<PyAny>>>> = vec![Vec::new(); self.workers];
        for (i, task) in task_objects.iter().enumerate() {
            let worker_idx = i % self.workers;
            worker_tasks[worker_idx].push(task.clone());
        }

        // Execute tasks in parallel groups
        let results: PyResult<Vec<Vec<Py<PyAny>>>> = py.detach(|| {
            worker_tasks
                .par_iter()
                .map(|worker_task_group| {
                    worker_task_group
                        .iter()
                        .map(|task| {
                            Python::attach(|py| {
                                let bound_task = task.bind(py);
                                bound_task.call0().map(|r| r.into())
                            })
                        })
                        .collect::<PyResult<Vec<_>>>()
                })
                .collect()
        });

        // Flatten results maintaining original order
        let mut final_results = Vec::new();
        let worker_results = results?;

        // Rebuild in original order
        for i in 0..task_objects.len() {
            let worker_idx = i % self.workers;
            let task_idx = i / self.workers;
            if task_idx < worker_results[worker_idx].len() {
                final_results.push(worker_results[worker_idx][task_idx].clone_ref(py));
            }
        }

        Ok(final_results)
    }

    /// Get next worker index
    pub fn next_worker(&self) -> usize {
        let mut current = self.current_worker.lock().unwrap();
        let worker = *current;
        *current = (*current + 1) % self.workers;
        worker
    }

    /// Get number of workers
    #[getter]
    pub fn workers(&self) -> usize {
        self.workers
    }
}

/// Scheduler that adapts to workload
#[pyclass]
pub struct AdaptiveScheduler {
    min_workers: usize,
    max_workers: usize,
    current_workers: Arc<Mutex<usize>>,
}

#[pymethods]
impl AdaptiveScheduler {
    #[new]
    #[pyo3(signature = (min_workers = None, max_workers = None))]
    pub fn new(min_workers: Option<usize>, max_workers: Option<usize>) -> Self {
        let min_workers = min_workers.unwrap_or(1);
        let max_workers = max_workers.unwrap_or_else(|| num_cpus::get() * 2);

        Self {
            min_workers,
            max_workers,
            current_workers: Arc::new(Mutex::new(min_workers)),
        }
    }

    /// Execute tasks with adaptive worker count
    pub fn execute(&self, py: Python, tasks: Vec<Bound<PyAny>>) -> PyResult<Vec<Py<PyAny>>> {
        if tasks.is_empty() {
            return Ok(Vec::new());
        }

        // Adapt worker count based on task count
        let optimal_workers = self.calculate_optimal_workers(tasks.len());
        {
            let mut current = self.current_workers.lock().unwrap();
            *current = optimal_workers;
        }

        // Store length before consuming tasks
        let task_count = tasks.len();
        let task_objects: Vec<Arc<Py<PyAny>>> =
            tasks.into_iter().map(|t| Arc::new(t.into())).collect();

        // Use dynamic chunk size based on worker count and task size
        let chunk_size = (task_count / optimal_workers).max(1);

        let results: PyResult<Vec<Py<PyAny>>> = py.detach(|| {
            task_objects
                .par_chunks(chunk_size)
                .flat_map(|chunk| {
                    chunk.par_iter().map(|task| {
                        Python::attach(|py| {
                            let bound_task = task.bind(py);
                            bound_task.call0().map(|r| r.into())
                        })
                    })
                })
                .collect()
        });

        results
    }

    /// Calculate optimal worker count based on task count
    fn calculate_optimal_workers(&self, task_count: usize) -> usize {
        if task_count < 10 {
            self.min_workers
        } else if task_count < 100 {
            ((task_count / 10).min(self.max_workers)).max(self.min_workers)
        } else {
            self.max_workers
        }
    }

    /// Get current worker count
    #[getter]
    pub fn current_workers(&self) -> usize {
        *self.current_workers.lock().unwrap()
    }

    /// Get min workers
    #[getter]
    pub fn min_workers(&self) -> usize {
        self.min_workers
    }

    /// Get max workers
    #[getter]
    pub fn max_workers(&self) -> usize {
        self.max_workers
    }
}
