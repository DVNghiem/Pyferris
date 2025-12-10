use pyo3::prelude::*;
use pyo3::types::{PyList, PySet, PyTuple};
use std::collections::HashSet;

/// Creates an array of elements split into groups the length of size.
#[pyfunction]
#[pyo3(signature = (array, size=1))]
pub fn chunk(py: Python, array: Bound<PyList>, size: usize) -> PyResult<Py<PyList>> {
    if size == 0 {
        return Ok(PyList::empty(py).into());
    }

    let len = array.len();
    let mut chunks = Vec::new();
    let mut current_chunk = Vec::new();

    for (i, item) in array.iter().enumerate() {
        current_chunk.push(item);
        if (i + 1) % size == 0 || i == len - 1 {
            let py_chunk = PyList::new(py, &current_chunk)?;
            chunks.push(py_chunk);
            current_chunk.clear();
        }
    }

    let result = PyList::new(py, chunks)?;
    Ok(result.into())
}

/// Creates an array with all falsey values removed.
#[pyfunction]
pub fn compact(py: Python, array: Bound<PyList>) -> PyResult<Py<PyList>> {
    let mut result = Vec::new();
    for item in array.iter() {
        if item.is_truthy()? {
            result.push(item);
        }
    }
    Ok(PyList::new(py, result)?.into())
}

/// Creates a duplicate-free version of an array.
#[pyfunction]
pub fn uniq(py: Python, array: Bound<PyList>) -> PyResult<Py<PyList>> {
    // Use a Python set to handle uniqueness of any Python object
    let set = PySet::empty(py)?;
    let mut result = Vec::new();

    for item in array.iter() {
        if !set.contains(&item)? {
            set.add(&item)?;
            result.push(item);
        }
    }
    Ok(PyList::new(py, result)?.into())
}

/// Flattens array a single level deep.
#[pyfunction]
pub fn flatten(py: Python, array: Bound<PyList>) -> PyResult<Py<PyList>> {
    let mut result = Vec::new();
    for item in array.iter() {
        if let Ok(sub_list) = item.downcast::<PyList>() {
            for sub_item in sub_list.iter() {
                result.push(sub_item);
            }
        } else {
            result.push(item);
        }
    }
    Ok(PyList::new(py, result)?.into())
}

/// Creates an array of unique values that are included in all given arrays.
#[pyfunction]
#[pyo3(signature = (*arrays))]
pub fn intersection(py: Python, arrays: &Bound<PyTuple>) -> PyResult<Py<PyList>> {
    if arrays.is_empty() {
        return Ok(PyList::empty(py).into());
    }

    let first_array = arrays.get_item(0)?.downcast::<PyList>()?.clone();
    let mut result_set = PySet::new(py, &first_array)?;

    for i in 1..arrays.len() {
        let item = arrays.get_item(i)?;
        let other_array = item.downcast::<PyList>()?;
        let other_set = PySet::new(py, other_array)?;
        
        // Intersection in Python: s1 & s2
        // PySet doesn't expose strict intersection method easily in PyO3 0.21+, 
        // but we can iterate and check.
        // Or use python method call.
        let intersection = result_set.call_method1("intersection", (other_set,))?;
        result_set = intersection.downcast::<PySet>()?.clone();
    }

    // Convert back to list
    Ok(PyList::new(py, result_set)?.into())
}

/// Creates an array of unique values from all given arrays.
#[pyfunction]
#[pyo3(signature = (*arrays))]
pub fn union(py: Python, arrays: &Bound<PyTuple>) -> PyResult<Py<PyList>> {
    let result_set = PySet::empty(py)?;
    
    for item in arrays.iter() {
        if let Ok(list) = item.downcast::<PyList>() {
            for elem in list.iter() {
                result_set.add(elem)?;
            }
        }
    }
    
    Ok(PyList::new(py, result_set)?.into())
}

/// Creates an array of grouped elements, the first of which contains the first elements of the given arrays, the second of which contains the second elements of the given arrays, and so on.
#[pyfunction]
#[pyo3(signature = (*arrays))]
pub fn zip(py: Python, arrays: &Bound<PyTuple>) -> PyResult<Py<PyList>> {
    if arrays.is_empty() {
        return Ok(PyList::empty(py).into());
    }

    let mut lists = Vec::new();
    let mut min_len = usize::MAX;

    for item in arrays.iter() {
        let list = item.downcast::<PyList>()?.clone(); // Clone the PyList to own it
        let len = list.len();
        if len < min_len {
            min_len = len;
        }
        lists.push(list);
    }

    if min_len == usize::MAX {
        return Ok(PyList::empty(py).into());
    }

    let mut result = Vec::new();
    for i in 0..min_len {
        let mut group = Vec::new();
        for list in &lists {
            group.push(list.get_item(i)?);
        }
        result.push(PyList::new(py, group)?);
    }

    Ok(PyList::new(py, result)?.into())
}

#[pymodule]
pub fn array(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(chunk, m)?)?;
    m.add_function(wrap_pyfunction!(compact, m)?)?;
    m.add_function(wrap_pyfunction!(uniq, m)?)?;
    m.add_function(wrap_pyfunction!(flatten, m)?)?;
    m.add_function(wrap_pyfunction!(intersection, m)?)?;
    m.add_function(wrap_pyfunction!(union, m)?)?;
    m.add_function(wrap_pyfunction!(zip, m)?)?;
    Ok(())
}
