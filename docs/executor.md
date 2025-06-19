# Executor

The PyFerris Executor provides advanced task management and thread pool functionality for complex parallel workloads. Built on Rust's Rayon parallel processing framework, it offers both Python callback support and high-performance pure Rust computations.

## Overview

The Executor module provides:
- Thread pool management with configurable worker counts
- Task queuing and scheduling with Rayon integration
- Python callback execution (with GIL limitations)
- Pure Rust computations for true parallel speedup
- Configurable chunking strategies for optimal performance
- Batch processing capabilities

## Performance Characteristics

### Python Callback Limitations
Due to Python's Global Interpreter Lock (GIL), Python callback-based tasks have limited parallel speedup. The executor still provides benefits through better CPU utilization and task scheduling, but true parallel speedup is constrained.

### Pure Rust Computations
For CPU-intensive mathematical operations, the executor provides `submit_computation()` which performs computations entirely in Rust, achieving true parallel speedup that scales with worker count.

## Core Components

### `Executor` Class

The main executor class for managing parallel tasks and thread pools.

#### Constructor

```python
from pyferris.executor import Executor

# Create executor with default settings (CPU count workers)
executor = Executor()

# Create executor with specific worker count
executor = Executor(max_workers=8)
```

**Parameters:**
- `max_workers` (int, optional): Maximum number of worker threads. Defaults to CPU count.

## Basic Usage

### Submitting Python Callback Tasks

```python
from pyferris.executor import Executor
import time

def cpu_intensive_task(n):
    """Simulate CPU-intensive work."""
    result = 0
    for i in range(n * 1000):
        result += i
    return result

executor = Executor(max_workers=4)

# Submit single task
future = executor.submit(cpu_intensive_task, 100)
result = future.result()  # Blocks until completion
print(f"Task result: {result}")

# Submit multiple tasks using map (recommended for multiple tasks)
numbers = list(range(10, 20))
results = executor.map(cpu_intensive_task, numbers)
print(f"All results: {results}")
```

### Pure Rust Computations (High Performance)

For CPU-intensive mathematical operations, use `submit_computation()` for true parallel speedup:

```python
# Test data
numbers = list(range(1, 101))

# Available computation types:
# - 'sum': Parallel sum of all numbers
# - 'product': Parallel product of all numbers  
# - 'square_sum': Parallel sum of squares
# - 'heavy_computation': CPU-intensive computation for benchmarking

# Pure Rust parallel computation
result = executor.submit_computation('heavy_computation', numbers)
print(f"Heavy computation result: {result}")

# Simple operations
sum_result = executor.submit_computation('sum', numbers)
print(f"Parallel sum: {sum_result}")

square_sum = executor.submit_computation('square_sum', numbers)
print(f"Parallel sum of squares: {square_sum}")
```

### Performance Tuning

```python
# Configure chunk size for better performance
executor = Executor(max_workers=4)

# Set smaller chunk size for better load balancing
executor.set_chunk_size(10)

# Check current chunk size
current_chunk_size = executor.get_chunk_size()
print(f"Current chunk size: {current_chunk_size}")

# Get worker information
worker_count = executor.get_worker_count()
is_active = executor.is_active()
print(f"Workers: {worker_count}, Active: {is_active}")
```

### Batch Processing

```python
def process_item(item):
    return item * item

# Process multiple items in batches
items = list(range(100))
batch_tasks = [(process_item, (item,)) for item in items]

# Submit batch of tasks
results = executor.submit_batch(batch_tasks)
print(f"Batch results: {results[:10]}...")  # Show first 10 results
```

## Advanced Features

### Task Futures and Results

```python
from pyferris import Executor
import time

def long_running_task(duration, task_id):
    time.sleep(duration)
    return f"Task {task_id} completed after {duration}s"

executor = Executor()

# Submit tasks and get futures
futures = []
for i in range(5):
    future = executor.submit(long_running_task, i + 1, i)
    futures.append(future)

# Check task status
for i, future in enumerate(futures):
    print(f"Task {i} done: {future.done()}")

# Wait for all tasks with timeout
completed_futures = executor.wait(futures, timeout=10.0)
print(f"Completed {len(completed_futures)} tasks within timeout")

# Get results as they complete
for future in executor.as_completed(futures):
    try:
        result = future.result()
        print(f"Got result: {result}")
    except Exception as e:
        print(f"Task failed: {e}")
```

### Context Manager Usage

```python
# Automatic cleanup with context manager
with Executor(max_workers=6) as executor:
    # Submit tasks
    futures = [executor.submit(some_function, i) for i in range(100)]
    
    # Process results
    for future in executor.as_completed(futures):
        result = future.result()
        process_result(result)
        
# Executor automatically shuts down when exiting context
```

### Exception Handling

```python
def risky_task(value):
    if value % 7 == 0:
        raise ValueError(f"Value {value} is divisible by 7!")
    return value ** 2

executor = Executor()

futures = [executor.submit(risky_task, i) for i in range(20)]

for i, future in enumerate(futures):
    try:
        result = future.result()
        print(f"Task {i}: {result}")
    except ValueError as e:
        print(f"Task {i} failed: {e}")
    except Exception as e:
        print(f"Task {i} unexpected error: {e}")
```

## Performance Monitoring

### Executor Statistics

```python
executor = Executor(max_workers=8)

# Submit some tasks
futures = [executor.submit(cpu_intensive_task, i) for i in range(100)]

# Get executor statistics
stats = executor.get_stats()
print(f"Active threads: {stats.active_threads}")
print(f"Queued tasks: {stats.queued_tasks}")
print(f"Completed tasks: {stats.completed_tasks}")
print(f"Failed tasks: {stats.failed_tasks}")
print(f"Total execution time: {stats.total_execution_time:.2f}s")
```

### Resource Monitoring

```python
import time

def monitor_executor_performance():
    executor = Executor(max_workers=4)
    
    # Submit long-running tasks
    futures = [executor.submit(cpu_intensive_task, 1000) for _ in range(20)]
    
    # Monitor while tasks execute
    start_time = time.time()
    while not all(f.done() for f in futures):
        stats = executor.get_stats()
        cpu_usage = executor.get_cpu_usage()
        memory_usage = executor.get_memory_usage()
        
        print(f"Progress: {stats.completed_tasks}/{len(futures)} tasks")
        print(f"CPU Usage: {cpu_usage:.1f}%")
        print(f"Memory Usage: {memory_usage / 1024 / 1024:.1f} MB")
        
        time.sleep(1)
    
    total_time = time.time() - start_time
    print(f"All tasks completed in {total_time:.2f}s")

monitor_executor_performance()
```

## Scheduling Strategies

### Priority Task Execution

```python
from pyferris import Executor, TaskPriority

executor = Executor(max_workers=4)

# Submit tasks with different priorities
high_priority_future = executor.submit(
    important_task, 
    priority=TaskPriority.HIGH
)

normal_future = executor.submit(normal_task)

low_priority_future = executor.submit(
    background_task,
    priority=TaskPriority.LOW
)

# High priority tasks execute first
```

### Work Stealing Scheduler

```python
from pyferris import Executor, WorkStealingScheduler

# Use work-stealing for better load balancing
executor = Executor(
    max_workers=8,
    scheduler=WorkStealingScheduler()
)

# Submit varied workloads
mixed_tasks = [
    executor.submit(quick_task, i) for i in range(50)
] + [
    executor.submit(slow_task, i) for i in range(10)
]

# Work-stealing ensures optimal load distribution
results = [task.result() for task in mixed_tasks]
```

## Integration Patterns

### With AsyncIO

```python
import asyncio
from pyferris import Executor

async def async_with_executor():
    executor = Executor(max_workers=4)
    loop = asyncio.get_event_loop()
    
    # Run CPU-bound task in executor
    def cpu_bound_task(n):
        return sum(i * i for i in range(n))
    
    # Submit to executor from async context
    result = await loop.run_in_executor(
        executor, 
        cpu_bound_task, 
        1000000
    )
    
    print(f"Async result: {result}")
    
    executor.shutdown()

# Run the async function
asyncio.run(async_with_executor())
```

### Pipeline Processing

```python
from pyferris import Executor
from queue import Queue
import threading

def create_processing_pipeline():
    executor = Executor(max_workers=6)
    input_queue = Queue()
    output_queue = Queue()
    
    def stage1_processor():
        while True:
            item = input_queue.get()
            if item is None:
                break
            
            # Submit stage 1 processing
            future = executor.submit(process_stage1, item)
            result = future.result()
            
            # Pass to stage 2
            stage2_future = executor.submit(process_stage2, result)
            output_queue.put(stage2_future)
    
    # Start pipeline thread
    pipeline_thread = threading.Thread(target=stage1_processor)
    pipeline_thread.start()
    
    return input_queue, output_queue, pipeline_thread

def process_stage1(data):
    # First processing stage
    return data * 2

def process_stage2(data):
    # Second processing stage
    return data + 1

# Use the pipeline
input_q, output_q, thread = create_processing_pipeline()

# Feed data into pipeline
for i in range(100):
    input_q.put(i)

# Signal completion
input_q.put(None)

# Collect results
results = []
for _ in range(100):
    future = output_q.get()
    result = future.result()
    results.append(result)

thread.join()
print(f"Pipeline processed {len(results)} items")
```

## Configuration and Tuning

### Optimal Worker Count

```python
import os
from pyferris import Executor

def determine_optimal_workers(task_type):
    """Determine optimal worker count based on task characteristics."""
    cpu_count = os.cpu_count()
    
    if task_type == 'cpu_bound':
        # CPU-bound tasks: use CPU count
        return cpu_count
    elif task_type == 'io_bound':
        # I/O-bound tasks: can use more workers
        return cpu_count * 2
    elif task_type == 'mixed':
        # Mixed workload: balance between CPU and I/O
        return int(cpu_count * 1.5)
    else:
        return cpu_count

# Configure executor based on workload
executor = Executor(max_workers=determine_optimal_workers('cpu_bound'))
```

### Memory-Aware Execution

```python
import psutil
from pyferris import Executor

class MemoryAwareExecutor:
    def __init__(self, max_workers=None, memory_limit_gb=8):
        self.memory_limit = memory_limit_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.executor = Executor(max_workers=max_workers)
    
    def submit_with_memory_check(self, fn, *args, **kwargs):
        # Check memory usage before submitting
        memory_usage = psutil.virtual_memory().used
        
        if memory_usage > self.memory_limit:
            # Wait for some tasks to complete
            print("Memory limit reached, waiting for tasks to complete...")
            time.sleep(1)
        
        return self.executor.submit(fn, *args, **kwargs)

# Use memory-aware executor
memory_executor = MemoryAwareExecutor(max_workers=4, memory_limit_gb=8)
```

## Best Practices

### 1. Proper Resource Management

```python
# Always clean up resources
try:
    executor = Executor(max_workers=8)
    
    # Submit and execute tasks
    futures = [executor.submit(task_func, i) for i in range(100)]
    results = [f.result() for f in futures]
    
finally:
    # Ensure executor is properly shut down
    executor.shutdown(wait=True)
```

### 2. Error Handling Strategy

```python
def robust_task_execution(executor, tasks):
    """Execute tasks with comprehensive error handling."""
    futures = []
    
    # Submit all tasks
    for task_func, args in tasks:
        try:
            future = executor.submit(task_func, *args)
            futures.append((future, task_func.__name__))
        except Exception as e:
            print(f"Failed to submit {task_func.__name__}: {e}")
    
    # Collect results with error handling
    successful_results = []
    failed_tasks = []
    
    for future, task_name in futures:
        try:
            result = future.result(timeout=30)  # 30-second timeout
            successful_results.append(result)
        except TimeoutError:
            print(f"Task {task_name} timed out")
            failed_tasks.append(task_name)
        except Exception as e:
            print(f"Task {task_name} failed: {e}")
            failed_tasks.append(task_name)
    
    return successful_results, failed_tasks
```

### 3. Performance Optimization

```python
def optimize_executor_performance():
    """Guidelines for optimal executor performance."""
    
    # 1. Size the thread pool appropriately
    cpu_count = os.cpu_count()
    
    # For CPU-bound tasks
    cpu_executor = Executor(max_workers=cpu_count)
    
    # For I/O-bound tasks
    io_executor = Executor(max_workers=cpu_count * 2)
    
    # 2. Batch small tasks to reduce overhead
    def batch_small_tasks(small_tasks, batch_size=100):
        def process_batch(task_batch):
            return [task() for task in task_batch]
        
        batches = [small_tasks[i:i+batch_size] 
                  for i in range(0, len(small_tasks), batch_size)]
        
        futures = [cpu_executor.submit(process_batch, batch) 
                  for batch in batches]
        
        results = []
        for future in futures:
            batch_results = future.result()
            results.extend(batch_results)
        
        return results
    
    # 3. Use appropriate timeout values
    def execute_with_timeout(executor, task_func, args, timeout=60):
        future = executor.submit(task_func, *args)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            print(f"Task timed out after {timeout} seconds")
            return None
```

## Troubleshooting

### Common Issues and Solutions

1. **Out of Memory Errors:**
   ```python
   # Solution: Limit concurrent tasks
   executor = Executor(max_workers=2)  # Reduce workers
   
   # Or process in smaller batches
   batch_size = 10
   for i in range(0, len(large_dataset), batch_size):
       batch = large_dataset[i:i+batch_size]
       futures = [executor.submit(process_item, item) for item in batch]
       results = [f.result() for f in futures]
   ```

2. **Deadlock Issues:**
   ```python
   # Avoid submitting tasks from within tasks
   def bad_nested_task():
       # This can cause deadlock!
       inner_future = executor.submit(another_task)
       return inner_future.result()
   
   # Better approach: use separate executor or avoid nesting
   def good_approach():
       # Process sequentially within task
       return another_task()
   ```

3. **Performance Bottlenecks:**
   ```python
   # Profile executor performance
   import time
   
   start_time = time.time()
   futures = [executor.submit(task_func, i) for i in range(1000)]
   
   # Measure submission time
   submission_time = time.time() - start_time
   
   # Measure execution time
   results = [f.result() for f in futures]
   total_time = time.time() - start_time
   
   print(f"Submission time: {submission_time:.2f}s")
   print(f"Total time: {total_time:.2f}s")
   print(f"Execution efficiency: {submission_time/total_time:.2%}")
   ```

The Executor provides powerful task management capabilities that scale from simple parallel execution to complex distributed processing workflows.

## Performance Recommendations

### When to Use Each Method

1. **`submit()`** - Single tasks or when you need Future objects
   ```python
   # Good for single tasks
   future = executor.submit(my_function)
   result = future.result()
   ```

2. **`map()`** - Multiple similar tasks (most common use case)
   ```python
   # Best for multiple tasks of the same type
   results = executor.map(process_function, data_list)
   ```

3. **`submit_computation()`** - CPU-intensive mathematical operations
   ```python
   # Best performance for pure computations
   result = executor.submit_computation('heavy_computation', numbers)
   ```

4. **`submit_batch()`** - Mixed task types or complex batching
   ```python
   # Good for heterogeneous task batches
   results = executor.submit_batch(mixed_tasks)
   ```

### Performance Scaling Examples

The following benchmarks show performance scaling with worker count:

```
Pure Rust Computation (200 numbers, heavy computation):
- 1 worker:  0.2246s
- 2 workers: 0.1065s (2.11x speedup)
- 4 workers: 0.0749s (3.00x speedup)
- 8 workers: 0.0467s (4.81x speedup)

Python Callbacks (20 CPU-intensive tasks):
- Sequential: 0.5461s
- 4 workers:  0.6061s (0.90x speedup due to GIL)
```

### Optimization Tips

1. **Choose the right method**: Use `submit_computation()` for mathematical operations
2. **Tune chunk size**: Smaller chunks = better load balancing, larger chunks = less overhead
3. **Consider task overhead**: Very quick tasks may not benefit from parallelization
4. **Use context managers**: Ensure proper cleanup with `with` statement
5. **Monitor worker utilization**: Adjust worker count based on CPU cores and task characteristics

### Common Pitfalls

- **GIL limitations**: Python callbacks don't scale linearly due to GIL
- **Task overhead**: Parallelizing very fast tasks can be slower than sequential
- **Memory usage**: More workers = more memory usage
- **I/O bound tasks**: Use async patterns instead of thread parallelism for I/O
