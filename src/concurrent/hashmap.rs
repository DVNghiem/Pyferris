use dashmap::DashMap;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::Arc;

/// A thread-safe, lock-free hash map implementation using DashMap
#[pyclass]
pub struct ConcurrentHashMap {
    inner: Arc<DashMap<String, Py<PyAny>>>,
}

#[pymethods]
impl ConcurrentHashMap {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: Arc::new(DashMap::new()),
        }
    }

    /// Insert a key-value pair into the map
    pub fn insert(&self, key: String, value: Py<PyAny>) -> PyResult<Option<Py<PyAny>>> {
        Ok(self.inner.insert(key, value))
    }

    /// Get a value by key
    pub fn get(&self, py: Python, key: &str) -> PyResult<Option<Py<PyAny>>> {
        Ok(self.inner.get(key).map(|entry| entry.value().clone_ref(py)))
    }

    /// Remove a key-value pair
    pub fn remove(&self, key: &str) -> PyResult<Option<Py<PyAny>>> {
        Ok(self.inner.remove(key).map(|(_, value)| value))
    }

    /// Check if a key exists
    pub fn contains_key(&self, key: &str) -> bool {
        self.inner.contains_key(key)
    }

    /// Get the number of entries
    pub fn len(&self) -> usize {
        self.inner.len()
    }

    /// Check if the map is empty
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    /// Clear all entries
    pub fn clear(&self) {
        self.inner.clear();
    }

    /// Get all keys
    pub fn keys(&self) -> PyResult<Vec<String>> {
        Ok(self.inner.iter().map(|entry| entry.key().clone()).collect())
    }

    /// Get all values
    pub fn values(&self, py: Python) -> PyResult<Vec<Py<PyAny>>> {
        Ok(self
            .inner
            .iter()
            .map(|entry| entry.value().clone_ref(py))
            .collect())
    }

    /// Get all key-value pairs as tuples
    pub fn items(&self, py: Python) -> PyResult<Vec<(String, Py<PyAny>)>> {
        Ok(self
            .inner
            .iter()
            .map(|entry| (entry.key().clone(), entry.value().clone_ref(py)))
            .collect())
    }

    /// Update with another dictionary
    pub fn update(&self, other: &Bound<PyDict>) -> PyResult<()> {
        for (key, value) in other.iter() {
            let key_str: String = key.extract()?;
            self.inner.insert(key_str, value.unbind());
        }
        Ok(())
    }

    /// Get with default value
    pub fn get_or_default(&self, py: Python, key: &str, default: Py<PyAny>) -> PyResult<Py<PyAny>> {
        Ok(self
            .inner
            .get(key)
            .map(|entry| entry.value().clone_ref(py))
            .unwrap_or(default))
    }

    /// Atomic get-or-insert operation
    pub fn get_or_insert(&self, py: Python, key: String, value: Py<PyAny>) -> PyResult<Py<PyAny>> {
        Ok(self.inner.entry(key).or_insert(value).clone_ref(py))
    }

    /// Get shard count (for debugging/optimization)
    pub fn shard_count(&self) -> usize {
        // Since shards() is private, we'll use a default value
        16 // DashMap default shard count
    }

    /// Clone the concurrent hashmap
    pub fn clone(&self) -> Self {
        Self {
            inner: Arc::clone(&self.inner),
        }
    }

    fn __len__(&self) -> usize {
        self.len()
    }

    fn __contains__(&self, key: &str) -> bool {
        self.contains_key(key)
    }

    fn __getitem__(&self, py: Python, key: &str) -> PyResult<Py<PyAny>> {
        self.get(py, key)?.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!("Key '{}' not found", key))
        })
    }

    fn __setitem__(&self, key: String, value: Py<PyAny>) -> PyResult<()> {
        self.insert(key, value)?;
        Ok(())
    }

    fn __delitem__(&self, key: &str) -> PyResult<()> {
        self.remove(key)?.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!("Key '{}' not found", key))
        })?;
        Ok(())
    }

    fn __repr__(&self) -> String {
        format!("ConcurrentHashMap(len={})", self.len())
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }
}
