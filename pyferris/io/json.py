"""
High-performance file I/O operations for Pyferris

This module provides efficient file reading/writing operations with parallel processing
capabilities, supporting various formats including text, CSV, and JSON.
"""

from typing import List, Any
from pyferris import _pyferris

__all__ = [
    # File I/O classes
    'JsonReader', 'JsonWriter',
    
    # JSON operations
    'read_json', 'write_json', 'read_jsonl', 'write_jsonl', 'append_jsonl',
    'parse_json', 'to_json_string',
    
]


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

