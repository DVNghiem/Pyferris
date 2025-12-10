use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString, PyTuple};

/// Performs a deep comparison between two values to determine if they are equivalent.
#[pyfunction]
pub fn is_equal(py: Python, value: Bound<PyAny>, other: Bound<PyAny>) -> PyResult<bool> {
    // Python's equality operator is already deep for built-in types
    let result = value.eq(other)?;
    Ok(result)
}

/// Checks if value is an empty object, collection, map, or set.
#[pyfunction]
pub fn is_empty(value: Bound<PyAny>) -> PyResult<bool> {
    if let Ok(len) = value.len() {
        Ok(len == 0)
    } else {
        // If it doesn't have len(), check if it's None or falsey
        Ok(value.is_none())
    }
}

/// Converts value to an array.
#[pyfunction]
pub fn to_array(py: Python, value: Bound<PyAny>) -> PyResult<Py<PyList>> {
    if let Ok(list) = value.downcast::<PyList>() {
        Ok(list.clone().into())
    } else if let Ok(tuple) = value.downcast::<PyTuple>() {
        Ok(PyList::new(py, tuple)?.into())
    } else if let Ok(dict) = value.downcast::<PyDict>() {
        Ok(dict.values().into())
    } else if let Ok(s) = value.downcast::<PyString>() {
        // Split string into chars? Or just wrap? Lodash splits string.
        let s_str = s.to_str()?;
        let chars: Vec<&str> = s_str.split("").filter(|c| !c.is_empty()).collect();
        Ok(PyList::new(py, chars)?.into())
    } else if value.is_none() {
        Ok(PyList::empty(py).into())
    } else {
        // Wrap in list
        Ok(PyList::new(py, vec![value])?.into())
    }
}

/// Performs a partial deep comparison between object and source to determine if object contains equivalent property values.
#[pyfunction]
pub fn is_match(object: Bound<PyAny>, source: Bound<PyAny>) -> PyResult<bool> {
    if let (Ok(obj_dict), Ok(source_dict)) = (object.downcast::<PyDict>(), source.downcast::<PyDict>()) {
        for (key, val) in source_dict.iter() {
            if let Some(obj_val) = obj_dict.get_item(key)? {
                if !obj_val.eq(val)? {
                    return Ok(false);
                }
            } else {
                return Ok(false);
            }
        }
        Ok(true)
    } else {
        object.eq(source).map_err(|e| e.into())
    }
}

#[pymodule]
pub fn lang(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_equal, m)?)?;
    m.add_function(wrap_pyfunction!(is_empty, m)?)?;
    m.add_function(wrap_pyfunction!(to_array, m)?)?;
    m.add_function(wrap_pyfunction!(is_match, m)?)?;
    Ok(())
}
