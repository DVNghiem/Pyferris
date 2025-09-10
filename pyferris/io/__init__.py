# I/O operations for PyFerris with performance optimizations

"""
High-performance I/O operations optimized for parallel processing.

This module provides optimized I/O operations that minimize memory usage
and maximize throughput for large datasets.
"""

from .csv import (
    CsvReader,
    CsvWriter,
    read_csv,
    read_csv_rows,
    write_csv,
    write_csv_rows,
)
from .file_reader import (
    FileReader,
    file_exists,
    file_size,
    read_file_bytes,
    read_file_text,
    read_files_parallel,
)
from .file_writer import (
    FileWriter,
    append_file,
    copy_file,
    create_directory,
    delete_file,
    move_file,
    write_file_bytes,
    write_file_text,
    write_files_parallel,
)
from .json import (
    JsonReader,
    JsonWriter,
    append_jsonl,
    parse_json,
    read_json,
    read_jsonl,
    to_json_string,
    write_json,
    write_jsonl,
)
from .parallel_io import (
    ParallelFileProcessor,
    count_lines,
    directory_size,
    find_files,
    process_file_chunks,
    process_files_parallel,
)
from .simple_io import SimpleFileReader, SimpleFileWriter, read_file, write_file

__all__ = [
    # CSV File I/O classes
    "CsvReader",
    "CsvWriter",
    # CSV operations
    "read_csv",
    "write_csv",
    "read_csv_rows",
    "write_csv_rows",
    # File I/O classes
    "FileReader",
    # Basic file operations
    "read_file_text",
    "read_file_bytes",
    "read_files_parallel",
    "file_exists",
    "file_size",
    # File I/O classes
    "FileWriter",
    "create_directory",
    "delete_file",
    "copy_file",
    "move_file",
    "append_file",
    "write_files_parallel",
    "write_file_text",
    "write_file_bytes",
    # File I/O classes
    "JsonReader",
    "JsonWriter",
    # JSON operations
    "read_json",
    "write_json",
    "read_jsonl",
    "write_jsonl",
    "append_jsonl",
    "parse_json",
    "to_json_string",
    # File I/O classes
    "ParallelFileProcessor",
    # Parallel operations
    "find_files",
    "directory_size",
    "count_lines",
    "process_files_parallel",
    # Chunk processing
    "process_file_chunks",
    # File I/O classes
    "SimpleFileReader",
    "SimpleFileWriter",
    # Basic file operations
    "read_file",
    "write_file",
    "file_exists",
    "file_size",
    "create_directory",
    "delete_file",
    "copy_file",
    "move_file",
    # Parallel operations
    "read_files_parallel",
    "write_files_parallel",
]
