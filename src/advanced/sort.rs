use pyo3::prelude::*;
use pyo3::types::PyList;
use rayon::prelude::*;
use std::sync::Arc;

/// Parallel sort implementation
#[pyfunction]
pub fn parallel_sort(
    py: Python,
    iterable: Bound<PyAny>,
    key_func: Option<Bound<PyAny>>,
    reverse: Option<bool>,
) -> PyResult<Py<PyList>> {
    // Convert to PyObjects to avoid Sync issues
    let mut items: Vec<PyObject> = iterable.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
    
    if items.is_empty() {
        return Ok(PyList::empty(py).into());
    }
    
    let reverse = reverse.unwrap_or(false);
    
    if let Some(key_func) = key_func {
        let key_func: Arc<PyObject> = Arc::new(key_func.into());
        
        // Create key-value pairs for sorting
        let mut keyed_items: Vec<(PyObject, PyObject)> = py.allow_threads(|| {
            items.par_iter().map(|item| {
                Python::with_gil(|py| {
                    let key = key_func.call1(py, (item,))?;
                    Ok((key, item.clone_ref(py)))
                })
            }).collect::<PyResult<Vec<_>>>()
        })?;
        
        // Sort by key
        keyed_items.par_sort_by(|a, b| {
            Python::with_gil(|py| {
                let cmp_result = a.0.bind(py).compare(&b.0.bind(py));
                match cmp_result {
                    Ok(ordering) => {
                        if reverse {
                            ordering.reverse()
                        } else {
                            ordering
                        }
                    }
                    Err(_) => std::cmp::Ordering::Equal,
                }
            })
        });
        
        // Extract sorted values
        items = keyed_items.into_iter().map(|(_, value)| value).collect();
    } else {
        // Direct comparison sort
        items.par_sort_by(|a, b| {
            Python::with_gil(|py| {
                let cmp_result = a.bind(py).compare(&b.bind(py));
                match cmp_result {
                    Ok(ordering) => {
                        if reverse {
                            ordering.reverse()
                        } else {
                            ordering
                        }
                    }
                    Err(_) => std::cmp::Ordering::Equal,
                }
            })
        });
    }
    
    let py_list = PyList::new(py, items)?;
    Ok(py_list.into())
}

/// Parallel unique implementation
#[pyfunction]
pub fn parallel_unique(
    py: Python,
    iterable: Bound<PyAny>,
    key_func: Option<Bound<PyAny>>,
) -> PyResult<Py<PyList>> {
    use std::collections::HashSet;
    use std::hash::{Hash, Hasher};
    use std::collections::hash_map::DefaultHasher;
    
    let items: Vec<PyObject> = iterable.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
    
    if items.is_empty() {
        return Ok(PyList::empty(py).into());
    }
    
    let unique_items = if let Some(key_func) = key_func {
        let key_func: Arc<PyObject> = Arc::new(key_func.into());
        let mut seen_keys = HashSet::new();
        let mut unique = Vec::new();
        
        for item in items {
            let key_result = Python::with_gil(|py| {
                key_func.call1(py, (&item,))
            });
            
            if let Ok(key) = key_result {
                // Create a hash of the key for comparison
                let key_hash = Python::with_gil(|py| {
                    let mut hasher = DefaultHasher::new();
                    if let Ok(hash_val) = key.bind(py).hash() {
                        hash_val.hash(&mut hasher);
                        hasher.finish()
                    } else {
                        // Fallback to string representation
                        if let Ok(str_repr) = key.bind(py).str() {
                            str_repr.to_string().hash(&mut hasher);
                            hasher.finish()
                        } else {
                            0
                        }
                    }
                });
                
                if seen_keys.insert(key_hash) {
                    unique.push(item);
                }
            }
        }
        unique
    } else {
        let mut seen_hashes = HashSet::new();
        let mut unique = Vec::new();
        
        for item in items {
            let item_hash = Python::with_gil(|py| {
                let mut hasher = DefaultHasher::new();
                if let Ok(hash_val) = item.bind(py).hash() {
                    hash_val.hash(&mut hasher);
                    hasher.finish()
                } else {
                    // Fallback to string representation
                    if let Ok(str_repr) = item.bind(py).str() {
                        str_repr.to_string().hash(&mut hasher);
                        hasher.finish()
                    } else {
                        0
                    }
                }
            });
            
            if seen_hashes.insert(item_hash) {
                unique.push(item);
            }
        }
        unique
    };
    
    let py_list = PyList::new(py, unique_items)?;
    Ok(py_list.into())
}

/// Parallel partition implementation
#[pyfunction]
pub fn parallel_partition(
    py: Python,
    predicate: Bound<PyAny>,
    iterable: Bound<PyAny>,
    chunk_size: Option<usize>,
) -> PyResult<(Py<PyList>, Py<PyList>)> {
    let items: Vec<PyObject> = iterable.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
    
    if items.is_empty() {
        return Ok((PyList::empty(py).into(), PyList::empty(py).into()));
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
    
    // Process in parallel chunks
    let (true_items, false_items): (Vec<Vec<PyObject>>, Vec<Vec<PyObject>>) = py.allow_threads(|| {
        items
            .par_chunks(chunk_size)
            .map(|chunk| {
                Python::with_gil(|py| {
                    let mut true_chunk = Vec::new();
                    let mut false_chunk = Vec::new();
                    
                    for item in chunk {
                        match predicate.call1(py, (item,)) {
                            Ok(result) => {
                                match result.extract::<bool>(py) {
                                    Ok(true) => true_chunk.push(item.clone_ref(py)),
                                    Ok(false) => false_chunk.push(item.clone_ref(py)),
                                    Err(_) => false_chunk.push(item.clone_ref(py)),
                                }
                            }
                            Err(_) => false_chunk.push(item.clone_ref(py)),
                        }
                    }
                    
                    (true_chunk, false_chunk)
                })
            })
            .collect::<(Vec<_>, Vec<_>)>()
    });
    
    // Flatten results
    let true_result: Vec<PyObject> = true_items.into_iter().flatten().collect();
    let false_result: Vec<PyObject> = false_items.into_iter().flatten().collect();
    
    let true_list = PyList::new(py, true_result)?;
    let false_list = PyList::new(py, false_result)?;
    
    Ok((true_list.into(), false_list.into()))
}
