use pyo3::prelude::*;
use pyo3::types::PyList;
use rayon::prelude::*;
use std::sync::Arc;
use smallvec::SmallVec;

/// Parallel filter implementation with advanced Rust optimizations
#[pyfunction]
pub fn parallel_filter(
    py: Python,
    predicate: Bound<PyAny>,
    iterable: Bound<PyAny>,
    chunk_size: Option<usize>,
) -> PyResult<Py<PyList>> {
    // Convert to PyObjects to avoid Sync issues - optimized with capacity hint
    let items: Vec<PyObject> = {
        let iter = iterable.try_iter()?;
        let mut items = Vec::new();
        
        // Try to get size hint for better allocation
        let (lower, upper) = iter.size_hint();
        if let Some(upper) = upper {
            items.reserve(upper);
        } else if lower > 0 {
            items.reserve(lower);
        }
        
        for item in iter {
            items.push(item?.into());
        }
        items
    };
    
    if items.is_empty() {
        return Ok(PyList::empty(py).into());
    }
    
    let chunk_size = chunk_size.unwrap_or_else(|| {
        let len = items.len();
        let num_threads = rayon::current_num_threads();
        
        // Advanced chunking strategy based on dataset characteristics
        match len {
            0..=1000 => len.max(1), // Sequential for tiny datasets
            1001..=10000 => (len / num_threads).max(100).min(1000),
            10001..=100000 => (len / (num_threads * 2)).max(500).min(2000),
            _ => (len / (num_threads * 4)).max(1000).min(5000),
        }
    });

    let predicate: Arc<PyObject> = Arc::new(predicate.into());
    
    // Use thread-local storage for better performance
    let filtered_results: Vec<SmallVec<[PyObject; 8]>> = py.allow_threads(|| {
        // Use try_fold for better error handling and performance
        let chunk_results: PyResult<Vec<SmallVec<[PyObject; 8]>>> = items
            .par_chunks(chunk_size)
            .map(|chunk| {
                Python::with_gil(|py| {
                    // Use SmallVec for small chunks to avoid heap allocation
                    let mut chunk_results = SmallVec::new();
                    let bound_predicate = predicate.bind(py);
                    
                    // Optimize inner loop with minimal allocations
                    for item in chunk {
                        let bound_item = item.bind(py);
                        
                        // Fast path for common cases
                        match bound_predicate.call1((bound_item,)) {
                            Ok(result) => {
                                // Use extract for better performance on bool results
                                match result.extract::<bool>() {
                                    Ok(true) => chunk_results.push(item.clone_ref(py)),
                                    Ok(false) => continue,
                                    Err(_) => {
                                        // Fallback to is_truthy for non-bool results
                                        match result.is_truthy() {
                                            Ok(true) => chunk_results.push(item.clone_ref(py)),
                                            Ok(false) => continue,
                                            Err(e) => return Err(e),
                                        }
                                    }
                                }
                            }
                            Err(e) => return Err(e),
                        }
                    }
                    Ok(chunk_results)
                })
            })
            .collect();
        
        chunk_results
    })?;

    // Flatten with capacity hint for better performance
    let total_capacity: usize = filtered_results.iter().map(|v| v.len()).sum();
    let mut final_results = Vec::with_capacity(total_capacity);
    
    for chunk in filtered_results {
        final_results.extend(chunk);
    }

    let py_list = PyList::new(py, final_results)?;
    Ok(py_list.into())
}
