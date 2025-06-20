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
mod async_ops;
mod pipeline;
mod shared_memory;
mod scheduler;

use core::*;
use executor::*;
use utils::*;
use error::*;
use io::*;
use advanced::*;
use async_ops::*;
use pipeline::*;
use shared_memory::*;
use scheduler::*;

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
    
    // Register Level 3: Pipeline Processing
    m.add_class::<Pipeline>()?;
    m.add_class::<Chain>()?;
    m.add_function(wrap_pyfunction!(pipeline_map, m)?)?;
    
    // Register Level 3: Async Support
    m.add_class::<AsyncExecutor>()?;
    m.add_class::<AsyncTask>()?;
    m.add_function(wrap_pyfunction!(async_parallel_map, m)?)?;
    m.add_function(wrap_pyfunction!(async_parallel_filter, m)?)?;
    
    // Register Level 3: Shared Memory
    m.add_class::<SharedArray>()?;
    m.add_class::<SharedDict>()?;
    m.add_class::<SharedQueue>()?;
    m.add_class::<SharedCounter>()?;
    
    // Register Level 3: Custom Schedulers
    m.add_class::<WorkStealingScheduler>()?;
    m.add_class::<RoundRobinScheduler>()?;
    m.add_class::<AdaptiveScheduler>()?;
    m.add_class::<PriorityScheduler>()?;
    m.add_class::<TaskPriority>()?;
    m.add_function(wrap_pyfunction!(execute_with_priority, m)?)?;
    m.add_function(wrap_pyfunction!(create_priority_task, m)?)?;
    
    // Register custom exception
    m.add("ParallelExecutionError", py.get_type::<ParallelExecutionError>())?;
    
    Ok(())
}
