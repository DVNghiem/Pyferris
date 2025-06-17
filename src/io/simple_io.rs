use pyo3::prelude::*;
use pyo3::types::{PyList, PyString};
use std::io::Write;
use std::path::Path;
use rayon::prelude::*;
use crate::error::ParallelExecutionError;

/// Simple file reader
#[pyclass]
pub struct SimpleFileReader {
    file_path: String,
}

#[pymethods]
impl SimpleFileReader {
    #[new]
    pub fn new(file_path: String) -> Self {
        Self { file_path }
    }

    /// Read entire file as text
    pub fn read_text(&self) -> PyResult<String> {
        std::fs::read_to_string(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read file: {}", e)))
    }

    /// Read file lines
    pub fn read_lines(&self, py: Python) -> PyResult<Py<PyList>> {
        let content = std::fs::read_to_string(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read file: {}", e)))?;
        
        let lines: Vec<&str> = content.lines().collect();
        let py_list = PyList::empty(py);
        
        for line in lines {
            py_list.append(PyString::new(py, line))?;
        }
        
        Ok(py_list.into())
    }
}

/// Simple file writer
#[pyclass]
pub struct SimpleFileWriter {
    file_path: String,
}

#[pymethods]
impl SimpleFileWriter {
    #[new]
    pub fn new(file_path: String) -> Self {
        Self { file_path }
    }

    /// Write text to file
    pub fn write_text(&self, content: &str) -> PyResult<()> {
        std::fs::write(&self.file_path, content)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to write file: {}", e)))
    }

    /// Append text to file
    pub fn append_text(&self, content: &str) -> PyResult<()> {
        use std::fs::OpenOptions;
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to open file: {}", e)))?;

        file.write_all(content.as_bytes())
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to append to file: {}", e)))
    }
}

/// Read file content as string
#[pyfunction]
pub fn simple_read_file(file_path: &str) -> PyResult<String> {
    std::fs::read_to_string(file_path)
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read file: {}", e)))
}

/// Write text content to file
#[pyfunction]
pub fn simple_write_file(file_path: &str, content: &str) -> PyResult<()> {
    std::fs::write(file_path, content)
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to write file: {}", e)))
}

/// Read multiple files in parallel
#[pyfunction]
pub fn simple_parallel_read_files(py: Python, file_paths: Vec<String>) -> PyResult<Py<PyList>> {
    let results: Result<Vec<_>, _> = file_paths
        .par_iter()
        .map(|path| {
            std::fs::read_to_string(path)
                .map_err(|e| format!("Failed to read {}: {}", path, e))
        })
        .collect();

    let results = results
        .map_err(|e| ParallelExecutionError::new_err(e))?;

    let py_results = PyList::empty(py);
    for result in results {
        py_results.append(PyString::new(py, &result))?;
    }
    
    Ok(py_results.into())
}

/// Write multiple files in parallel
#[pyfunction]
pub fn simple_parallel_write_files(file_data: Vec<(String, String)>) -> PyResult<()> {
    let results: Result<Vec<_>, _> = file_data
        .par_iter()
        .map(|(path, content)| {
            std::fs::write(path, content)
                .map_err(|e| format!("Failed to write {}: {}", path, e))
        })
        .collect();

    results.map_err(|e| ParallelExecutionError::new_err(e))?;
    Ok(())
}

/// Check if file exists
#[pyfunction]
pub fn simple_file_exists(file_path: &str) -> bool {
    Path::new(file_path).exists()
}

/// Get file size in bytes
#[pyfunction]
pub fn simple_get_file_size(file_path: &str) -> PyResult<u64> {
    let metadata = std::fs::metadata(file_path)
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to get file metadata: {}", e)))?;
    
    Ok(metadata.len())
}

/// Create directory if it doesn't exist
#[pyfunction]
pub fn simple_create_directory(dir_path: &str) -> PyResult<()> {
    std::fs::create_dir_all(dir_path)
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to create directory: {}", e)))
}

/// Delete file
#[pyfunction]
pub fn simple_delete_file(file_path: &str) -> PyResult<()> {
    std::fs::remove_file(file_path)
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to delete file: {}", e)))
}

/// Copy file
#[pyfunction]
pub fn simple_copy_file(src_path: &str, dst_path: &str) -> PyResult<()> {
    std::fs::copy(src_path, dst_path)
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to copy file: {}", e)))?;
    Ok(())
}

/// Move/rename file
#[pyfunction]
pub fn simple_move_file(src_path: &str, dst_path: &str) -> PyResult<()> {
    std::fs::rename(src_path, dst_path)
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to move file: {}", e)))
}
