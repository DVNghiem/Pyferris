use pyo3::prelude::*;

pub mod csv;
pub mod file_reader;
pub mod file_writer;
pub mod json;
pub mod parallel_io;
pub mod simple_io;

/// Register all io functions and classes with Python
pub fn register_io(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register individual io classes
    // Register simple IO functions
    m.add_class::<simple_io::SimpleFileReader>()?;
    m.add_class::<simple_io::SimpleFileWriter>()?;

    // Basic file operations
    m.add_function(wrap_pyfunction!(simple_io::simple_read_file, m)?)?;
    m.add_function(wrap_pyfunction!(simple_io::simple_write_file, m)?)?;
    m.add_function(wrap_pyfunction!(simple_io::simple_parallel_read_files, m)?)?;
    m.add_function(wrap_pyfunction!(simple_io::simple_parallel_write_files, m)?)?;
    m.add_function(wrap_pyfunction!(simple_io::simple_file_exists, m)?)?;
    m.add_function(wrap_pyfunction!(simple_io::simple_get_file_size, m)?)?;
    m.add_function(wrap_pyfunction!(simple_io::simple_create_directory, m)?)?;
    m.add_function(wrap_pyfunction!(simple_io::simple_delete_file, m)?)?;
    m.add_function(wrap_pyfunction!(simple_io::simple_copy_file, m)?)?;
    m.add_function(wrap_pyfunction!(simple_io::simple_move_file, m)?)?;

    // Register CSV operations
    m.add_class::<csv::CsvReader>()?;
    m.add_class::<csv::CsvWriter>()?;
    m.add_function(wrap_pyfunction!(csv::read_csv_dict, m)?)?;
    m.add_function(wrap_pyfunction!(csv::read_csv_rows, m)?)?;
    m.add_function(wrap_pyfunction!(csv::write_csv_dict, m)?)?;
    m.add_function(wrap_pyfunction!(csv::write_csv_rows, m)?)?;

    // Register JSON operations
    m.add_class::<json::JsonReader>()?;
    m.add_class::<json::JsonWriter>()?;
    m.add_function(wrap_pyfunction!(json::read_json, m)?)?;
    m.add_function(wrap_pyfunction!(json::write_json, m)?)?;
    m.add_function(wrap_pyfunction!(json::read_jsonl, m)?)?;
    m.add_function(wrap_pyfunction!(json::write_jsonl, m)?)?;
    m.add_function(wrap_pyfunction!(json::append_jsonl, m)?)?;
    m.add_function(wrap_pyfunction!(json::to_json_string, m)?)?;
    m.add_function(wrap_pyfunction!(json::parse_json, m)?)?;

    // Register file reader and writer
    m.add_class::<file_reader::FileReader>()?;
    m.add_function(wrap_pyfunction!(file_reader::read_file_text, m)?)?;
    m.add_function(wrap_pyfunction!(file_reader::read_file_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(file_reader::parallel_read_files, m)?)?;
    m.add_function(wrap_pyfunction!(file_reader::file_exists, m)?)?;
    m.add_function(wrap_pyfunction!(file_reader::get_file_size, m)?)?;

    m.add_class::<file_writer::FileWriter>()?;
    m.add_function(wrap_pyfunction!(file_writer::write_file_text, m)?)?;
    m.add_function(wrap_pyfunction!(file_writer::write_file_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(file_writer::append_file_text, m)?)?;
    m.add_function(wrap_pyfunction!(file_writer::parallel_write_files, m)?)?;
    m.add_function(wrap_pyfunction!(file_writer::create_directory, m)?)?;
    m.add_function(wrap_pyfunction!(file_writer::delete_file, m)?)?;
    m.add_function(wrap_pyfunction!(file_writer::copy_file, m)?)?;
    m.add_function(wrap_pyfunction!(file_writer::move_file, m)?)?;

    // Register parallel IO operations
    m.add_class::<parallel_io::ParallelFileProcessor>()?;
    m.add_function(wrap_pyfunction!(
        parallel_io::parallel_process_file_chunks,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(parallel_io::parallel_find_files, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_io::parallel_directory_size, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_io::parallel_count_lines, m)?)?;

    Ok(())
}
