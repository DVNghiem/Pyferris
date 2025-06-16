use pyo3::prelude::*;
use pyo3::types::{PyAny, PyList, PyTuple};
use rayon::prelude::*;

/// Parallel map implementation
#[pyfunction]
pub fn parallel_map(
    py: Python,
    func: Bound<PyAny>,
    iterable: Bound<PyAny>,
    chunk_size: Option<usize>,
) -> PyResult<Py<PyList>> {
    // Convert to PyObjects to avoid Sync issues
    let items: Vec<PyObject> = iterable.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
    
    let chunk_size = chunk_size.unwrap_or_else(|| {
        let len = items.len();
        if len < 1000 {
            len / rayon::current_num_threads().max(1)
        } else {
            1000
        }
    });

    let func: PyObject = func.into();
    
    let results: Vec<PyObject> = items
        .par_chunks(chunk_size)
        .map(|chunk| {
            Python::with_gil(|py| {
                chunk
                    .iter()
                    .map(|item| {
                        let bound_item = item.bind(py);
                        let bound_func = func.bind(py);
                        let result = bound_func.call1((bound_item,))?;
                        Ok(result.into())
                    })
                    .collect::<PyResult<Vec<PyObject>>>()
            })
        })
        .collect::<PyResult<Vec<Vec<PyObject>>>>()?
        .into_iter()
        .flatten()
        .collect::<Vec<PyObject>>();

    let py_list = PyList::new(py, results)?;
    Ok(py_list.into())
}

/// Parallel starmap implementation (for functions with multiple arguments)
#[pyfunction]
pub fn parallel_starmap(
    py: Python,
    func: Bound<PyAny>,
    iterable: Bound<PyAny>,
    chunk_size: Option<usize>,
) -> PyResult<Py<PyList>> {
    // Convert to PyObjects to avoid Sync issues
    let items: Vec<PyObject> = iterable.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
    
    let chunk_size = chunk_size.unwrap_or_else(|| {
        let len = items.len();
        if len < 1000 {
            len / rayon::current_num_threads().max(1)
        } else {
            1000
        }
    });

    let func: PyObject = func.into();
    
    let results: Vec<PyObject> = items
        .par_chunks(chunk_size)
        .map(|chunk| {
            Python::with_gil(|py| {
                chunk
                    .iter()
                    .map(|item| {
                        let bound_item = item.bind(py);
                        let bound_func = func.bind(py);
                        
                        // Convert item to tuple for starmap
                        let result = if let Ok(tuple) = bound_item.downcast::<PyTuple>() {
                            bound_func.call1((tuple,))?
                        } else {
                            let args = PyTuple::new(py, [bound_item])?;
                            bound_func.call1((args,))?
                        };
                        Ok(result.into())
                    })
                    .collect::<PyResult<Vec<PyObject>>>()
            })
        })
        .collect::<PyResult<Vec<Vec<PyObject>>>>()?
        .into_iter()
        .flatten()
        .collect::<Vec<PyObject>>();

    let py_list = PyList::new(py, results)?;
    Ok(py_list.into())
}
