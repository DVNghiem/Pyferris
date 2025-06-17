"""
High-performance file I/O operations for Pyferris

This module provides efficient file reading/writing operations with parallel processing
"""

from typing import List, Dict, Any, Optional, Callable, Tuple
from pyferris import _pyferris

__all__ = [
    # File I/O classes
    'ParallelFileProcessor',
    
    # Parallel operations
    'find_files', 'directory_size', 'count_lines', 'process_files_parallel',
    
    # Chunk processing
    'process_file_chunks',
]

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


# Chunk processing
def process_file_chunks(file_path: str, chunk_size: int, processor_func: Callable[[int, List[str]], Any]) -> List[Any]:
    """Process file in chunks with parallel execution"""
    return _pyferris.parallel_process_file_chunks(file_path, chunk_size, processor_func)
