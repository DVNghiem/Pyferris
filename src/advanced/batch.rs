use pyo3::prelude::*;
use pyo3::types::PyList;
use rayon::prelude::*;
use std::sync::Arc;

/// Batch processor for handling large datasets
#[pyclass]
pub struct BatchProcessor {
    batch_size: usize,
    max_workers: usize,
}

#[pymethods]
impl BatchProcessor {
    #[new]
    #[pyo3(signature = (batch_size = 1000, max_workers = 0))]
    pub fn new(batch_size: usize, max_workers: usize) -> Self {
        let workers = if max_workers == 0 {
            rayon::current_num_threads()
        } else {
            max_workers
        };
        
        Self {
            batch_size,
            max_workers: workers,
        }
    }
    
    /// Process data in batches with a custom function
    pub fn process_batches(
        &self,
        py: Python,
        data: Bound<PyAny>,
        processor_func: Bound<PyAny>,
    ) -> PyResult<Py<PyList>> {
        let items: Vec<PyObject> = data.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
        
        if items.is_empty() {
            return Ok(PyList::empty(py).into());
        }
        
        let processor_func: Arc<PyObject> = Arc::new(processor_func.into());
        
        // Process batches in parallel
        let results: Vec<PyObject> = py.allow_threads(|| {
            items
                .par_chunks(self.batch_size)
                .enumerate()
                .map(|(batch_idx, batch)| {
                    Python::with_gil(|py| {
                        let batch_list = PyList::new(py, batch)?;
                        let args = (batch_idx, batch_list);
                        processor_func.call1(py, args)
                    })
                })
                .collect::<PyResult<Vec<_>>>()
        })?;
        
        let py_list = PyList::new(py, results)?;
        Ok(py_list.into())
    }
    
    /// Get batch size
    #[getter]
    pub fn batch_size(&self) -> usize {
        self.batch_size
    }
    
    /// Get max workers
    #[getter]
    pub fn max_workers(&self) -> usize {
        self.max_workers
    }
}

/// Process data in parallel chunks
#[pyfunction]
pub fn parallel_chunks(
    py: Python,
    iterable: Bound<PyAny>,
    chunk_size: usize,
    processor_func: Bound<PyAny>,
) -> PyResult<Py<PyList>> {
    let items: Vec<PyObject> = iterable.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
    
    if items.is_empty() {
        return Ok(PyList::empty(py).into());
    }
    
    let processor_func: Arc<PyObject> = Arc::new(processor_func.into());
    
    // Process chunks in parallel
    let results: Vec<PyObject> = py.allow_threads(|| {
        items
            .par_chunks(chunk_size)
            .enumerate()
            .map(|(chunk_idx, chunk)| {
                Python::with_gil(|py| {
                    let chunk_list = PyList::new(py, chunk)?;
                    let args = (chunk_idx, chunk_list);
                    processor_func.call1(py, args)
                })
            })
            .collect::<PyResult<Vec<_>>>()
    })?;
    
    let py_list = PyList::new(py, results)?;
    Ok(py_list.into())
}
