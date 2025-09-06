use pyo3::prelude::*;
use rayon::prelude::*;
use std::sync::Arc;

/// Parallel reduce implementation with advanced Rust optimizations
#[pyfunction]
pub fn parallel_reduce(
    func: Bound<PyAny>,
    iterable: Bound<PyAny>,
    initializer: Option<Bound<PyAny>>,
    chunk_size: Option<usize>,
) -> PyResult<Py<PyAny>> {
    // Convert to Py<PyAny>s with optimized allocation
    let items: Vec<Py<PyAny>> = {
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
        return match initializer {
            Some(init) => Ok(init.into()),
            None => Err(pyo3::exceptions::PyTypeError::new_err(
                "reduce() of empty sequence with no initial value"
            )),
        };
    }

    let chunk_size = chunk_size.unwrap_or_else(|| {
        let len = items.len();
        let num_threads = rayon::current_num_threads();
        
        // Advanced chunking strategy optimized for reduce operations
        match len {
            0..=1000 => len.max(1), // Sequential for tiny datasets
            1001..=10000 => (len / num_threads).max(100).min(1000),
            10001..=100000 => (len / (num_threads * 2)).max(500).min(2000),
            _ => (len / (num_threads * 2)).max(1000).min(5000), // Larger chunks for reduce
        }
    });

    let func: Arc<Py<PyAny>> = Arc::new(func.into());
    let initializer: Option<Py<PyAny>> = initializer.map(|init| init.into());
    
    // First, reduce within each chunk using parallel processing with optimized error handling
    let chunk_results: Vec<Py<PyAny>> = Python::attach(|py| {
        py.detach(|| {
            let results: PyResult<Vec<Py<PyAny>>> = items
                .par_chunks(chunk_size)
                .map(|chunk| {
                    Python::attach(|py| {
                        let bound_func = func.bind(py);
                        let mut result = if let Some(ref init) = initializer {
                            init.clone_ref(py)
                        } else {
                            chunk[0].clone_ref(py)
                        };
                        
                        let start_idx = if initializer.is_some() { 0 } else { 1 };
                        
                        // Optimized inner loop with minimal overhead
                        for item in &chunk[start_idx..] {
                            let bound_item = item.bind(py);
                            let bound_result = result.bind(py);
                            result = bound_func.call1((bound_result, bound_item))?.into();
                        }
                        
                        Ok(result)
                    })
                })
                .collect();
            results
        })
    })?;
    
    // Then reduce the chunk results sequentially (should be small)
    if chunk_results.len() == 1 {
        Ok(chunk_results.into_iter().next().unwrap())
    } else {
        Python::attach(|py| {
            let bound_func = func.bind(py);
            let mut final_result = chunk_results[0].clone_ref(py);
            
            // Sequential reduction of chunk results
            for item in &chunk_results[1..] {
                let bound_item = item.bind(py);
                let bound_result = final_result.bind(py);
                final_result = bound_func.call1((bound_result, bound_item))?.into();
            }
            
            Ok(final_result)
        })
    }
}
