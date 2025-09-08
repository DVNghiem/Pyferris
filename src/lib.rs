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
mod advanced;
mod async_ops;
mod cache;
mod concurrent;
mod core;
mod distributed;
mod error;
mod executor;
mod io;
mod memory;
mod pipeline;
mod scheduler;
mod shared_memory;
mod utils;

use advanced::*;
use async_ops::*;
use cache::*;
use concurrent::*;
use core::*;
use distributed::*;
use error::*;
use executor::*;
use io::*;
use memory::*;
use pipeline::*;
use scheduler::*;
use shared_memory::*;
use utils::*;

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

    // Register simple IO functions
    register_io(py, m)?;

    // Register advanced parallel operations
    m.add_function(wrap_pyfunction!(parallel_sort, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_group_by, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_unique, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_partition, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_chunks, m)?)?;
    m.add_class::<crate::advanced::BatchProcessor>()?;

    m.add_class::<Pipeline>()?;
    m.add_class::<Chain>()?;
    m.add_function(wrap_pyfunction!(pipeline_map, m)?)?;

    m.add_class::<AsyncExecutor>()?;
    m.add_class::<AsyncTask>()?;
    m.add_function(wrap_pyfunction!(async_parallel_map, m)?)?;
    m.add_function(wrap_pyfunction!(async_parallel_filter, m)?)?;

    m.add_class::<SharedArray>()?;
    m.add_class::<SharedArrayInt>()?;
    m.add_class::<SharedArrayStr>()?;
    m.add_class::<SharedArrayObj>()?;
    m.add_class::<SharedDict>()?;
    m.add_class::<SharedQueue>()?;
    m.add_class::<SharedCounter>()?;
    m.add_function(wrap_pyfunction!(create_shared_array, m)?)?;

    m.add_class::<WorkStealingScheduler>()?;
    m.add_class::<RoundRobinScheduler>()?;
    m.add_class::<AdaptiveScheduler>()?;
    m.add_class::<PriorityScheduler>()?;
    m.add_class::<TaskPriority>()?;
    m.add_function(wrap_pyfunction!(execute_with_priority, m)?)?;
    m.add_function(wrap_pyfunction!(create_priority_task, m)?)?;

    m.add_class::<MemoryPool>()?;
    m.add_function(wrap_pyfunction!(memory_mapped_array, m)?)?;
    m.add_function(wrap_pyfunction!(memory_mapped_array_2d, m)?)?;
    m.add_function(wrap_pyfunction!(memory_mapped_info, m)?)?;
    m.add_function(wrap_pyfunction!(create_temp_mmap, m)?)?;

    m.add_class::<ConcurrentHashMap>()?;
    m.add_class::<LockFreeQueue>()?;
    m.add_class::<AtomicCounter>()?;
    m.add_class::<RwLockDict>()?;

    m.add_class::<SmartCache>()?;
    m.add_class::<EvictionPolicy>()?;

    m.add_class::<ClusterManager>()?;
    m.add_class::<LoadBalancer>()?;
    m.add_class::<DistributedExecutor>()?;
    m.add_class::<DistributedBatchProcessor>()?;
    m.add_function(wrap_pyfunction!(cluster_map, m)?)?;
    m.add_function(wrap_pyfunction!(distributed_reduce, m)?)?;

    // Register custom exception
    m.add(
        "ParallelExecutionError",
        py.get_type::<ParallelExecutionError>(),
    )?;

    Ok(())
}
