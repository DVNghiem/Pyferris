use crate::error::ParallelExecutionError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList, PyString};
use rayon::prelude::*;
use std::fs::File;
use std::io::{BufRead, BufReader, Read};
use std::path::Path;

/// High-performance file reader with parallel processing capabilities
#[pyclass]
pub struct FileReader {
    file_path: String,
    chunk_size: usize,
}

#[pymethods]
impl FileReader {
    #[new]
    #[pyo3(signature = (file_path, chunk_size = 8192))]
    pub fn new(file_path: String, chunk_size: usize) -> Self {
        Self {
            file_path,
            chunk_size,
        }
    }

    /// Read entire file as bytes
    pub fn read_bytes(&self, py: Python) -> PyResult<Py<PyBytes>> {
        let mut file = File::open(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to open file: {}", e)))?;

        let mut buffer = Vec::new();
        file.read_to_end(&mut buffer)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read file: {}", e)))?;

        Ok(PyBytes::new(py, &buffer).into())
    }

    /// Read entire file as string
    pub fn read_text(&self) -> PyResult<String> {
        std::fs::read_to_string(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read file: {}", e)))
    }

    /// Read file line by line
    pub fn read_lines(&self, py: Python) -> PyResult<Py<PyList>> {
        let file = File::open(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to open file: {}", e)))?;

        let reader = BufReader::new(file);
        let lines: Result<Vec<String>, _> = reader.lines().collect();
        let lines = lines
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read lines: {}", e)))?;

        let py_lines = PyList::empty(py);
        for line in lines {
            py_lines.append(PyString::new(py, &line))?;
        }
        Ok(py_lines.into())
    }

    /// Read file in chunks for memory-efficient processing
    pub fn read_chunks(&self) -> PyResult<Vec<Vec<u8>>> {
        let mut file = File::open(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to open file: {}", e)))?;

        let mut chunks = Vec::new();
        let mut buffer = vec![0; self.chunk_size];

        loop {
            let bytes_read = file.read(&mut buffer).map_err(|e| {
                ParallelExecutionError::new_err(format!("Failed to read chunk: {}", e))
            })?;

            if bytes_read == 0 {
                break;
            }

            chunks.push(buffer[..bytes_read].to_vec());
        }

        Ok(chunks)
    }

    /// Parallel line processing with custom function
    pub fn parallel_process_lines(&self, py: Python, func: Py<PyAny>) -> PyResult<Py<PyList>> {
        let file = File::open(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to open file: {}", e)))?;

        let reader = BufReader::new(file);
        let lines: Result<Vec<String>, _> = reader.lines().collect();
        let lines = lines
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read lines: {}", e)))?;

        let results: Result<Vec<_>, _> = lines
            .par_iter()
            .map(|line| {
                Python::attach(|py| {
                    let py_line = PyString::new(py, line);
                    func.call1(py, (py_line,))
                })
            })
            .collect();

        let results = results.map_err(|e| {
            ParallelExecutionError::new_err(format!("Error in parallel processing: {}", e))
        })?;

        let py_results = PyList::empty(py);
        for result in results {
            py_results.append(result)?;
        }

        Ok(py_results.into())
    }
}

/// Read file content as string
#[pyfunction]
pub fn read_file_text(file_path: &str) -> PyResult<String> {
    std::fs::read_to_string(file_path)
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read file: {}", e)))
}

/// Read file content as bytes
#[pyfunction]
pub fn read_file_bytes(py: Python, file_path: &str) -> PyResult<Py<PyBytes>> {
    let content = std::fs::read(file_path)
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read file: {}", e)))?;

    Ok(PyBytes::new(py, &content).into())
}

/// Read multiple files in parallel
#[pyfunction]
pub fn parallel_read_files(py: Python, file_paths: Vec<String>) -> PyResult<Py<PyList>> {
    let results: Result<Vec<_>, _> = file_paths
        .par_iter()
        .map(|path| {
            std::fs::read_to_string(path).map_err(|e| format!("Failed to read {}: {}", path, e))
        })
        .collect();

    let results = results.map_err(|e| ParallelExecutionError::new_err(e))?;

    let py_results = PyList::empty(py);
    for result in results {
        py_results.append(PyString::new(py, &result))?;
    }

    Ok(py_results.into())
}

/// Check if file exists
#[pyfunction]
pub fn file_exists(file_path: &str) -> bool {
    Path::new(file_path).exists()
}

/// Get file size in bytes
#[pyfunction]
pub fn get_file_size(file_path: &str) -> PyResult<u64> {
    let metadata = std::fs::metadata(file_path).map_err(|e| {
        ParallelExecutionError::new_err(format!("Failed to get file metadata: {}", e))
    })?;

    Ok(metadata.len())
}
