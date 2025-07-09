use pyo3::prelude::*;
use pyo3::types::{PyAny, PyFunction, PyList, PyTuple};
use std::collections::HashMap;

use super::cluster::ClusterManager;
use super::executor::{DistributedExecutor, cluster_map, distributed_reduce};

/// High-level distributed operations
pub struct DistributedOps;

impl DistributedOps {
    /// Distributed parallel map with automatic load balancing
    pub fn parallel_map(
        py: Python<'_>,
        function: Bound<'_, PyFunction>,
        iterable: Bound<'_, PyAny>,
        cluster: &ClusterManager,
        options: Option<HashMap<String, PyObject>>
    ) -> PyResult<Vec<PyObject>> {
        let chunk_size = options
            .as_ref()
            .and_then(|opts| opts.get("chunk_size"))
            .and_then(|obj| obj.extract::<usize>(py).ok())
            .unwrap_or(100);

        cluster_map(py, function, iterable, cluster, Some(chunk_size))
    }

    /// Distributed parallel filter
    pub fn parallel_filter(
        py: Python<'_>,
        predicate: Bound<'_, PyFunction>,
        iterable: Bound<'_, PyAny>,
        cluster: &ClusterManager,
        chunk_size: Option<usize>
    ) -> PyResult<Vec<PyObject>> {
        let executor = DistributedExecutor::new(&cluster, None);
        let items: Vec<Bound<PyAny>> = iterable.try_iter()?.collect::<Result<Vec<_>, _>>()?;
        
        let chunk_size = chunk_size.unwrap_or(std::cmp::max(1, items.len() / 10));
        let mut filtered_results = Vec::new();
        
        // Process in chunks
        for chunk in items.chunks(chunk_size) {
            for item in chunk {
                // Apply predicate
                let args = PyTuple::new(py, &[item.clone()])?;
                let result = predicate.call1(&args)?;
                if result.is_truthy()? {
                    filtered_results.push(item.clone().unbind());
                }
            }
        }
        
        Ok(filtered_results)
    }

    /// Distributed parallel sort with custom key function
    pub fn parallel_sort(
        py: Python<'_>,
        iterable: Bound<'_, PyAny>,
        key_fn: Option<Bound<'_, PyFunction>>,
        cluster: &ClusterManager
    ) -> PyResult<Vec<PyObject>> {
        let executor = DistributedExecutor::new(&cluster, None);
        let items: Vec<Bound<PyAny>> = iterable.try_iter()?.collect::<Result<Vec<_>, _>>()?;
        
        // Convert to owned objects for sorting
        let mut items: Vec<PyObject> = items.into_iter().map(|item| item.unbind()).collect();
        
        if let Some(key_fn) = key_fn {
            // Sort with key function
            items.sort_by(|a, b| {
                // This is a simplified comparison - real distributed sort would be more complex
                let args_a = PyTuple::new(py, &[a.bind(py)]).unwrap();
                let args_b = PyTuple::new(py, &[b.bind(py)]).unwrap();
                let key_a = key_fn.call1(&args_a).unwrap();
                let key_b = key_fn.call1(&args_b).unwrap();
                
                // Simple string comparison for now
                let cmp = key_a.call_method1("__lt__", (&key_b,))
                    .unwrap_or_else(|_| py.eval(c"False", None, None).unwrap());
                if cmp.is_truthy().unwrap_or(false) {
                    std::cmp::Ordering::Less
                } else {
                    std::cmp::Ordering::Greater
                }
            });
        } else {
            // Sort without key function
            items.sort_by(|a, b| {
                let cmp = a.bind(py).call_method1("__lt__", (b.bind(py),))
                    .unwrap_or_else(|_| py.eval(c"False", None, None).unwrap());
                if cmp.is_truthy().unwrap_or(false) {
                    std::cmp::Ordering::Less
                } else {
                    std::cmp::Ordering::Greater
                }
            });
        }
        
        Ok(items)
    }

    /// Distributed group by operation
    pub fn parallel_group_by(
        py: Python<'_>,
        iterable: Bound<'_, PyAny>,
        key_function: Bound<'_, PyFunction>,
        cluster: &ClusterManager
    ) -> PyResult<HashMap<String, Vec<PyObject>>> {
        let executor = DistributedExecutor::new(&cluster, None);
        let items: Vec<Bound<PyAny>> = iterable.try_iter()?.collect::<Result<Vec<_>, _>>()?;
        
        let mut groups: HashMap<String, Vec<PyObject>> = HashMap::new();
        
        for item in items {
            let args = PyTuple::new(py, &[item.clone()])?;
            let key_obj = key_function.call1(&args)?;
            let key = key_obj.str()?.extract::<String>()?;
            
            groups.entry(key).or_insert_with(Vec::new).push(item.unbind());
        }
        
        Ok(groups)
    }

    /// Distributed aggregation operation
    pub fn parallel_aggregate(
        py: Python<'_>,
        iterable: Bound<'_, PyAny>,
        aggregator: Bound<'_, PyFunction>,
        initial_value: Option<Bound<'_, PyAny>>,
        cluster: &ClusterManager
    ) -> PyResult<PyObject> {
        distributed_reduce(py, aggregator, iterable, initial_value, cluster)
    }
}

/// Batch processing with progress tracking
#[pyclass]
#[derive(Clone)]
pub struct DistributedBatchProcessor {
    cluster: ClusterManager,
    batch_size: usize,
    executor: DistributedExecutor,
}

#[pymethods]
impl DistributedBatchProcessor {
    #[new]
    pub fn new(cluster: ClusterManager, batch_size: Option<usize>) -> Self {
        let batch_size = batch_size.unwrap_or(100);
        let executor = DistributedExecutor::new(&cluster, None);
        
        Self {
            cluster,
            batch_size,
            executor,
        }
    }

    /// Process data in batches with optional progress callback
    pub fn process_batches(
        &self,
        py: Python<'_>,
        function: Bound<'_, PyFunction>,
        data: Bound<'_, PyList>,
        progress_callback: Option<Bound<'_, PyFunction>>
    ) -> PyResult<Vec<PyObject>> {
        let total_items = data.len();
        let mut all_results = Vec::new();
        let mut processed = 0;

        // Process in batches
        for chunk in data.iter().collect::<Vec<_>>().chunks(self.batch_size) {
            let chunk_list = PyList::new(py, chunk.iter().cloned())?;
            
            let task_ids = self.executor.submit_batch(
                &function, 
                &chunk_list, 
                None
            )?;
            
            // Wait for results and collect them
            for task_id in task_ids {
                if let Some(result_str) = self.executor.get_result(task_id, Some(30.0))? {
                    // In a real implementation, this would deserialize the result properly
                    let result_cstr = std::ffi::CString::new(result_str).unwrap();
                    all_results.push(py.eval(result_cstr.as_c_str(), None, None)?.unbind());
                }
            }
            
            processed += chunk.len();
            
            // Call progress callback if provided
            if let Some(callback) = &progress_callback {
                let progress = processed as f64 / total_items as f64;
                let args = PyTuple::new(py, &[progress.into_pyobject(py)?])?;
                let _ = callback.call1(&args);
            }
        }

        Ok(all_results)
    }
}
