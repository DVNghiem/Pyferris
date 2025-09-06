use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyBool};
use std::fs::File;
use std::io::{BufReader, BufWriter};
use serde_json::{Value, Map};
use crate::error::ParallelExecutionError;

/// High-performance JSON reader
#[pyclass]
pub struct JsonReader {
    file_path: String,
}

#[pymethods]
impl JsonReader {
    #[new]
    pub fn new(file_path: String) -> Self {
        Self { file_path }
    }

    /// Read JSON file as Python object
    pub fn read(&self, py: Python) -> PyResult<Py<PyAny>> {
        let file = File::open(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to open JSON file: {}", e)))?;

        let reader = BufReader::new(file);
        let json_value: Value = serde_json::from_reader(reader)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to parse JSON: {}", e)))?;

        json_value_to_python(py, &json_value)
    }

    /// Read JSON Lines file (JSONL) as list of objects
    pub fn read_lines(&self, py: Python) -> PyResult<Py<PyList>> {
        let content = std::fs::read_to_string(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read file: {}", e)))?;

        let py_list = PyList::empty(py);
        
        for line in content.lines() {
            if line.trim().is_empty() {
                continue;
            }
            
            let json_value: Value = serde_json::from_str(line)
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to parse JSON line: {}", e)))?;
            
            let py_obj = json_value_to_python(py, &json_value)?;
            py_list.append(py_obj)?;
        }

        Ok(py_list.into())
    }

    /// Read large JSON file in streaming mode
    pub fn read_array_stream(&self, py: Python) -> PyResult<Py<PyList>> {
        let file = File::open(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to open JSON file: {}", e)))?;

        let reader = BufReader::new(file);
        let json_value: Value = serde_json::from_reader(reader)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to parse JSON: {}", e)))?;

        match json_value {
            Value::Array(arr) => {
                let py_list = PyList::empty(py);
                for item in arr {
                    let py_obj = json_value_to_python(py, &item)?;
                    py_list.append(py_obj)?;
                }
                Ok(py_list.into())
            }
            _ => Err(ParallelExecutionError::new_err("JSON root is not an array".to_string())),
        }
    }
}

/// High-performance JSON writer
#[pyclass]
pub struct JsonWriter {
    file_path: String,
    pretty_print: bool,
}

#[pymethods]
impl JsonWriter {
    #[new]
    #[pyo3(signature = (file_path, pretty_print = false))]
    pub fn new(file_path: String, pretty_print: bool) -> Self {
        Self { file_path, pretty_print }
    }

    /// Write Python object as JSON
    pub fn write(&self, py: Python, data: Py<PyAny>) -> PyResult<()> {
        let json_value = python_to_json_value(py, &data)?;
        
        let file = File::create(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to create JSON file: {}", e)))?;

        let writer = BufWriter::new(file);
        
        if self.pretty_print {
            serde_json::to_writer_pretty(writer, &json_value)
        } else {
            serde_json::to_writer(writer, &json_value)
        }
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to write JSON: {}", e)))?;

        Ok(())
    }

    /// Write list of objects as JSON Lines (JSONL)
    pub fn write_lines(&self, py: Python, data: &Bound<'_, PyList>) -> PyResult<()> {
        let file = File::create(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to create JSONL file: {}", e)))?;

        let mut writer = BufWriter::new(file);
        
        for item in data.iter() {
            let json_value = python_to_json_value(py, &item.into())?;
            let json_string = serde_json::to_string(&json_value)
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to serialize JSON: {}", e)))?;
            
            writeln!(writer, "{}", json_string)
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to write line: {}", e)))?;
        }

        use std::io::Write;
        writer.flush()
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to flush writer: {}", e)))?;

        Ok(())
    }

    /// Append object to JSON Lines file
    pub fn append_line(&self, py: Python, data: Py<PyAny>) -> PyResult<()> {
        use std::fs::OpenOptions;
        use std::io::Write;
        
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.file_path)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to open JSONL file: {}", e)))?;

        let json_value = python_to_json_value(py, &data)?;
        let json_string = serde_json::to_string(&json_value)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to serialize JSON: {}", e)))?;
        
        writeln!(file, "{}", json_string)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to write line: {}", e)))?;

        Ok(())
    }
}

/// Convert JSON Value to Python object
fn json_value_to_python(py: Python, value: &Value) -> PyResult<Py<PyAny>> {
    match value {
        Value::Null => Ok(py.None()),
        Value::Bool(b) => Ok(<pyo3::Bound<'_, PyBool> as Clone>::clone(&PyBool::new(py, *b)).into_any().unbind()),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(i.into_pyobject(py)?.into_any().unbind())
            } else if let Some(f) = n.as_f64() {
                Ok(f.into_pyobject(py)?.into_any().unbind())
            } else {
                Ok(n.to_string().into_pyobject(py)?.into_any().unbind())
            }
        }
        Value::String(s) => Ok(s.into_pyobject(py)?.into_any().unbind()),
        Value::Array(arr) => {
            let py_list = PyList::empty(py);
            for item in arr {
                let py_item = json_value_to_python(py, item)?;
                py_list.append(py_item)?;
            }
            Ok(py_list.into_any().unbind())
        }
        Value::Object(obj) => {
            let py_dict = PyDict::new(py);
            for (key, val) in obj {
                let py_val = json_value_to_python(py, val)?;
                py_dict.set_item(key, py_val)?;
            }
            Ok(py_dict.into_any().unbind())
        }
    }
}

/// Convert Python object to JSON Value
fn python_to_json_value(py: Python, obj: &Py<PyAny>) -> PyResult<Value> {
    if obj.is_none(py) {
        Ok(Value::Null)
    } else if let Ok(b) = obj.extract::<bool>(py) {
        Ok(Value::Bool(b))
    } else if let Ok(i) = obj.extract::<i64>(py) {
        Ok(Value::Number(serde_json::Number::from(i)))
    } else if let Ok(f) = obj.extract::<f64>(py) {
        if let Some(n) = serde_json::Number::from_f64(f) {
            Ok(Value::Number(n))
        } else {
            Err(ParallelExecutionError::new_err("Invalid float value".to_string()))
        }
    } else if let Ok(s) = obj.extract::<String>(py) {
        Ok(Value::String(s))
    } else if let Ok(list) = obj.downcast_bound::<PyList>(py) {
        let mut arr = Vec::new();
        for item in list.iter() {
            let json_item = python_to_json_value(py, &item.into())?;
            arr.push(json_item);
        }
        Ok(Value::Array(arr))
    } else if let Ok(dict) = obj.downcast_bound::<PyDict>(py) {
        let mut map = Map::new();
        for (key, val) in dict.iter() {
            let key_str: String = key.extract()
                .map_err(|e| ParallelExecutionError::new_err(format!("Dictionary key must be string: {}", e)))?;
            let json_val = python_to_json_value(py, &val.into())?;
            map.insert(key_str, json_val);
        }
        Ok(Value::Object(map))
    } else {
        // Try to convert using str()
        let str_repr = obj.call_method0(py, "__str__")?;
        let s: String = str_repr.extract(py)?;
        Ok(Value::String(s))
    }
}

/// Read JSON file as Python object
#[pyfunction]
pub fn read_json(py: Python, file_path: &str) -> PyResult<Py<PyAny>> {
    let reader = JsonReader::new(file_path.to_string());
    reader.read(py)
}

/// Write Python object as JSON file
#[pyfunction]
pub fn write_json(py: Python, file_path: &str, data: Py<PyAny>, pretty_print: Option<bool>) -> PyResult<()> {
    let writer = JsonWriter::new(file_path.to_string(), pretty_print.unwrap_or(false));
    writer.write(py, data)
}

/// Read JSON Lines file as list
#[pyfunction]
pub fn read_jsonl(py: Python, file_path: &str) -> PyResult<Py<PyList>> {
    let reader = JsonReader::new(file_path.to_string());
    reader.read_lines(py)
}

/// Write list as JSON Lines file
#[pyfunction]
pub fn write_jsonl(py: Python, file_path: &str, data: &Bound<'_, PyList>) -> PyResult<()> {
    let writer = JsonWriter::new(file_path.to_string(), false);
    writer.write_lines(py, data)
}

/// Append object to JSON Lines file
#[pyfunction]
pub fn append_jsonl(py: Python, file_path: &str, data: Py<PyAny>) -> PyResult<()> {
    let writer = JsonWriter::new(file_path.to_string(), false);
    writer.append_line(py, data)
}

/// Parse JSON string to Python object
#[pyfunction]
pub fn parse_json(py: Python, json_str: &str) -> PyResult<Py<PyAny>> {
    let json_value: Value = serde_json::from_str(json_str)
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to parse JSON: {}", e)))?;
    
    json_value_to_python(py, &json_value)
}

/// Convert Python object to JSON string
#[pyfunction]
pub fn to_json_string(py: Python, data: Py<PyAny>, pretty_print: Option<bool>) -> PyResult<String> {
    let json_value = python_to_json_value(py, &data)?;
    
    if pretty_print.unwrap_or(false) {
        serde_json::to_string_pretty(&json_value)
    } else {
        serde_json::to_string(&json_value)
    }
    .map_err(|e| ParallelExecutionError::new_err(format!("Failed to serialize JSON: {}", e)))
}
