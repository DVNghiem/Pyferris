"""
High-performance file I/O operations for Pyferris
Handles reading/writing CSV, JSON, and text files with parallel processing capabilities.
"""

from typing import List, Dict, Any
from pyferris import _pyferris

__all__ = [
    # File I/O classes
    'CsvReader', 'CsvWriter', 
    
    # CSV operations
    'read_csv', 'write_csv', 'read_csv_rows', 'write_csv_rows',
]


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
