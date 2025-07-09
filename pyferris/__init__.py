"""
PyFerris - High-performance parallel processing library for Python, powered by Rust and PyO3.
"""

__version__ = "0.3.1"
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

# Level 4: Expert Features
from .concurrent import ConcurrentHashMap, LockFreeQueue, AtomicCounter, RwLockDict
from .memory import MemoryPool, memory_mapped_array, memory_mapped_array_2d, memory_mapped_info, create_temp_mmap
from .profiling import Profiler, auto_tune_workers, profile_parallel_operation
from .cache import SmartCache, EvictionPolicy, cached

# Level 5: Enterprise Features
from .distributed import (
    DistributedCluster, create_cluster, distributed_map, distributed_filter,
    async_distributed_map, ClusterManager, LoadBalancer, DistributedExecutor,
    DistributedBatchProcessor, cluster_map, distributed_reduce
)
from .fault_tolerance import (
    RetryExecutor, CircuitBreaker, CheckpointManager, AutoCheckpoint,
    retry, circuit_breaker, with_checkpoints, resilient_operation, ResilientOperation
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
    "create_priority_task",
    
    # Level 4: Concurrent Data Structures
    "ConcurrentHashMap",
    "LockFreeQueue",
    "AtomicCounter", 
    "RwLockDict",
    
    # Level 4: Memory Management
    "MemoryPool",
    "memory_mapped_array",
    "memory_mapped_array_2d",
    "memory_mapped_info",
    "create_temp_mmap",
    
    # Level 4: Performance Profiling
    "Profiler",
    "auto_tune_workers",
    "profile_parallel_operation",
    
    # Level 4: Smart Cache
    "SmartCache",
    "EvictionPolicy",
    "cached",
    
    # Level 5: Distributed Processing
    "DistributedCluster",
    "create_cluster",
    "distributed_map", 
    "distributed_filter",
    "async_distributed_map",
    "ClusterManager",
    "LoadBalancer",
    "DistributedExecutor",
    "DistributedBatchProcessor",
    "cluster_map",
    "distributed_reduce",
    
    # Level 5: Fault Tolerance
    "RetryExecutor",
    "CircuitBreaker",
    "CheckpointManager", 
    "AutoCheckpoint",
    "retry",
    "circuit_breaker",
    "with_checkpoints",
    "resilient_operation",
    "ResilientOperation"
]