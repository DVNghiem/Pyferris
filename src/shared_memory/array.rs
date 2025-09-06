use pyo3::prelude::*;
use std::collections::VecDeque;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex, RwLock};

/// Shared array for zero-copy data sharing between threads (Float64 type)
#[pyclass]
pub struct SharedArray {
    data: Arc<RwLock<Vec<f64>>>,
    capacity: usize,
}

/// Shared array for integers
#[pyclass]
pub struct SharedArrayInt {
    data: Arc<RwLock<Vec<i64>>>,
    capacity: usize,
}

/// Shared array for strings
#[pyclass]
pub struct SharedArrayStr {
    data: Arc<RwLock<Vec<String>>>,
    capacity: usize,
}

/// Shared array for generic Python objects
#[pyclass]
pub struct SharedArrayObj {
    data: Arc<RwLock<Vec<Py<PyAny>>>>,
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
        let capacity = std::cmp::max(data.len() * 3 / 2, data.len() + 10); // 50% more or at least +10
        Self {
            data: Arc::new(RwLock::new(data)),
            capacity,
        }
    }

    /// Get length of the array
    #[getter]
    pub fn len(&self) -> PyResult<usize> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.len())
    }

    /// Check if array is empty
    pub fn is_empty(&self) -> PyResult<bool> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.is_empty())
    }

    /// Get item at index
    pub fn get(&self, index: usize) -> PyResult<f64> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.get(index)
            .copied()
            .ok_or_else(|| pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
    }

    /// Set item at index
    pub fn set(&self, index: usize, value: f64) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if index >= data.len() {
            return Err(pyo3::exceptions::PyIndexError::new_err(
                "Index out of bounds",
            ));
        }
        data[index] = value;
        Ok(())
    }

    /// Append item to array
    pub fn append(&self, value: f64) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if data.len() >= self.capacity {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Array at capacity",
            ));
        }
        data.push(value);
        Ok(())
    }

    /// Extend array with multiple values
    pub fn extend(&self, values: Vec<f64>) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if data.len() + values.len() > self.capacity {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Not enough capacity",
            ));
        }
        data.extend(values);
        Ok(())
    }

    /// Clear the array
    pub fn clear(&self) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.clear();
        Ok(())
    }

    /// Get a copy of all data
    pub fn to_list(&self) -> PyResult<Vec<f64>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.clone())
    }

    /// Get slice of data
    pub fn slice(&self, start: usize, end: Option<usize>) -> PyResult<Vec<f64>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        let end = end.unwrap_or(data.len());
        if start > data.len() || end > data.len() || start > end {
            return Err(pyo3::exceptions::PyIndexError::new_err(
                "Invalid slice bounds",
            ));
        }
        Ok(data[start..end].to_vec())
    }

    /// Parallel sum of all elements
    pub fn sum(&self) -> PyResult<f64> {
        use rayon::prelude::*;
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.par_iter().sum())
    }

    /// Parallel map operation (simplified to avoid threading issues)
    pub fn parallel_map(&self, func: Bound<PyAny>) -> PyResult<Vec<f64>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;

        let results: PyResult<Vec<f64>> = data
            .iter()
            .map(|&value| {
                let result = func.call1((value,))?;
                result.extract::<f64>()
            })
            .collect();

        results
    }
}

// Implementation for SharedArrayInt (integers)
#[pymethods]
impl SharedArrayInt {
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
    pub fn from_data(_cls: &Bound<'_, pyo3::types::PyType>, data: Vec<i64>) -> Self {
        let capacity = std::cmp::max(data.len() * 3 / 2, data.len() + 10); // 50% more or at least +10
        Self {
            data: Arc::new(RwLock::new(data)),
            capacity,
        }
    }

    /// Get length of the array
    #[getter]
    pub fn len(&self) -> PyResult<usize> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.len())
    }

    /// Check if array is empty
    pub fn is_empty(&self) -> PyResult<bool> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.is_empty())
    }

    /// Get item at index
    pub fn get(&self, index: usize) -> PyResult<i64> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.get(index)
            .copied()
            .ok_or_else(|| pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
    }

    /// Set item at index
    pub fn set(&self, index: usize, value: i64) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if index >= data.len() {
            return Err(pyo3::exceptions::PyIndexError::new_err(
                "Index out of bounds",
            ));
        }
        data[index] = value;
        Ok(())
    }

    /// Append item to array
    pub fn append(&self, value: i64) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if data.len() >= self.capacity {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Array at capacity",
            ));
        }
        data.push(value);
        Ok(())
    }

    /// Extend array with multiple values
    pub fn extend(&self, values: Vec<i64>) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if data.len() + values.len() > self.capacity {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Not enough capacity",
            ));
        }
        data.extend(values);
        Ok(())
    }

    /// Clear the array
    pub fn clear(&self) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.clear();
        Ok(())
    }

    /// Get a copy of all data
    pub fn to_list(&self) -> PyResult<Vec<i64>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.clone())
    }

    /// Get slice of data
    pub fn slice(&self, start: usize, end: Option<usize>) -> PyResult<Vec<i64>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        let end = end.unwrap_or(data.len());
        if start > data.len() || end > data.len() || start > end {
            return Err(pyo3::exceptions::PyIndexError::new_err(
                "Invalid slice bounds",
            ));
        }
        Ok(data[start..end].to_vec())
    }

    /// Parallel sum of all elements
    pub fn sum(&self) -> PyResult<i64> {
        use rayon::prelude::*;
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.par_iter().sum())
    }

    /// Parallel map operation
    pub fn parallel_map(&self, _py: Python, func: Bound<PyAny>) -> PyResult<Vec<i64>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;

        let results: PyResult<Vec<i64>> = data
            .iter()
            .map(|&value| {
                let result = func.call1((value,))?;
                result.extract::<i64>()
            })
            .collect();

        results
    }
}

// Implementation for SharedArrayStr (strings)
#[pymethods]
impl SharedArrayStr {
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
    pub fn from_data(_cls: &Bound<'_, pyo3::types::PyType>, data: Vec<String>) -> Self {
        let capacity = std::cmp::max(data.len() * 3 / 2, data.len() + 10); // 50% more or at least +10
        Self {
            data: Arc::new(RwLock::new(data)),
            capacity,
        }
    }

    /// Get length of the array
    #[getter]
    pub fn len(&self) -> PyResult<usize> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.len())
    }

    /// Check if array is empty
    pub fn is_empty(&self) -> PyResult<bool> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.is_empty())
    }

    /// Get item at index
    pub fn get(&self, index: usize) -> PyResult<String> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.get(index)
            .cloned()
            .ok_or_else(|| pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
    }

    /// Set item at index
    pub fn set(&self, index: usize, value: String) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if index >= data.len() {
            return Err(pyo3::exceptions::PyIndexError::new_err(
                "Index out of bounds",
            ));
        }
        data[index] = value;
        Ok(())
    }

    /// Append item to array
    pub fn append(&self, value: String) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if data.len() >= self.capacity {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Array at capacity",
            ));
        }
        data.push(value);
        Ok(())
    }

    /// Extend array with multiple values
    pub fn extend(&self, values: Vec<String>) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if data.len() + values.len() > self.capacity {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Not enough capacity",
            ));
        }
        data.extend(values);
        Ok(())
    }

    /// Clear the array
    pub fn clear(&self) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.clear();
        Ok(())
    }

    /// Get a copy of all data
    pub fn to_list(&self) -> PyResult<Vec<String>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.clone())
    }

    /// Get slice of data
    pub fn slice(&self, start: usize, end: Option<usize>) -> PyResult<Vec<String>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        let end = end.unwrap_or(data.len());
        if start > data.len() || end > data.len() || start > end {
            return Err(pyo3::exceptions::PyIndexError::new_err(
                "Invalid slice bounds",
            ));
        }
        Ok(data[start..end].to_vec())
    }

    /// Parallel map operation
    pub fn parallel_map(&self, _py: Python, func: Bound<PyAny>) -> PyResult<Vec<String>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;

        let results: PyResult<Vec<String>> = data
            .iter()
            .map(|value| {
                let result = func.call1((value,))?;
                result.extract::<String>()
            })
            .collect();

        results
    }
}

// Implementation for SharedArrayObj (generic Python objects)
#[pymethods]
impl SharedArrayObj {
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
    pub fn from_data(_cls: &Bound<'_, pyo3::types::PyType>, data: Vec<Bound<PyAny>>) -> Self {
        let capacity = std::cmp::max(data.len() * 3 / 2, data.len() + 10); // 50% more or at least +10
        let objects: Vec<Py<PyAny>> = data.into_iter().map(|obj| obj.into()).collect();
        Self {
            data: Arc::new(RwLock::new(objects)),
            capacity,
        }
    }

    /// Get length of the array
    #[getter]
    pub fn len(&self) -> PyResult<usize> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.len())
    }

    /// Check if array is empty
    pub fn is_empty(&self) -> PyResult<bool> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.is_empty())
    }

    /// Get item at index
    pub fn get(&self, py: Python, index: usize) -> PyResult<Py<PyAny>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.get(index)
            .map(|obj| obj.clone_ref(py))
            .ok_or_else(|| pyo3::exceptions::PyIndexError::new_err("Index out of bounds"))
    }

    /// Set item at index
    pub fn set(&self, index: usize, value: Bound<PyAny>) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if index >= data.len() {
            return Err(pyo3::exceptions::PyIndexError::new_err(
                "Index out of bounds",
            ));
        }
        data[index] = value.into();
        Ok(())
    }

    /// Append item to array
    pub fn append(&self, value: Bound<PyAny>) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if data.len() >= self.capacity {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Array at capacity",
            ));
        }
        data.push(value.into());
        Ok(())
    }

    /// Extend array with multiple values
    pub fn extend(&self, values: Vec<Bound<PyAny>>) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        if data.len() + values.len() > self.capacity {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Not enough capacity",
            ));
        }
        data.extend(values.into_iter().map(|obj| obj.into()));
        Ok(())
    }

    /// Clear the array
    pub fn clear(&self) -> PyResult<()> {
        let mut data = self
            .data
            .write()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        data.clear();
        Ok(())
    }

    /// Get a copy of all data
    pub fn to_list(&self, py: Python) -> PyResult<Vec<Py<PyAny>>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(data.iter().map(|obj| obj.clone_ref(py)).collect())
    }

    /// Get slice of data
    pub fn slice(&self, py: Python, start: usize, end: Option<usize>) -> PyResult<Vec<Py<PyAny>>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        let end = end.unwrap_or(data.len());
        if start > data.len() || end > data.len() || start > end {
            return Err(pyo3::exceptions::PyIndexError::new_err(
                "Invalid slice bounds",
            ));
        }
        Ok(data[start..end]
            .iter()
            .map(|obj| obj.clone_ref(py))
            .collect())
    }

    /// Parallel map operation
    pub fn parallel_map(&self, py: Python, func: Bound<PyAny>) -> PyResult<Vec<Py<PyAny>>> {
        let data = self
            .data
            .read()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;

        let results: PyResult<Vec<Py<PyAny>>> = data
            .iter()
            .map(|value| {
                let bound_value = value.bind(py);
                let result = func.call1((bound_value,))?;
                Ok(result.into())
            })
            .collect();

        results
    }
}

/// Shared queue for thread-safe message passing
#[pyclass]
pub struct SharedQueue {
    data: Arc<Mutex<VecDeque<Py<PyAny>>>>,
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
    pub fn put(&self, item: Bound<PyAny>) -> PyResult<()> {
        let mut queue = self
            .data
            .lock()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;

        if let Some(max_size) = self.max_size {
            if queue.len() >= max_size {
                return Err(pyo3::exceptions::PyRuntimeError::new_err("Queue is full"));
            }
        }

        queue.push_back(item.into());
        Ok(())
    }

    /// Get an item from the queue (blocks if empty)
    pub fn get(&self) -> PyResult<Py<PyAny>> {
        let mut queue = self
            .data
            .lock()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;

        queue
            .pop_front()
            .ok_or_else(|| pyo3::exceptions::PyRuntimeError::new_err("Queue is empty"))
    }

    /// Try to get an item without blocking
    pub fn get_nowait(&self) -> PyResult<Option<Py<PyAny>>> {
        let mut queue = self
            .data
            .lock()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(queue.pop_front())
    }

    /// Check if queue is empty
    pub fn empty(&self) -> PyResult<bool> {
        let queue = self
            .data
            .lock()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(queue.is_empty())
    }

    /// Get queue size
    #[getter]
    pub fn size(&self) -> PyResult<usize> {
        let queue = self
            .data
            .lock()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
        Ok(queue.len())
    }

    /// Clear the queue
    pub fn clear(&self) -> PyResult<()> {
        let mut queue = self
            .data
            .lock()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Lock error: {}", e)))?;
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
        match self
            .value
            .compare_exchange(current, new, Ordering::SeqCst, Ordering::SeqCst)
        {
            Ok(old_value) => old_value,
            Err(actual_current) => actual_current,
        }
    }

    /// Reset to zero
    pub fn reset(&self) -> usize {
        self.value.swap(0, Ordering::SeqCst)
    }
}

/// Factory function to create appropriate SharedArray based on data type
#[pyfunction]
pub fn create_shared_array(py: Python, data: Bound<PyAny>) -> PyResult<Py<PyAny>> {
    // Try to extract as different types and create appropriate array
    // Order matters: check for more specific types first

    // Try as list of integers first (before f64 since integers can be converted to f64)
    if let Ok(int_data) = data.extract::<Vec<i64>>() {
        let capacity = std::cmp::max(int_data.len() * 3 / 2, int_data.len() + 10); // 50% more or at least +10
        let array = SharedArrayInt {
            data: Arc::new(RwLock::new(int_data.clone())),
            capacity,
        };
        return Ok(Py::new(py, array)?.into());
    }

    // Try as list of floats
    if let Ok(float_data) = data.extract::<Vec<f64>>() {
        let capacity = std::cmp::max(float_data.len() * 3 / 2, float_data.len() + 10); // 50% more or at least +10
        let array = SharedArray {
            data: Arc::new(RwLock::new(float_data.clone())),
            capacity,
        };
        return Ok(Py::new(py, array)?.into());
    }

    // Try as list of strings
    if let Ok(str_data) = data.extract::<Vec<String>>() {
        let capacity = std::cmp::max(str_data.len() * 3 / 2, str_data.len() + 10); // 50% more or at least +10
        let array = SharedArrayStr {
            data: Arc::new(RwLock::new(str_data.clone())),
            capacity,
        };
        return Ok(Py::new(py, array)?.into());
    }

    // Fall back to generic object array
    if let Ok(list) = data.downcast::<pyo3::types::PyList>() {
        let obj_data: Vec<Py<PyAny>> = list.iter().map(|obj| obj.into()).collect();
        let capacity = std::cmp::max(list.len() * 3 / 2, list.len() + 10); // 50% more or at least +10
        let array = SharedArrayObj {
            data: Arc::new(RwLock::new(obj_data)),
            capacity,
        };
        return Ok(Py::new(py, array)?.into());
    }

    Err(pyo3::exceptions::PyTypeError::new_err(
        "Unsupported data type for SharedArray creation",
    ))
}
