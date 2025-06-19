"""
PyFerris - High-performance parallel processing library for Python, powered by Rust and PyO3.
"""

__version__ = "0.2.1"
from .core import parallel_map, parallel_reduce, parallel_filter, parallel_starmap
from .config import Config, get_chunk_size, get_worker_count, set_chunk_size, set_worker_count
from .executor import Executor
from .io import csv, file_reader, simple_io, file_writer, json, parallel_io
from .advanced import (
    parallel_sort, parallel_group_by, parallel_unique, parallel_partition,
    parallel_chunks, BatchProcessor, ProgressTracker, ResultCollector
)

__all__ = [
    # core base functionality
    "__version__",
    "parallel_map",
    "parallel_reduce",
    "parallel_filter",
    "parallel_starmap",

    # configuration management
    "Config",
    "get_chunk_size",
    "get_worker_count",
    "set_chunk_size",
    "set_worker_count",

    # executor
    "Executor",

    # I/O operations
    "csv",
    "file_reader",
    "simple_io",
    "file_writer",
    "json",
    "parallel_io",
    
    # Level 2: Advanced parallel operations
    "parallel_sort",
    "parallel_group_by", 
    "parallel_unique",
    "parallel_partition",
    "parallel_chunks",
    "BatchProcessor",
    "ProgressTracker", 
    "ResultCollector"
]