use pyo3::prelude::*;
use pyo3::types::{PyAny, PyFunction, PyList, PyTuple};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use uuid::Uuid;

use super::cluster::{ClusterManager, LoadBalancer};
use crate::error::ParallelExecutionError;

/// Task to be executed in distributed environment
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DistributedTask {
    pub id: String,
    pub function_name: String,
    pub args: Vec<String>, // Serialized arguments
    pub node_id: Option<String>,
    pub priority: u8,
    pub requirements: HashMap<String, f64>,
}

/// Result of a distributed task execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskResult {
    pub task_id: String,
    pub success: bool,
    pub result: Option<String>, // Serialized result
    pub error: Option<String>,
    pub execution_time: f64,
    pub node_id: String,
}

/// Status of a distributed task
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TaskStatus {
    Pending,
    Assigned,
    Running,
    Completed,
    Failed,
    Cancelled,
}

/// Distributed executor for running tasks across a cluster
#[pyclass]
#[derive(Clone)]
pub struct DistributedExecutor {
    cluster: Arc<Mutex<ClusterManager>>,
    load_balancer: LoadBalancer,
    tasks: Arc<Mutex<HashMap<String, (DistributedTask, TaskStatus)>>>,
    results: Arc<Mutex<HashMap<String, TaskResult>>>,
}

#[pymethods]
impl DistributedExecutor {
    #[new]
    pub fn new(cluster_manager: &ClusterManager, load_balancer: Option<&LoadBalancer>) -> Self {
        let load_balancer = load_balancer.cloned().unwrap_or_else(|| LoadBalancer::new(None));
        
        Self {
            cluster: Arc::new(Mutex::new(cluster_manager.clone())),
            load_balancer,
            tasks: Arc::new(Mutex::new(HashMap::new())),
            results: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Submit a task for distributed execution
    pub fn submit_task(
        &self, 
        function: &Bound<'_, PyFunction>,
        args: &Bound<'_, PyTuple>,
        requirements: Option<HashMap<String, f64>>
    ) -> PyResult<String> {
        let task_id = Uuid::new_v4().to_string();
        
        // Serialize function and arguments (simplified)
        let function_name = function.getattr("__name__")?.extract::<String>()?;
        let serialized_args: Vec<String> = args.iter()
            .map(|arg| format!("{:?}", arg)) // Simplified serialization
            .collect();

        let task = DistributedTask {
            id: task_id.clone(),
            function_name,
            args: serialized_args,
            node_id: None,
            priority: 5, // Default priority
            requirements: requirements.unwrap_or_default(),
        };

        // Select a node for the task
        let cluster = self.cluster.lock().unwrap();
        let selected_node = self.load_balancer.select_node(&cluster, task.requirements.clone().into())?;
        drop(cluster);

        let mut tasks = self.tasks.lock().unwrap();
        tasks.insert(task_id.clone(), (task, TaskStatus::Pending));

        Ok(task_id)
    }

    /// Submit multiple tasks in batch
    pub fn submit_batch(
        &self,
        function: &Bound<'_, PyFunction>,
        args_list: &Bound<'_, PyList>,
        requirements: Option<HashMap<String, f64>>
    ) -> PyResult<Vec<String>> {
        let mut task_ids = Vec::new();
        
        for args in args_list.iter() {
            let args_tuple = args.downcast::<PyTuple>()?;
            let task_id = self.submit_task(function, args_tuple, requirements.clone())?;
            task_ids.push(task_id);
        }

        Ok(task_ids)
    }

    /// Get task status
    pub fn get_task_status(&self, task_id: String) -> PyResult<String> {
        let tasks = self.tasks.lock().unwrap();
        if let Some((_, status)) = tasks.get(&task_id) {
            let status_str = match status {
                TaskStatus::Pending => "pending",
                TaskStatus::Assigned => "assigned", 
                TaskStatus::Running => "running",
                TaskStatus::Completed => "completed",
                TaskStatus::Failed => "failed",
                TaskStatus::Cancelled => "cancelled",
            };
            Ok(status_str.to_string())
        } else {
            Err(pyo3::exceptions::PyKeyError::new_err("Task not found"))
        }
    }

    /// Get task result (blocking)
    pub fn get_result(&self, task_id: String, timeout: Option<f64>) -> PyResult<Option<String>> {
        // TODO: Implement timeout and actual distributed execution
        let results = self.results.lock().unwrap();
        if let Some(result) = results.get(&task_id) {
            if result.success {
                Ok(result.result.clone())
            } else {
                Err(ParallelExecutionError::new_err(
                    result.error.clone().unwrap_or_else(|| "Unknown error".to_string())
                ))
            }
        } else {
            Ok(None)
        }
    }

    /// Wait for all submitted tasks to complete
    pub fn wait_for_all(&self, timeout: Option<f64>) -> PyResult<HashMap<String, String>> {
        // TODO: Implement actual waiting logic with timeout
        let results = self.results.lock().unwrap();
        let mut all_results = HashMap::new();
        
        for (task_id, result) in results.iter() {
            if result.success {
                all_results.insert(task_id.clone(), result.result.clone().unwrap_or_default());
            }
        }

        Ok(all_results)
    }

    /// Cancel a task
    pub fn cancel_task(&self, task_id: String) -> PyResult<bool> {
        let mut tasks = self.tasks.lock().unwrap();
        if let Some((_, status)) = tasks.get_mut(&task_id) {
            match status {
                TaskStatus::Pending | TaskStatus::Assigned => {
                    *status = TaskStatus::Cancelled;
                    Ok(true)
                }
                _ => Ok(false) // Cannot cancel running/completed tasks
            }
        } else {
            Ok(false)
        }
    }

    /// Get execution statistics
    pub fn get_stats(&self) -> PyResult<HashMap<String, f64>> {
        let tasks = self.tasks.lock().unwrap();
        let results = self.results.lock().unwrap();
        
        let total_tasks = tasks.len() as f64;
        let completed_tasks = tasks.values()
            .filter(|(_, status)| matches!(status, TaskStatus::Completed))
            .count() as f64;
        let failed_tasks = tasks.values()
            .filter(|(_, status)| matches!(status, TaskStatus::Failed))
            .count() as f64;
        
        let avg_execution_time = if !results.is_empty() {
            results.values()
                .map(|r| r.execution_time)
                .sum::<f64>() / results.len() as f64
        } else {
            0.0
        };

        let mut stats = HashMap::new();
        stats.insert("total_tasks".to_string(), total_tasks);
        stats.insert("completed_tasks".to_string(), completed_tasks);
        stats.insert("failed_tasks".to_string(), failed_tasks);
        stats.insert("success_rate".to_string(), 
                    if total_tasks > 0.0 { completed_tasks / total_tasks } else { 0.0 });
        stats.insert("average_execution_time".to_string(), avg_execution_time);

        Ok(stats)
    }
}

/// Distributed Map operation
#[pyfunction]
pub fn cluster_map(
    py: Python<'_>,
    function: Bound<'_, PyFunction>,
    iterable: Bound<'_, PyAny>,
    cluster_manager: &ClusterManager,
    chunk_size: Option<usize>
) -> PyResult<Vec<PyObject>> {
    let executor = DistributedExecutor::new(cluster_manager, None);
    
    // Convert iterable to Vec
    let items: Vec<Bound<PyAny>> = iterable.try_iter()?.collect::<Result<Vec<_>, _>>()?;
    
    let chunk_size = chunk_size.unwrap_or(std::cmp::max(1, items.len() / 10));
    let mut results = Vec::new();
    
    // Process in chunks (simplified for now)
    for chunk in items.chunks(chunk_size) {
        for item in chunk {
            // For now, just call the function directly (in real distributed version, would be remote)
            let args = PyTuple::new(py, &[item.clone()])?;
            let result = function.call1(&args)?;
            results.push(result.unbind());
        }
    }
    
    Ok(results)
}

/// Distributed Reduce operation  
#[pyfunction]
pub fn distributed_reduce(
    py: Python<'_>,
    function: Bound<'_, PyFunction>,
    iterable: Bound<'_, PyAny>,
    initializer: Option<Bound<'_, PyAny>>,
    cluster_manager: &ClusterManager
) -> PyResult<PyObject> {
    // Convert to list for easier handling
    let items: Vec<Bound<PyAny>> = iterable.try_iter()?.collect::<Result<Vec<_>, _>>()?;
    
    if items.is_empty() {
        return match initializer {
            Some(init) => Ok(init.unbind()),
            None => Err(pyo3::exceptions::PyValueError::new_err("reduce() of empty sequence with no initial value"))
        };
    }

    // For distributed reduce, we need to implement tree reduction
    // This is a simplified version - real implementation would distribute across nodes
    let mut result = initializer.as_ref().map(|init| init.clone().unbind())
        .unwrap_or_else(|| items[0].clone().unbind());
    
    let start_idx = if initializer.is_some() { 0 } else { 1 };
    
    for item in &items[start_idx..] {
        let args = PyTuple::new(py, &[result.bind(py), &item.clone()])?;
        result = function.call1(&args)?.unbind();
    }

    Ok(result)
}
