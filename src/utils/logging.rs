use pyo3::prelude::*;

/// Simple logging utility
#[pyfunction]
pub fn log_info(message: String) {
    println!("[INFO] {}", message);
}

#[pyfunction]
pub fn log_warning(message: String) {
    println!("[WARNING] {}", message);
}

#[pyfunction]
pub fn log_error(message: String) {
    eprintln!("[ERROR] {}", message);
}
