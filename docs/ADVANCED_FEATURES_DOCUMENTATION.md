# Pyferris Advanced Features Documentation

## Table of Contents
1. [Overview](#overview)
2. [Concurrent Data Structures](#concurrent-data-structures)
3. [Memory Management](#memory-management)
4. [Performance Profiling](#performance-profiling)
5. [Dynamic Load Balancing](#dynamic-load-balancing)
6. [Installation & Setup](#installation--setup)
7. [API Reference](#api-reference)
8. [Performance Guidelines](#performance-guidelines)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Overview

Pyferris Advanced Features provide sophisticated capabilities for high-performance computing, concurrent programming, and memory-intensive applications. These features are designed for production environments requiring:

- **Thread-safe concurrent operations**
- **Efficient memory management for large datasets**
- **Comprehensive performance monitoring**
- **Automatic optimization capabilities**

### Key Benefits
- 🚀 **High Performance**: Lock-free data structures and optimized memory management
- 🔒 **Thread Safety**: All concurrent operations are guaranteed thread-safe
- 📊 **Observability**: Detailed profiling and performance metrics
- ⚖️ **Auto-Optimization**: Automatic worker tuning for optimal throughput
- 💾 **Memory Efficiency**: Memory pools and memory-mapped arrays for large datasets

## Concurrent Data Structures

### ConcurrentHashMap

A thread-safe hash map that allows concurrent reads and writes without blocking.

#### Features
- Based on DashMap for high-performance concurrent access
- Automatic sharding for reduced contention
- Thread-safe operations without explicit locking

#### Basic Usage
```python
from pyferris import ConcurrentHashMap

# Create a concurrent hash map
hashmap = ConcurrentHashMap()

# Thread-safe operations
hashmap.insert("user_1", {"name": "Alice", "score": 100})
hashmap.insert("user_2", {"name": "Bob", "score": 85})

# Concurrent reads (safe from multiple threads)
user_data = hashmap.get("user_1")
print(f"User data: {user_data}")

# Check existence
if hashmap.contains_key("user_1"):
    print("User exists")

# Get all keys and values
all_keys = hashmap.keys()
all_values = hashmap.values()
all_items = hashmap.items()

# Update from another dictionary
update_data = {"user_3": {"name": "Charlie", "score": 95}}
hashmap.update(update_data)

# Atomic operations
existing_value = hashmap.get_or_insert("user_4", {"name": "David", "score": 75})
```

#### Advanced Usage
```python
import threading
from concurrent.futures import ThreadPoolExecutor

# Thread-safe concurrent operations
def worker(worker_id):
    for i in range(1000):
        key = f"worker_{worker_id}_item_{i}"
        value = {"worker": worker_id, "item": i, "timestamp": time.time()}
        hashmap.insert(key, value)

# Run multiple workers concurrently
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(worker, i) for i in range(8)]
    for future in futures:
        future.result()

print(f"Total items: {len(hashmap)}")  # 8000 items
```

### LockFreeQueue

A high-performance, lock-free FIFO queue for producer-consumer scenarios.

#### Features
- Lock-free implementation using atomic operations
- FIFO (First In, First Out) ordering
- High throughput with minimal contention

#### Basic Usage
```python
from pyferris import LockFreeQueue

# Create a lock-free queue
queue = LockFreeQueue()

# Producer operations
queue.push("task_1")
queue.push("task_2")
queue.push("task_3")

print(f"Queue size: {len(queue)}")  # 3

# Consumer operations
task = queue.pop()  # Returns "task_1"
print(f"Processing: {task}")

# Check if empty
if not queue.is_empty():
    next_task = queue.pop()
```

#### Producer-Consumer Pattern
```python
import threading
import time

# Shared queue
task_queue = LockFreeQueue()
results_queue = LockFreeQueue()

def producer(num_tasks):
    """Produce tasks and add them to the queue"""
    for i in range(num_tasks):
        task = f"task_{i}_{time.time()}"
        task_queue.push(task)
        time.sleep(0.01)  # Simulate work

def consumer(consumer_id):
    """Consume tasks from the queue"""
    processed = 0
    while processed < 100:  # Process 100 tasks
        task = task_queue.pop()
        if task is not None:
            # Process the task
            result = f"result_for_{task}_by_consumer_{consumer_id}"
            results_queue.push(result)
            processed += 1
        else:
            time.sleep(0.001)  # Brief pause if no tasks

# Start producer and consumers
producer_thread = threading.Thread(target=producer, args=(1000,))
consumer_threads = [
    threading.Thread(target=consumer, args=(i,)) 
    for i in range(4)
]

producer_thread.start()
for t in consumer_threads:
    t.start()

# Wait for completion
producer_thread.join()
for t in consumer_threads:
    t.join()

print(f"Results produced: {len(results_queue)}")
```

### AtomicCounter

Thread-safe counter with atomic operations for concurrent incrementing/decrementing.

#### Features
- Atomic operations for thread safety
- Compare-and-swap functionality
- High-performance increment/decrement operations

#### Basic Usage
```python
from pyferris import AtomicCounter

# Create an atomic counter
counter = AtomicCounter(initial_value=0)

# Basic operations
counter.increment()  # Atomically increment by 1
counter.decrement()  # Atomically decrement by 1
counter.add(5)       # Add 5 atomically
counter.sub(2)       # Subtract 2 atomically

current_value = counter.get()
print(f"Current value: {current_value}")  # 4

# Set new value
counter.set(100)

# Compare and swap (atomic conditional update)
old_value = counter.compare_and_swap(expected=100, new=200)
if old_value == 100:
    print("Successfully updated to 200")
```

#### Concurrent Counting
```python
import threading

# Shared counter
shared_counter = AtomicCounter()
iterations = 100000

def increment_worker():
    """Worker that increments the counter many times"""
    for _ in range(iterations):
        shared_counter.increment()

def decrement_worker():
    """Worker that decrements the counter many times"""
    for _ in range(iterations // 2):
        shared_counter.decrement()

# Start multiple threads
threads = []
for _ in range(4):
    threads.append(threading.Thread(target=increment_worker))
for _ in range(2):
    threads.append(threading.Thread(target=decrement_worker))

# Run all threads
for t in threads:
    t.start()
for t in threads:
    t.join()

# Final value should be: (4 * 100000) - (2 * 50000) = 300000
print(f"Final counter value: {shared_counter.get()}")
```

### RwLockDict

A dictionary protected by a reader-writer lock, allowing concurrent reads but exclusive writes.

#### Features
- Multiple concurrent readers
- Exclusive writer access
- Deadlock-free implementation
- Dictionary-like interface

#### Basic Usage
```python
from pyferris import RwLockDict

# Create an RwLock-protected dictionary
rwdict = RwLockDict()

# Write operations (exclusive access)
rwdict.insert("config", {"timeout": 30, "retries": 3})
rwdict.insert("stats", {"requests": 0, "errors": 0})

# Read operations (concurrent access allowed)
config = rwdict.get("config")
all_keys = rwdict.keys()
all_values = rwdict.values()
all_items = rwdict.items()

# Check operations
if rwdict.contains_key("config"):
    print("Config exists")

# Update operations
updates = {"metrics": {"cpu": 45.2, "memory": 67.8}}
rwdict.update(updates)

# Remove operations
old_value = rwdict.remove("stats")
```

## Memory Management

### MemoryPool

Pre-allocated memory blocks for efficient allocation and deallocation patterns.

#### Features
- Reduces allocation overhead
- Prevents memory fragmentation
- Configurable block size and pool size
- Thread-safe operations

#### Basic Usage
```python
from pyferris import MemoryPool

# Create a memory pool
pool = MemoryPool(block_size=1024, max_blocks=1000)

# Allocate memory blocks
block1 = pool.allocate()  # Returns a 1024-byte bytearray
block2 = pool.allocate()

print(f"Block size: {len(block1)}")  # 1024

# Use the blocks
block1[0:10] = b"Hello Pool"
print(block1[0:10])  # b'Hello Pool'

# Return blocks to the pool
pool.deallocate(block1)
pool.deallocate(block2)

# Get pool statistics
stats = pool.stats()
print(f"Pool stats: {stats}")
```

#### High-Frequency Allocation Pattern
```python
import time

# Pool for frequent allocations
message_pool = MemoryPool(block_size=512, max_blocks=10000)

def process_messages(num_messages):
    """Simulate processing many messages with temporary buffers"""
    start_time = time.time()
    
    for i in range(num_messages):
        # Allocate buffer for message processing
        buffer = message_pool.allocate()
        
        # Simulate message processing
        message = f"Message {i}".encode('utf-8')
        buffer[0:len(message)] = message
        
        # Process the message...
        
        # Return buffer to pool
        message_pool.deallocate(buffer)
    
    end_time = time.time()
    print(f"Processed {num_messages} messages in {end_time - start_time:.2f}s")

# Process messages efficiently
process_messages(50000)
```

### Memory-Mapped Arrays

File-backed arrays for working with datasets larger than available RAM.

#### Features
- Work with datasets larger than RAM
- Persistent storage automatically handled
- NumPy-compatible interface
- Efficient random access

#### 1D Memory-Mapped Arrays
```python
from pyferris import memory_mapped_array
import tempfile
import os

# Create a temporary file for the array
with tempfile.NamedTemporaryFile(delete=False) as f:
    filepath = f.name

try:
    # Create a large memory-mapped array
    arr = memory_mapped_array(
        filepath=filepath,
        size=10_000_000,  # 10 million elements
        dtype="float64",
        mode="w+"
    )
    
    print(f"Array shape: {arr.shape}")        # (10000000,)
    print(f"Array dtype: {arr.dtype}")        # float64
    
    # Use like a regular numpy array
    arr[0:1000] = range(1000)
    arr[1000:2000] = [x * x for x in range(1000)]
    
    # Random access
    print(f"Element 500: {arr[500]}")         # 500.0
    print(f"Element 1500: {arr[1500]}")       # 250000.0
    
    # Changes are automatically persisted to disk
    
finally:
    # Cleanup
    del arr
    os.unlink(filepath)
```

#### 2D Memory-Mapped Arrays
```python
from pyferris import memory_mapped_array_2d
import tempfile
import os

# Create a temporary file
with tempfile.NamedTemporaryFile(delete=False) as f:
    filepath = f.name

try:
    # Create a 2D memory-mapped array
    matrix = memory_mapped_array_2d(
        filepath=filepath,
        shape=(5000, 2000),  # 5000 x 2000 matrix
        dtype="float32",
        mode="w+"
    )
    
    print(f"Matrix shape: {matrix.shape}")    # (5000, 2000)
    print(f"Matrix dtype: {matrix.dtype}")    # float32
    
    # Initialize data
    matrix[0, :] = range(2000)              # First row
    matrix[:, 0] = range(5000)              # First column
    
    # Set specific regions
    matrix[100:200, 100:200] = 42.0         # 100x100 block
    
    # Access patterns
    print(f"First row sum: {matrix[0, :].sum()}")
    print(f"First column mean: {matrix[:, 0].mean()}")
    
finally:
    # Cleanup
    del matrix
    os.unlink(filepath)
```

#### Temporary Memory-Mapped Arrays
```python
from pyferris import create_temp_mmap
import os

# Create temporary memory-mapped array
result = create_temp_mmap(
    size=1_000_000,
    dtype="int32",
    prefix="data_processing_"
)

temp_array = result['array']
temp_filepath = result['filepath']

print(f"Temporary file: {temp_filepath}")
print(f"Array shape: {temp_array.shape}")

# Use the array
temp_array[:10000] = range(10000)
temp_array[10000:20000] = [x * 2 for x in range(10000)]

# Process data...
processed_sum = temp_array[:20000].sum()
print(f"Processed sum: {processed_sum}")

# Cleanup when done
del temp_array
os.unlink(temp_filepath)
```

## Performance Profiling

### Profiler Class

Comprehensive performance monitoring for CPU, memory, and operation timing.

#### Features
- High-resolution timing
- Memory usage tracking
- Performance counters
- Context managers and decorators
- Comprehensive reporting

#### Basic Timing
```python
from pyferris import Profiler
import time

profiler = Profiler()

# Manual timing
profiler.start()
profiler.start_timer("database_query")

# Simulate database operation
time.sleep(0.1)

query_time = profiler.stop_timer("database_query")
total_time = profiler.stop()

print(f"Query time: {query_time:.3f}s")
print(f"Total time: {total_time:.3f}s")
```

#### Context Manager Usage
```python
from pyferris import Profiler
import time

profiler = Profiler()

# Using context manager for timing
with profiler.timer("data_processing"):
    # Simulate data processing
    time.sleep(0.05)
    
    with profiler.timer("computation"):
        # Nested timing
        time.sleep(0.02)
    
    with profiler.timer("io_operations"):
        # Another nested operation
        time.sleep(0.01)

# Get timing results
timings = profiler.get_timings()
for operation, duration in timings.items():
    print(f"{operation}: {duration:.3f}s")
```

#### Function Decorator
```python
from pyferris import Profiler

profiler = Profiler()

@profiler.profile_function("fibonacci")
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

@profiler.profile_function("factorial")
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

# Use the functions
result1 = fibonacci(30)
result2 = factorial(100)

# Get comprehensive report
report = profiler.get_report()
print(f"Timing data: {report['timings']}")
print(f"Counters: {report['counters']}")
```

#### Memory and Counter Tracking
```python
from pyferris import Profiler
import sys

profiler = Profiler()

def process_large_dataset(size):
    profiler.start_timer("allocation")
    
    # Track memory allocation
    data = list(range(size))
    memory_used = sys.getsizeof(data)
    profiler.record_memory("dataset_allocation", memory_used)
    
    profiler.stop_timer("allocation")
    
    profiler.start_timer("processing")
    
    # Process data and track operations
    processed = []
    for i, item in enumerate(data):
        if i % 1000 == 0:
            profiler.increment_counter("batch_processed")
        
        processed.append(item * 2)
    
    profiler.stop_timer("processing")
    
    profiler.increment_counter("datasets_processed")
    
    return processed

# Process multiple datasets
for size in [10000, 50000, 100000]:
    result = process_large_dataset(size)

# Get comprehensive metrics
print("Timing Results:")
for operation, time_taken in profiler.get_timings().items():
    print(f"  {operation}: {time_taken:.3f}s")

print("\nMemory Usage:")
for operation, bytes_used in profiler.get_memory_usage().items():
    print(f"  {operation}: {bytes_used / 1024:.2f} KB")

print("\nCounters:")
for counter, value in profiler.get_counters().items():
    print(f"  {counter}: {value}")
```

### Profiling Parallel Operations

Profile any parallel operation with automatic metrics collection.

#### Basic Usage
```python
from pyferris import profile_parallel_operation, parallel_map

def expensive_operation(x):
    """Simulate CPU-intensive work"""
    return sum(i * i for i in range(x * 100))

# Profile parallel execution
data = range(1000)
results, report = profile_parallel_operation(
    parallel_map,
    expensive_operation, 
    data,
    operation_name="parallel_computation"
)

print(f"Results count: {len(list(results))}")
print(f"Timing data: {report['timings']}")
print(f"Memory usage: {report['memory_usage']}")
print(f"Counters: {report['counters']}")
```

## Dynamic Load Balancing

### Auto-Tune Workers

Automatically determine the optimal number of workers for maximum throughput.

#### Features
- Automatic benchmarking across worker counts
- Throughput optimization
- Hardware-aware configuration
- Performance reporting

#### Basic Usage
```python
from pyferris import auto_tune_workers

def cpu_intensive_task(x):
    """Simulate CPU-bound work"""
    return sum(i * i for i in range(x * 1000))

# Sample data for benchmarking
sample_data = list(range(10, 100))

# Auto-tune for optimal performance
result = auto_tune_workers(
    task_function=cpu_intensive_task,
    sample_data=sample_data,
    test_duration=2.0  # Test each configuration for 2 seconds
)

print(f"Optimal workers: {result['optimal_workers']}")
print(f"Best throughput: {result['best_throughput']:.2f} items/sec")
print(f"Tested configurations: {result['tested_workers']}")

# Use the optimal configuration
from pyferris import set_worker_count
set_worker_count(result['optimal_workers'])
```

#### Advanced Configuration
```python
from pyferris import auto_tune_workers
import multiprocessing

def io_bound_task(x):
    """Simulate I/O-bound work"""
    import time
    time.sleep(0.001)  # Simulate I/O delay
    return x * 2

# Custom worker range for I/O-bound tasks
cpu_count = multiprocessing.cpu_count()

result = auto_tune_workers(
    task_function=io_bound_task,
    sample_data=list(range(100)),
    min_workers=1,
    max_workers=cpu_count * 4,  # I/O-bound can benefit from more workers
    test_duration=1.0
)

print(f"For I/O-bound tasks:")
print(f"  CPU cores: {cpu_count}")
print(f"  Optimal workers: {result['optimal_workers']}")
print(f"  Worker/Core ratio: {result['optimal_workers'] / cpu_count:.1f}")
print(f"  Best throughput: {result['best_throughput']:.2f} items/sec")
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Rust 1.70+ (for building from source)
- NumPy (for memory-mapped arrays)

### Installation
```bash
# Install from PyPI (when available)
pip install pyferris

# Or install from source
git clone https://github.com/DVNghiem/Pyferris.git
cd Pyferris
pip install maturin
maturin develop

# Install optional dependencies
pip install numpy  # For memory-mapped arrays
```

### Verification
```python
# Test advanced features
from pyferris import (
    ConcurrentHashMap, LockFreeQueue, AtomicCounter, RwLockDict,
    MemoryPool, memory_mapped_array, Profiler, auto_tune_workers
)

# Quick functionality test
hashmap = ConcurrentHashMap()
hashmap.insert("test", "success")
print(f"Advanced features available: {hashmap.get('test')}")
```

## API Reference

### Concurrent Data Structures

#### ConcurrentHashMap
```python
class ConcurrentHashMap:
    def __init__(self) -> None
    def insert(self, key: str, value: Any) -> Optional[Any]
    def get(self, key: str) -> Optional[Any]
    def remove(self, key: str) -> Optional[Any]
    def contains_key(self, key: str) -> bool
    def keys(self) -> List[str]
    def values(self) -> List[Any]
    def items(self) -> List[Tuple[str, Any]]
    def update(self, other: Dict[str, Any]) -> None
    def get_or_default(self, key: str, default: Any) -> Any
    def get_or_insert(self, key: str, value: Any) -> Any
    def is_empty(self) -> bool
    def clear(self) -> None
    def shard_count(self) -> int
    def __len__(self) -> int
    def __contains__(self, key: str) -> bool
    def __getitem__(self, key: str) -> Any
    def __setitem__(self, key: str, value: Any) -> None
    def __delitem__(self, key: str) -> None
```

#### LockFreeQueue
```python
class LockFreeQueue:
    def __init__(self) -> None
    def push(self, item: Any) -> None
    def pop(self) -> Optional[Any]
    def is_empty(self) -> bool
    def clear(self) -> None
    def __len__(self) -> int
```

#### AtomicCounter
```python
class AtomicCounter:
    def __init__(self, initial_value: int = 0) -> None
    def get(self) -> int
    def set(self, value: int) -> None
    def increment(self) -> int
    def decrement(self) -> int
    def add(self, value: int) -> int
    def sub(self, value: int) -> int
    def compare_and_swap(self, expected: int, new: int) -> int
    def reset(self) -> None
    def __int__(self) -> int
    def __add__(self, other: int) -> int
    def __sub__(self, other: int) -> int
```

#### RwLockDict
```python
class RwLockDict:
    def __init__(self) -> None
    def get(self, key: str) -> Optional[Any]
    def insert(self, key: str, value: Any) -> Optional[Any]
    def remove(self, key: str) -> Optional[Any]
    def contains_key(self, key: str) -> bool
    def keys(self) -> List[str]
    def values(self) -> List[Any]
    def items(self) -> List[Tuple[str, Any]]
    def update(self, other: Dict[str, Any]) -> None
    def get_or_default(self, key: str, default: Any) -> Any
    def is_empty(self) -> bool
    def clear(self) -> None
    def __len__(self) -> int
```

### Memory Management

#### MemoryPool
```python
class MemoryPool:
    def __init__(self, block_size: int, max_blocks: int) -> None
    def allocate(self) -> bytearray
    def deallocate(self, block: bytearray) -> None
    def clear(self) -> None
    def stats(self) -> Dict[str, int]
    @property
    def block_size(self) -> int
    @property
    def max_blocks(self) -> int
    def available_blocks(self) -> int
    def allocated_blocks(self) -> int
```

#### Memory-Mapped Functions
```python
def memory_mapped_array(
    filepath: str,
    size: int,
    dtype: str = "float64",
    mode: str = "r+"
) -> Any

def memory_mapped_array_2d(
    filepath: str,
    shape: Tuple[int, int],
    dtype: str = "float64",
    mode: str = "r+"
) -> Any

def create_temp_mmap(
    size: int,
    dtype: str = "float64",
    prefix: Optional[str] = None
) -> Dict[str, Any]

def memory_mapped_info(filepath: str) -> Dict[str, Any]
```

### Performance Profiling

#### Profiler
```python
class Profiler:
    def __init__(self) -> None
    def start(self) -> None
    def stop(self) -> Optional[float]
    def start_timer(self, name: str) -> None
    def stop_timer(self, name: str) -> float
    def record_memory(self, name: str, bytes_used: int) -> None
    def increment_counter(self, name: str, value: int = 1) -> None
    def get_timings(self) -> Dict[str, float]
    def get_memory_usage(self) -> Dict[str, int]
    def get_counters(self) -> Dict[str, int]
    def get_report(self) -> Dict[str, Any]
    def clear(self) -> None
    def timer(self, name: str) -> ContextManager
    def profile_function(self, name: Optional[str] = None) -> Decorator
```

#### Profiling Functions
```python
def profile_parallel_operation(
    operation_func: Callable,
    *args,
    profiler: Optional[Profiler] = None,
    operation_name: str = "parallel_operation",
    **kwargs
) -> Tuple[Any, Dict[str, Any]]

def auto_tune_workers(
    task_function: Callable,
    sample_data: List[Any],
    min_workers: Optional[int] = None,
    max_workers: Optional[int] = None,
    test_duration: float = 1.0
) -> Dict[str, Any]
```

## Performance Guidelines

### When to Use Each Feature

#### ConcurrentHashMap
- **Best for**: High-frequency read/write operations with many threads
- **Avoid when**: Single-threaded access or infrequent updates
- **Performance**: O(1) average access time, scales well with cores

#### LockFreeQueue
- **Best for**: Producer-consumer patterns, high-throughput scenarios
- **Avoid when**: Need ordering guarantees beyond FIFO
- **Performance**: Lock-free, minimal contention, excellent scalability

#### AtomicCounter
- **Best for**: Shared counters, statistics collection, simple coordination
- **Avoid when**: Complex state management needed
- **Performance**: CPU cache-friendly, very fast atomic operations

#### RwLockDict
- **Best for**: Read-heavy workloads with occasional writes
- **Avoid when**: Write-heavy or balanced read/write patterns
- **Performance**: Excellent for read-heavy scenarios, write operations are exclusive

#### MemoryPool
- **Best for**: Frequent allocation/deallocation of same-sized blocks
- **Avoid when**: Variable block sizes or infrequent allocations
- **Performance**: Eliminates allocation overhead, reduces GC pressure

#### Memory-Mapped Arrays
- **Best for**: Large datasets, persistence, memory-efficient processing
- **Avoid when**: Small datasets that fit in RAM
- **Performance**: OS-level optimization, minimal memory footprint

## Best Practices

### Thread Safety
```python
# ✅ Good: Use concurrent data structures
shared_data = ConcurrentHashMap()
counter = AtomicCounter()

def worker():
    shared_data.insert("key", "value")  # Thread-safe
    counter.increment()                 # Thread-safe

# ❌ Bad: Regular data structures in concurrent code
shared_dict = {}  # Not thread-safe
shared_count = 0  # Not thread-safe
```

### Memory Management
```python
# ✅ Good: Reuse memory pools
pool = MemoryPool(1024, 1000)

def process_item(item):
    buffer = pool.allocate()
    try:
        # Process with buffer
        result = do_work(buffer, item)
        return result
    finally:
        pool.deallocate(buffer)  # Always return to pool

# ❌ Bad: Frequent allocations
def process_item_bad(item):
    buffer = bytearray(1024)  # New allocation every time
    return do_work(buffer, item)
```

### Error Handling
```python
# ✅ Good: Proper cleanup in error cases
from pyferris import MemoryPool, Profiler

pool = MemoryPool(1024, 100)
profiler = Profiler()

def safe_processing(data):
    buffer = None
    try:
        profiler.start_timer("processing")
        buffer = pool.allocate()
        
        # Your processing logic
        result = process_data(buffer, data)
        
        profiler.increment_counter("success")
        return result
        
    except Exception as e:
        profiler.increment_counter("error")
        raise
    finally:
        if buffer is not None:
            pool.deallocate(buffer)
        profiler.stop_timer("processing")
```

## Troubleshooting

### Common Issues

#### Memory Pool Exhaustion
```python
# Problem: Pool runs out of blocks
pool = MemoryPool(1024, 10)  # Only 10 blocks

# Solution: Monitor and size appropriately
pool = MemoryPool(1024, 100)  # More blocks
stats = pool.stats()
if stats['available_blocks'] < 5:
    print("Warning: Pool running low")
```

#### High Contention
```python
# Problem: Many threads contending for same resource
shared_counter = AtomicCounter()  # High contention point

# Solution: Use per-thread counters and combine
import threading

thread_local = threading.local()

def get_local_counter():
    if not hasattr(thread_local, 'counter'):
        thread_local.counter = AtomicCounter()
    return thread_local.counter

# Combine periodically
def get_total_count():
    return sum(counter.get() for counter in all_thread_counters)
```

### Performance Issues

#### Suboptimal Worker Count
```python
# Problem: Manual worker configuration
workers = 4  # Might not be optimal

# Solution: Use auto-tuning
result = auto_tune_workers(your_task, sample_data)
optimal_workers = result['optimal_workers']
print(f"Optimal workers: {optimal_workers} (was using {workers})")
```

#### Memory Leaks
```python
# Problem: Not releasing memory-mapped arrays
def process_data():
    arr = memory_mapped_array("data.bin", 1000000)
    # Process data
    # Missing: del arr or proper cleanup

# Solution: Use context managers or explicit cleanup
def process_data_safe():
    arr = memory_mapped_array("data.bin", 1000000)
    try:
        # Process data
        return process(arr)
    finally:
        del arr  # Ensure cleanup
```

### Debugging Tips

#### Enable Detailed Profiling
```python
# Use comprehensive profiling for debugging
profiler = Profiler()

@profiler.profile_function()
def debug_function():
    with profiler.timer("step_1"):
        step_1()
    
    with profiler.timer("step_2"):
        step_2()
    
    with profiler.timer("step_3"):
        step_3()

debug_function()

# Analyze bottlenecks
timings = profiler.get_timings()
bottleneck = max(timings.items(), key=lambda x: x[1])
print(f"Bottleneck: {bottleneck[0]} ({bottleneck[1]:.3f}s)")
```

---

This documentation provides comprehensive coverage of all advanced features with practical examples and best practices for production use.
