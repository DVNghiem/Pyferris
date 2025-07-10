use pyo3::prelude::*;
use pyo3::types::{PyAny, PyList, PyTuple};
use rayon::prelude::*;
use std::sync::Arc;
use smallvec::SmallVec;

/// Parallel map implementation with advanced Rust optimizations
#[pyfunction]
pub fn parallel_map(
    py: Python,
    func: Bound<PyAny>,
    iterable: Bound<PyAny>,
    chunk_size: Option<usize>,
) -> PyResult<Py<PyList>> {
    // Convert to PyObjects with optimized allocation
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

    let func: Arc<PyObject> = Arc::new(func.into());
    
    // Release GIL for parallel processing with optimized error handling
    let results: Vec<SmallVec<[PyObject; 8]>> = py.allow_threads(|| {
        let chunk_results: PyResult<Vec<SmallVec<[PyObject; 8]>>> = items
            .par_chunks(chunk_size)
            .map(|chunk| {
                Python::with_gil(|py| {
                    let mut chunk_results = SmallVec::with_capacity(chunk.len());
                    let bound_func = func.bind(py);
                    
                    for item in chunk {
                        let bound_item = item.bind(py);
                        let result = bound_func.call1((bound_item,))?;
                        chunk_results.push(result.into());
                    }
                    Ok(chunk_results)
                })
            })
            .collect();
        
        chunk_results
    })?;

    // Flatten with capacity hint for better performance
    let total_capacity: usize = results.iter().map(|v| v.len()).sum();
    let mut final_results = Vec::with_capacity(total_capacity);
    
    for chunk in results {
        final_results.extend(chunk);
    }

    let py_list = PyList::new(py, final_results)?;
    Ok(py_list.into())
}

/// Parallel starmap implementation with advanced Rust optimizations (for functions with multiple arguments)
#[pyfunction]
pub fn parallel_starmap(
    py: Python,
    func: Bound<PyAny>,
    iterable: Bound<PyAny>,
    chunk_size: Option<usize>,
) -> PyResult<Py<PyList>> {
    // Convert to PyObjects with optimized allocation
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

    let func: Arc<PyObject> = Arc::new(func.into());
    
    // Release GIL for parallel processing with optimized error handling
    let results: Vec<SmallVec<[PyObject; 8]>> = py.allow_threads(|| {
        let chunk_results: PyResult<Vec<SmallVec<[PyObject; 8]>>> = items
            .par_chunks(chunk_size)
            .map(|chunk| {
                Python::with_gil(|py| {
                    let mut chunk_results = SmallVec::with_capacity(chunk.len());
                    let bound_func = func.bind(py);
                    
                    for item in chunk {
                        let bound_item = item.bind(py);
                        
                        // Convert item to tuple for starmap with optimized handling
                        let result = if let Ok(tuple) = bound_item.downcast::<PyTuple>() {
                            bound_func.call(tuple, None)?
                        } else {
                            bound_func.call1((bound_item,))?
                        };
                        chunk_results.push(result.into());
                    }
                    Ok(chunk_results)
                })
            })
            .collect();
        
        chunk_results
    })?;

    // Flatten with capacity hint for better performance
    let total_capacity: usize = results.iter().map(|v| v.len()).sum();
    let mut final_results = Vec::with_capacity(total_capacity);
    
    for chunk in results {
        final_results.extend(chunk);
    }

    let py_list = PyList::new(py, final_results)?;
    Ok(py_list.into())
}
