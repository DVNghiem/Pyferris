# Executor

The PyFerris Executor provides advanced task execution and thread pool management capabilities, going beyond simple parallel operations to offer fine-grained control over task execution, scheduling, and resource management.

## Overview

The Executor module provides:
- Advanced thread pool management
- Task submission and execution control
- Future-based result handling
- Resource management and cleanup
- Performance tuning capabilities

## Basic Usage

### Creating an Executor

```python
from pyferris.executor import Executor

# Basic executor with default settings
executor = Executor()

# Executor with custom configuration
executor = Executor(
    max_workers=8,          # Number of worker threads
    queue_size=1000,        # Task queue size
    thread_name_prefix="PyFerris-Worker"
)
```

### Context Manager Usage

```python
from pyferris.executor import Executor

# Recommended: Use as context manager for automatic cleanup
with Executor(max_workers=4) as executor:
    future = executor.submit(expensive_function, data)
    result = future.result()
    print(f"Result: {result}")
# Executor is automatically shut down when exiting context
```

## Task Submission

### Single Task Submission

```python
from pyferris.executor import Executor
import time

def cpu_intensive_task(n):
    """Simulate CPU-intensive work."""
    total = 0
    for i in range(n):
        total += i * i
    return total

with Executor(max_workers=4) as executor:
    # Submit a single task
    future = executor.submit(cpu_intensive_task, 1000000)
    
    # Get the result (blocks until completion)
    result = future.result()
    print(f"Task result: {result}")
    
    # Check if task is done
    future2 = executor.submit(cpu_intensive_task, 500000)
    if future2.done():
        print("Task completed immediately")
    else:
        print("Task still running...")
        result2 = future2.result(timeout=10)  # Wait up to 10 seconds
```

### Multiple Task Submission

```python
from pyferris.executor import Executor

def process_item(item):
    return item * item

data = range(100)

with Executor(max_workers=4) as executor:
    # Submit multiple tasks
    futures = [executor.submit(process_item, item) for item in data]
    
    # Collect results as they complete
    results = [future.result() for future in futures]
    print(f"Processed {len(results)} items")
```

### Map Operation

```python
from pyferris.executor import Executor

def transform_data(x):
    return x * 2 + 1

data = range(1000)

with Executor(max_workers=4) as executor:
    # Map operation (similar to parallel_map but with more control)
    results = list(executor.map(transform_data, data))
    print(f"Transformed {len(results)} items")
    
    # Map with custom chunk size
    results = list(executor.map(transform_data, data, chunksize=50))
```

## Advanced Features

### Task Callbacks

```python
from pyferris.executor import Executor

def process_data(x):
    return x ** 2

def success_callback(future):
    result = future.result()
    print(f"Task completed successfully: {result}")

def error_callback(future):
    try:
        future.result()
    except Exception as e:
        print(f"Task failed with error: {e}")

with Executor(max_workers=4) as executor:
    future = executor.submit(process_data, 10)
    
    # Add callbacks
    future.add_done_callback(success_callback)
    future.add_done_callback(error_callback)
    
    # Wait for completion
    future.result()
```

### Task Prioritization

```python
from pyferris.executor import Executor
from pyferris.scheduler import TaskPriority

def high_priority_task():
    return "Important result"

def low_priority_task():
    return "Less important result"

with Executor(max_workers=4) as executor:
    # Submit tasks with different priorities
    high_future = executor.submit(
        high_priority_task, 
        priority=TaskPriority.HIGH
    )
    
    low_future = executor.submit(
        low_priority_task, 
        priority=TaskPriority.LOW
    )
    
    # High priority task will be executed first
    results = [high_future.result(), low_future.result()]
```

### Batch Task Submission

```python
from pyferris.executor import Executor

def batch_processor(batch):
    """Process a batch of items."""
    return [item * 2 for item in batch]

def create_batches(data, batch_size):
    """Split data into batches."""
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

data = list(range(10000))
batch_size = 100

with Executor(max_workers=4) as executor:
    # Submit batch processing tasks
    futures = []
    for batch in create_batches(data, batch_size):
        future = executor.submit(batch_processor, batch)
        futures.append(future)
    
    # Collect all results
    all_results = []
    for future in futures:
        batch_results = future.result()
        all_results.extend(batch_results)
    
    print(f"Processed {len(all_results)} items in batches")
```

## Resource Management

### Memory Management

```python
from pyferris.executor import Executor
import gc

def memory_intensive_task(size):
    """Task that uses significant memory."""
    data = list(range(size))
    result = sum(data)
    del data  # Explicit cleanup
    return result

with Executor(max_workers=2) as executor:  # Fewer workers for memory-intensive tasks
    futures = []
    
    for i in range(10):
        future = executor.submit(memory_intensive_task, 1000000)
        futures.append(future)
        
        # Process results immediately to free memory
        if len(futures) >= 2:
            for f in futures[:2]:
                result = f.result()
                print(f"Processed: {result}")
            futures = futures[2:]
            gc.collect()  # Force garbage collection
    
    # Process remaining futures
    for future in futures:
        result = future.result()
        print(f"Final result: {result}")
```

### Timeout Management

```python
from pyferris.executor import Executor
import time
from concurrent.futures import TimeoutError

def slow_task(duration):
    time.sleep(duration)
    return f"Completed after {duration} seconds"

with Executor(max_workers=4) as executor:
    # Submit tasks with different durations
    fast_future = executor.submit(slow_task, 1)
    slow_future = executor.submit(slow_task, 10)
    
    try:
        # Get fast result
        fast_result = fast_future.result(timeout=2)
        print(f"Fast task: {fast_result}")
        
        # Try to get slow result with timeout
        slow_result = slow_future.result(timeout=3)
        print(f"Slow task: {slow_result}")
        
    except TimeoutError:
        print("Slow task timed out")
        # Cancel the slow task if possible
        if slow_future.cancel():
            print("Slow task cancelled")
        else:
            print("Slow task already running, cannot cancel")
```

## Performance Tuning

### Optimal Worker Count

```python
from pyferris.executor import Executor
import os
import time

def cpu_bound_task(n):
    return sum(i * i for i in range(n))

def benchmark_executor(max_workers, task_count=100):
    start_time = time.time()
    
    with Executor(max_workers=max_workers) as executor:
        futures = [executor.submit(cpu_bound_task, 10000) for _ in range(task_count)]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    return end_time - start_time

# Test different worker counts
cpu_count = os.cpu_count()
worker_counts = [1, 2, 4, cpu_count, cpu_count * 2]

print("Worker Count | Execution Time")
print("-" * 30)
for workers in worker_counts:
    execution_time = benchmark_executor(workers)
    print(f"{workers:11d} | {execution_time:.2f}s")
```

### Chunk Size Optimization

```python
from pyferris.executor import Executor
import time

def simple_task(x):
    return x * 2

def benchmark_chunk_size(chunk_size, data_size=10000):
    data = range(data_size)
    start_time = time.time()
    
    with Executor(max_workers=4) as executor:
        results = list(executor.map(simple_task, data, chunksize=chunk_size))
    
    end_time = time.time()
    return end_time - start_time

# Test different chunk sizes
chunk_sizes = [1, 10, 50, 100, 500, 1000]

print("Chunk Size | Execution Time")
print("-" * 25)
for chunk_size in chunk_sizes:
    execution_time = benchmark_chunk_size(chunk_size)
    print(f"{chunk_size:9d} | {execution_time:.3f}s")
```

### Custom Executor Configuration

```python
from pyferris.executor import Executor

class OptimizedExecutor:
    def __init__(self, workload_type='cpu'):
        if workload_type == 'cpu':
            # CPU-bound workload configuration
            self.max_workers = os.cpu_count()
            self.queue_size = 100
            self.chunk_size = 1
        elif workload_type == 'io':
            # I/O-bound workload configuration
            self.max_workers = os.cpu_count() * 4
            self.queue_size = 1000
            self.chunk_size = 10
        elif workload_type == 'memory':
            # Memory-intensive workload configuration
            self.max_workers = max(1, os.cpu_count() // 2)
            self.queue_size = 50
            self.chunk_size = 1
    
    def create_executor(self):
        return Executor(
            max_workers=self.max_workers,
            queue_size=self.queue_size
        )

# Usage
cpu_executor_config = OptimizedExecutor('cpu')
with cpu_executor_config.create_executor() as executor:
    # Execute CPU-bound tasks
    pass

io_executor_config = OptimizedExecutor('io')
with io_executor_config.create_executor() as executor:
    # Execute I/O-bound tasks
    pass
```

## Integration with Other PyFerris Components

### With Shared Memory

```python
from pyferris.executor import Executor
from pyferris.shared_memory import SharedArray

def process_shared_data(shared_array, start_idx, end_idx):
    """Process a slice of shared array."""
    total = 0
    for i in range(start_idx, end_idx):
        total += shared_array[i] * 2
    return total

# Create shared array
data = list(range(10000))
shared_arr = SharedArray(data)

with Executor(max_workers=4) as executor:
    # Divide work among workers
    chunk_size = len(data) // 4
    futures = []
    
    for i in range(4):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < 3 else len(data)
        future = executor.submit(process_shared_data, shared_arr, start_idx, end_idx)
        futures.append(future)
    
    # Collect results
    results = [future.result() for future in futures]
    total_result = sum(results)
    print(f"Total result: {total_result}")
```

### With Cache

```python
from pyferris.executor import Executor
from pyferris.cache import SmartCache, EvictionPolicy

# Global cache for expensive computations
computation_cache = SmartCache(max_size=1000, policy=EvictionPolicy.LRU)

def expensive_computation(n):
    """Expensive computation with caching."""
    cache_key = f"comp_{n}"
    
    # Check cache first
    cached_result = computation_cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Perform computation
    result = sum(i * i for i in range(n))
    
    # Cache the result
    computation_cache.put(cache_key, result)
    
    return result

with Executor(max_workers=4) as executor:
    # Submit tasks that may benefit from caching
    tasks = [100, 200, 100, 300, 200, 400]  # Note duplicates
    futures = [executor.submit(expensive_computation, n) for n in tasks]
    results = [future.result() for future in futures]
    
    print(f"Cache hit rate: {computation_cache.hit_rate():.2%}")
```

## Error Handling and Debugging

### Exception Handling

```python
from pyferris.executor import Executor

def risky_task(x):
    if x < 0:
        raise ValueError(f"Negative value not allowed: {x}")
    return x * x

def safe_task_wrapper(x):
    try:
        return ('success', risky_task(x))
    except Exception as e:
        return ('error', str(e))

data = range(-5, 6)  # Includes negative numbers

with Executor(max_workers=4) as executor:
    futures = [executor.submit(safe_task_wrapper, x) for x in data]
    
    successes = []
    errors = []
    
    for future in futures:
        status, result = future.result()
        if status == 'success':
            successes.append(result)
        else:
            errors.append(result)
    
    print(f"Successful results: {successes}")
    print(f"Errors: {errors}")
```

### Debugging and Monitoring

```python
from pyferris.executor import Executor
import time
import threading

class MonitoredExecutor:
    def __init__(self, max_workers=4):
        self.executor = Executor(max_workers=max_workers)
        self.task_count = 0
        self.completed_count = 0
        self.lock = threading.Lock()
    
    def submit(self, fn, *args, **kwargs):
        with self.lock:
            self.task_count += 1
        
        def wrapped_fn(*args, **kwargs):
            try:
                result = fn(*args, **kwargs)
                with self.lock:
                    self.completed_count += 1
                return result
            except Exception as e:
                with self.lock:
                    self.completed_count += 1
                raise
        
        return self.executor.submit(wrapped_fn, *args, **kwargs)
    
    def get_progress(self):
        with self.lock:
            return self.completed_count, self.task_count
    
    def shutdown(self):
        self.executor.shutdown()

# Usage
def sample_task(x):
    time.sleep(0.1)
    return x * x

monitored_executor = MonitoredExecutor(max_workers=4)

# Submit tasks
futures = [monitored_executor.submit(sample_task, i) for i in range(20)]

# Monitor progress
while True:
    completed, total = monitored_executor.get_progress()
    if completed == total:
        break
    print(f"Progress: {completed}/{total}")
    time.sleep(0.5)

# Collect results
results = [future.result() for future in futures]
monitored_executor.shutdown()
```

## Best Practices

1. **Use Context Managers**: Always use `with` statements for automatic cleanup
2. **Right-size Worker Pools**: Match worker count to workload type (CPU vs I/O bound)
3. **Handle Exceptions**: Wrap risky operations in try-catch blocks
4. **Monitor Resource Usage**: Track memory and CPU usage in long-running tasks
5. **Use Timeouts**: Set reasonable timeouts for task execution
6. **Batch Similar Tasks**: Group similar operations for better efficiency
7. **Profile Performance**: Test different configurations to find optimal settings

## Next Steps

- Learn about [Schedulers](schedulers.md) for advanced task scheduling strategies
- Explore [Shared Memory](shared_memory.md) for efficient data sharing
- Check out [Async Operations](async_ops.md) for asynchronous task execution
