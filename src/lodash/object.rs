use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

/// Gets the value at path of object. If the resolved value is undefined, the defaultValue is returned in its place.
#[pyfunction]
#[pyo3(signature = (object, path, default_value=None))]
pub fn get(py: Python, object: Bound<PyAny>, path: Bound<PyAny>, default_value: Option<Bound<PyAny>>) -> PyResult<Py<PyAny>> {
    let path_str: String = if let Ok(s) = path.extract() {
        s
    } else {
        return Ok(default_value.map(|v| v.into()).unwrap_or_else(|| py.None()));
    };

    let keys: Vec<&str> = path_str.split('.').collect();
    let mut current = object;

    for key in keys {
        if let Ok(item) = current.get_item(key) {
            current = item;
        } else {
            return Ok(default_value.map(|v| v.into()).unwrap_or_else(|| py.None()));
        }
    }

    Ok(current.into())
}

/// Sets the value at path of object. If a portion of path doesn't exist, it's created.
#[pyfunction]
pub fn set(py: Python, object: Bound<PyAny>, path: &str, value: Bound<PyAny>) -> PyResult<Py<PyAny>> {
    let keys: Vec<&str> = path.split('.').collect();
    if keys.is_empty() {
        return Ok(object.into());
    }

    let mut current = object.clone();
    
    for (i, key) in keys.iter().enumerate() {
        if i == keys.len() - 1 {
            // Last key, set the value
            if let Ok(dict) = current.downcast::<PyDict>() {
                dict.set_item(key, &value)?;
            } else {
                // If not a dict, we can't set property easily on generic PyAny without setattr
                current.setattr(*key, &value)?;
            }
        } else {
            // Intermediate key, traverse or create
            let next_item = if let Ok(item) = current.get_item(*key) {
                item
            } else {
                // Create new dict if missing
                let new_dict = PyDict::new(py);
                if let Ok(dict) = current.downcast::<PyDict>() {
                    dict.set_item(*key, &new_dict)?;
                } else {
                    current.setattr(*key, &new_dict)?;
                }
                new_dict.into_any()
            };
            current = next_item;
        }
    }

    Ok(object.into())
}

/// Recursively merges own and inherited enumerable string keyed properties of source objects into the destination object.
#[pyfunction]
pub fn merge(py: Python, object: Bound<PyAny>, sources: Bound<PyAny>) -> PyResult<Py<PyAny>> {
    // Deep merge implementation
    // This is a simplified version. A full version would need to handle recursion carefully.
    
    if let (Ok(target_dict), Ok(source_dict)) = (object.downcast::<PyDict>(), sources.downcast::<PyDict>()) {
        for (key, value) in source_dict.iter() {
            if let Ok(target_value) = target_dict.get_item(&key) {
                if let Some(target_val) = target_value {
                    if target_val.is_instance_of::<PyDict>() && value.is_instance_of::<PyDict>() {
                        // Recursive merge for dicts
                        merge(py, target_val, value)?;
                    } else {
                        // Overwrite
                        target_dict.set_item(&key, value)?;
                    }
                } else {
                     target_dict.set_item(&key, value)?;
                }
            } else {
                target_dict.set_item(&key, value)?;
            }
        }
    }
    
    Ok(object.into())
}

/// Creates a deep clone of value.
#[pyfunction]
pub fn clone_deep(py: Python, value: Bound<PyAny>) -> PyResult<Py<PyAny>> {
    // Use Python's copy.deepcopy for correctness as implementing full deepcopy in Rust for PyAny is complex
    let copy_mod = py.import("copy")?;
    let deepcopy = copy_mod.getattr("deepcopy")?;
    let result = deepcopy.call1((value,))?;
    Ok(result.into())
}

/// Creates an object composed of the picked object properties.
#[pyfunction]
pub fn pick(py: Python, object: Bound<PyDict>, paths: Bound<PyList>) -> PyResult<Py<PyDict>> {
    let result = PyDict::new(py);
    for path in paths.iter() {
        let key = path.extract::<String>()?;
        if let Some(value) = object.get_item(&key)? {
            result.set_item(key, value)?;
        }
    }
    Ok(result.into())
}

/// The opposite of `pick`; this method creates an object composed of the own and inherited enumerable property paths of object that are not omitted.
#[pyfunction]
pub fn omit(py: Python, object: Bound<PyDict>, paths: Bound<PyList>) -> PyResult<Py<PyDict>> {
    let result = object.copy()?;
    for path in paths.iter() {
        let key = path.extract::<String>()?;
        if result.contains(&key)? {
            result.del_item(key)?;
        }
    }
    Ok(result.into())
}

/// Checks if path is a direct property of object.
#[pyfunction]
pub fn has(object: Bound<PyAny>, path: &str) -> PyResult<bool> {
    let keys: Vec<&str> = path.split('.').collect();
    let mut current = object;

    for key in keys {
        if let Ok(item) = current.get_item(key) {
            current = item;
        } else {
            return Ok(false);
        }
    }
    Ok(true)
}

/// Creates an object composed of the inverted keys and values of object.
#[pyfunction]
pub fn invert(py: Python, object: Bound<PyDict>) -> PyResult<Py<PyDict>> {
    let result = PyDict::new(py);
    for (key, value) in object.iter() {
        // Value becomes key, key becomes value. Value must be hashable.
        result.set_item(value, key)?;
    }
    Ok(result.into())
}

/// Creates an array of the own enumerable property names of object.
#[pyfunction]
pub fn keys(py: Python, object: Bound<PyDict>) -> PyResult<Py<PyList>> {
    Ok(object.keys().into())
}

/// Creates an array of the own enumerable string keyed property values of object.
#[pyfunction]
pub fn values(py: Python, object: Bound<PyDict>) -> PyResult<Py<PyList>> {
    Ok(object.values().into())
}

#[pymodule]
pub fn object(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get, m)?)?;
    m.add_function(wrap_pyfunction!(set, m)?)?;
    m.add_function(wrap_pyfunction!(merge, m)?)?;
    m.add_function(wrap_pyfunction!(clone_deep, m)?)?;
    m.add_function(wrap_pyfunction!(pick, m)?)?;
    m.add_function(wrap_pyfunction!(omit, m)?)?;
    m.add_function(wrap_pyfunction!(has, m)?)?;
    m.add_function(wrap_pyfunction!(invert, m)?)?;
    m.add_function(wrap_pyfunction!(keys, m)?)?;
    m.add_function(wrap_pyfunction!(values, m)?)?;
    Ok(())
}
