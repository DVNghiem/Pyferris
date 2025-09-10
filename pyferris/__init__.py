"""
PyFerris - High-performance parallel processing library for Python, powered by Rust and PyO3.
"""

__version__ = "0.4.0"

from .core import (
    parallel_map, parallel_reduce, parallel_filter, parallel_starmap,
    parallel_sort, parallel_group_by, parallel_unique, parallel_partition,
    parallel_chunks, BatchProcessor, ProgressTracker, ResultCollector
)
from .config import Config, get_chunk_size, get_worker_count, set_chunk_size, set_worker_count
from .executor import Executor
from .io import csv, file_reader, simple_io, file_writer, json, parallel_io

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

from .concurrent import ConcurrentHashMap, LockFreeQueue, AtomicCounter, RwLockDict
from .memory import MemoryPool, memory_mapped_array, memory_mapped_array_2d, memory_mapped_info, create_temp_mmap
from .cache import SmartCache, EvictionPolicy, cached

from .distributed import (
    DistributedCluster, create_cluster, distributed_map, distributed_filter,
    async_distributed_map, ClusterManager, LoadBalancer, DistributedExecutor,
    DistributedBatchProcessor, cluster_map, distributed_reduce
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
    
    "parallel_sort",
    "parallel_group_by", 
    "parallel_unique",
    "parallel_partition",
    "parallel_chunks",
    "BatchProcessor",
    "ProgressTracker", 
    "ResultCollector",
    
    "Pipeline",
    "Chain", 
    "pipeline_map",
    
    "AsyncExecutor",
    "AsyncTask",
    "async_parallel_map",
    "async_parallel_filter",
    
    "SharedArray",
    "SharedArrayInt",
    "SharedArrayStr", 
    "SharedArrayObj",
    "SharedDict",
    "SharedQueue", 
    "SharedCounter",
    "create_shared_array",
    
    "WorkStealingScheduler",
    "RoundRobinScheduler",
    "AdaptiveScheduler",
    "PriorityScheduler",
    "TaskPriority",
    "execute_with_priority",
    "create_priority_task",
    
    "ConcurrentHashMap",
    "LockFreeQueue",
    "AtomicCounter", 
    "RwLockDict",
    
    "MemoryPool",
    "memory_mapped_array",
    "memory_mapped_array_2d",
    "memory_mapped_info",
    "create_temp_mmap",
        
    "SmartCache",
    "EvictionPolicy",
    "cached",
    
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

]