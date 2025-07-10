# I/O operations for PyFerris with performance optimizations

"""
High-performance I/O operations optimized for parallel processing.

This module provides optimized I/O operations that minimize memory usage
and maximize throughput for large datasets.
"""

import gc
import weakref

# Re-export optimized I/O functions
try:
    from .._pyferris import (
        read_csv as _read_csv,
        write_csv as _write_csv,
        read_file as _read_file,
        write_file as _write_file,
        read_json as _read_json,
        write_json as _write_json,
        parallel_read_files as _parallel_read_files,
        parallel_write_files as _parallel_write_files,
    )
except ImportError:
    # Fallback for development/testing
    def _dummy_io_op(*args, **kwargs):
        raise NotImplementedError("IO operations require compiled Rust extension")
    
    _read_csv = _write_csv = _read_file = _write_file = _dummy_io_op
    _read_json = _write_json = _parallel_read_files = _parallel_write_files = _dummy_io_op

# File handle cache for better performance
_FILE_CACHE = weakref.WeakValueDictionary()
_CACHE_LOCK = None

def _get_cache_lock():
    global _CACHE_LOCK
    if _CACHE_LOCK is None:
        import threading
        _CACHE_LOCK = threading.Lock()
    return _CACHE_LOCK

def _optimize_io_operation(operation_func):
    """Decorator to add memory optimization to I/O operations."""
    def wrapper(*args, **kwargs):
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            if "memory" in str(e).lower():
                gc.collect()  # Force garbage collection on memory errors
                return operation_func(*args, **kwargs)
            raise
    return wrapper

# Apply optimizations to all I/O functions
read_csv = _optimize_io_operation(_read_csv)
write_csv = _optimize_io_operation(_write_csv)
read_file = _optimize_io_operation(_read_file)
write_file = _optimize_io_operation(_write_file)
read_json = _optimize_io_operation(_read_json)
write_json = _optimize_io_operation(_write_json)
parallel_read_files = _optimize_io_operation(_parallel_read_files)
parallel_write_files = _optimize_io_operation(_parallel_write_files)

# Aliases for backward compatibility
csv = type('CSV', (), {
    'read': read_csv,
    'write': write_csv,
})()

json = type('JSON', (), {
    'read': read_json,
    'write': write_json,
})()

file_reader = read_file
file_writer = write_file
simple_io = type('SimpleIO', (), {
    'read': read_file,
    'write': write_file,
})()

parallel_io = type('ParallelIO', (), {
    'read_files': parallel_read_files,
    'write_files': parallel_write_files,
})()

__all__ = [
    'csv', 'json', 'file_reader', 'file_writer', 'simple_io', 'parallel_io',
    'read_csv', 'write_csv', 'read_file', 'write_file', 
    'read_json', 'write_json', 'parallel_read_files', 'parallel_write_files'
]