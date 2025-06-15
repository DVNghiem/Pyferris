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


/// Pyferris Rust Extensions
/// High-performance Rust implementations
#[pymodule(gil_used = false)]
fn _pyferris(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register 
    
    Ok(())
}
