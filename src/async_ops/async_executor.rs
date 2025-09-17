use pyo3::prelude::*;
use pyo3::types::PyList;
use std::sync::Arc;
use tokio::runtime::Runtime;
use tokio::sync::Semaphore;

// Thread-local storage for Python state optimization  
thread_local! {
    static PYTHON_STATE: std::cell::RefCell<Option<Python<'static>>> = std::cell::RefCell::new(None);
}

/// Optimized task wrapper for better GIL handling
struct OptimizedTask {
    func: Py<PyAny>,
    args: Option<Py<PyAny>>,
}

impl OptimizedTask {
    fn new(func: Py<PyAny>, args: Option<Py<PyAny>>) -> Self {
        Self { func, args }
    }
    
    fn execute(&self) -> PyResult<Py<PyAny>> {
        Python::attach(|py| {
            let bound_func = self.func.bind(py);
            match &self.args {
                Some(args) => {
                    let bound_args = args.bind(py);
                    bound_func.call1((bound_args,)).map(|r| r.into())
                }
                None => bound_func.call0().map(|r| r.into())
            }
        })
    }
}

/// High-performance asynchronous executor optimized for loop.run_in_executor
#[pyclass]
pub struct AsyncExecutor {
    max_workers: usize,
    runtime: Arc<Runtime>,
    semaphore: Arc<Semaphore>,
    work_stealing_runtime: Arc<Runtime>, // Separate runtime for work-stealing
}

#[pymethods]
impl AsyncExecutor {
    #[new]
    #[pyo3(signature = (max_workers = None))]
    pub fn new(max_workers: Option<usize>) -> PyResult<Self> {
        let max_workers = max_workers.unwrap_or_else(|| num_cpus::get());
        
        // Create optimized tokio runtime for async tasks with custom configuration
        let runtime = tokio::runtime::Builder::new_multi_thread()
            .worker_threads(max_workers)
            .enable_all()
            .thread_name("pyferris-async-worker")
            .thread_stack_size(2 * 1024 * 1024) // 2MB stack for better performance
            .build()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create tokio runtime: {}", e)))?;
            
        // Create separate work-stealing runtime for CPU-bound tasks
        let work_stealing_runtime = tokio::runtime::Builder::new_multi_thread()
            .worker_threads(max_workers * 2) // More threads for work-stealing
            .enable_all()
            .thread_name("pyferris-work-steal")
            .build()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create work-stealing runtime: {}", e)))?;
        
        Ok(Self { 
            max_workers,
            runtime: Arc::new(runtime),
            semaphore: Arc::new(Semaphore::new(max_workers)),
            work_stealing_runtime: Arc::new(work_stealing_runtime),
        })
    }

    /// Submit an async task - optimized for execution
    pub fn submit_async(&self, coro: Bound<PyAny>) -> PyResult<Py<PyAny>> {
        // Return the coroutine for now - can be enhanced later
        let coro_obj: Py<PyAny> = coro.into();
        Ok(coro_obj)
    }

    /// Submit a single task for execution using optimized runtime with GIL optimization
    pub fn submit_task(
        &self,
        py: Python,
        func: Bound<PyAny>,
        args: Option<Bound<PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let task = OptimizedTask::new(func.into(), args.map(|a| a.into()));
        let runtime = Arc::clone(&self.runtime);
        let semaphore = Arc::clone(&self.semaphore);
        
        // Optimized execution with minimal GIL contention
        let handle = runtime.spawn(async move {
            let _permit = semaphore.acquire().await.unwrap();
            
            // Use spawn_blocking for CPU-bound tasks with optimized thread pool
            tokio::task::spawn_blocking(move || {
                task.execute()
            }).await.unwrap()
        });

        // Release GIL during execution for better concurrency
        py.detach(|| {
            runtime.block_on(handle).unwrap()
        })
    }

    /// High-performance submit with work-stealing optimization for CPU-intensive tasks
    pub fn submit_task_optimized(
        &self,
        py: Python,
        func: Bound<PyAny>,
        args: Option<Bound<PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let task = OptimizedTask::new(func.into(), args.map(|a| a.into()));
        let work_runtime = Arc::clone(&self.work_stealing_runtime);
        
        // Use work-stealing runtime for maximum CPU utilization
        let handle = work_runtime.spawn(async move {
            // Direct spawn_blocking without semaphore for work-stealing efficiency
            tokio::task::spawn_blocking(move || {
                task.execute()
            }).await.unwrap()
        });

        // Optimized blocking with GIL release
        py.detach(|| work_runtime.block_on(handle).unwrap())
    }

    /// Batch submit multiple tasks for maximum throughput with optimized scheduling
    pub fn submit_batch(
        &self,
        py: Python,
        tasks: Vec<(Bound<PyAny>, Option<Bound<PyAny>>)>,
    ) -> PyResult<Vec<Py<PyAny>>> {
        if tasks.is_empty() {
            return Ok(Vec::new());
        }

        let runtime = Arc::clone(&self.work_stealing_runtime); // Use work-stealing for batches
        let semaphore = Arc::clone(&self.semaphore);
        
        // Convert to optimized task format
        let optimized_tasks: Vec<OptimizedTask> = tasks
            .into_iter()
            .map(|(func, args)| OptimizedTask::new(func.into(), args.map(|a| a.into())))
            .collect();

        let results = py.detach(|| {
            runtime.block_on(async {
                let handles: Vec<_> = optimized_tasks
                    .into_iter()
                    .map(|task| {
                        let sem_clone = Arc::clone(&semaphore);
                        tokio::spawn(async move {
                            let _permit = sem_clone.acquire().await.unwrap();
                            tokio::task::spawn_blocking(move || {
                                task.execute()
                            }).await.unwrap()
                        })
                    })
                    .collect();

                // Collect all results efficiently
                let mut results = Vec::new();
                for handle in handles {
                    results.push(handle.await.unwrap()?);
                }
                Ok::<Vec<Py<PyAny>>, PyErr>(results)
            })
        })?;

        Ok(results)
    }

    /// Execute multiple async tasks concurrently with optimal performance and GIL optimization
    pub fn map_async(
        &self,
        py: Python,
        func: Bound<PyAny>,
        data: Bound<PyAny>,
    ) -> PyResult<Py<PyList>> {
        let items: Vec<Py<PyAny>> = data
            .try_iter()?
            .map(|item| item.map(|i| i.into()))
            .collect::<PyResult<Vec<_>>>()?;

        if items.is_empty() {
            return Ok(PyList::empty(py).into());
        }

        let func_obj: Py<PyAny> = func.into();
        let runtime = Arc::clone(&self.work_stealing_runtime); // Use work-stealing for map operations
        
        // Optimized async execution with GIL release during computation
        let results: PyResult<Vec<Py<PyAny>>> = py.detach(|| {
            runtime.block_on(async {
                let tasks: Vec<_> = items
                    .into_iter()
                    .map(|item| {
                        let func_copy = Python::attach(|py| func_obj.clone_ref(py));
                        tokio::task::spawn_blocking(move || {
                            Python::attach(|py| {
                                let bound_func = func_copy.bind(py);
                                let bound_item = item.bind(py);
                                bound_func.call1((bound_item,)).map(|r| r.into())
                            })
                        })
                    })
                    .collect();

                // Wait for all tasks to complete concurrently
                let mut results = Vec::new();
                for task in tasks {
                    match task.await {
                        Ok(result) => results.push(result?),
                        Err(e) => return Err(pyo3::exceptions::PyRuntimeError::new_err(format!("Task failed: {}", e))),
                    }
                }
                Ok(results)
            })
        });

        let py_list = PyList::new(py, &results?)?;
        Ok(py_list.into())
    }

    /// Execute async tasks with semaphore-controlled concurrency for optimal resource management
    pub fn map_async_limited(
        &self,
        py: Python,
        func: Bound<PyAny>,
        data: Bound<PyAny>,
    ) -> PyResult<Py<PyList>> {
        let items: Vec<Py<PyAny>> = data
            .try_iter()?
            .map(|item| item.map(|i| i.into()))
            .collect::<PyResult<Vec<_>>>()?;

        if items.is_empty() {
            return Ok(PyList::empty(py).into());
        }

        let func_obj: Py<PyAny> = func.into();
        let runtime = Arc::clone(&self.runtime); // Use regular runtime with semaphore control
        let semaphore = Arc::clone(&self.semaphore);
        
        // Use semaphore to limit concurrency and prevent resource exhaustion
        let results: PyResult<Vec<Py<PyAny>>> = py.detach(|| {
            runtime.block_on(async {
                let tasks: Vec<_> = items
                    .into_iter()
                    .map(|item| {
                        let func_copy = Python::attach(|py| func_obj.clone_ref(py));
                        let sem_clone = Arc::clone(&semaphore);
                        tokio::task::spawn(async move {
                            let _permit = sem_clone.acquire().await.unwrap();
                            tokio::task::spawn_blocking(move || {
                                Python::attach(|py| {
                                    let bound_func = func_copy.bind(py);
                                    let bound_item = item.bind(py);
                                    bound_func.call1((bound_item,)).map(|r| r.into())
                                })
                            }).await.unwrap()
                        })
                    })
                    .collect();

                // Wait for all tasks with controlled concurrency
                let mut results = Vec::new();
                for task in tasks {
                    match task.await {
                        Ok(result) => results.push(result?),
                        Err(e) => return Err(pyo3::exceptions::PyRuntimeError::new_err(format!("Task failed: {}", e))),
                    }
                }
                Ok(results)
            })
        });

        let py_list = PyList::new(py, &results?)?;
        Ok(py_list.into())
    }

    /// Get the number of worker threads
    #[getter]
    pub fn max_workers(&self) -> usize {
        self.max_workers
    }

    /// Get runtime statistics for performance monitoring
    pub fn get_stats(&self) -> PyResult<Py<PyAny>> {
        Python::attach(|py| {
            let stats = pyo3::types::PyDict::new(py);
            stats.set_item("max_workers", self.max_workers)?;
            stats.set_item("available_permits", self.semaphore.available_permits())?;
            stats.set_item("runtime_type", "optimized_dual_runtime")?;
            stats.set_item("optimization_features", vec![
                "work_stealing", 
                "gil_optimization", 
                "dual_runtime",
                "task_batching",
                "semaphore_control"
            ])?;
            Ok(stats.into())
        })
    }

    /// Check if the executor is healthy and responsive
    pub fn health_check(&self) -> bool {
        // Basic health check - can be extended with more sophisticated metrics
        self.semaphore.available_permits() <= self.max_workers
    }

    /// Shutdown the async executor with proper cleanup
    pub fn shutdown(&self) {
        // Tokio runtimes will be dropped automatically
        // Additional cleanup can be added here if needed
    }
}

/// Wrapper for async tasks (simplified version)
#[pyclass]
pub struct AsyncTask {
    result: Option<Py<PyAny>>,
}

#[pymethods]
impl AsyncTask {
    #[new]
    pub fn new() -> Self {
        Self { result: None }
    }

    /// Check if the task is done
    pub fn done(&self) -> bool {
        self.result.is_some()
    }

    /// Get the result (blocking)
    pub fn result(&mut self, py: Python) -> PyResult<Py<PyAny>> {
        if let Some(result) = &self.result {
            Ok(result.clone_ref(py))
        } else {
            Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Task not completed",
            ))
        }
    }
}

/// Async parallel map function
#[pyfunction]
pub fn async_parallel_map(
    py: Python,
    func: Bound<PyAny>,
    data: Bound<PyAny>,
) -> PyResult<Py<PyList>> {
    let executor = AsyncExecutor::new(None)?;
    executor.map_async(py, func, data)
}

/// Async parallel filter function
#[pyfunction]
pub fn async_parallel_filter(
    py: Python,
    predicate: Bound<PyAny>,
    data: Bound<PyAny>,
) -> PyResult<Py<PyList>> {
    let items: Vec<Py<PyAny>> = data
        .try_iter()?
        .map(|item| item.map(|i| i.into()))
        .collect::<PyResult<Vec<_>>>()?;

    if items.is_empty() {
        return Ok(PyList::empty(py).into());
    }

    let pred_obj: Arc<Py<PyAny>> = Arc::new(predicate.into());

    let results: PyResult<Vec<Py<PyAny>>> = items
        .into_iter()
        .filter_map(|item| {
            let bound_pred = pred_obj.bind(py);
            let bound_item = item.bind(py);
            match bound_pred.call1((bound_item,)) {
                Ok(result) => match result.extract::<bool>() {
                    Ok(true) => Some(Ok(item)),
                    Ok(false) => None,
                    Err(_) => None,
                },
                Err(e) => Some(Err(e)),
            }
        })
        .collect();

    let py_list = PyList::new(py, results?)?;
    Ok(py_list.into())
}
