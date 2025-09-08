"""
High-performance file I/O operations for Pyferris

This module provides efficient file Reading operations with buffering and parallel processing
"""

from typing import List, Any, Callable
from pyferris import _pyferris

__all__ = [
    # File I/O classes
    'FileReader',
    
    # Basic file operations
    'read_file_text', 'read_file_bytes', 'read_files_parallel', 'file_exists', 'file_size',

]


class FileReader:
    """High-performance file reader with parallel processing capabilities"""
    
    def __init__(self, file_path: str, chunk_size: int = 8192):
        """
        Initialize FileReader
        
        Args:
            file_path: Path to the file to read
            chunk_size: Size of chunks for reading (default: 8192)
        """
        self._reader = _pyferris.FileReader(file_path, chunk_size)
    
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

# Basic file operations
def read_file_text(file_path: str) -> str:
    """Read text file content"""
    return _pyferris.read_file_text(file_path)

def read_file_bytes(file_path: str) -> bytes:
    """Read binary file content"""
    return _pyferris.read_file_bytes(file_path)

# Parallel operations
def read_files_parallel(file_paths: List[str]) -> List[str]:
    """Read multiple files in parallel"""
    return _pyferris.parallel_read_files(file_paths)


def file_exists(file_path: str) -> bool:
    """Check if file exists"""
    return _pyferris.file_exists(file_path)


def file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return _pyferris.get_file_size(file_path)

