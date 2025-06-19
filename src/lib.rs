#[cfg(not(any(
    target_env = "musl",
    target_os = "freebsd",
    target_os = "openbsd",
    target_os = "windows",
    feature = "mimalloc"
)))]
#[global_allocator]
static GLOBAL: tikv_jemallocator::Jemalloc = tikv_jemallocator::Jemalloc;

#[cfg(feature = "mimalloc")]
#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

use pyo3::prelude::*;

// Import modules
mod core;
mod executor;
mod utils;
mod error;
mod io;
mod advanced;

use core::*;
use executor::*;
use utils::*;
use error::*;
use io::*;
use advanced::*;

/// Pyferris Rust Extensions
/// High-performance Rust implementations
#[pymodule]
fn _pyferris(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register core parallel operations
    m.add_function(wrap_pyfunction!(parallel_map, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_starmap, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_filter, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_reduce, m)?)?;
    
    // Register executor
    m.add_class::<Executor>()?;
    
    // Register configuration functions
    m.add_function(wrap_pyfunction!(set_worker_count, m)?)?;
    m.add_function(wrap_pyfunction!(get_worker_count, m)?)?;
    m.add_function(wrap_pyfunction!(set_chunk_size, m)?)?;
    m.add_function(wrap_pyfunction!(get_chunk_size, m)?)?;
    m.add_class::<Config>()?;
    
    // Register logging functions
    m.add_function(wrap_pyfunction!(log_info, m)?)?;
    m.add_function(wrap_pyfunction!(log_warning, m)?)?;
    m.add_function(wrap_pyfunction!(log_error, m)?)?;
    
    // Register simple IO functions
    register_io(py, m)?;
    
    // Register advanced parallel operations
    m.add_function(wrap_pyfunction!(parallel_sort, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_group_by, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_unique, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_partition, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_chunks, m)?)?;
    m.add_class::<BatchProcessor>()?;
    
    // Register custom exception
    m.add("ParallelExecutionError", py.get_type::<ParallelExecutionError>())?;
    
    Ok(())
}
