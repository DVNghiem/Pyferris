use pyo3::prelude::*;
use pyo3::create_exception;

create_exception!(pyferris, ParallelExecutionError, pyo3::exceptions::PyException);

/// Error handling utilities
pub fn handle_parallel_error(error: PyErr, strategy: &str) -> PyResult<()> {
    match strategy {
        "raise" => Err(error),
        "ignore" => Ok(()),
        "collect" => {
            // For now, just log the error and continue
            eprintln!("Parallel execution error (collected): {}", error);
            Ok(())
        }
        _ => Err(pyo3::exceptions::PyValueError::new_err(
            format!("Unknown error strategy: {}", strategy)
        ))
    }
}
