"""
High-performance file I/O operations for Pyferris

This module provides efficient file Writing operations with buffering and parallel processing
"""

from typing import List, Tuple
from pyferris import _pyferris

__all__ = [
    # File I/O classes
    'FileWriter',
    
    'create_directory', 'delete_file', 'copy_file', 'move_file', 'append_file',
    'write_files_parallel', 'write_file_text', 'write_file_bytes',
]


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


def write_file_text(file_path: str, content: str) -> None:
    """Write text content to file"""
    _pyferris.write_file_text(file_path, content)

def write_file_bytes(file_path: str, content: bytes) -> None:
    """Write binary content to file"""
    _pyferris.write_file_bytes(file_path, content)


def append_file(file_path: str, content: str) -> None:
    """Append text content to file"""
    _pyferris.append_file_text(file_path, content)

def write_files_parallel(file_data: List[Tuple[str, str]]) -> None:
    """Write multiple files in parallel"""
    _pyferris.parallel_write_files(file_data)


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

