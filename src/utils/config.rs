use pyo3::prelude::*;
use std::sync::Once;
use std::sync::atomic::{AtomicUsize, Ordering};

static WORKER_COUNT: AtomicUsize = AtomicUsize::new(0);
static CHUNK_SIZE: AtomicUsize = AtomicUsize::new(1000);
static INIT: Once = Once::new();

/// Initialize the global thread pool (called only once)
fn init_thread_pool() {
    INIT.call_once(|| {
        let worker_count = WORKER_COUNT.load(Ordering::SeqCst);
        let count = if worker_count == 0 {
            rayon::current_num_threads()
        } else {
            worker_count
        };

        if let Err(e) = rayon::ThreadPoolBuilder::new()
            .num_threads(count)
            .thread_name(|i| format!("pyferris-{}", i))
            .build_global()
        {
            eprintln!(
                "Warning: Failed to initialize custom thread pool: {}. Using default rayon pool.",
                e
            );
        }
    });
}

/// Set the number of worker threads for parallel operations
#[pyfunction]
pub fn set_worker_count(count: usize) -> PyResult<()> {
    if count == 0 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Worker count must be greater than 0",
        ));
    }

    WORKER_COUNT.store(count, Ordering::SeqCst);

    // Initialize thread pool if not already done
    init_thread_pool();

    Ok(())
}

/// Get the current number of worker threads
#[pyfunction]
pub fn get_worker_count() -> usize {
    let count = WORKER_COUNT.load(Ordering::SeqCst);
    if count == 0 {
        rayon::current_num_threads()
    } else {
        count
    }
}

/// Set the default chunk size for parallel operations
#[pyfunction]
pub fn set_chunk_size(size: usize) -> PyResult<()> {
    if size == 0 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Chunk size must be greater than 0",
        ));
    }

    CHUNK_SIZE.store(size, Ordering::SeqCst);
    Ok(())
}

/// Get the current default chunk size
#[pyfunction]
pub fn get_chunk_size() -> usize {
    CHUNK_SIZE.load(Ordering::SeqCst)
}

/// Configuration class for managing global settings
#[pyclass]
#[derive(Clone)]
pub struct Config {
    #[pyo3(get, set)]
    pub worker_count: usize,
    #[pyo3(get, set)]
    pub chunk_size: usize,
    #[pyo3(get, set)]
    pub error_strategy: String,
}

#[pymethods]
impl Config {
    #[new]
    pub fn new(
        worker_count: Option<usize>,
        chunk_size: Option<usize>,
        error_strategy: Option<String>,
    ) -> Self {
        Self {
            worker_count: worker_count.unwrap_or_else(|| rayon::current_num_threads()),
            chunk_size: chunk_size.unwrap_or(1000),
            error_strategy: error_strategy.unwrap_or_else(|| "raise".to_string()),
        }
    }

    /// Apply the configuration globally
    pub fn apply(&self) -> PyResult<()> {
        set_worker_count(self.worker_count)?;
        set_chunk_size(self.chunk_size)?;
        Ok(())
    }

    pub fn __repr__(&self) -> String {
        format!(
            "Config(worker_count={}, chunk_size={}, error_strategy='{}')",
            self.worker_count, self.chunk_size, self.error_strategy
        )
    }
}
