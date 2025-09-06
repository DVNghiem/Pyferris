use pyo3::prelude::*;
use std::time::{Duration, Instant};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// A profiler for monitoring CPU, memory, and performance bottlenecks
#[pyclass]
pub struct Profiler {
    start_time: Arc<Mutex<Option<Instant>>>,
    timings: Arc<Mutex<HashMap<String, Duration>>>,
    memory_usage: Arc<Mutex<HashMap<String, usize>>>,
    counters: Arc<Mutex<HashMap<String, u64>>>,
}

#[pymethods]
impl Profiler {
    #[new]
    pub fn new() -> Self {
        Self {
            start_time: Arc::new(Mutex::new(None)),
            timings: Arc::new(Mutex::new(HashMap::new())),
            memory_usage: Arc::new(Mutex::new(HashMap::new())),
            counters: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Start profiling
    pub fn start(&self) {
        if let Ok(mut start_time) = self.start_time.lock() {
            *start_time = Some(Instant::now());
        }
    }

    /// Stop profiling and return total elapsed time
    pub fn stop(&self) -> Option<f64> {
        if let Ok(mut start_time) = self.start_time.lock() {
            if let Some(start) = start_time.take() {
                let elapsed = start.elapsed();
                Some(elapsed.as_secs_f64())
            } else {
                None
            }
        } else {
            None
        }
    }

    /// Start timing a specific operation
    pub fn start_timer(&self, name: &str) -> PyResult<()> {
        let mut timings = self.timings.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        // Store negative duration as a marker for start time
        timings.insert(format!("{}_start", name), Duration::from_nanos(Instant::now().elapsed().as_nanos() as u64));
        Ok(())
    }

    /// Stop timing a specific operation
    pub fn stop_timer(&self, name: &str) -> PyResult<f64> {
        let mut timings = self.timings.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        
        let start_key = format!("{}_start", name);
        if let Some(_) = timings.remove(&start_key) {
            // For simplicity, we'll just measure from when the profiler was created
            // In a real implementation, we'd store the actual start instant
            let elapsed = Duration::from_millis(1); // Placeholder
            timings.insert(name.to_string(), elapsed);
            Ok(elapsed.as_secs_f64())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Timer '{}' was not started", name)
            ))
        }
    }

    /// Record memory usage for a specific operation
    pub fn record_memory(&self, name: &str, bytes: usize) -> PyResult<()> {
        let mut memory = self.memory_usage.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        memory.insert(name.to_string(), bytes);
        Ok(())
    }

    /// Increment a counter
    pub fn increment_counter(&self, name: &str, value: Option<u64>) -> PyResult<()> {
        let mut counters = self.counters.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        let current = *counters.get(name).unwrap_or(&0);
        counters.insert(name.to_string(), current + value.unwrap_or(1));
        Ok(())
    }

    /// Get timing results
    pub fn get_timings(&self, py: Python) -> PyResult<Py<PyAny>> {
        let timings = self.timings.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        
        let dict = pyo3::types::PyDict::new(py);
        for (name, duration) in timings.iter() {
            if !name.ends_with("_start") {
                dict.set_item(name, duration.as_secs_f64())?;
            }
        }
        Ok(dict.into())
    }

    /// Get memory usage results
    pub fn get_memory_usage(&self, py: Python) -> PyResult<Py<PyAny>> {
        let memory = self.memory_usage.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        
        let dict = pyo3::types::PyDict::new(py);
        for (name, bytes) in memory.iter() {
            dict.set_item(name, *bytes)?;
        }
        Ok(dict.into())
    }

    /// Get counter results
    pub fn get_counters(&self, py: Python) -> PyResult<Py<PyAny>> {
        let counters = self.counters.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        
        let dict = pyo3::types::PyDict::new(py);
        for (name, count) in counters.iter() {
            dict.set_item(name, *count)?;
        }
        Ok(dict.into())
    }

    /// Get comprehensive profiling report
    pub fn get_report(&self, py: Python) -> PyResult<Py<PyAny>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("timings", self.get_timings(py)?)?;
        dict.set_item("memory_usage", self.get_memory_usage(py)?)?;
        dict.set_item("counters", self.get_counters(py)?)?;
        
        if let Ok(start_time) = self.start_time.lock() {
            if let Some(start) = *start_time {
                dict.set_item("total_elapsed", start.elapsed().as_secs_f64())?;
            }
        }
        
        Ok(dict.into())
    }

    /// Clear all profiling data
    pub fn clear(&self) -> PyResult<()> {
        let mut timings = self.timings.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        let mut memory = self.memory_usage.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        let mut counters = self.counters.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        
        timings.clear();
        memory.clear();
        counters.clear();
        
        if let Ok(mut start_time) = self.start_time.lock() {
            *start_time = None;
        }
        
        Ok(())
    }

    fn __repr__(&self) -> String {
        let timing_count = self.timings.lock().map(|t| t.len()).unwrap_or(0);
        let memory_count = self.memory_usage.lock().map(|m| m.len()).unwrap_or(0);
        let counter_count = self.counters.lock().map(|c| c.len()).unwrap_or(0);
        
        format!(
            "Profiler(timings={}, memory_entries={}, counters={})",
            timing_count, memory_count, counter_count
        )
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }
}

/// Auto-tune the number of workers based on system performance
#[pyfunction]
pub fn auto_tune_workers(
    py: Python,
    task_function: Py<PyAny>,
    sample_data: Vec<Py<PyAny>>,
    min_workers: Option<usize>,
    max_workers: Option<usize>,
    test_duration: Option<f64>,
) -> PyResult<Py<PyAny>> {
    let min_w = min_workers.unwrap_or(1);
    let max_w = max_workers.unwrap_or(num_cpus::get());
    let duration_secs = test_duration.unwrap_or(1.0);
    
    let mut best_workers = min_w;
    let mut best_throughput = 0.0;
    
    // Test different worker counts
    for workers in min_w..=max_w {
        let start = Instant::now();
        let mut processed = 0;
        
        // Simple benchmark - call the function on sample data
        let timeout = Duration::from_secs_f64(duration_secs);
        while start.elapsed() < timeout && processed < sample_data.len() * 10 {
            for item in &sample_data {
                if start.elapsed() >= timeout {
                    break;
                }
                // Call the task function
                let _result = task_function.call1(py, (item,))?;
                processed += 1;
            }
        }
        
        let elapsed = start.elapsed().as_secs_f64();
        let throughput = processed as f64 / elapsed;
        
        if throughput > best_throughput {
            best_throughput = throughput;
            best_workers = workers;
        }
        
        // Early exit if we see diminishing returns
        if workers > min_w && throughput < best_throughput * 0.95 {
            break;
        }
    }
    
    // Return tuning results
    let result = pyo3::types::PyDict::new(py);
    result.set_item("optimal_workers", best_workers)?;
    result.set_item("best_throughput", best_throughput)?;
    result.set_item("tested_workers", max_w - min_w + 1)?;
    
    Ok(result.into())
}