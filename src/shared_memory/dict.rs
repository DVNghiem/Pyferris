use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

/// Shared dictionary for thread-safe key-value storage
#[pyclass]
pub struct SharedDict {
    data: Arc<RwLock<HashMap<String, Py<PyAny>>>>,
}

#[pymethods]
impl SharedDict {
    #[new]
    pub fn new() -> Self {
        Self {
            data: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Create from existing dictionary
    #[classmethod]
    pub fn from_dict(_cls: &Bound<'_, pyo3::types::PyType>, dict: Bound<PyDict>) -> PyResult<Self> {
        let mut map = HashMap::new();

        for (key, value) in dict.iter() {
            let key_str = key.extract::<String>()?;
            map.insert(key_str, value.into());
        }

        Ok(Self {
            data: Arc::new(RwLock::new(map)),
        })
    }

    /// Get value by key
    pub fn get(&self, py: Python, key: &str) -> PyResult<Option<Py<PyAny>>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.get(key).map(|v| v.clone_ref(py)))
    }

    /// Set value by key
    pub fn set(&self, key: &str, value: Bound<PyAny>) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.insert(key.to_string(), value.into());
        Ok(())
    }

    /// Check if key exists
    pub fn contains(&self, key: &str) -> PyResult<bool> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.contains_key(key))
    }

    /// Remove key and return value
    pub fn pop(&self, key: &str) -> PyResult<Option<Py<PyAny>>> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.remove(key))
    }

    /// Get all keys
    pub fn keys(&self) -> PyResult<Vec<String>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.keys().cloned().collect())
    }

    /// Get all values
    pub fn values(&self, py: Python) -> PyResult<Vec<Py<PyAny>>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.values().map(|v| v.clone_ref(py)).collect())
    }

    /// Get all items as tuples
    pub fn items(&self, py: Python) -> PyResult<Vec<(String, Py<PyAny>)>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data
            .iter()
            .map(|(k, v)| (k.clone(), v.clone_ref(py)))
            .collect())
    }

    /// Get length
    #[getter]
    pub fn len(&self) -> PyResult<usize> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.len())
    }

    /// Check if empty
    pub fn is_empty(&self) -> PyResult<bool> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.is_empty())
    }

    /// Clear all items
    pub fn clear(&self) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.clear();
        Ok(())
    }

    /// Update with another dictionary
    pub fn update(&self, other: Bound<PyDict>) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;

        for (key, value) in other.iter() {
            let key_str = key.extract::<String>()?;
            data.insert(key_str, value.into());
        }

        Ok(())
    }

    /// Get or set default value
    pub fn setdefault(&self, py: Python, key: &str, default: Bound<PyAny>) -> PyResult<Py<PyAny>> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;

        if let Some(existing) = data.get(key) {
            Ok(existing.clone_ref(py))
        } else {
            let default_obj: Py<PyAny> = default.into();
            data.insert(key.to_string(), default_obj.clone_ref(py));
            Ok(default_obj)
        }
    }

    /// Convert to Python dictionary
    pub fn to_dict(&self, py: Python) -> PyResult<Py<PyDict>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        let dict = PyDict::new(py);

        for (key, value) in data.iter() {
            dict.set_item(key, value)?;
        }

        Ok(dict.into())
    }

    /// Map over values (sequential to avoid GIL issues)
    pub fn parallel_map_values(&self, py: Python, func: Bound<PyAny>) -> PyResult<Py<PyDict>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        let items: Vec<(String, Py<PyAny>)> = data
            .iter()
            .map(|(k, v)| (k.clone(), v.clone_ref(py)))
            .collect();
        drop(data); // Release read lock

        // Sequential processing to avoid GIL issues
        let results: PyResult<Vec<(String, Py<PyAny>)>> = items
            .iter()
            .map(|(key, value)| {
                let bound_value = value.bind(py);
                let result = func.call1((bound_value,))?;
                Ok((key.clone(), result.into()))
            })
            .collect();

        let result_dict = PyDict::new(py);
        for (key, value) in results? {
            result_dict.set_item(key, value)?;
        }

        Ok(result_dict.into())
    }
}
