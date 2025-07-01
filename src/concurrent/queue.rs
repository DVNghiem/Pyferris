use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::{Arc, RwLock, atomic::{AtomicI64, Ordering}};
use crossbeam::queue::SegQueue;
use std::collections::HashMap;

/// A lock-free queue implementation using crossbeam
#[pyclass]
pub struct LockFreeQueue {
    inner: Arc<SegQueue<PyObject>>,
}

#[pymethods]
impl LockFreeQueue {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: Arc::new(SegQueue::new()),
        }
    }

    /// Push an item to the queue
    pub fn push(&self, py: Python, item: PyObject) {
        self.inner.push(item);
    }

    /// Pop an item from the queue (returns None if empty)
    pub fn pop(&self, py: Python) -> Option<PyObject> {
        self.inner.pop()
    }

    /// Check if the queue is empty
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    /// Get approximate length (may not be exact due to concurrent operations)
    pub fn len(&self) -> usize {
        self.inner.len()
    }

    /// Clear all items from the queue
    pub fn clear(&self) {
        while !self.inner.is_empty() {
            self.inner.pop();
        }
    }

    /// Clone the queue
    pub fn clone(&self) -> Self {
        Self {
            inner: Arc::clone(&self.inner),
        }
    }

    fn __len__(&self) -> usize {
        self.len()
    }

    fn __repr__(&self) -> String {
        format!("LockFreeQueue(len={})", self.len())
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }
}

/// An atomic counter for thread-safe counting operations
#[pyclass]
pub struct AtomicCounter {
    inner: Arc<AtomicI64>,
}

#[pymethods]
impl AtomicCounter {
    #[new]
    pub fn new(initial_value: Option<i64>) -> Self {
        Self {
            inner: Arc::new(AtomicI64::new(initial_value.unwrap_or(0))),
        }
    }

    /// Get the current value
    pub fn get(&self) -> i64 {
        self.inner.load(Ordering::SeqCst)
    }

    /// Set the value
    pub fn set(&self, value: i64) {
        self.inner.store(value, Ordering::SeqCst);
    }

    /// Increment by 1 and return the new value
    pub fn increment(&self) -> i64 {
        self.inner.fetch_add(1, Ordering::SeqCst) + 1
    }

    /// Decrement by 1 and return the new value
    pub fn decrement(&self) -> i64 {
        self.inner.fetch_sub(1, Ordering::SeqCst) - 1
    }

    /// Add a value and return the new value
    pub fn add(&self, value: i64) -> i64 {
        self.inner.fetch_add(value, Ordering::SeqCst) + value
    }

    /// Subtract a value and return the new value
    pub fn sub(&self, value: i64) -> i64 {
        self.inner.fetch_sub(value, Ordering::SeqCst) - value
    }

    /// Compare and swap - atomically sets new value if current equals expected
    pub fn compare_and_swap(&self, expected: i64, new: i64) -> i64 {
        self.inner.compare_exchange(expected, new, Ordering::SeqCst, Ordering::SeqCst)
            .unwrap_or_else(|x| x)
    }

    /// Reset to zero
    pub fn reset(&self) {
        self.inner.store(0, Ordering::SeqCst);
    }

    /// Clone the counter (shares the same underlying atomic value)
    pub fn clone(&self) -> Self {
        Self {
            inner: Arc::clone(&self.inner),
        }
    }

    fn __repr__(&self) -> String {
        format!("AtomicCounter(value={})", self.get())
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn __int__(&self) -> i64 {
        self.get()
    }

    fn __add__(&self, other: i64) -> i64 {
        self.add(other)
    }

    fn __sub__(&self, other: i64) -> i64 {
        self.sub(other)
    }
}

/// A readers-writer lock dictionary for concurrent read access with exclusive write access
#[pyclass]
pub struct RwLockDict {
    inner: Arc<RwLock<HashMap<String, PyObject>>>,
}

#[pymethods]
impl RwLockDict {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Get a value by key (allows concurrent reads)
    pub fn get(&self, py: Python, key: &str) -> PyResult<Option<PyObject>> {
        let map = self.inner.read().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(map.get(key).map(|v| v.clone_ref(py)))
    }

    /// Insert a key-value pair (exclusive write access)
    pub fn insert(&self, py: Python, key: String, value: PyObject) -> PyResult<Option<PyObject>> {
        let mut map = self.inner.write().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(map.insert(key, value))
    }

    /// Remove a key-value pair (exclusive write access)
    pub fn remove(&self, py: Python, key: &str) -> PyResult<Option<PyObject>> {
        let mut map = self.inner.write().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(map.remove(key))
    }

    /// Check if a key exists (allows concurrent reads)
    pub fn contains_key(&self, key: &str) -> PyResult<bool> {
        let map = self.inner.read().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(map.contains_key(key))
    }

    /// Get the number of entries (allows concurrent reads)
    pub fn len(&self) -> PyResult<usize> {
        let map = self.inner.read().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(map.len())
    }

    /// Check if the dictionary is empty (allows concurrent reads)
    pub fn is_empty(&self) -> PyResult<bool> {
        let map = self.inner.read().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(map.is_empty())
    }

    /// Clear all entries (exclusive write access)
    pub fn clear(&self) -> PyResult<()> {
        let mut map = self.inner.write().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        map.clear();
        Ok(())
    }

    /// Get all keys (allows concurrent reads)
    pub fn keys(&self, py: Python) -> PyResult<Vec<String>> {
        let map = self.inner.read().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(map.keys().cloned().collect())
    }

    /// Get all values (allows concurrent reads)
    pub fn values(&self, py: Python) -> PyResult<Vec<PyObject>> {
        let map = self.inner.read().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(map.values().map(|v| v.clone_ref(py)).collect())
    }

    /// Get all key-value pairs as tuples (allows concurrent reads)
    pub fn items(&self, py: Python) -> PyResult<Vec<(String, PyObject)>> {
        let map = self.inner.read().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(map.iter().map(|(k, v)| (k.clone(), v.clone_ref(py))).collect())
    }

    /// Update with another dictionary (exclusive write access)
    pub fn update(&self, py: Python, other: &Bound<PyDict>) -> PyResult<()> {
        let mut map = self.inner.write().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        for (key, value) in other.iter() {
            let key_str: String = key.extract()?;
            map.insert(key_str, value.unbind());
        }
        Ok(())
    }

    /// Get with default value (allows concurrent reads)
    pub fn get_or_default(&self, py: Python, key: &str, default: PyObject) -> PyResult<PyObject> {
        let map = self.inner.read().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(map.get(key).map(|v| v.clone_ref(py)).unwrap_or(default))
    }

    /// Clone the RwLockDict (shares the same underlying data)
    pub fn clone(&self) -> Self {
        Self {
            inner: Arc::clone(&self.inner),
        }
    }

    fn __len__(&self) -> PyResult<usize> {
        self.len()
    }

    fn __contains__(&self, key: &str) -> PyResult<bool> {
        self.contains_key(key)
    }

    fn __getitem__(&self, py: Python, key: &str) -> PyResult<PyObject> {
        self.get(py, key)?
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!("Key '{}' not found", key)))
    }

    fn __setitem__(&self, py: Python, key: String, value: PyObject) -> PyResult<()> {
        self.insert(py, key, value)?;
        Ok(())
    }

    fn __delitem__(&self, py: Python, key: &str) -> PyResult<()> {
        self.remove(py, key)?
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!("Key '{}' not found", key)))?;
        Ok(())
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("RwLockDict(len={})", self.len()?))
    }

    fn __str__(&self) -> PyResult<String> {
        self.__repr__()
    }
}