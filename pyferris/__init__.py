"""
PyFerris - High-performance parallel processing library for Python, powered by Rust and PyO3.

Level 1 Features:
- Core Parallel Operations: parallel_map, parallel_filter, parallel_reduce, parallel_starmap
- Task Executor: Executor class for managing tasks
- Basic Configuration: set_worker_count, set_chunk_size
- Error Handling: ParallelExecutionError and error strategies
"""

from ._pyferris import (
    parallel_map,
    parallel_starmap, 
    parallel_filter,
    parallel_reduce,
    Executor,
    set_worker_count,
    get_worker_count,
    set_chunk_size,
    get_chunk_size,
    Config,
    ParallelExecutionError,
    log_info,
    log_warning,
    log_error,
)

from .core import *
from .executor import *
from .config import *

__version__ = "0.1.0"
__all__ = [
    # Core parallel operations
    "parallel_map",
    "parallel_starmap",
    "parallel_filter", 
    "parallel_reduce",
    
    # Executor
    "Executor",
    
    # Configuration
    "set_worker_count",
    "get_worker_count",
    "set_chunk_size", 
    "get_chunk_size",
    "Config",
    
    # Error handling
    "ParallelExecutionError",
    
    # Logging
    "log_info",
    "log_warning",
    "log_error",
]