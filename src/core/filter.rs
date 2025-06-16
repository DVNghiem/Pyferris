use pyo3::prelude::*;
use pyo3::types::PyList;
use rayon::prelude::*;
use std::sync::Arc;

/// Parallel filter implementation
#[pyfunction]
pub fn parallel_filter(
    py: Python,
    predicate: Bound<PyAny>,
    iterable: Bound<PyAny>,
    chunk_size: Option<usize>,
) -> PyResult<Py<PyList>> {
    // Convert to PyObjects to avoid Sync issues
    let items: Vec<PyObject> = iterable.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
    
    if items.is_empty() {
        return Ok(PyList::empty(py).into());
    }
    
    let chunk_size = chunk_size.unwrap_or_else(|| {
        let len = items.len();
        if len < 1000 {
            (len / rayon::current_num_threads().max(1)).max(1)
        } else {
            1000
        }
    });

    let predicate: Arc<PyObject> = Arc::new(predicate.into());
    
    // Release GIL for parallel processing
    let filtered_results: Vec<PyObject> = py.allow_threads(|| {
        let chunk_results: PyResult<Vec<Vec<PyObject>>> = items
            .par_chunks(chunk_size)
            .map(|chunk| {
                Python::with_gil(|py| {
                    let chunk_results: PyResult<Vec<PyObject>> = chunk
                        .iter()
                        .filter_map(|item| {
                            let bound_item = item.bind(py);
                            let bound_predicate = predicate.bind(py);
                            match bound_predicate.call1((bound_item,)) {
                                Ok(result) => {
                                    match result.is_truthy() {
                                        Ok(true) => Some(Ok(item.clone_ref(py))),
                                        Ok(false) => None,
                                        Err(e) => Some(Err(e)),
                                    }
                                }
                                Err(e) => Some(Err(e)),
                            }
                        })
                        .collect();
                    chunk_results
                })
            })
            .collect();
        
        chunk_results
    })?
    .into_iter()
    .flatten()
    .collect();

    let py_list = PyList::new(py, filtered_results)?;
    Ok(py_list.into())
}
