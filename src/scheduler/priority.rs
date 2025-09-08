use pyo3::prelude::*;
use rayon::prelude::*;
use std::cmp::Ordering;
use std::collections::BinaryHeap;
use std::sync::{Arc, Mutex};

/// Task priority levels
#[pyclass]
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum TaskPriority {
    Low = 0,
    Normal = 1,
    High = 2,
    Critical = 3,
}

#[pymethods]
impl TaskPriority {
    #[new]
    pub fn new() -> Self {
        TaskPriority::Normal
    }

    /// Create from integer value
    #[classmethod]
    pub fn from_int(_cls: &Bound<'_, pyo3::types::PyType>, value: i32) -> Self {
        match value {
            0 => TaskPriority::Low,
            1 => TaskPriority::Normal,
            2 => TaskPriority::High,
            3 => TaskPriority::Critical,
            _ => TaskPriority::Normal,
        }
    }

    /// Convert to integer
    pub fn to_int(&self) -> i32 {
        *self as i32
    }

    fn __repr__(&self) -> String {
        format!("TaskPriority.{:?}", self)
    }
}

impl PartialOrd for TaskPriority {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for TaskPriority {
    fn cmp(&self, other: &Self) -> Ordering {
        (*self as i32).cmp(&(*other as i32))
    }
}

/// Task with priority
#[derive(Clone)]
pub struct PriorityTask {
    task: Arc<Py<PyAny>>,
    priority: TaskPriority,
    id: usize,
}

impl PriorityTask {
    pub fn new(task: Arc<Py<PyAny>>, priority: TaskPriority, id: usize) -> Self {
        Self { task, priority, id }
    }
}

impl PartialEq for PriorityTask {
    fn eq(&self, other: &Self) -> bool {
        self.priority == other.priority && self.id == other.id
    }
}

impl Eq for PriorityTask {}

impl PartialOrd for PriorityTask {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for PriorityTask {
    fn cmp(&self, other: &Self) -> Ordering {
        // Higher priority first, then by id for stability
        match self.priority.cmp(&other.priority) {
            Ordering::Equal => other.id.cmp(&self.id), // Reverse order for FIFO within same priority
            other => other,                            // Higher priority first
        }
    }
}

/// Priority scheduler for task execution
#[pyclass]
pub struct PriorityScheduler {
    workers: usize,
    task_queue: Arc<Mutex<BinaryHeap<PriorityTask>>>,
    next_id: Arc<Mutex<usize>>,
}

#[pymethods]
impl PriorityScheduler {
    #[new]
    #[pyo3(signature = (workers = None))]
    pub fn new(workers: Option<usize>) -> Self {
        let num_workers = workers.unwrap_or_else(|| num_cpus::get());

        Self {
            workers: num_workers,
            task_queue: Arc::new(Mutex::new(BinaryHeap::new())),
            next_id: Arc::new(Mutex::new(0)),
        }
    }

    /// Add task with priority
    pub fn add_task(&self, task: Bound<PyAny>, priority: Option<TaskPriority>) -> PyResult<usize> {
        let priority = priority.unwrap_or(TaskPriority::Normal);
        let mut id_counter = self.next_id.lock().unwrap();
        let task_id = *id_counter;
        *id_counter += 1;
        drop(id_counter);

        let priority_task = PriorityTask::new(Arc::new(task.into()), priority, task_id);

        let mut queue = self.task_queue.lock().unwrap();
        queue.push(priority_task);

        Ok(task_id)
    }

    /// Execute tasks in priority order
    pub fn execute(
        &self,
        py: Python,
        tasks_with_priorities: Vec<(Bound<PyAny>, Option<TaskPriority>)>,
    ) -> PyResult<Vec<Py<PyAny>>> {
        if tasks_with_priorities.is_empty() {
            return Ok(Vec::new());
        }

        // Add all tasks to priority queue
        let mut priority_tasks = Vec::new();
        for (i, (task, priority)) in tasks_with_priorities.into_iter().enumerate() {
            let priority = priority.unwrap_or(TaskPriority::Normal);
            let priority_task = PriorityTask::new(Arc::new(task.into()), priority, i);
            priority_tasks.push(priority_task);
        }

        // Sort by priority (highest first)
        priority_tasks.sort_by(|a, b| b.cmp(a));

        // Execute tasks in priority order using parallel processing within each priority level
        let mut results: Vec<Option<Py<PyAny>>> = (0..priority_tasks.len()).map(|_| None).collect();
        let mut current_priority = None;
        let mut priority_group = Vec::new();
        let mut group_indices = Vec::new();

        // Group tasks by priority
        for priority_task in priority_tasks {
            if current_priority != Some(priority_task.priority) {
                if !priority_group.is_empty() {
                    // Execute current priority group
                    self.execute_priority_group(py, &priority_group, &group_indices, &mut results)?;
                    priority_group.clear();
                    group_indices.clear();
                }
                current_priority = Some(priority_task.priority);
            }

            group_indices.push(priority_task.id);
            priority_group.push(priority_task.task.clone());
        }

        // Execute the last priority group
        if !priority_group.is_empty() {
            self.execute_priority_group(py, &priority_group, &group_indices, &mut results)?;
        }

        // Collect results in original order
        Ok(results.into_iter().map(|r| r.unwrap()).collect())
    }

    /// Execute all tasks in queue
    pub fn execute_queue(&self, py: Python) -> PyResult<Vec<Py<PyAny>>> {
        let mut queue = self.task_queue.lock().unwrap();
        if queue.is_empty() {
            return Ok(Vec::new());
        }

        // Extract all tasks
        let mut tasks = Vec::new();
        while let Some(priority_task) = queue.pop() {
            tasks.push(priority_task);
        }
        drop(queue);

        // Execute tasks in priority order
        let mut results: Vec<Option<Py<PyAny>>> = (0..tasks.len()).map(|_| None).collect();
        let mut current_priority = None;
        let mut priority_group = Vec::new();
        let mut group_indices = Vec::new();

        for priority_task in tasks {
            if current_priority != Some(priority_task.priority) {
                if !priority_group.is_empty() {
                    // Execute current priority group
                    self.execute_priority_group(py, &priority_group, &group_indices, &mut results)?;
                    priority_group.clear();
                    group_indices.clear();
                }
                current_priority = Some(priority_task.priority);
            }

            group_indices.push(priority_task.id);
            priority_group.push(priority_task.task.clone());
        }

        // Execute the last priority group
        if !priority_group.is_empty() {
            self.execute_priority_group(py, &priority_group, &group_indices, &mut results)?;
        }

        Ok(results.into_iter().map(|r| r.unwrap()).collect())
    }

    /// Get number of workers
    #[getter]
    pub fn workers(&self) -> usize {
        self.workers
    }

    /// Get number of pending tasks
    pub fn pending_tasks(&self) -> usize {
        let queue = self.task_queue.lock().unwrap();
        queue.len()
    }

    /// Clear all pending tasks
    pub fn clear(&self) {
        let mut queue = self.task_queue.lock().unwrap();
        queue.clear();
    }
}

// Internal implementation for PriorityScheduler
impl PriorityScheduler {
    /// Execute a group of tasks with the same priority
    fn execute_priority_group(
        &self,
        py: Python,
        tasks: &[Arc<Py<PyAny>>],
        indices: &[usize],
        results: &mut Vec<Option<Py<PyAny>>>,
    ) -> PyResult<()> {
        // Execute tasks in parallel within the same priority group
        let group_results: PyResult<Vec<Py<PyAny>>> = py.detach(|| {
            tasks
                .par_iter()
                .map(|task| {
                    Python::attach(|py| {
                        let bound_task = task.bind(py);
                        bound_task.call0().map(|r| r.into())
                    })
                })
                .collect()
        });

        let group_results = group_results?;

        // Store results at their original indices
        for (i, &original_idx) in indices.iter().enumerate() {
            if let Some(result) = group_results.get(i) {
                results[original_idx] = Some(result.clone_ref(py));
            }
        }

        Ok(())
    }
}

/// Helper function to execute tasks with priorities
#[pyfunction]
pub fn execute_with_priority(
    py: Python,
    tasks_with_priorities: Vec<(Bound<PyAny>, Option<TaskPriority>)>,
    workers: Option<usize>,
) -> PyResult<Vec<Py<PyAny>>> {
    let scheduler = PriorityScheduler::new(workers);
    scheduler.execute(py, tasks_with_priorities)
}

/// Helper function to create priority tasks
#[pyfunction]
pub fn create_priority_task(
    task: Bound<PyAny>,
    priority: Option<TaskPriority>,
) -> (Py<PyAny>, Option<TaskPriority>) {
    (task.into(), priority)
}
