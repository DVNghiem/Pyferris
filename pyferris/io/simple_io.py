"""
Simple file I/O operations for Pyferris

This module provides basic file reading/writing operations with parallel processing
capabilities for text files.
"""

from typing import List, Tuple
from . import _pyferris

__all__ = [
    # File I/O classes
    'SimpleFileReader', 'SimpleFileWriter',
    
    # Basic file operations
    'read_file', 'write_file', 'file_exists', 'file_size',
    'create_directory', 'delete_file', 'copy_file', 'move_file',
    
    # Parallel operations
    'read_files_parallel', 'write_files_parallel',
]


class SimpleFileReader:
    """Simple file reader"""
    
    def __init__(self, file_path: str):
        """Initialize SimpleFileReader"""
        self._reader = _pyferris.SimpleFileReader(file_path)
    
    def read_text(self) -> str:
        """Read entire file as text"""
        return self._reader.read_text()
    
    def read_lines(self) -> List[str]:
        """Read file line by line"""
        return self._reader.read_lines()


class SimpleFileWriter:
    """Simple file writer"""
    
    def __init__(self, file_path: str):
        """Initialize SimpleFileWriter"""
        self._writer = _pyferris.SimpleFileWriter(file_path)
    
    def write_text(self, content: str) -> None:
        """Write text to file"""
        self._writer.write_text(content)
    
    def append_text(self, content: str) -> None:
        """Append text to file"""
        self._writer.append_text(content)


# Basic file operations
def read_file(file_path: str) -> str:
    """Read text file content"""
    return _pyferris.simple_read_file(file_path)


def write_file(file_path: str, content: str) -> None:
    """Write text content to file"""
    _pyferris.simple_write_file(file_path, content)


def file_exists(file_path: str) -> bool:
    """Check if file exists"""
    return _pyferris.simple_file_exists(file_path)


def file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return _pyferris.simple_get_file_size(file_path)


def create_directory(dir_path: str) -> None:
    """Create directory if it doesn't exist"""
    _pyferris.simple_create_directory(dir_path)


def delete_file(file_path: str) -> None:
    """Delete file"""
    _pyferris.simple_delete_file(file_path)


def copy_file(src_path: str, dst_path: str) -> None:
    """Copy file"""
    _pyferris.simple_copy_file(src_path, dst_path)


def move_file(src_path: str, dst_path: str) -> None:
    """Move/rename file"""
    _pyferris.simple_move_file(src_path, dst_path)


# Parallel operations
def read_files_parallel(file_paths: List[str]) -> List[str]:
    """Read multiple files in parallel"""
    return _pyferris.simple_parallel_read_files(file_paths)


def write_files_parallel(file_data: List[Tuple[str, str]]) -> None:
    """Write multiple files in parallel"""
    _pyferris.simple_parallel_write_files(file_data)
