use pyo3::prelude::*;
use pyo3::types::PyAny;
use rayon::prelude::*;

/// Parallel reduce implementation
#[pyfunction]
pub fn parallel_reduce(
    func: Bound<PyAny>,
    iterable: Bound<PyAny>,
    initializer: Option<Bound<PyAny>>,
    chunk_size: Option<usize>,
) -> PyResult<PyObject> {
    // Convert to PyObjects to avoid Sync issues
    let items: Vec<PyObject> = iterable.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
    
    if items.is_empty() {
        return match initializer {
            Some(init) => Ok(init.into()),
            None => Err(pyo3::exceptions::PyTypeError::new_err(
                "reduce() of empty sequence with no initial value"
            )),
        };
    }

    let chunk_size = chunk_size.unwrap_or_else(|| {
        let len = items.len();
        if len < 1000 {
            len / rayon::current_num_threads().max(1)
        } else {
            1000
        }
    });

    let func: PyObject = func.into();
    let initializer: Option<PyObject> = initializer.map(|init| init.into());
    
    // First, reduce within each chunk
    let chunk_results: Vec<PyObject> = items
        .par_chunks(chunk_size)
        .map(|chunk| {
            Python::with_gil(|py| {
                let bound_func = func.bind(py);
                let mut result = if let Some(ref init) = initializer {
                    init.clone_ref(py)
                } else {
                    chunk[0].clone_ref(py)
                };
                
                let start_idx = if initializer.is_some() { 0 } else { 1 };
                
                for item in &chunk[start_idx..] {
                    let bound_item = item.bind(py);
                    result = bound_func.call1((result, bound_item))?.into();
                }
                
                Ok(result)
            })
        })
        .collect::<PyResult<Vec<PyObject>>>()?;
    
    // Then reduce the chunk results
    if chunk_results.len() == 1 {
        Ok(chunk_results.into_iter().next().unwrap())
    } else {
        Python::with_gil(|py| {
            let bound_func = func.bind(py);
            let mut final_result = chunk_results[0].clone_ref(py);
            
            for item in &chunk_results[1..] {
                let bound_item = item.bind(py);
                final_result = bound_func.call1((final_result, bound_item))?.into();
            }
            
            Ok(final_result)
        })
    }
}
