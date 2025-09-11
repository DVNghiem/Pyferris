# Virtual Threads

Virtual threads are a revolutionary approach to concurrent programming, inspired by Java's Project Loom. They provide the ability to create millions of lightweight threads that are managed by a small pool of OS threads, enabling massive concurrency with minimal overhead.

## Overview

PyFerris virtual threads offer:
- **Lightweight**: Each virtual thread uses only a few KB of memory
- **Scalable**: Support for millions of concurrent virtual threads
- **Efficient**: Managed by a small pool of OS threads using work-stealing
- **Non-blocking**: Automatic yielding for blocking operations
- **Priority-based**: Support for task prioritization
- **Future-compatible**: Seamless integration with Python's concurrent.futures

## Key Concepts

### Virtual Threads vs Traditional Threads

| Feature | Traditional Threads | Virtual Threads |
|---------|-------------------|-----------------|
| Memory per thread | ~2MB | ~Few KB |
| Creation cost | High | Very low |
| Context switching | Expensive | Cheap |
| Scalability | Limited (~thousands) | High (~millions) |
| OS overhead | High | Low |

### How Virtual Threads Work

1. **Virtual threads** are lightweight user-space threads
2. **Platform threads** are OS threads that execute virtual threads
3. **Work-stealing scheduler** distributes virtual threads across platform threads
4. **Automatic yielding** occurs when virtual threads would block
5. **Continuation-based execution** allows efficient context switching

## Basic Usage

### Simple Virtual Thread Execution

```python
from pyferris.virtual_thread import run_in_virtual_thread

def cpu_intensive_task(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

# Execute in a virtual thread
result = run_in_virtual_thread(cpu_intensive_task, 1000000)
print(f"Result: {result}")
```

### Using Virtual Thread Pool

```python
from pyferris.virtual_thread import VirtualThreadPool
import time

def io_task(duration, message):
    time.sleep(duration)  # Simulated I/O
    return f"Completed: {message}"

# Create and use virtual thread pool
with VirtualThreadPool(max_platform_threads=4) as pool:
    # Submit individual tasks
    future1 = pool.submit(io_task, 0.1, "Task 1")
    future2 = pool.submit(io_task, 0.2, "Task 2")
    
    # Get results
    print(future1.result())  # Completed: Task 1
    print(future2.result())  # Completed: Task 2
    
    # Use map for multiple items
    tasks = [(0.1, f"Batch task {i}") for i in range(10)]
    results = pool.starmap(io_task, tasks)
    print(f"Completed {len(results)} tasks")
```

### Convenience Functions

```python
from pyferris.virtual_thread import virtual_map

def square(x):
    return x * x

# Process items in parallel using virtual threads
numbers = range(10)
squares = virtual_map(square, numbers)
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

## Advanced Features

### Priority-Based Scheduling

```python
with VirtualThreadPool() as pool:
    # High priority task (lower number = higher priority)
    urgent_task = pool.submit(critical_function, priority=50)
    
    # Normal priority task
    normal_task = pool.submit(regular_function, priority=128)
    
    # Low priority task
    background_task = pool.submit(background_function, priority=200)
```

### Blocking Operation Handling

```python
import requests

def fetch_url(url):
    # This is a blocking I/O operation
    response = requests.get(url)
    return response.status_code

urls = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/2", 
    "https://httpbin.org/delay/1"
]

with VirtualThreadPool() as pool:
    # Mark as blocking for better scheduling
    futures = [
        pool.submit(fetch_url, url, is_blocking=True) 
        for url in urls
    ]
    
    results = [f.result() for f in futures]
    print(f"Status codes: {results}")
```

### Async Integration

```python
from pyferris.virtual_thread import AsyncVirtualThreadPool
import asyncio

async def async_worker():
    def cpu_work(n):
        return sum(i * i for i in range(n))
    
    async with AsyncVirtualThreadPool() as pool:
        # Execute CPU-bound work in virtual threads
        result = await pool.submit(cpu_work, 100000)
        
        # Map over multiple items
        results = await pool.map(cpu_work, [10000, 20000, 30000])
        
        return result, results

# Run the async function
result, batch_results = asyncio.run(async_worker())
```

## Performance Optimization

### Choosing the Right Configuration

```python
# For I/O-bound workloads
io_pool = VirtualThreadPool(
    max_virtual_threads=100000,  # Many virtual threads
    max_platform_threads=4       # Few OS threads
)

# For CPU-bound workloads  
cpu_pool = VirtualThreadPool(
    max_virtual_threads=1000,    # Fewer virtual threads
    max_platform_threads=8       # More OS threads (≈ CPU cores)
)

# For mixed workloads
mixed_pool = VirtualThreadPool(
    max_virtual_threads=50000,   # Moderate virtual threads
    max_platform_threads=6       # Balanced OS threads
)
```

### Monitoring and Statistics

```python
with VirtualThreadPool() as pool:
    # Submit some work
    futures = [pool.submit(some_function, i) for i in range(100)]
    
    # Monitor progress
    while not all(f.done() for f in futures):
        stats = pool.get_stats()
        print(f"Active: {stats['active_threads']}, "
              f"Completed: {stats['completed_threads']}")
        time.sleep(0.1)
    
    # Final statistics
    final_stats = pool.get_stats()
    print(f"Total created: {final_stats['total_threads_created']}")
    print(f"Platform threads: {final_stats['platform_threads']}")
```

### Benchmarking Virtual vs Traditional Threads

```python
from pyferris.virtual_thread import virtual_thread_benchmark

def computation_task(n):
    return sum(i * i for i in range(n))

# Define test cases
test_cases = [(1000,), (2000,), (3000,), (4000,), (5000,)]

# Run benchmark
results = virtual_thread_benchmark(
    computation_task,
    test_cases,
    traditional_threads=True,
    max_platform_threads=4
)

print(f"Virtual threads time: {results['virtual_threads']['time']:.3f}s")
print(f"Traditional threads time: {results['traditional_threads']['time']:.3f}s")
print(f"Speedup: {results['speedup']:.2f}x")
```

## Best Practices

### When to Use Virtual Threads

✅ **Good for:**
- I/O-bound operations (file, network, database)
- High-concurrency scenarios (thousands of concurrent tasks)
- Blocking operations that can be made asynchronous
- Mixed CPU/I/O workloads
- Server applications with many concurrent requests

❌ **Not ideal for:**
- Pure CPU-bound work (use regular thread pools)
- Very short-lived tasks (overhead may not be worth it)
- Memory-intensive operations (due to virtual thread overhead)

### Error Handling

```python
def potentially_failing_task(should_fail):
    if should_fail:
        raise ValueError("Task failed!")
    return "Success"

with VirtualThreadPool() as pool:
    futures = [
        pool.submit(potentially_failing_task, i % 3 == 0) 
        for i in range(10)
    ]
    
    for i, future in enumerate(futures):
        try:
            result = future.result()
            print(f"Task {i}: {result}")
        except ValueError as e:
            print(f"Task {i} failed: {e}")
```

### Resource Management

```python
# Always use context managers for automatic cleanup
with VirtualThreadPool() as pool:
    # Your work here
    pass  # Pool is automatically shut down

# Or manual management
pool = VirtualThreadPool()
try:
    # Your work here
    pass
finally:
    pool.shutdown()
```

### Memory Considerations

```python
# For long-running applications, be mindful of virtual thread limits
long_running_pool = VirtualThreadPool(
    max_virtual_threads=10000,  # Set reasonable limits
    max_platform_threads=4
)

# Monitor memory usage in production
import psutil
process = psutil.Process()

with long_running_pool as pool:
    initial_memory = process.memory_info().rss
    
    # Submit work...
    
    current_memory = process.memory_info().rss
    memory_increase = current_memory - initial_memory
    print(f"Memory increase: {memory_increase / 1024 / 1024:.1f} MB")
```

## Real-World Examples

### Web Scraping with Virtual Threads

```python
import requests
from pyferris.virtual_thread import VirtualThreadPool

def fetch_page(url):
    try:
        response = requests.get(url, timeout=10)
        return {
            'url': url,
            'status': response.status_code,
            'size': len(response.content)
        }
    except Exception as e:
        return {'url': url, 'error': str(e)}

urls = [
    'https://httpbin.org/delay/1',
    'https://httpbin.org/delay/2',
    'https://jsonplaceholder.typicode.com/posts/1',
    'https://jsonplaceholder.typicode.com/users',
    # ... many more URLs
]

with VirtualThreadPool(max_platform_threads=8) as pool:
    results = pool.map(
        fetch_page, 
        urls, 
        is_blocking=True  # Network I/O is blocking
    )

successful = [r for r in results if 'error' not in r]
failed = [r for r in results if 'error' in r]

print(f"Successfully fetched: {len(successful)}")
print(f"Failed: {len(failed)}")
```

### Parallel File Processing

```python
import os
from pathlib import Path
from pyferris.virtual_thread import VirtualThreadPool

def process_file(file_path):
    """Process a single file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Process content (count words, extract data, etc.)
        word_count = len(content.split())
        
        return {
            'file': file_path.name,
            'size': file_path.stat().st_size,
            'words': word_count
        }
    except Exception as e:
        return {'file': file_path.name, 'error': str(e)}

# Get all text files in directory
data_dir = Path('./data')
text_files = list(data_dir.glob('*.txt'))

with VirtualThreadPool() as pool:
    results = pool.map(
        process_file,
        text_files,
        is_blocking=True  # File I/O is blocking
    )

total_words = sum(r.get('words', 0) for r in results)
print(f"Processed {len(results)} files, total words: {total_words}")
```

### Database Operations

```python
import sqlite3
from pyferris.virtual_thread import VirtualThreadPool

def query_database(query_id, query):
    """Execute a database query."""
    conn = sqlite3.connect('example.db')  # Thread-safe in most cases
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return {
            'query_id': query_id,
            'results': results,
            'count': len(results)
        }
    except Exception as e:
        return {'query_id': query_id, 'error': str(e)}
    finally:
        conn.close()

queries = [
    (1, "SELECT COUNT(*) FROM users"),
    (2, "SELECT * FROM products WHERE price > 100"),
    (3, "SELECT category, COUNT(*) FROM products GROUP BY category"),
    # ... more queries
]

with VirtualThreadPool(max_platform_threads=4) as pool:
    results = pool.starmap(
        query_database,
        queries,
        is_blocking=True  # Database I/O is blocking
    )

for result in results:
    if 'error' not in result:
        print(f"Query {result['query_id']}: {result['count']} results")
    else:
        print(f"Query {result['query_id']} failed: {result['error']}")
```

## Performance Comparison

### Scalability Test

```python
import time
from concurrent.futures import ThreadPoolExecutor
from pyferris.virtual_thread import VirtualThreadPool

def io_simulation(duration):
    time.sleep(duration)
    return "completed"

def test_scalability(num_tasks, task_duration):
    """Test scalability with increasing number of tasks."""
    
    # Virtual threads
    start = time.time()
    with VirtualThreadPool(max_platform_threads=4) as pool:
        futures = [
            pool.submit(io_simulation, task_duration, is_blocking=True)
            for _ in range(num_tasks)
        ]
        vt_results = [f.result() for f in futures]
    vt_time = time.time() - start
    
    # Traditional threads (limited by system)
    max_workers = min(num_tasks, 100)  # Limit to avoid system overload
    start = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(io_simulation, task_duration)
            for _ in range(num_tasks)
        ]
        tt_results = [f.result() for f in futures]
    tt_time = time.time() - start
    
    return {
        'tasks': num_tasks,
        'virtual_threads_time': vt_time,
        'traditional_threads_time': tt_time,
        'speedup': tt_time / vt_time if vt_time > 0 else float('inf')
    }

# Test with increasing load
test_cases = [10, 50, 100, 500, 1000]
task_duration = 0.1

for num_tasks in test_cases:
    result = test_scalability(num_tasks, task_duration)
    print(f"Tasks: {result['tasks']:4d}, "
          f"VT: {result['virtual_threads_time']:.2f}s, "
          f"TT: {result['traditional_threads_time']:.2f}s, "
          f"Speedup: {result['speedup']:.2f}x")
```

## Integration with Existing Code

### Drop-in Replacement for ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor
from pyferris.virtual_thread import VirtualThreadPool

# Traditional approach
def traditional_approach():
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(some_function, i) for i in range(100)]
        results = [f.result() for f in futures]
    return results

# Virtual thread approach (similar interface)
def virtual_thread_approach():
    with VirtualThreadPool(max_platform_threads=4) as pool:
        futures = [pool.submit(some_function, i) for i in range(100)]
        results = [f.result() for f in futures]
    return results
```

### Gradual Migration

```python
# Phase 1: Replace I/O-bound operations
def process_io_bound_tasks(tasks):
    with VirtualThreadPool() as pool:
        return pool.map(io_bound_function, tasks, is_blocking=True)

# Phase 2: Replace high-concurrency operations  
def process_high_concurrency_tasks(tasks):
    with VirtualThreadPool(max_virtual_threads=len(tasks)) as pool:
        return pool.map(concurrent_function, tasks)

# Phase 3: Keep CPU-bound operations with traditional threads
def process_cpu_bound_tasks(tasks):
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(cpu_bound_function, tasks))
```

## Troubleshooting

### Common Issues

1. **Memory Usage Higher Than Expected**
   - Reduce `max_virtual_threads`
   - Ensure proper cleanup of resources in tasks
   - Monitor for memory leaks in long-running applications

2. **Performance Worse Than Traditional Threads**
   - For CPU-bound tasks, use traditional thread pools
   - Ensure tasks are properly marked as `is_blocking=True` for I/O
   - Check if task overhead is too high for very simple operations

3. **Tasks Not Completing**
   - Check for exceptions in task functions
   - Ensure proper timeout handling
   - Verify that blocking operations yield control

### Debugging

```python
import logging
from pyferris.virtual_thread import VirtualThreadPool

# Enable logging
logging.basicConfig(level=logging.DEBUG)

def debug_task(task_id):
    logging.info(f"Starting task {task_id}")
    # Your task logic here
    result = f"Task {task_id} completed"
    logging.info(f"Finished task {task_id}")
    return result

with VirtualThreadPool() as pool:
    # Monitor statistics during execution
    futures = [pool.submit(debug_task, i) for i in range(10)]
    
    while not all(f.done() for f in futures):
        stats = pool.get_stats()
        logging.info(f"Stats: {stats}")
        time.sleep(0.5)
    
    results = [f.result() for f in futures]
```

Virtual threads in PyFerris provide a powerful foundation for building highly concurrent applications with excellent performance characteristics. They bridge the gap between traditional threading and async programming, offering the best of both worlds.
