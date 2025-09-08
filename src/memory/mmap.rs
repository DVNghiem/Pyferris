use pyo3::prelude::*;
use std::path::Path;

/// Create a memory-mapped array backed by a file
#[pyfunction]
pub fn memory_mapped_array(
    py: Python,
    filepath: &str,
    size: usize,
    dtype: Option<&str>,
    mode: Option<&str>,
) -> PyResult<Py<PyAny>> {
    // Import numpy
    let numpy = py.import("numpy")?;
    let memmap = numpy.getattr("memmap")?;

    // Determine the data type
    let dt = match dtype.unwrap_or("float64") {
        "int8" => "i1",
        "int16" => "i2",
        "int32" => "i4",
        "int64" => "i8",
        "uint8" => "u1",
        "uint16" => "u2",
        "uint32" => "u4",
        "uint64" => "u8",
        "float32" => "f4",
        "float64" => "f8",
        "bool" => "bool",
        other => other,
    };

    // Determine the access mode
    let access_mode = mode.unwrap_or("r+");

    // Create the memory-mapped array
    let kwargs = pyo3::types::PyDict::new(py);
    kwargs.set_item("dtype", dt)?;
    kwargs.set_item("mode", access_mode)?;
    kwargs.set_item("shape", (size,))?;

    let mmap_array = memmap.call((filepath,), Some(&kwargs))?;

    Ok(mmap_array.into())
}

/// Create a memory-mapped 2D array backed by a file
#[pyfunction]
pub fn memory_mapped_array_2d(
    py: Python,
    filepath: &str,
    shape: (usize, usize),
    dtype: Option<&str>,
    mode: Option<&str>,
) -> PyResult<Py<PyAny>> {
    // Import numpy
    let numpy = py.import("numpy")?;
    let memmap = numpy.getattr("memmap")?;

    // Determine the data type
    let dt = match dtype.unwrap_or("float64") {
        "int8" => "i1",
        "int16" => "i2",
        "int32" => "i4",
        "int64" => "i8",
        "uint8" => "u1",
        "uint16" => "u2",
        "uint32" => "u4",
        "uint64" => "u8",
        "float32" => "f4",
        "float64" => "f8",
        "bool" => "bool",
        other => other,
    };

    // Determine the access mode
    let access_mode = mode.unwrap_or("r+");

    // Create the memory-mapped array
    let kwargs = pyo3::types::PyDict::new(py);
    kwargs.set_item("dtype", dt)?;
    kwargs.set_item("mode", access_mode)?;
    kwargs.set_item("shape", shape)?;

    let mmap_array = memmap.call((filepath,), Some(&kwargs))?;

    Ok(mmap_array.into())
}

/// Get information about a memory-mapped file
#[pyfunction]
pub fn memory_mapped_info(py: Python, filepath: &str) -> PyResult<Py<PyAny>> {
    let path = Path::new(filepath);

    if !path.exists() {
        return Err(PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
            format!("File not found: {}", filepath),
        ));
    }

    let metadata = path.metadata().map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Cannot read file metadata: {}", e))
    })?;

    let dict = pyo3::types::PyDict::new(py);
    dict.set_item("filepath", filepath)?;
    dict.set_item("size_bytes", metadata.len())?;
    dict.set_item("size_mb", metadata.len() as f64 / (1024.0 * 1024.0))?;
    dict.set_item("is_file", metadata.is_file())?;
    dict.set_item("is_readonly", metadata.permissions().readonly())?;

    // Get modification time if available
    if let Ok(modified) = metadata.modified() {
        if let Ok(duration) = modified.duration_since(std::time::UNIX_EPOCH) {
            dict.set_item("modified_timestamp", duration.as_secs())?;
        }
    }

    Ok(dict.into())
}

/// Create a temporary memory-mapped file
#[pyfunction]
pub fn create_temp_mmap(
    py: Python,
    size: usize,
    dtype: Option<&str>,
    prefix: Option<&str>,
) -> PyResult<Py<PyAny>> {
    // Import tempfile
    let tempfile = py.import("tempfile")?;
    let named_temp_file = tempfile.getattr("NamedTemporaryFile")?;

    // Create temporary file
    let kwargs = pyo3::types::PyDict::new(py);
    kwargs.set_item("delete", false)?; // Keep file for memory mapping
    if let Some(p) = prefix {
        kwargs.set_item("prefix", p)?;
    }

    let temp_file = named_temp_file.call((), Some(&kwargs))?;
    let filepath = temp_file.getattr("name")?.extract::<String>()?;

    // Close the file handle
    temp_file.call_method0("close")?;

    // Create memory-mapped array using the temporary file
    let mmap_array = memory_mapped_array(py, &filepath, size, dtype, Some("w+"))?;

    // Return both the array and the filepath
    let result = pyo3::types::PyDict::new(py);
    result.set_item("array", mmap_array)?;
    result.set_item("filepath", filepath)?;

    Ok(result.into())
}
