use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use std::collections::VecDeque;

/// A memory pool for efficient allocation and reuse of memory blocks
#[pyclass]
pub struct MemoryPool {
    block_size: usize,
    pool: Arc<Mutex<VecDeque<Vec<u8>>>>,
    max_blocks: usize,
    allocated_count: Arc<Mutex<usize>>,
}

#[pymethods]
impl MemoryPool {
    #[new]
    pub fn new(block_size: usize, max_blocks: Option<usize>) -> Self {
        Self {
            block_size,
            pool: Arc::new(Mutex::new(VecDeque::new())),
            max_blocks: max_blocks.unwrap_or(1000),
            allocated_count: Arc::new(Mutex::new(0)),
        }
    }

    /// Allocate a memory block from the pool
    pub fn allocate(&self) -> PyResult<Vec<u8>> {
        let mut pool = self.pool.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        
        if let Some(block) = pool.pop_front() {
            Ok(block)
        } else {
            // Create new block if pool is empty
            let mut count = self.allocated_count.lock().map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
            })?;
            
            if *count >= self.max_blocks {
                return Err(PyErr::new::<pyo3::exceptions::PyMemoryError, _>(
                    "Memory pool exhausted"
                ));
            }
            
            *count += 1;
            Ok(vec![0u8; self.block_size])
        }
    }

    /// Return a memory block to the pool
    pub fn deallocate(&self, mut block: Vec<u8>) -> PyResult<()> {
        if block.len() != self.block_size {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Block size mismatch"
            ));
        }

        let mut pool = self.pool.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;

        if pool.len() < self.max_blocks / 2 {
            // Clear the block and return it to the pool
            block.fill(0);
            pool.push_back(block);
        } else {
            // Pool is full, let the block be deallocated normally
            let mut count = self.allocated_count.lock().map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
            })?;
            *count -= 1;
        }

        Ok(())
    }

    /// Get the number of available blocks in the pool
    pub fn available_blocks(&self) -> PyResult<usize> {
        let pool = self.pool.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(pool.len())
    }

    /// Get the total number of allocated blocks
    pub fn allocated_blocks(&self) -> PyResult<usize> {
        let count = self.allocated_count.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(*count)
    }

    /// Get the block size
    pub fn block_size(&self) -> usize {
        self.block_size
    }

    /// Get the maximum number of blocks
    pub fn max_blocks(&self) -> usize {
        self.max_blocks
    }

    /// Clear all blocks from the pool
    pub fn clear(&self) -> PyResult<()> {
        let mut pool = self.pool.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        let cleared_count = pool.len();
        pool.clear();

        let mut count = self.allocated_count.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        *count = (*count).saturating_sub(cleared_count);

        Ok(())
    }

    /// Get memory usage statistics
    pub fn stats(&self, py: Python) -> PyResult<PyObject> {
        let pool = self.pool.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        let count = self.allocated_count.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;

        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("block_size", self.block_size)?;
        dict.set_item("max_blocks", self.max_blocks)?;
        dict.set_item("allocated_blocks", *count)?;
        dict.set_item("available_blocks", pool.len())?;
        dict.set_item("total_memory_bytes", *count * self.block_size)?;
        dict.set_item("pool_memory_bytes", pool.len() * self.block_size)?;
        
        Ok(dict.into())
    }

    fn __repr__(&self) -> PyResult<String> {
        let count = self.allocated_count.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Lock poisoned")
        })?;
        Ok(format!(
            "MemoryPool(block_size={}, allocated={}, max_blocks={})",
            self.block_size, *count, self.max_blocks
        ))
    }

    fn __str__(&self) -> PyResult<String> {
        self.__repr__()
    }
}