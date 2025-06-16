use pyo3::prelude::*;
use pyo3::types::{PyAny, PyList};
use rayon::prelude::*;

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
    
    let chunk_size = chunk_size.unwrap_or_else(|| {
        let len = items.len();
        if len < 1000 {
            len / rayon::current_num_threads().max(1)
        } else {
            1000
        }
    });

    let predicate: PyObject = predicate.into();
    
    let filtered_results: Vec<PyObject> = items
        .par_chunks(chunk_size)
        .map(|chunk| {
            Python::with_gil(|py| {
                chunk
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
                    .collect::<PyResult<Vec<PyObject>>>()
            })
        })
        .collect::<PyResult<Vec<Vec<PyObject>>>>()?
        .into_iter()
        .flatten()
        .collect::<Vec<PyObject>>();

    let py_list = PyList::new(py, filtered_results)?;
    Ok(py_list.into())
}
