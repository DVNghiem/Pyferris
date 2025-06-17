use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::fs::File;
use crate::error::ParallelExecutionError;

/// High-performance CSV reader with parallel processing
#[pyclass]
pub struct CsvReader {
    file_path: String,
    delimiter: u8,
    has_headers: bool,
}

#[pymethods]
impl CsvReader {
    #[new]
    #[pyo3(signature = (file_path, delimiter = b',', has_headers = true))]
    pub fn new(file_path: String, delimiter: u8, has_headers: bool) -> Self {
        Self {
            file_path,
            delimiter,
            has_headers,
        }
    }

    /// Read CSV as list of dictionaries
    pub fn read_dict(&self, py: Python) -> PyResult<Py<PyList>> {
        let file = File::open(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to open CSV file: {}", e)))?;

        let mut reader = csv::ReaderBuilder::new()
            .delimiter(self.delimiter)
            .has_headers(self.has_headers)
            .from_reader(file);

        let headers = if self.has_headers {
            reader.headers()
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read headers: {}", e)))?
                .iter()
                .map(|h| h.to_string())
                .collect::<Vec<_>>()
        } else {
            // Generate column names if no headers
            let first_record = reader.records().next();
            match first_record {
                Some(Ok(record)) => {
                    (0..record.len()).map(|i| format!("column_{}", i)).collect()
                }
                _ => return Err(ParallelExecutionError::new_err("Empty CSV file".to_string())),
            }
        };

        let py_list = PyList::empty(py);
        for result in reader.records() {
            let record = result
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read record: {}", e)))?;
            
            let py_dict = PyDict::new(py);
            for (header, field) in headers.iter().zip(record.iter()) {
                py_dict.set_item(header, field)?;
            }
            py_list.append(py_dict)?;
        }

        Ok(py_list.into())
    }

    /// Read CSV as list of lists
    pub fn read_rows(&self, py: Python) -> PyResult<Py<PyList>> {
        let file = File::open(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to open CSV file: {}", e)))?;

        let mut reader = csv::ReaderBuilder::new()
            .delimiter(self.delimiter)
            .has_headers(self.has_headers)
            .from_reader(file);

        let py_list = PyList::empty(py);
        
        // Add headers if present
        if self.has_headers {
            let headers = reader.headers()
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read headers: {}", e)))?;
            
            let header_list = PyList::empty(py);
            for header in headers.iter() {
                header_list.append(header)?;
            }
            py_list.append(header_list)?;
        }

        // Add data rows
        for result in reader.records() {
            let record = result
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read record: {}", e)))?;
            
            let row_list = PyList::empty(py);
            for field in record.iter() {
                row_list.append(field)?;
            }
            py_list.append(row_list)?;
        }

        Ok(py_list.into())
    }

    /// Get column names/headers
    pub fn get_headers(&self) -> PyResult<Vec<String>> {
        let file = File::open(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to open CSV file: {}", e)))?;

        let mut reader = csv::ReaderBuilder::new()
            .delimiter(self.delimiter)
            .has_headers(self.has_headers)
            .from_reader(file);

        if self.has_headers {
            let headers = reader.headers()
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read headers: {}", e)))?;
            
            Ok(headers.iter().map(|h| h.to_string()).collect())
        } else {
            Ok(vec![])
        }
    }
}

/// High-performance CSV writer
#[pyclass]
pub struct CsvWriter {
    file_path: String,
    delimiter: u8,
    write_headers: bool,
}

#[pymethods]
impl CsvWriter {
    #[new]
    #[pyo3(signature = (file_path, delimiter = b',', write_headers = true))]
    pub fn new(file_path: String, delimiter: u8, write_headers: bool) -> Self {
        Self {
            file_path,
            delimiter,
            write_headers,
        }
    }

    /// Write data from list of dictionaries
    pub fn write_dict(&self, data: &Bound<'_, PyList>) -> PyResult<()> {
        let file = File::create(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to create CSV file: {}", e)))?;

        let mut writer = csv::WriterBuilder::new()
            .delimiter(self.delimiter)
            .from_writer(file);

        if data.len() == 0 {
            return Ok(());
        }

        // Extract headers from first dictionary
        let first_item = data.get_item(0)?;
        let first_dict = first_item.downcast::<PyDict>()
            .map_err(|e| ParallelExecutionError::new_err(format!("Expected dictionary: {}", e)))?;

        let headers: Vec<String> = first_dict.keys()
            .iter()
            .map(|k| k.extract::<String>())
            .collect::<Result<Vec<_>, _>>()
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to extract headers: {}", e)))?;

        // Write headers if requested
        if self.write_headers {
            writer.write_record(&headers)
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to write headers: {}", e)))?;
        }

        // Write data rows
        for item in data.iter() {
            let dict = item.downcast::<PyDict>()
                .map_err(|e| ParallelExecutionError::new_err(format!("Expected dictionary: {}", e)))?;
            
            let row: Vec<String> = headers.iter()
                .map(|header| {
                    match dict.get_item(header) {
                        Ok(Some(val)) => val.extract::<String>().unwrap_or_else(|_| String::new()),
                        _ => String::new(),
                    }
                })
                .collect();

            writer.write_record(&row)
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to write row: {}", e)))?;
        }

        writer.flush()
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to flush CSV writer: {}", e)))?;

        Ok(())
    }

    /// Write data from list of lists
    pub fn write_rows(&self, data: &Bound<'_, PyList>) -> PyResult<()> {
        let file = File::create(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to create CSV file: {}", e)))?;

        let mut writer = csv::WriterBuilder::new()
            .delimiter(self.delimiter)
            .from_writer(file);

        for item in data.iter() {
            let row = item.downcast::<PyList>()
                .map_err(|e| ParallelExecutionError::new_err(format!("Expected list: {}", e)))?;
            
            let row_data: Vec<String> = row.iter()
                .map(|cell| cell.extract::<String>())
                .collect::<Result<Vec<_>, _>>()
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to extract row data: {}", e)))?;

            writer.write_record(&row_data)
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to write row: {}", e)))?;
        }

        writer.flush()
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to flush CSV writer: {}", e)))?;

        Ok(())
    }
}

/// Read CSV file as list of dictionaries
#[pyfunction]
pub fn read_csv_dict(py: Python, file_path: &str, delimiter: Option<u8>, has_headers: Option<bool>) -> PyResult<Py<PyList>> {
    let reader = CsvReader::new(
        file_path.to_string(),
        delimiter.unwrap_or(b','),
        has_headers.unwrap_or(true),
    );
    reader.read_dict(py)
}

/// Read CSV file as list of lists
#[pyfunction]
pub fn read_csv_rows(py: Python, file_path: &str, delimiter: Option<u8>, has_headers: Option<bool>) -> PyResult<Py<PyList>> {
    let reader = CsvReader::new(
        file_path.to_string(),
        delimiter.unwrap_or(b','),
        has_headers.unwrap_or(true),
    );
    reader.read_rows(py)
}

/// Write CSV file from list of dictionaries
#[pyfunction]
pub fn write_csv_dict(file_path: &str, data: &Bound<'_, PyList>, delimiter: Option<u8>, write_headers: Option<bool>) -> PyResult<()> {
    let writer = CsvWriter::new(
        file_path.to_string(),
        delimiter.unwrap_or(b','),
        write_headers.unwrap_or(true),
    );
    writer.write_dict(data)
}

/// Write CSV file from list of lists
#[pyfunction]
pub fn write_csv_rows(file_path: &str, data: &Bound<'_, PyList>, delimiter: Option<u8>) -> PyResult<()> {
    let writer = CsvWriter::new(
        file_path.to_string(),
        delimiter.unwrap_or(b','),
        false, // No headers for raw rows
    );
    writer.write_rows(data)
}
