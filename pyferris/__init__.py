"""
PyFerris - High-performance parallel processing library for Python, powered by Rust and PyO3.
"""

__version__ = "0.2.2"
from .core import parallel_map, parallel_reduce, parallel_filter, parallel_starmap
from .config import Config, get_chunk_size, get_worker_count, set_chunk_size, set_worker_count
from .executor import Executor
from .io import csv, file_reader, simple_io, file_writer, json, parallel_io
from .advanced import (
    parallel_sort, parallel_group_by, parallel_unique, parallel_partition,
    parallel_chunks, BatchProcessor, ProgressTracker, ResultCollector
)

# Level 3: Advanced Features
from .pipeline import Pipeline, Chain, pipeline_map
from .async_ops import AsyncExecutor, AsyncTask, async_parallel_map, async_parallel_filter
from .shared_memory import (
    SharedArray, SharedArrayInt, SharedArrayStr, SharedArrayObj,
    SharedDict, SharedQueue, SharedCounter, create_shared_array
)
from .scheduler import (
    WorkStealingScheduler, RoundRobinScheduler, AdaptiveScheduler,
    PriorityScheduler, TaskPriority, execute_with_priority, create_priority_task
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
    "ResultCollector",
    
    # Level 3: Pipeline Processing
    "Pipeline",
    "Chain", 
    "pipeline_map",
    
    # Level 3: Async Support
    "AsyncExecutor",
    "AsyncTask",
    "async_parallel_map",
    "async_parallel_filter",
    
    # Level 3: Shared Memory
    "SharedArray",
    "SharedArrayInt",
    "SharedArrayStr", 
    "SharedArrayObj",
    "SharedDict",
    "SharedQueue", 
    "SharedCounter",
    "create_shared_array",
    
    # Level 3: Custom Schedulers
    "WorkStealingScheduler",
    "RoundRobinScheduler",
    "AdaptiveScheduler",
    "PriorityScheduler",
    "TaskPriority",
    "execute_with_priority",
    "create_priority_task"
]