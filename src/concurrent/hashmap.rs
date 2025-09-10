use dashmap::DashMap;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::hash::Hash;
use std::sync::Arc;

/// A hashable key wrapper for Python objects
#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub struct PyKey(u64);

impl PyKey {
    pub fn new(_py: Python, obj: &Bound<PyAny>) -> PyResult<Self> {
        let hash = obj.hash()?;
        Ok(PyKey(hash as u64))
    }
}

/// A thread-safe, lock-free hash map implementation using DashMap with dynamic key types
#[pyclass]
pub struct ConcurrentHashMap {
    inner: Arc<DashMap<PyKey, (Py<PyAny>, Py<PyAny>)>>, // (key_obj, value)
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
    pub fn insert(&self, py: Python, key: Bound<PyAny>, value: Py<PyAny>) -> PyResult<Option<Py<PyAny>>> {
        let py_key = PyKey::new(py, &key)?;
        let key_obj = key.unbind();
        Ok(self.inner.insert(py_key, (key_obj, value)).map(|(_, v)| v))
    }

    /// Get a value by key
    pub fn get(&self, py: Python, key: Bound<PyAny>) -> PyResult<Option<Py<PyAny>>> {
        let py_key = PyKey::new(py, &key)?;
        Ok(self.inner.get(&py_key).map(|entry| entry.value().1.clone_ref(py)))
    }

    /// Remove a key-value pair
    pub fn remove(&self, py: Python, key: Bound<PyAny>) -> PyResult<Option<Py<PyAny>>> {
        let py_key = PyKey::new(py, &key)?;
        Ok(self.inner.remove(&py_key).map(|(_, (_, value))| value))
    }

    /// Check if a key exists
    pub fn contains_key(&self, py: Python, key: Bound<PyAny>) -> PyResult<bool> {
        let py_key = PyKey::new(py, &key)?;
        Ok(self.inner.contains_key(&py_key))
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
    pub fn keys(&self, py: Python) -> PyResult<Vec<Py<PyAny>>> {
        Ok(self.inner.iter().map(|entry| entry.value().0.clone_ref(py)).collect())
    }

    /// Get all values
    pub fn values(&self, py: Python) -> PyResult<Vec<Py<PyAny>>> {
        Ok(self
            .inner
            .iter()
            .map(|entry| entry.value().1.clone_ref(py))
            .collect())
    }

    /// Get all key-value pairs as tuples
    pub fn items(&self, py: Python) -> PyResult<Vec<(Py<PyAny>, Py<PyAny>)>> {
        Ok(self
            .inner
            .iter()
            .map(|entry| (entry.value().0.clone_ref(py), entry.value().1.clone_ref(py)))
            .collect())
    }

    /// Update with another dictionary
    pub fn update(&self, py: Python, other: &Bound<PyDict>) -> PyResult<()> {
        for (key, value) in other.iter() {
            let py_key = PyKey::new(py, &key)?;
            let key_obj = key.unbind();
            self.inner.insert(py_key, (key_obj, value.unbind()));
        }
        Ok(())
    }

    /// Get with default value
    pub fn get_or_default(&self, py: Python, key: Bound<PyAny>, default: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let py_key = PyKey::new(py, &key)?;
        Ok(self
            .inner
            .get(&py_key)
            .map(|entry| entry.value().1.clone_ref(py))
            .unwrap_or(default))
    }

    /// Atomic get-or-insert operation
    pub fn get_or_insert(&self, py: Python, key: Bound<PyAny>, value: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let py_key = PyKey::new(py, &key)?;
        let key_obj = key.unbind();
        let entry = self.inner.entry(py_key).or_insert((key_obj, value.clone_ref(py)));
        Ok(entry.1.clone_ref(py))
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

    fn __contains__(&self, py: Python, key: Bound<PyAny>) -> PyResult<bool> {
        self.contains_key(py, key)
    }

    fn __getitem__(&self, py: Python, key: Bound<PyAny>) -> PyResult<Py<PyAny>> {
        self.get(py, key.clone())?.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!("Key not found"))
        })
    }

    fn __setitem__(&self, py: Python, key: Bound<PyAny>, value: Py<PyAny>) -> PyResult<()> {
        self.insert(py, key, value)?;
        Ok(())
    }

    fn __delitem__(&self, py: Python, key: Bound<PyAny>) -> PyResult<()> {
        self.remove(py, key)?.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!("Key not found"))
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
