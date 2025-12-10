use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyBool};
use rand::seq::SliceRandom;
use rand::thread_rng;

/// Creates an object composed of keys generated from the results of running each element of collection thru iteratee.
#[pyfunction]
pub fn group_by(py: Python, collection: Bound<PyList>, iteratee: Bound<PyAny>) -> PyResult<Py<PyDict>> {
    let result = PyDict::new(py);
    
    for item in collection.iter() {
        let key = if iteratee.is_callable() {
            iteratee.call1((&item,))?
        } else {
            // Assume iteratee is a string key or index
            item.get_item(&iteratee)?
        };
        
        if result.contains(&key)? {
            let list = result.get_item(&key)?.unwrap().downcast::<PyList>()?.clone();
            list.append(&item)?;
        } else {
            let list = PyList::new(py, vec![item])?;
            result.set_item(&key, list)?;
        }
    }
    
    Ok(result.into())
}

/// Creates an object composed of keys generated from the results of running each element of collection thru iteratee. The corresponding value of each key is the number of times the key was returned by iteratee.
#[pyfunction]
pub fn count_by(py: Python, collection: Bound<PyList>, iteratee: Bound<PyAny>) -> PyResult<Py<PyDict>> {
    let result = PyDict::new(py);
    
    for item in collection.iter() {
        let key = if iteratee.is_callable() {
            iteratee.call1((&item,))?
        } else {
            item.get_item(&iteratee)?
        };
        
        if result.contains(&key)? {
            let count: i64 = result.get_item(&key)?.unwrap().extract()?;
            result.set_item(&key, count + 1)?;
        } else {
            result.set_item(&key, 1)?;
        }
    }
    
    Ok(result.into())
}

/// Creates an array of shuffled values, using a version of the Fisher-Yates shuffle.
#[pyfunction]
pub fn shuffle(py: Python, collection: Bound<PyList>) -> PyResult<Py<PyList>> {
    // Convert to Rust vector to shuffle
    let mut items: Vec<Py<PyAny>> = collection.iter().map(|i| i.into()).collect();
    let mut rng = thread_rng();
    items.shuffle(&mut rng);
    
    Ok(PyList::new(py, items)?.into())
}

/// Gets a random element from collection.
#[pyfunction]
pub fn sample(py: Python, collection: Bound<PyList>) -> PyResult<Py<PyAny>> {
    let len = collection.len();
    if len == 0 {
        return Ok(py.None());
    }
    
    let mut rng = thread_rng();
    let index = rand::Rng::gen_range(&mut rng, 0..len);
    let item = collection.get_item(index)?;
    Ok(item.into())
}

/// Creates an object composed of keys generated from the results of running each element of collection thru iteratee. The corresponding value of each key is the last element responsible for generating the key.
#[pyfunction]
pub fn key_by(py: Python, collection: Bound<PyList>, iteratee: Bound<PyAny>) -> PyResult<Py<PyDict>> {
    let result = PyDict::new(py);
    
    for item in collection.iter() {
        let key = if iteratee.is_callable() {
            iteratee.call1((&item,))?
        } else {
            item.get_item(&iteratee)?
        };
        result.set_item(key, item)?;
    }
    
    Ok(result.into())
}

/// Creates an array of elements split into two groups, the first of which contains elements predicate returns truthy for, the second of which contains elements predicate returns falsey for.
#[pyfunction]
pub fn partition(py: Python, collection: Bound<PyList>, predicate: Bound<PyAny>) -> PyResult<(Py<PyList>, Py<PyList>)> {
    let true_list = PyList::empty(py);
    let false_list = PyList::empty(py);
    
    for item in collection.iter() {
        let is_true = if predicate.is_callable() {
            predicate.call1((&item,))?.is_truthy()?
        } else {
            // If predicate is not callable, treat it as a property match (shorthand)
            // This is a simplification; full Lodash supports deep matches
            if let Ok(val) = item.get_item(&predicate) {
                val.is_truthy()?
            } else {
                false
            }
        };
        
        if is_true {
            true_list.append(&item)?;
        } else {
            false_list.append(&item)?;
        }
    }
    
    Ok((true_list.into(), false_list.into()))
}

/// Checks if predicate returns truthy for all elements of collection.
#[pyfunction]
pub fn every(collection: Bound<PyList>, predicate: Bound<PyAny>) -> PyResult<bool> {
    for item in collection.iter() {
        let is_true = if predicate.is_callable() {
            predicate.call1((&item,))?.is_truthy()?
        } else {
            if let Ok(val) = item.get_item(&predicate) {
                val.is_truthy()?
            } else {
                false
            }
        };
        
        if !is_true {
            return Ok(false);
        }
    }
    Ok(true)
}

/// Checks if predicate returns truthy for any element of collection.
#[pyfunction]
pub fn some(collection: Bound<PyList>, predicate: Bound<PyAny>) -> PyResult<bool> {
    for item in collection.iter() {
        let is_true = if predicate.is_callable() {
            predicate.call1((&item,))?.is_truthy()?
        } else {
            if let Ok(val) = item.get_item(&predicate) {
                val.is_truthy()?
            } else {
                false
            }
        };
        
        if is_true {
            return Ok(true);
        }
    }
    Ok(false)
}

#[pymodule]
pub fn collection(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(group_by, m)?)?;
    m.add_function(wrap_pyfunction!(count_by, m)?)?;
    m.add_function(wrap_pyfunction!(shuffle, m)?)?;
    m.add_function(wrap_pyfunction!(sample, m)?)?;
    m.add_function(wrap_pyfunction!(key_by, m)?)?;
    m.add_function(wrap_pyfunction!(partition, m)?)?;
    m.add_function(wrap_pyfunction!(every, m)?)?;
    m.add_function(wrap_pyfunction!(some, m)?)?;
    Ok(())
}
