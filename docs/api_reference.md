# API Reference

Complete API reference for PyFerris - a high-performance parallel processing library for Python.

## Core Module (`pyferris.core`)

### Parallel Operations

#### `parallel_map(func, iterable, chunk_size=None, progress=None)`

Apply a function to every item in an iterable in parallel.

**Parameters:**
- `func` (callable): Function to apply to each item
- `iterable` (iterable): Input data to process
- `chunk_size` (int, optional): Size of chunks for parallel processing
- `progress` (ProgressTracker, optional): Progress tracking object

**Returns:**
- Iterator of results

**Example:**
```python
from pyferris import parallel_map
results = parallel_map(lambda x: x**2, range(1000))
```

#### `parallel_filter(predicate, iterable, chunk_size=None, progress=None)`

Filter elements in parallel based on a predicate function.

**Parameters:**
- `predicate` (callable): Function that returns True/False
- `iterable` (iterable): Input data to filter
- `chunk_size` (int, optional): Size of chunks for parallel processing
- `progress` (ProgressTracker, optional): Progress tracking object

**Returns:**
- Iterator of filtered results

#### `parallel_reduce(function, iterable, initial=None, chunk_size=None)`

Apply a reduction function to an iterable in parallel.

**Parameters:**
- `function` (callable): Reduction function taking two arguments
- `iterable` (iterable): Input data to reduce
- `initial` (any, optional): Initial value for reduction
- `chunk_size` (int, optional): Size of chunks for parallel processing

**Returns:**
- Single reduced result

#### `parallel_starmap(function, iterable, chunk_size=None, progress=None)`

Apply a function to arguments unpacked from tuples in parallel.

**Parameters:**
- `function` (callable): Function to apply
- `iterable` (iterable): Iterable of tuples containing function arguments
- `chunk_size` (int, optional): Size of chunks for parallel processing
- `progress` (ProgressTracker, optional): Progress tracking object

**Returns:**
- Iterator of results

### Advanced Operations

#### `parallel_sort(iterable, key=None, reverse=False, chunk_size=None)`

Sort a large dataset in parallel using merge sort.

**Parameters:**
- `iterable` (iterable): Data to sort
- `key` (callable, optional): Key function for sorting
- `reverse` (bool): Sort in descending order if True
- `chunk_size` (int, optional): Size of chunks for parallel processing

**Returns:**
- List of sorted items

#### `parallel_group_by(iterable, key, chunk_size=None)`

Group elements by a key function in parallel.

**Parameters:**
- `iterable` (iterable): Data to group
- `key` (callable): Key function for grouping
- `chunk_size` (int, optional): Size of chunks for parallel processing

**Returns:**
- Dictionary mapping keys to lists of values

#### `parallel_unique(iterable, key=None, chunk_size=None)`

Remove duplicates from a dataset in parallel.

**Parameters:**
- `iterable` (iterable): Input data
- `key` (callable, optional): Key function for uniqueness comparison
- `chunk_size` (int, optional): Size of chunks for parallel processing

**Returns:**
- List of unique items

#### `parallel_partition(iterable, predicate, chunk_size=None)`

Partition data into two groups based on a predicate.

**Parameters:**
- `iterable` (iterable): Data to partition
- `predicate` (callable): Function returning True/False
- `chunk_size` (int, optional): Size of chunks for parallel processing

**Returns:**
- Tuple of (true_items, false_items)

#### `parallel_chunks(iterable, chunk_size)`

Split data into chunks for batch processing.

**Parameters:**
- `iterable` (iterable): Data to chunk
- `chunk_size` (int): Size of each chunk

**Returns:**
- List of chunks

### Utility Classes

#### `BatchProcessor`

Process large datasets in configurable batches.

```python
class BatchProcessor:
    def __init__(self, batch_size=1000, max_memory_mb=100, progress=True)
    def process(self, iterable, process_function)
```

**Methods:**
- `process(iterable, process_function)`: Process data in batches

#### `ProgressTracker`

Track progress of parallel operations.

```python
class ProgressTracker:
    def __init__(self, total, desc="Processing", update_frequency=1, show_eta=True, show_speed=True)
```

**Parameters:**
- `total` (int): Total number of items to process
- `desc` (str): Description for progress bar
- `update_frequency` (int): Update frequency for progress display
- `show_eta` (bool): Show estimated time to completion
- `show_speed` (bool): Show processing speed

#### `ResultCollector`

Collect and manage results from parallel operations.

```python
class ResultCollector:
    def __init__(self, max_size=10000, auto_save=False, save_path=None)
    def add(self, result)
    def get_results(self)
    def filter(self, predicate)
    def save_to_file(self, path)
```

## Configuration Module (`pyferris.config`)

### Configuration Functions

#### `get_chunk_size()` → `int`

Get the current default chunk size for parallel operations.

#### `set_chunk_size(size)`

Set the default chunk size for parallel operations.

**Parameters:**
- `size` (int): New chunk size

#### `get_worker_count()` → `int`

Get the current number of worker threads.

#### `set_worker_count(count)`

Set the number of worker threads.

**Parameters:**
- `count` (int): Number of worker threads

#### `Config`

Configuration class for PyFerris settings.

```python
class Config:
    @staticmethod
    def get_optimal_chunk_size(iterable_size, operation_type="default")
    @staticmethod
    def auto_configure(workload_type="balanced")
```

## Executor Module (`pyferris.executor`)

#### `Executor`

Advanced task execution and thread pool management.

```python
class Executor:
    def __init__(self, max_workers=None, queue_size=1000, thread_name_prefix="PyFerris-Worker")
    def submit(self, fn, *args, **kwargs)
    def map(self, fn, iterable, chunksize=1)
    def shutdown(self, wait=True)
```

**Methods:**
- `submit(fn, *args, **kwargs)`: Submit a single task
- `map(fn, iterable, chunksize=1)`: Map function over iterable
- `shutdown(wait=True)`: Shutdown the executor

## I/O Module (`pyferris.io`)

### Simple I/O (`pyferris.io.simple_io`)

#### `read_file(path, encoding='utf-8', mode='r')` → `str|bytes`

Read a single file.

#### `write_file(path, content, encoding='utf-8', mode='w')`

Write content to a file.

#### `read_files_parallel(file_paths, encoding='utf-8')` → `List[str]`

Read multiple files in parallel.

#### `write_files_parallel(file_data, encoding='utf-8')`

Write multiple files in parallel.

**Parameters:**
- `file_data` (List[Tuple[str, str]]): List of (path, content) tuples

### CSV Operations (`pyferris.io.csv`)

#### `read_csv(path, delimiter=',', columns=None)` → `List[Dict]`

Read CSV file into list of dictionaries.

#### `write_csv(path, data, delimiter=',', columns=None, mode='w')`

Write data to CSV file.

#### `read_csv_chunked(path, chunk_size=10000, delimiter=',')` → `Iterator[List[Dict]]`

Read large CSV file in chunks.

### JSON Operations (`pyferris.io.json`)

#### `read_json(path)` → `Any`

Read JSON file.

#### `write_json(path, data, indent=None)`

Write data to JSON file.

#### `read_json_parallel(file_paths)` → `List[Any]`

Read multiple JSON files in parallel.

#### `write_json_parallel(file_data)`

Write multiple JSON files in parallel.

#### `read_jsonl(path)` → `List[Dict]`

Read JSON Lines format file.

#### `write_jsonl(path, records)`

Write records in JSON Lines format.

### Parallel I/O (`pyferris.io.parallel_io`)

#### `read_and_process_files(file_paths, process_function, progress=None)`

Read and process multiple files in parallel.

#### `process_files_in_batches(file_paths, process_function, batch_size=10)`

Process files in batches.

#### `read_file_stream(path, chunk_size=8192)` → `Iterator[str]`

Read large file as stream of chunks.

## Async Operations Module (`pyferris.async_ops`)

#### `AsyncExecutor`

Asynchronous task executor.

```python
class AsyncExecutor:
    def __init__(self, max_workers=None)
    async def submit(self, coro)
    async def map(self, coro_func, iterable)
    async def shutdown()
```

#### `async_parallel_map(coro_func, iterable, max_workers=None, progress=None)`

Asynchronous parallel map operation.

#### `async_parallel_filter(predicate, iterable, max_workers=None, progress=None)`

Asynchronous parallel filter operation.

#### `AsyncTask`

Wrapper for asynchronous tasks.

```python
class AsyncTask:
    def __init__(self, coro)
    async def result()
    def done()
    def cancel()
```

## Shared Memory Module (`pyferris.shared_memory`)

### Shared Arrays

#### `SharedArray`

Base class for shared arrays.

```python
class SharedArray:
    def __init__(self, data=None, size=None)
    def __getitem__(self, index)
    def __setitem__(self, index, value)
    def __len__()
    def to_list()
```

#### `SharedArrayInt`, `SharedArrayStr`, `SharedArrayObj`

Typed shared arrays for integers, strings, and objects respectively.

#### `create_shared_array(data, array_type='auto')` → `SharedArray`

Create a shared array from data.

### Shared Data Structures

#### `SharedDict`

Thread-safe shared dictionary.

```python
class SharedDict:
    def __init__(self, initial_data=None)
    def get(self, key, default=None)
    def put(self, key, value)
    def keys()
    def values()
    def items()
```

#### `SharedQueue`

Thread-safe shared queue.

```python
class SharedQueue:
    def __init__(self, maxsize=0)
    def put(self, item, block=True, timeout=None)
    def get(self, block=True, timeout=None)
    def empty()
    def full()
    def qsize()
```

#### `SharedCounter`

Thread-safe shared counter.

```python
class SharedCounter:
    def __init__(self, initial_value=0)
    def increment(self, amount=1)
    def decrement(self, amount=1)
    def value()
    def reset()
```

## Scheduler Module (`pyferris.scheduler`)

### Scheduler Classes

#### `WorkStealingScheduler`

Work-stealing task scheduler.

```python
class WorkStealingScheduler:
    def __init__(self, num_workers=None)
    def submit(self, task, priority=TaskPriority.NORMAL)
    def shutdown()
```

#### `RoundRobinScheduler`

Round-robin task scheduler.

#### `AdaptiveScheduler`

Adaptive task scheduler that adjusts based on workload.

#### `PriorityScheduler`

Priority-based task scheduler.

### Enums and Functions

#### `TaskPriority`

Enumeration for task priorities.

```python
class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
```

#### `execute_with_priority(func, args, priority=TaskPriority.NORMAL)`

Execute function with specified priority.

#### `create_priority_task(func, args, priority=TaskPriority.NORMAL)`

Create a priority task.

## Concurrent Module (`pyferris.concurrent`)

### Concurrent Data Structures

#### `ConcurrentHashMap`

Thread-safe hash map.

```python
class ConcurrentHashMap:
    def __init__(self, initial_capacity=16)
    def put(self, key, value)
    def get(self, key, default=None)
    def remove(self, key)
    def size()
```

#### `LockFreeQueue`

Lock-free queue implementation.

```python
class LockFreeQueue:
    def __init__(self)
    def enqueue(self, item)
    def dequeue()
    def is_empty()
```

#### `AtomicCounter`

Atomic counter for thread-safe counting.

```python
class AtomicCounter:
    def __init__(self, initial_value=0)
    def increment()
    def decrement()
    def get()
    def set(self, value)
```

#### `RwLockDict`

Reader-writer lock protected dictionary.

```python
class RwLockDict:
    def __init__(self)
    def read(self, key, default=None)
    def write(self, key, value)
    def read_all()
```

## Memory Module (`pyferris.memory`)

### Memory Management

#### `MemoryPool`

Memory pool for efficient allocation.

```python
class MemoryPool:
    def __init__(self, block_size=1024, initial_blocks=10)
    def allocate()
    def deallocate(self, block)
    def get_stats()
```

#### Memory-Mapped Arrays

#### `memory_mapped_array(size, dtype='float64', mode='w+')` → `MmapArray`

Create memory-mapped array.

#### `memory_mapped_array_2d(shape, dtype='float64', mode='w+')` → `MmapArray`

Create 2D memory-mapped array.

#### `memory_mapped_info(mmap_array)` → `Dict`

Get information about memory-mapped array.

#### `create_temp_mmap(size, dtype='float64')` → `MmapArray`

Create temporary memory-mapped array.

## Cache Module (`pyferris.cache`)

### Caching

#### `SmartCache`

Intelligent cache with configurable eviction policies.

```python
class SmartCache:
    def __init__(self, max_size=1000, policy=EvictionPolicy.LRU, ttl=None)
    def get(self, key, default=None)
    def put(self, key, value)
    def evict(self, key)
    def clear()
    def size()
    def hit_rate()
```

#### `EvictionPolicy`

Cache eviction policies.

```python
class EvictionPolicy(Enum):
    LRU = "lru"          # Least Recently Used
    LFU = "lfu"          # Least Frequently Used
    FIFO = "fifo"        # First In, First Out
    RANDOM = "random"    # Random eviction
    ADAPTIVE = "adaptive" # Adaptive policy
```

#### `cached(max_size=128, policy=EvictionPolicy.LRU, ttl=None)`

Decorator for function caching.

**Example:**
```python
@cached(max_size=100, policy=EvictionPolicy.LRU)
def expensive_function(x):
    return x ** 2
```

## Distributed Module (`pyferris.distributed`)

### Distributed Computing

#### `DistributedCluster`

Distributed computing cluster.

```python
class DistributedCluster:
    def __init__(self, nodes=None, coordinator_host='localhost', coordinator_port=8080)
    def add_node(self, host, port)
    def remove_node(self, node_id)
    def get_status()
    def shutdown()
```

#### `create_cluster(nodes=None, **kwargs)` → `DistributedCluster`

Create a distributed cluster.

#### `distributed_map(func, iterable, cluster=None, chunk_size=None)`

Distributed map operation.

#### `distributed_filter(predicate, iterable, cluster=None, chunk_size=None)`

Distributed filter operation.

#### `distributed_reduce(function, iterable, initial=None, cluster=None)`

Distributed reduce operation.

#### `async_distributed_map(coro_func, iterable, cluster=None)`

Asynchronous distributed map operation.

### Management Classes

#### `ClusterManager`

Manage distributed cluster operations.

#### `LoadBalancer`

Load balancing for distributed tasks.

#### `DistributedExecutor`

Executor for distributed task execution.

#### `DistributedBatchProcessor`

Batch processing across distributed nodes.

## Pipeline Module (`pyferris.pipeline`)

### Pipeline Operations

#### `Pipeline`

Chainable data processing pipeline.

```python
class Pipeline:
    def __init__(self, initial_data=None)
    def map(self, func, parallel=True)
    def filter(self, predicate, parallel=True)
    def reduce(self, function, initial=None)
    def sort(self, key=None, reverse=False)
    def group_by(self, key)
    def collect()
    def to_list()
```

#### `Chain`

Chain multiple operations together.

```python
class Chain:
    def __init__(self, operations=None)
    def add(self, operation)
    def execute(self, data)
```

#### `pipeline_map(pipeline, iterable)`

Apply pipeline to iterable.

## Error Classes

### `PyFerrisError`

Base exception class for PyFerris.

### `ExecutorError`

Exceptions related to executor operations.

### `MemoryError`

Exceptions related to memory operations.

### `IOError`

Exceptions related to I/O operations.

### `DistributedError`

Exceptions related to distributed operations.

## Type Hints

PyFerris includes comprehensive type hints. Import them as:

```python
from pyferris.types import (
    ParallelFunction,
    ReduceFunction,
    PredicateFunction,
    KeyFunction,
    ProcessFunction
)
```

## Constants and Enums

### Default Values

```python
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_WORKER_COUNT = os.cpu_count()
DEFAULT_QUEUE_SIZE = 1000
DEFAULT_CACHE_SIZE = 1000
```

### Configuration Constants

```python
MAX_WORKERS = 128
MIN_CHUNK_SIZE = 1
MAX_CHUNK_SIZE = 100000
DEFAULT_TIMEOUT = 300  # seconds
```

This API reference provides a comprehensive overview of all PyFerris functionality. For detailed examples and usage patterns, see the specific module documentation and the [Examples](examples.md) section.
