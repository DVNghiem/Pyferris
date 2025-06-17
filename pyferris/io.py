"""
High-performance file I/O operations for Pyferris

This module provides efficient file reading/writing operations with parallel processing
capabilities, supporting various formats including text, CSV, and JSON.
"""

from typing import List, Dict, Any, Optional, Callable, Tuple
from . import _pyferris

__all__ = [
    # File I/O classes
    'FileReader', 'FileWriter', 'CsvReader', 'CsvWriter', 
    'JsonReader', 'JsonWriter', 'ParallelFileProcessor',
    
    # Basic file operations
    'read_file', 'write_file', 'append_file', 'file_exists', 'file_size',
    'create_directory', 'delete_file', 'copy_file', 'move_file',
    
    # Parallel operations
    'read_files_parallel', 'write_files_parallel', 'process_files_parallel',
    'find_files', 'directory_size', 'count_lines',
    
    # CSV operations
    'read_csv', 'write_csv', 'read_csv_rows', 'write_csv_rows',
    
    # JSON operations
    'read_json', 'write_json', 'read_jsonl', 'write_jsonl', 'append_jsonl',
    'parse_json', 'to_json_string',
    
    # Chunk processing
    'process_file_chunks',
]


class FileReader:
    """High-performance file reader with parallel processing capabilities"""
    
    def __init__(self, file_path: str, chunk_size: int = 8192, encoding: str = "utf-8"):
        """
        Initialize FileReader
        
        Args:
            file_path: Path to the file to read
            chunk_size: Size of chunks for reading (default: 8192)
            encoding: Text encoding (default: utf-8)
        """
        self._reader = _pyferris.FileReader(file_path, chunk_size, encoding)
    
    def read_bytes(self) -> bytes:
        """Read entire file as bytes"""
        return self._reader.read_bytes()
    
    def read_text(self) -> str:
        """Read entire file as text"""
        return self._reader.read_text()
    
    def read_lines(self) -> List[str]:
        """Read file line by line"""
        return self._reader.read_lines()
    
    def read_chunks(self) -> List[bytes]:
        """Read file in chunks for memory-efficient processing"""
        return self._reader.read_chunks()
    
    def process_lines_parallel(self, func: Callable[[str], Any]) -> List[Any]:
        """Process lines in parallel with custom function"""
        return self._reader.parallel_process_lines(func)


class FileWriter:
    """High-performance file writer with buffering"""
    
    def __init__(self, file_path: str, append_mode: bool = False, buffer_size: int = 8192):
        """
        Initialize FileWriter
        
        Args:
            file_path: Path to the file to write
            append_mode: Whether to append to existing file (default: False)
            buffer_size: Size of write buffer (default: 8192)
        """
        self._writer = _pyferris.FileWriter(file_path, append_mode, buffer_size)
    
    def write_text(self, content: str) -> None:
        """Write text to file"""
        self._writer.write_text(content)
    
    def write_bytes(self, content: bytes) -> None:
        """Write bytes to file"""
        self._writer.write_bytes(content)
    
    def write_lines(self, lines: List[str]) -> None:
        """Write lines to file"""
        self._writer.write_lines(lines)
    
    def append_text(self, content: str) -> None:
        """Append text to file"""
        self._writer.append_text(content)
    
    def append_line(self, line: str) -> None:
        """Append line to file"""
        self._writer.append_line(line)


class CsvReader:
    """High-performance CSV reader"""
    
    def __init__(self, file_path: str, delimiter: str = ',', has_headers: bool = True):
        """
        Initialize CsvReader
        
        Args:
            file_path: Path to CSV file
            delimiter: Field delimiter (default: ',')
            has_headers: Whether file has headers (default: True)
        """
        delimiter_byte = ord(delimiter) if len(delimiter) == 1 else ord(',')
        self._reader = _pyferris.CsvReader(file_path, delimiter_byte, has_headers)
    
    def read_dict(self) -> List[Dict[str, str]]:
        """Read CSV as list of dictionaries"""
        return self._reader.read_dict()
    
    def read_rows(self) -> List[List[str]]:
        """Read CSV as list of lists"""
        return self._reader.read_rows()
    
    def get_headers(self) -> List[str]:
        """Get column headers"""
        return self._reader.get_headers()


class CsvWriter:
    """High-performance CSV writer"""
    
    def __init__(self, file_path: str, delimiter: str = ',', write_headers: bool = True):
        """
        Initialize CsvWriter
        
        Args:
            file_path: Path to CSV file
            delimiter: Field delimiter (default: ',')
            write_headers: Whether to write headers (default: True)
        """
        delimiter_byte = ord(delimiter) if len(delimiter) == 1 else ord(',')
        self._writer = _pyferris.CsvWriter(file_path, delimiter_byte, write_headers)
    
    def write_dict(self, data: List[Dict[str, Any]]) -> None:
        """Write data from list of dictionaries"""
        self._writer.write_dict(data)
    
    def write_rows(self, data: List[List[str]]) -> None:
        """Write data from list of lists"""
        self._writer.write_rows(data)


class JsonReader:
    """High-performance JSON reader"""
    
    def __init__(self, file_path: str):
        """
        Initialize JsonReader
        
        Args:
            file_path: Path to JSON file
        """
        self._reader = _pyferris.JsonReader(file_path)
    
    def read(self) -> Any:
        """Read JSON file as Python object"""
        return self._reader.read()
    
    def read_lines(self) -> List[Any]:
        """Read JSON Lines file as list of objects"""
        return self._reader.read_lines()
    
    def read_array_stream(self) -> List[Any]:
        """Read large JSON array in streaming mode"""
        return self._reader.read_array_stream()


class JsonWriter:
    """High-performance JSON writer"""
    
    def __init__(self, file_path: str, pretty_print: bool = False):
        """
        Initialize JsonWriter
        
        Args:
            file_path: Path to JSON file
            pretty_print: Whether to format JSON with indentation (default: False)
        """
        self._writer = _pyferris.JsonWriter(file_path, pretty_print)
    
    def write(self, data: Any) -> None:
        """Write Python object as JSON"""
        self._writer.write(data)
    
    def write_lines(self, data: List[Any]) -> None:
        """Write list of objects as JSON Lines"""
        self._writer.write_lines(data)
    
    def append_line(self, data: Any) -> None:
        """Append object to JSON Lines file"""
        self._writer.append_line(data)


class ParallelFileProcessor:
    """Parallel file operations for batch processing"""
    
    def __init__(self, max_workers: int = 0, chunk_size: int = 1000):
        """
        Initialize ParallelFileProcessor
        
        Args:
            max_workers: Maximum number of worker threads (0 = auto)
            chunk_size: Size of processing chunks
        """
        self._processor = _pyferris.ParallelFileProcessor(max_workers, chunk_size)
    
    def process_files(self, file_paths: List[str], processor_func: Callable[[str, str], Any]) -> List[Any]:
        """Process multiple files in parallel with custom function"""
        return self._processor.process_files(file_paths, processor_func)
    
    def read_files_parallel(self, file_paths: List[str]) -> List[Tuple[str, str]]:
        """Read multiple files in parallel"""
        return self._processor.read_files_parallel(file_paths)
    
    def write_files_parallel(self, file_data: List[Tuple[str, str]]) -> None:
        """Write multiple files in parallel"""
        self._processor.write_files_parallel(file_data)
    
    def copy_files_parallel(self, file_pairs: List[Tuple[str, str]]) -> None:
        """Copy multiple files in parallel"""
        self._processor.copy_files_parallel(file_pairs)
    
    def process_directory(self, dir_path: str, processor_func: Callable[[str, str], Any], 
                         file_filter: Optional[Callable[[str], bool]] = None) -> List[Any]:
        """Process directory recursively in parallel"""
        return self._processor.process_directory(dir_path, file_filter, processor_func)
    
    def get_file_stats_parallel(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Get file statistics in parallel"""
        return self._processor.get_file_stats_parallel(file_paths)


# Basic file operations
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """Read text file content"""
    return _pyferris.read_file_text(file_path)


def write_file(file_path: str, content: str) -> None:
    """Write text content to file"""
    _pyferris.write_file_text(file_path, content)


def append_file(file_path: str, content: str) -> None:
    """Append text content to file"""
    _pyferris.append_file_text(file_path, content)


def file_exists(file_path: str) -> bool:
    """Check if file exists"""
    return _pyferris.file_exists(file_path)


def file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return _pyferris.get_file_size(file_path)


def create_directory(dir_path: str) -> None:
    """Create directory if it doesn't exist"""
    _pyferris.create_directory(dir_path)


def delete_file(file_path: str) -> None:
    """Delete file"""
    _pyferris.delete_file(file_path)


def copy_file(src_path: str, dst_path: str) -> None:
    """Copy file"""
    _pyferris.copy_file(src_path, dst_path)


def move_file(src_path: str, dst_path: str) -> None:
    """Move/rename file"""
    _pyferris.move_file(src_path, dst_path)


# Parallel operations
def read_files_parallel(file_paths: List[str]) -> List[str]:
    """Read multiple files in parallel"""
    return _pyferris.parallel_read_files(file_paths)


def write_files_parallel(file_data: List[Tuple[str, str]]) -> None:
    """Write multiple files in parallel"""
    _pyferris.parallel_write_files(file_data)


def process_files_parallel(file_paths: List[str], processor_func: Callable[[str, str], Any]) -> List[Any]:
    """Process multiple files in parallel with custom function"""
    processor = ParallelFileProcessor()
    return processor.process_files(file_paths, processor_func)


def find_files(root_dir: str, pattern: str) -> List[str]:
    """Find files matching pattern in parallel"""
    return _pyferris.parallel_find_files(root_dir, pattern)


def directory_size(dir_path: str) -> int:
    """Get directory size in parallel"""
    return _pyferris.parallel_directory_size(dir_path)


def count_lines(file_paths: List[str]) -> int:
    """Count lines in multiple files in parallel"""
    return _pyferris.parallel_count_lines(file_paths)


# CSV operations
def read_csv(file_path: str, delimiter: str = ',', has_headers: bool = True) -> List[Dict[str, str]]:
    """Read CSV file as list of dictionaries"""
    delimiter_byte = ord(delimiter) if len(delimiter) == 1 else ord(',')
    return _pyferris.read_csv_dict(file_path, delimiter_byte, has_headers)


def write_csv(file_path: str, data: List[Dict[str, Any]], delimiter: str = ',', write_headers: bool = True) -> None:
    """Write CSV file from list of dictionaries"""
    delimiter_byte = ord(delimiter) if len(delimiter) == 1 else ord(',')
    _pyferris.write_csv_dict(file_path, data, delimiter_byte, write_headers)


def read_csv_rows(file_path: str, delimiter: str = ',', has_headers: bool = True) -> List[List[str]]:
    """Read CSV file as list of lists"""
    delimiter_byte = ord(delimiter) if len(delimiter) == 1 else ord(',')
    return _pyferris.read_csv_rows(file_path, delimiter_byte, has_headers)


def write_csv_rows(file_path: str, data: List[List[str]], delimiter: str = ',') -> None:
    """Write CSV file from list of lists"""
    delimiter_byte = ord(delimiter) if len(delimiter) == 1 else ord(',')
    _pyferris.write_csv_rows(file_path, data, delimiter_byte)


# JSON operations
def read_json(file_path: str) -> Any:
    """Read JSON file as Python object"""
    return _pyferris.read_json(file_path)


def write_json(file_path: str, data: Any, pretty_print: bool = False) -> None:
    """Write Python object as JSON file"""
    _pyferris.write_json(file_path, data, pretty_print)


def read_jsonl(file_path: str) -> List[Any]:
    """Read JSON Lines file as list"""
    return _pyferris.read_jsonl(file_path)


def write_jsonl(file_path: str, data: List[Any]) -> None:
    """Write list as JSON Lines file"""
    _pyferris.write_jsonl(file_path, data)


def append_jsonl(file_path: str, data: Any) -> None:
    """Append object to JSON Lines file"""
    _pyferris.append_jsonl(file_path, data)


def parse_json(json_str: str) -> Any:
    """Parse JSON string to Python object"""
    return _pyferris.parse_json(json_str)


def to_json_string(data: Any, pretty_print: bool = False) -> str:
    """Convert Python object to JSON string"""
    return _pyferris.to_json_string(data, pretty_print)


# Chunk processing
def process_file_chunks(file_path: str, chunk_size: int, processor_func: Callable[[int, List[str]], Any]) -> List[Any]:
    """Process file in chunks with parallel execution"""
    return _pyferris.parallel_process_file_chunks(file_path, chunk_size, processor_func)
