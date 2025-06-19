use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};
use rayon::prelude::*;
use std::sync::Arc;

/// Task executor for managing parallel tasks
#[pyclass]
pub struct Executor {
    #[pyo3(get, set)]
    pub max_workers: usize,
}

#[pymethods]
impl Executor {
    #[new]
    #[pyo3(signature = (max_workers = None))]
    pub fn new(max_workers: Option<usize>) -> Self {
        let max_workers = max_workers.unwrap_or_else(|| rayon::current_num_threads());
        
        Self {
            max_workers,
        }
    }

    /// Submit a single task
    #[pyo3(signature = (func, args = None))]
    pub fn submit(&self, func: Bound<PyAny>, args: Option<Bound<PyTuple>>) -> PyResult<PyObject> {
        let py = func.py();
        let args = args.unwrap_or_else(|| PyTuple::empty(py));
        let result = func.call1((args,))?;
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
        
        // Use allow_threads to release GIL during parallel processing
        let results: Vec<PyObject> = py.allow_threads(|| {
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
        })?;

        let py_list = PyList::new(py, results)?;
        Ok(py_list.into())
    }

    /// Shutdown the executor
    pub fn shutdown(&mut self) {
        // No-op for now since we're using rayon's global pool
        // In a real implementation, you might want to track and clean up resources
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
