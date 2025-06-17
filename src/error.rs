use pyo3::create_exception;

create_exception!(pyferris, ParallelExecutionError, pyo3::exceptions::PyException);
