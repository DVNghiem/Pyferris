use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};
use rayon::prelude::*;
use std::sync::Arc;

/// Task executor for managing parallel tasks
#[pyclass]
pub struct Executor {
    #[pyo3(get, set)]
    pub max_workers: usize,
    thread_pool: Option<rayon::ThreadPool>,
}

#[pymethods]
impl Executor {
    #[new]
    #[pyo3(signature = (max_workers = None))]
    pub fn new(max_workers: Option<usize>) -> PyResult<Self> {
        let max_workers = max_workers.unwrap_or_else(|| rayon::current_num_threads());
        
        // Create a custom thread pool with the specified number of workers
        let thread_pool = rayon::ThreadPoolBuilder::new()
            .num_threads(max_workers)
            .build()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create thread pool: {}", e)))?;
        
        Ok(Self {
            max_workers,
            thread_pool: Some(thread_pool),
        })
    }

    /// Submit a single task with explicit arguments (runs immediately for compatibility)
    pub fn submit_with_args(&self, func: Bound<PyAny>, args: Bound<PyTuple>) -> PyResult<PyObject> {
        // For individual tasks, we run them immediately to maintain compatibility
        // with concurrent.futures interface expectations
        let result = func.call1(&args)?;
        Ok(result.into())
    }

    /// Submit a single task (for compatibility with asyncio.run_in_executor)
    pub fn submit(&self, func: Bound<PyAny>) -> PyResult<PyObject> {
        // For individual tasks, we run them immediately
        let result = func.call0()?;
        Ok(result.into())
    }

    /// Submit multiple tasks and collect results
    pub fn map(&self, func: Bound<PyAny>, iterable: Bound<PyAny>) -> PyResult<Py<PyList>> {
        let py = func.py();
        // Convert to PyObjects to avoid Sync issues
        let items: Vec<PyObject> = iterable.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
        
        if items.is_empty() {
            return Ok(PyList::empty(py).into());
        }
        
        let func: Arc<PyObject> = Arc::new(func.into());
        
        // Use our custom thread pool if available, otherwise fall back to global pool
        let results: Vec<PyObject> = if let Some(ref pool) = self.thread_pool {
            py.allow_threads(|| {
                pool.install(|| {
                    let chunk_results: PyResult<Vec<PyObject>> = items
                        .par_iter()
                        .map(|item| {
                            Python::with_gil(|py| {
                                let bound_item = item.bind(py);
                                let bound_func = func.bind(py);
                                let result = bound_func.call1((bound_item,))?;
                                Ok(result.into())
                            })
                        })
                        .collect();
                    chunk_results
                })
            })?
        } else {
            // Use global pool as fallback
            py.allow_threads(|| {
                let chunk_results: PyResult<Vec<PyObject>> = items
                    .par_iter()
                    .map(|item| {
                        Python::with_gil(|py| {
                            let bound_item = item.bind(py);
                            let bound_func = func.bind(py);
                            let result = bound_func.call1((bound_item,))?;
                            Ok(result.into())
                        })
                    })
                    .collect();
                chunk_results
            })?
        };

        let py_list = PyList::new(py, results)?;
        Ok(py_list.into())
    }

    /// Get the number of worker threads
    pub fn get_worker_count(&self) -> usize {
        self.max_workers
    }

    /// Check if the executor is active
    pub fn is_active(&self) -> bool {
        self.thread_pool.is_some()
    }

    /// Shutdown the executor
    pub fn shutdown(&mut self) {
        // Drop the thread pool to shut it down
        self.thread_pool = None;
    }

    pub fn __enter__(pyself: PyRef<'_, Self>) -> PyRef<'_, Self> {
        pyself
    }

    pub fn __exit__(
        &mut self,
        _exc_type: Option<&Bound<'_, PyAny>>,
        _exc_value: Option<&Bound<'_, PyAny>>,
        _traceback: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<bool> {
        self.shutdown();
        Ok(false)
    }
}
