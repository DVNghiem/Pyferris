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
        use std::time::{Duration, Instant};
        
        let timeout_duration = timeout.map(|t| Duration::from_secs_f64(t))
            .unwrap_or(Duration::from_secs(300)); // Default 5-minute timeout
        
        let start_time = Instant::now();
        
        // Start task execution if not already running
        self.execute_task_if_needed(&task_id)?;
        
        // Poll for result with timeout
        loop {
            {
                let results = self.results.lock().unwrap();
                if let Some(result) = results.get(&task_id) {
                    return if result.success {
                        Ok(result.result.clone())
                    } else {
                        Err(ParallelExecutionError::new_err(
                            result.error.clone().unwrap_or_else(|| "Unknown error".to_string())
                        ))
                    };
                }
            }
            
            // Check timeout
            if start_time.elapsed() > timeout_duration {
                return Err(pyo3::exceptions::PyTimeoutError::new_err(
                    format!("Task {} timed out after {:.2} seconds", task_id, timeout_duration.as_secs_f64())
                ));
            }
            
            // Sleep before next check
            std::thread::sleep(Duration::from_millis(100));
        }
    }

    /// Wait for all submitted tasks to complete
    pub fn wait_for_all(&self, timeout: Option<f64>) -> PyResult<HashMap<String, String>> {
        use std::time::{Duration, Instant};
        
        let timeout_duration = timeout.map(|t| Duration::from_secs_f64(t))
            .unwrap_or(Duration::from_secs(600)); // Default 10-minute timeout
        
        let start_time = Instant::now();
        
        // Get all task IDs to wait for
        let task_ids: Vec<String> = {
            let tasks = self.tasks.lock().unwrap();
            tasks.keys().cloned().collect()
        };
        
        // Start execution for all pending tasks
        for task_id in &task_ids {
            self.execute_task_if_needed(task_id)?;
        }
        
        // Poll for all results
        loop {
            let mut all_results = HashMap::new();
            let mut completed_count = 0;
            
            {
                let results = self.results.lock().unwrap();
                for task_id in &task_ids {
                    if let Some(result) = results.get(task_id) {
                        completed_count += 1;
                        if result.success {
                            all_results.insert(task_id.clone(), result.result.clone().unwrap_or_default());
                        } else {
                            // For failed tasks, include error information
                            all_results.insert(
                                task_id.clone(), 
                                format!("ERROR: {}", result.error.as_ref().unwrap_or(&"Unknown error".to_string()))
                            );
                        }
                    }
                }
            }
            
            // All tasks completed
            if completed_count == task_ids.len() {
                return Ok(all_results);
            }
            
            // Check timeout
            if start_time.elapsed() > timeout_duration {
                return Err(pyo3::exceptions::PyTimeoutError::new_err(
                    format!("Batch execution timed out after {:.2} seconds. {}/{} tasks completed", 
                        timeout_duration.as_secs_f64(), completed_count, task_ids.len())
                ));
            }
            
            // Sleep before next check
            std::thread::sleep(Duration::from_millis(200));
        }
    }

    /// Cancel a task
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

impl DistributedExecutor {
    /// Execute a task if it's not already running
    fn execute_task_if_needed(&self, task_id: &str) -> PyResult<()> {
        // Check if task is already running or completed
        {
            let tasks = self.tasks.lock().unwrap();
            if let Some((_, status)) = tasks.get(task_id) {
                match status {
                    TaskStatus::Running | TaskStatus::Completed => {
                        return Ok(()); // Already running or completed
                    }
                    _ => {}
                }
            } else {
                return Err(pyo3::exceptions::PyKeyError::new_err("Task not found"));
            }
        }
        
        // Start task execution
        self.execute_task(task_id)?;
        Ok(())
    }
    
    /// Execute a task on a selected node
    fn execute_task(&self, task_id: &str) -> PyResult<()> {
        // Get task details
        let (task, _) = {
            let tasks = self.tasks.lock().unwrap();
            match tasks.get(task_id) {
                Some((task, _)) => (task.clone(), ()),
                None => return Err(pyo3::exceptions::PyKeyError::new_err("Task not found")),
            }
        };
        
        // Update task status to running
        {
            let mut tasks = self.tasks.lock().unwrap();
            if let Some((_, status)) = tasks.get_mut(task_id) {
                *status = TaskStatus::Running;
            }
        }
        
        // Select node for execution
        let cluster = self.cluster.lock().unwrap();
        let selected_node = self.load_balancer.select_node(&cluster, Some(task.requirements.clone()))?;
        drop(cluster);
        
        // Execute task (simplified implementation)
        let result = self.execute_task_on_node(&task, selected_node)?;
        
        // Store result
        {
            let mut results = self.results.lock().unwrap();
            results.insert(task_id.to_string(), result);
        }
        
        // Update task status to completed
        {
            let mut tasks = self.tasks.lock().unwrap();
            if let Some((_, status)) = tasks.get_mut(task_id) {
                *status = TaskStatus::Completed;
            }
        }
        
        Ok(())
    }
    
    /// Execute a task on a specific node
    fn execute_task_on_node(&self, task: &DistributedTask, node_id: Option<String>) -> PyResult<TaskResult> {
        use std::time::Instant;
        
        let start_time = Instant::now();
        
        // In a real implementation, this would send the task to the remote node
        // For now, we'll simulate execution locally
        let result = match task.function_name.as_str() {
            "sum" => {
                // Parse arguments and compute sum
                let numbers: Result<Vec<f64>, _> = task.args.iter()
                    .map(|arg| arg.parse::<f64>())
                    .collect();
                
                match numbers {
                    Ok(nums) => {
                        let sum: f64 = nums.iter().sum();
                        TaskResult {
                            task_id: task.id.clone(),
                            result: Some(sum.to_string()),
                            success: true,
                            error: None,
                            execution_time: start_time.elapsed().as_secs_f64(),
                            node_id: node_id.unwrap_or_else(|| "local".to_string()),
                        }
                    }
                    Err(e) => {
                        TaskResult {
                            task_id: task.id.clone(),
                            result: None,
                            success: false,
                            error: Some(format!("Argument parsing error: {}", e)),
                            execution_time: start_time.elapsed().as_secs_f64(),
                            node_id: node_id.unwrap_or_else(|| "local".to_string()),
                        }
                    }
                }
            }
            "multiply" => {
                // Parse two arguments and multiply
                if task.args.len() >= 2 {
                    let a: Result<f64, _> = task.args[0].parse();
                    let b: Result<f64, _> = task.args[1].parse();
                    
                    match (a, b) {
                        (Ok(a), Ok(b)) => {
                            TaskResult {
                                task_id: task.id.clone(),
                                result: Some((a * b).to_string()),
                                success: true,
                                error: None,
                                execution_time: start_time.elapsed().as_secs_f64(),
                                node_id: node_id.unwrap_or_else(|| "local".to_string()),
                            }
                        }
                        _ => {
                            TaskResult {
                                task_id: task.id.clone(),
                                result: None,
                                success: false,
                                error: Some("Invalid arguments for multiply".to_string()),
                                execution_time: start_time.elapsed().as_secs_f64(),
                                node_id: node_id.unwrap_or_else(|| "local".to_string()),
                            }
                        }
                    }
                } else {
                    TaskResult {
                        task_id: task.id.clone(),
                        result: None,
                        success: false,
                        error: Some("Insufficient arguments for multiply".to_string()),
                        execution_time: start_time.elapsed().as_secs_f64(),
                        node_id: node_id.unwrap_or_else(|| "local".to_string()),
                    }
                }
            }
            "heavy_computation" => {
                // Simulate heavy computation
                let mut total = 0.0;
                for i in 0..1000000 {
                    total += (i as f64).sin();
                }
                
                TaskResult {
                    task_id: task.id.clone(),
                    result: Some(total.to_string()),
                    success: true,
                    error: None,
                    execution_time: start_time.elapsed().as_secs_f64(),
                    node_id: node_id.unwrap_or_else(|| "local".to_string()),
                }
            }
            _ => {
                TaskResult {
                    task_id: task.id.clone(),
                    result: None,
                    success: false,
                    error: Some(format!("Unknown function: {}", task.function_name)),
                    execution_time: start_time.elapsed().as_secs_f64(),
                    node_id: node_id.unwrap_or_else(|| "local".to_string()),
                }
            }
        };
        
        Ok(result)
    }
    
    /// Get comprehensive cluster and execution statistics
    pub fn get_execution_stats(&self) -> PyResult<HashMap<String, f64>> {
        let tasks = self.tasks.lock().unwrap();
        let results = self.results.lock().unwrap();
        
        let mut stats = HashMap::new();
        
        // Task statistics
        stats.insert("total_tasks".to_string(), tasks.len() as f64);
        stats.insert("completed_tasks".to_string(), results.len() as f64);
        
        // Status counts
        let mut pending = 0;
        let mut running = 0;
        let mut completed = 0;
        
        for (_, status) in tasks.values() {
            match status {
                TaskStatus::Pending => pending += 1,
                TaskStatus::Running => running += 1,
                TaskStatus::Completed => completed += 1,
                _ => {}
            }
        }
        
        stats.insert("pending_tasks".to_string(), pending as f64);
        stats.insert("running_tasks".to_string(), running as f64);
        stats.insert("completed_tasks_status".to_string(), completed as f64);
        
        // Success rate
        let successful = results.values().filter(|r| r.success).count() as f64;
        let total_results = results.len() as f64;
        
        if total_results > 0.0 {
            stats.insert("success_rate".to_string(), successful / total_results);
        }
        
        // Average execution time
        if !results.is_empty() {
            let avg_time: f64 = results.values()
                .map(|r| r.execution_time)
                .sum::<f64>() / results.len() as f64;
            stats.insert("avg_execution_time".to_string(), avg_time);
        }
        
        Ok(stats)
    }
    
    /// Cancel a pending or running task
    pub fn cancel_task(&self, task_id: String) -> PyResult<bool> {
        let mut tasks = self.tasks.lock().unwrap();
        
        if let Some((_, status)) = tasks.get_mut(&task_id) {
            match status {
                TaskStatus::Pending | TaskStatus::Running => {
                    *status = TaskStatus::Cancelled;
                    Ok(true)
                }
                _ => Ok(false) // Already completed or cancelled
            }
        } else {
            Err(pyo3::exceptions::PyKeyError::new_err("Task not found"))
        }
    }
    
    /// Clear completed tasks and results to free memory
    pub fn cleanup_completed_tasks(&self) -> PyResult<usize> {
        let mut tasks = self.tasks.lock().unwrap();
        let mut results = self.results.lock().unwrap();
        
        // Find completed tasks
        let completed_tasks: Vec<String> = tasks
            .iter()
            .filter(|(_, (_, status))| matches!(status, TaskStatus::Completed))
            .map(|(id, _)| id.clone())
            .collect();
        
        // Remove completed tasks and their results
        for task_id in &completed_tasks {
            tasks.remove(task_id);
            results.remove(task_id);
        }
        
        Ok(completed_tasks.len())
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
    let _executor = DistributedExecutor::new(cluster_manager, None);
    
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
    _cluster_manager: &ClusterManager
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
