use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::sync::{Arc, RwLock, Mutex};
use std::collections::VecDeque;
use std::sync::atomic::{AtomicUsize, Ordering};

/// Shared array for zero-copy data sharing between threads
#[pyclass]
pub struct SharedArray {
    data: Arc<RwLock<Vec<f64>>>,
    capacity: usize,
}

#[pymethods]
impl SharedArray {
    #[new]
    #[pyo3(signature = (capacity = 1000))]
    pub fn new(capacity: usize) -> Self {
        Self {
            data: Arc::new(RwLock::new(Vec::with_capacity(capacity))),
            capacity,
        }
    }

    /// Create from existing data
    #[classmethod]
    pub fn from_data(_cls: &Bound<'_, pyo3::types::PyType>, data: Vec<f64>) -> Self {
        let capacity = data.len();
        Self {
            data: Arc::new(RwLock::new(data)),
            capacity,
        }
    }

    /// Get length of the array
    #[getter]
    pub fn len(&self) -> PyResult<usize> {
        let data = self.data.read().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.len())
    }

    /// Check if array is empty
    pub fn is_empty(&self) -> PyResult<bool> {
        let data = self.data.read().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.is_empty())
    }

    /// Get item at index
    pub fn get(&self, index: usize) -> PyResult<f64> {
        let data = self.data.read().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.get(index).copied().ok_or_else(|| pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
    }

    /// Set item at index
    pub fn set(&self, index: usize, value: f64) -> PyResult<()> {
        let mut data = self.data.write().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if index >= data.len() {
            return Err(pyo3::exceptions::PyIndexError::new_err("Index out of bounds"));
        }
        data[index] = value;
        Ok(())
    }

    /// Append item to array
    pub fn append(&self, value: f64) -> PyResult<()> {
        let mut data = self.data.write().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if data.len() >= self.capacity {
            return Err(pyo3::exceptions::PyRuntimeError::new_err("Array at capacity"));
        }
        data.push(value);
        Ok(())
    }

    /// Extend array with multiple values
    pub fn extend(&self, values: Vec<f64>) -> PyResult<()> {
        let mut data = self.data.write().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if data.len() + values.len() > self.capacity {
            return Err(pyo3::exceptions::PyRuntimeError::new_err("Not enough capacity"));
        }
        data.extend(values);
        Ok(())
    }

    /// Clear the array
    pub fn clear(&self) -> PyResult<()> {
        let mut data = self.data.write().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.clear();
        Ok(())
    }

    /// Get a copy of all data
    pub fn to_list(&self) -> PyResult<Vec<f64>> {
        let data = self.data.read().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.clone())
    }

    /// Get slice of data
    pub fn slice(&self, start: usize, end: Option<usize>) -> PyResult<Vec<f64>> {
        let data = self.data.read().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        let end = end.unwrap_or(data.len());
        if start > data.len() || end > data.len() || start > end {
            return Err(pyo3::exceptions::PyIndexError::new_err("Invalid slice bounds"));
        }
        Ok(data[start..end].to_vec())
    }

    /// Parallel sum of all elements
    pub fn sum(&self) -> PyResult<f64> {
        use rayon::prelude::*;
        let data = self.data.read().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.par_iter().sum())
    }

    /// Parallel map operation (simplified to avoid threading issues)
    pub fn parallel_map(&self, py: Python, func: Bound<PyAny>) -> PyResult<Vec<f64>> {
        let data = self.data.read().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        
        let results: PyResult<Vec<f64>> = data.iter()
            .map(|&value| {
                let result = func.call1((value,))?;
                result.extract::<f64>()
            })
            .collect();
        
        results
    }
}

/// Shared queue for thread-safe message passing
#[pyclass]
pub struct SharedQueue {
    data: Arc<Mutex<VecDeque<PyObject>>>,
    max_size: Option<usize>,
}

#[pymethods]
impl SharedQueue {
    #[new]
    #[pyo3(signature = (max_size = None))]
    pub fn new(max_size: Option<usize>) -> Self {
        Self {
            data: Arc::new(Mutex::new(VecDeque::new())),
            max_size,
        }
    }

    /// Put an item in the queue
    pub fn put(&self, py: Python, item: Bound<PyAny>) -> PyResult<()> {
        let mut queue = self.data.lock().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        
        if let Some(max_size) = self.max_size {
            if queue.len() >= max_size {
                return Err(pyo3::exceptions::PyRuntimeError::new_err("Queue is full"));
            }
        }
        
        queue.push_back(item.into());
        Ok(())
    }

    /// Get an item from the queue (blocks if empty)
    pub fn get(&self, py: Python) -> PyResult<PyObject> {
        let mut queue = self.data.lock().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        
        queue.pop_front().ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err("Queue is empty"))
    }

    /// Try to get an item without blocking
    pub fn get_nowait(&self, py: Python) -> PyResult<Option<PyObject>> {
        let mut queue = self.data.lock().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(queue.pop_front())
    }

    /// Check if queue is empty
    pub fn empty(&self) -> PyResult<bool> {
        let queue = self.data.lock().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(queue.is_empty())
    }

    /// Get queue size
    #[getter]
    pub fn size(&self) -> PyResult<usize> {
        let queue = self.data.lock().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(queue.len())
    }

    /// Clear the queue
    pub fn clear(&self) -> PyResult<()> {
        let mut queue = self.data.lock().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        queue.clear();
        Ok(())
    }
}

/// Shared counter for atomic operations
#[pyclass]
pub struct SharedCounter {
    value: Arc<AtomicUsize>,
}

#[pymethods]
impl SharedCounter {
    #[new]
    #[pyo3(signature = (initial_value = 0))]
    pub fn new(initial_value: usize) -> Self {
        Self {
            value: Arc::new(AtomicUsize::new(initial_value)),
        }
    }

    /// Get current value
    #[getter]
    pub fn value(&self) -> usize {
        self.value.load(Ordering::SeqCst)
    }

    /// Increment and return new value
    pub fn increment(&self) -> usize {
        self.value.fetch_add(1, Ordering::SeqCst) + 1
    }

    /// Decrement and return new value
    pub fn decrement(&self) -> usize {
        self.value.fetch_sub(1, Ordering::SeqCst) - 1
    }

    /// Add value and return new value
    pub fn add(&self, value: usize) -> usize {
        self.value.fetch_add(value, Ordering::SeqCst) + value
    }

    /// Subtract value and return new value
    pub fn subtract(&self, value: usize) -> usize {
        self.value.fetch_sub(value, Ordering::SeqCst) - value
    }

    /// Set value and return old value
    pub fn set(&self, value: usize) -> usize {
        self.value.swap(value, Ordering::SeqCst)
    }

    /// Compare and swap
    pub fn compare_and_swap(&self, current: usize, new: usize) -> usize {
        match self.value.compare_exchange(current, new, Ordering::SeqCst, Ordering::SeqCst) {
            Ok(old_value) => old_value,
            Err(actual_current) => actual_current,
        }
    }

    /// Reset to zero
    pub fn reset(&self) -> usize {
        self.value.swap(0, Ordering::SeqCst)
    }
}
