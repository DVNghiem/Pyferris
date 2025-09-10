use crate::error::{FileReaderError, FileWriterError, FolderCreationError, ParallelExecutionError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList};
use rayon::prelude::*;
use std::fs::OpenOptions;
use std::io::{BufWriter, Write};

/// High-performance file writer with parallel processing capabilities
#[pyclass]
pub struct FileWriter {
    file_path: String,
    append_mode: bool,
    buffer_size: usize,
}

#[pymethods]
impl FileWriter {
    #[new]
    #[pyo3(signature = (file_path, append_mode = false, buffer_size = 8192))]
    pub fn new(file_path: String, append_mode: bool, buffer_size: usize) -> Self {
        Self {
            file_path,
            append_mode,
            buffer_size,
        }
    }

    /// Write text to file
    pub fn write_text(&self, content: &str) -> PyResult<()> {
        let mut file = if self.append_mode {
            OpenOptions::new()
                .create(true)
                .append(true)
                .open(&self.file_path)
        } else {
            OpenOptions::new()
                .create(true)
                .write(true)
                .truncate(true)
                .open(&self.file_path)
        }
        .map_err(|e| FileReaderError::new_err(format!("Failed to open file: {}", e)))?;

        file.write_all(content.as_bytes()).map_err(|e| {
            FileWriterError::new_err(format!("Failed to write to file: {}", e))
        })?;

        Ok(())
    }

    /// Write bytes to file
    pub fn write_bytes(&self, _py: Python, content: &Bound<'_, PyBytes>) -> PyResult<()> {
        let mut file = if self.append_mode {
            OpenOptions::new()
                .create(true)
                .append(true)
                .open(&self.file_path)
        } else {
            OpenOptions::new()
                .create(true)
                .write(true)
                .truncate(true)
                .open(&self.file_path)
        }
        .map_err(|e| FileWriterError::new_err(format!("Failed to open file: {}", e)))?;

        file.write_all(content.as_bytes()).map_err(|e| {
            FileWriterError::new_err(format!("Failed to write to file: {}", e))
        })?;

        Ok(())
    }

    /// Write lines to file
    pub fn write_lines(&self, lines: &Bound<'_, PyList>) -> PyResult<()> {
        let file = if self.append_mode {
            OpenOptions::new()
                .create(true)
                .append(true)
                .open(&self.file_path)
        } else {
            OpenOptions::new()
                .create(true)
                .write(true)
                .truncate(true)
                .open(&self.file_path)
        }
        .map_err(|e| FileReaderError::new_err(format!("Failed to open file: {}", e)))?;

        let mut writer = BufWriter::with_capacity(self.buffer_size, file);

        for item in lines.iter() {
            let line: String = item.extract().map_err(|e| {
                FileReaderError::new_err(format!("Failed to extract line: {}", e))
            })?;

            writeln!(writer, "{}", line).map_err(|e| {
                FileWriterError::new_err(format!("Failed to write line: {}", e))
            })?;
        }

        writer.flush().map_err(|e| {
            FileWriterError::new_err(format!("Failed to flush buffer: {}", e))
        })?;

        Ok(())
    }

    /// Append text to file
    pub fn append_text(&self, content: &str) -> PyResult<()> {
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.file_path)
            .map_err(|e| FileReaderError::new_err(format!("Failed to open file: {}", e)))?;

        file.write_all(content.as_bytes()).map_err(|e| {
            FileWriterError::new_err(format!("Failed to append to file: {}", e))
        })?;

        Ok(())
    }

    /// Append line to file
    pub fn append_line(&self, line: &str) -> PyResult<()> {
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.file_path)
            .map_err(|e| FileReaderError::new_err(format!("Failed to open file: {}", e)))?;

        writeln!(file, "{}", line).map_err(|e| {
            FileWriterError::new_err(format!("Failed to append line: {}", e))
        })?;

        Ok(())
    }
}

/// Write text content to file
#[pyfunction]
pub fn write_file_text(file_path: &str, content: &str) -> PyResult<()> {
    std::fs::write(file_path, content)
        .map_err(|e| FileWriterError::new_err(format!("Failed to write file: {}", e)))
}

/// Write bytes content to file
#[pyfunction]
pub fn write_file_bytes(file_path: &str, content: &Bound<'_, PyBytes>) -> PyResult<()> {
    std::fs::write(file_path, content.as_bytes())
        .map_err(|e| FileWriterError::new_err(format!("Failed to write file: {}", e)))
}

/// Append text to file
#[pyfunction]
pub fn append_file_text(file_path: &str, content: &str) -> PyResult<()> {
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(file_path)
        .map_err(|e| FileReaderError::new_err(format!("Failed to open file: {}", e)))?;

    file.write_all(content.as_bytes())
        .map_err(|e| FileWriterError::new_err(format!("Failed to append to file: {}", e)))
}

/// Write multiple files in parallel
#[pyfunction]
pub fn parallel_write_files(file_data: Vec<(String, String)>) -> PyResult<()> {
    let results: Result<Vec<_>, _> = file_data
        .par_iter()
        .map(|(path, content)| {
            std::fs::write(path, content).map_err(|e| format!("Failed to write {}: {}", path, e))
        })
        .collect();

    results.map_err(|e| ParallelExecutionError::new_err(e))?;
    Ok(())
}

/// Create directory if it doesn't exist
#[pyfunction]
pub fn create_directory(dir_path: &str) -> PyResult<()> {
    std::fs::create_dir_all(dir_path)
        .map_err(|e| FolderCreationError::new_err(format!("Failed to create directory: {}", e)))
}

/// Delete file
#[pyfunction]
pub fn delete_file(file_path: &str) -> PyResult<()> {
    std::fs::remove_file(file_path)
        .map_err(|e| FileWriterError::new_err(format!("Failed to delete file: {}", e)))
}

/// Copy file
#[pyfunction]
pub fn copy_file(src_path: &str, dst_path: &str) -> PyResult<()> {
    std::fs::copy(src_path, dst_path)
        .map_err(|e| FileWriterError::new_err(format!("Failed to copy file: {}", e)))?;
    Ok(())
}

/// Move/rename file
#[pyfunction]
pub fn move_file(src_path: &str, dst_path: &str) -> PyResult<()> {
    std::fs::rename(src_path, dst_path)
        .map_err(|e| FileWriterError::new_err(format!("Failed to move file: {}", e)))
}
