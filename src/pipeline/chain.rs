use pyo3::prelude::*;
use pyo3::types::PyList;
use rayon::prelude::*;
use std::sync::Arc;

/// Pipeline for chaining operations
#[pyclass]
pub struct Pipeline {
    operations: Vec<Arc<Py<PyAny>>>,
    chunk_size: usize,
}

#[pymethods]
impl Pipeline {
    #[new]
    #[pyo3(signature = (chunk_size = 1000))]
    pub fn new(chunk_size: usize) -> Self {
        Self {
            operations: Vec::new(),
            chunk_size,
        }
    }

    /// Add an operation to the pipeline
    pub fn add(&mut self, operation: Bound<PyAny>) -> PyResult<()> {
        self.operations.push(Arc::new(operation.into()));
        Ok(())
    }

    /// Execute the pipeline on data
    pub fn execute(&self, py: Python, data: Bound<PyAny>) -> PyResult<Py<PyList>> {
        let items: Vec<Py<PyAny>> = data.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
        
        if items.is_empty() || self.operations.is_empty() {
            return Ok(PyList::new(py, items)?.into());
        }

        let operations = self.operations.clone();
        let chunk_size = self.chunk_size;

        // Process in parallel chunks
        let results: Vec<Py<PyAny>> = py.detach(|| {
            items
                .par_chunks(chunk_size)
                .map(|chunk| {
                    Python::attach(|py| {
                        let mut chunk_results = Vec::new();
                        
                        for item in chunk {
                            let mut current_item = item.clone_ref(py);
                            
                            // Apply each operation in sequence
                            for operation in &operations {
                                let bound_op = operation.bind(py);
                                let bound_item = current_item.bind(py);
                                current_item = bound_op.call1((bound_item,))?.into();
                            }
                            chunk_results.push(current_item);
                        }
                        Ok(chunk_results)
                    })
                })
                .collect::<PyResult<Vec<_>>>()
        })?
        .into_iter()
        .flatten()
        .collect();

        let py_list = PyList::new(py, results)?;
        Ok(py_list.into())
    }

    /// Chain multiple operations at once
    pub fn chain(&mut self, operations: Bound<PyList>) -> PyResult<()> {
        for op in operations.iter() {
            self.operations.push(Arc::new(op.into()));
        }
        Ok(())
    }

    /// Get the number of operations in the pipeline
    #[getter]
    pub fn length(&self) -> usize {
        self.operations.len()
    }

    /// Clear all operations
    pub fn clear(&mut self) {
        self.operations.clear();
    }
}

/// Chain operations together
#[pyclass]
pub struct Chain {
    operations: Vec<Arc<Py<PyAny>>>,
}

#[pymethods]
impl Chain {
    #[new]
    pub fn new() -> Self {
        Self {
            operations: Vec::new(),
        }
    }

    /// Add an operation to the chain
    pub fn then(&mut self, operation: Bound<PyAny>) -> PyResult<()> {
        self.operations.push(Arc::new(operation.into()));
        Ok(())
    }

    /// Execute the chain on a single item
    pub fn execute_one(&self, py: Python, item: Bound<PyAny>) -> PyResult<Py<PyAny>> {
        let mut current_item: Py<PyAny> = item.into();
        
        for operation in &self.operations {
            let bound_op = operation.bind(py);
            let bound_item = current_item.bind(py);
            current_item = bound_op.call1((bound_item,))?.into();
        }
        
        Ok(current_item)
    }

    /// Execute the chain on multiple items in parallel
    pub fn execute_many(&self, py: Python, data: Bound<PyAny>, chunk_size: Option<usize>) -> PyResult<Py<PyList>> {
        let items: Vec<Py<PyAny>> = data.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
        
        if items.is_empty() || self.operations.is_empty() {
            return Ok(PyList::new(py, items)?.into());
        }

        let chunk_size = chunk_size.unwrap_or(1000);
        let operations = self.operations.clone();

        // Process in parallel chunks
        let results: Vec<Py<PyAny>> = py.detach(|| {
            items
                .par_chunks(chunk_size)
                .map(|chunk| {
                    Python::attach(|py| {
                        let mut chunk_results = Vec::new();
                        
                        for item in chunk {
                            let mut current_item = item.clone_ref(py);
                            
                            // Apply each operation in sequence
                            for operation in &operations {
                                let bound_op = operation.bind(py);
                                let bound_item = current_item.bind(py);
                                current_item = bound_op.call1((bound_item,))?.into();
                            }
                            
                            chunk_results.push(current_item);
                        }
                        
                        Ok(chunk_results)
                    })
                })
                .collect::<PyResult<Vec<_>>>()
        })?
        .into_iter()
        .flatten()
        .collect();

        let py_list = PyList::new(py, results)?;
        Ok(py_list.into())
    }

    /// Get the number of operations in the chain
    #[getter]
    pub fn length(&self) -> usize {
        self.operations.len()
    }
}

/// Functional-style pipeline that can be composed
#[pyfunction]
pub fn pipeline_map(
    py: Python,
    data: Bound<PyAny>,
    operations: Bound<PyList>,
    chunk_size: Option<usize>,
) -> PyResult<Py<PyList>> {
    let items: Vec<Py<PyAny>> = data.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
    
    if items.is_empty() {
        return Ok(PyList::empty(py).into());
    }

    let ops: Vec<Arc<Py<PyAny>>> = operations.iter().map(|op| Arc::new(op.into())).collect();
    if ops.is_empty() {
        return Ok(PyList::new(py, items)?.into());
    }

    let chunk_size = chunk_size.unwrap_or(1000);

    // Process in parallel chunks
    let results: Vec<Py<PyAny>> = py.detach(|| {
        items
            .par_chunks(chunk_size)
            .map(|chunk| {
                Python::attach(|py| {
                    let mut chunk_results = Vec::new();
                    
                    for item in chunk {
                        let mut current_item = item.clone_ref(py);
                        
                        // Apply each operation in sequence
                        for operation in &ops {
                            let bound_op = operation.bind(py);
                            let bound_item = current_item.bind(py);
                            current_item = bound_op.call1((bound_item,))?.into();
                        }
                        
                        chunk_results.push(current_item);
                    }
                    
                    Ok(chunk_results)
                })
            })
            .collect::<PyResult<Vec<_>>>()
    })?
    .into_iter()
    .flatten()
    .collect();

    let py_list = PyList::new(py, results)?;
    Ok(py_list.into())
}