use pyo3::prelude::*;
use pyo3::types::{PyFunction, PyList, PyTuple};

use super::cluster::ClusterManager;
use super::executor::DistributedExecutor;

/// Batch processing with progress tracking
#[pyclass]
#[derive(Clone)]
pub struct DistributedBatchProcessor {
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
        progress_callback: Option<Bound<'_, PyFunction>>,
    ) -> PyResult<Vec<Py<PyAny>>> {
        let total_items = data.len();
        let mut all_results = Vec::new();
        let mut processed = 0;

        // Process in batches
        for chunk in data.iter().collect::<Vec<_>>().chunks(self.batch_size) {
            let chunk_list = PyList::new(py, chunk.iter().cloned())?;

            let task_ids = self.executor.submit_batch(&function, &chunk_list, None)?;

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
