use pyo3::prelude::*;
use pyo3::types::{PyAny, PyList, PyTuple};
use rayon::prelude::*;

/// Task executor for managing parallel tasks
#[pyclass]
pub struct Executor {
    #[pyo3(get, set)]
    pub max_workers: usize,
}

#[pymethods]
impl Executor {
    #[new]
    pub fn new(max_workers: Option<usize>) -> Self {
        let max_workers = max_workers.unwrap_or_else(|| rayon::current_num_threads());
        
        Self {
            max_workers,
        }
    }

    /// Submit a single task
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
        let func: PyObject = func.into();
        
        let results: Vec<PyObject> = items
            .par_iter()
            .map(|item| {
                Python::with_gil(|py| {
                    let bound_item = item.bind(py);
                    let bound_func = func.bind(py);
                    let result = bound_func.call1((bound_item,))?;
                    Ok(result.into())
                })
            })
            .collect::<PyResult<Vec<PyObject>>>()?;

        let py_list = PyList::new(py, results)?;
        Ok(py_list.into())
    }

    /// Shutdown the executor
    pub fn shutdown(&mut self) {
        // No-op for now since we're using rayon's global pool
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
