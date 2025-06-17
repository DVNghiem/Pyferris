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

use core::*;
use executor::*;
use utils::*;
use error::*;
use io::*;

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
    m.add_class::<SimpleFileReader>()?;
    m.add_class::<SimpleFileWriter>()?;
    
    // Basic file operations
    m.add_function(wrap_pyfunction!(simple_read_file, m)?)?;
    m.add_function(wrap_pyfunction!(simple_write_file, m)?)?;
    m.add_function(wrap_pyfunction!(simple_parallel_read_files, m)?)?;
    m.add_function(wrap_pyfunction!(simple_parallel_write_files, m)?)?;
    m.add_function(wrap_pyfunction!(simple_file_exists, m)?)?;
    m.add_function(wrap_pyfunction!(simple_get_file_size, m)?)?;
    m.add_function(wrap_pyfunction!(simple_create_directory, m)?)?;
    m.add_function(wrap_pyfunction!(simple_delete_file, m)?)?;
    m.add_function(wrap_pyfunction!(simple_copy_file, m)?)?;
    m.add_function(wrap_pyfunction!(simple_move_file, m)?)?;
    
    // Register custom exception
    m.add("ParallelExecutionError", py.get_type::<ParallelExecutionError>())?;
    
    Ok(())
}
