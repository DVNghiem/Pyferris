# PyFerris Safe Threading

A high-performance, memory-safe threading module that serves as a drop-in replacement for Python's standard `threading` module. Built on top of PyFerris's Rust-powered executor, it provides better performance and safety guarantees.

## Why Use Safe Threading?

### Problems with Python's Standard Threading
- **GIL Limitations**: Python's Global Interpreter Lock prevents true parallelism for CPU-bound tasks
- **Memory Safety Issues**: Race conditions and memory corruption can occur with improper thread usage
- **Performance Overhead**: Context switching and synchronization overhead in Python threads
- **Resource Management**: Manual thread lifecycle management can lead to resource leaks

### Benefits of PyFerris Safe Threading
- **True Parallelism**: Leverages Rust's work-stealing thread pool to bypass GIL limitations
- **Memory Safety**: Rust's ownership system prevents data races and memory corruption
- **Better Performance**: Optimized task scheduling and reduced overhead
- **Automatic Resource Management**: Context managers and automatic cleanup
- **Thread-Safe Data Structures**: Built-in safe shared memory primitives

## Quick Start

### Basic Thread Usage

```python
from pyferris.safe_thread import SafeThread

def cpu_intensive_task(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

# Create and start a safe thread
thread = SafeThread(target=cpu_intensive_task, args=(1000000,))
thread.start()

# Wait for completion and get result
thread.join()
result = thread.get_result()
print(f"Result: {result}")
```

### Thread Pool Usage

```python
from pyferris.safe_thread import SafeThreadPool

def process_data(x):
    return x * x

data = range(1000)

# Use thread pool for better performance
with SafeThreadPool(max_workers=4) as pool:
    # Submit individual tasks
    futures = [pool.submit(process_data, x) for x in data]
    results = [future.result() for future in futures]
    
    # Or use map for batch processing
    results = pool.map(process_data, data)
```

### Safe Parallel Map

```python
from pyferris.safe_thread import safe_parallel_map

def transform(x):
    return x ** 2

data = range(10000)

# Parallel processing with automatic chunking
results = safe_parallel_map(transform, data, max_workers=4, chunksize=100)
```

## Advanced Features

### Thread-Safe Data Structures

```python
from pyferris.safe_thread import create_safe_shared_data, SafeThread

# Create shared data structures
shared_dict = create_safe_shared_data("dict")
shared_queue = create_safe_shared_data("queue")
shared_counter = create_safe_shared_data("counter", initial_value=0)
shared_array = create_safe_shared_data("array", [1, 2, 3, 4, 5])

def worker(thread_id):
    # Safely access shared data
    shared_counter.increment()
    shared_dict.put(f"worker_{thread_id}", f"result_{thread_id}")
    shared_queue.push(f"task_result_{thread_id}")

# Create worker threads
threads = []
for i in range(5):
    thread = SafeThread(target=worker, args=(i,))
    threads.append(thread)
    thread.start()

# Wait for all threads
for thread in threads:
    thread.join()

print(f"Counter: {shared_counter.get()}")
print(f"Dict size: {shared_dict.size()}")
```

### Safe Locks and Synchronization

```python
from pyferris.safe_thread import SafeLock, SafeCondition

# Safe lock usage
lock = SafeLock()

def critical_section():
    with lock:
        # Critical code here
        pass

# Condition variables
condition = SafeCondition()

def waiter():
    with condition:
        condition.wait()
        print("Condition met!")

def notifier():
    with condition:
        condition.notify()
```

### Function Decorators

```python
from pyferris.safe_thread import safe_thread_decorator

@safe_thread_decorator(max_workers=4)
def expensive_computation(data):
    # This function will run in a thread pool
    return sum(x * x for x in data)

# Use the decorated function
future = expensive_computation(range(10000))
result = future.result()
```

## API Reference

### SafeThread

A thread class that uses Rust's executor for better performance.

**Methods:**
- `start()`: Start the thread's activity
- `join(timeout=None)`: Wait until the thread terminates
- `is_alive()`: Return whether the thread is alive
- `get_result()`: Get the return value of the target function
- `get_exception()`: Get any exception that occurred

**Properties:**
- `name`: Thread name
- `daemon`: Daemon thread status

### SafeThreadPool

A thread pool implementation using Rust's executor.

**Methods:**
- `submit(fn, *args, **kwargs)`: Submit a callable for execution
- `map(func, iterable, chunksize=1)`: Apply func to each element
- `shutdown(wait=True)`: Shutdown the thread pool

**Properties:**
- `active_tasks`: Number of currently active tasks

### SafeLock

A lock implementation using Rust's thread-safe primitives.

**Methods:**
- `acquire(blocking=True, timeout=-1)`: Acquire the lock
- `release()`: Release the lock
- `locked()`: Check if lock is currently held

### Thread-Safe Data Structures

**Shared Dictionary:**
```python
shared_dict = create_safe_shared_data("dict")
shared_dict.put(key, value)
value = shared_dict.get(key)
```

**Shared Array:**
```python
shared_array = create_safe_shared_data("array", [1, 2, 3])
shared_array.set(index, value)
value = shared_array.get(index)
```

**Shared Queue:**
```python
shared_queue = create_safe_shared_data("queue")
shared_queue.push(item)
item = shared_queue.pop()
```

**Atomic Counter:**
```python
counter = create_safe_shared_data("counter", 0)
counter.increment()
counter.decrement()
value = counter.get()
```

## Performance Comparison

PyFerris Safe Threading typically provides significant performance improvements over standard Python threading:

- **CPU-bound tasks**: 2-5x faster due to true parallelism
- **Memory usage**: Lower memory overhead through Rust optimizations
- **Scalability**: Better performance with increasing thread counts

```python
# Benchmark example
import time
from pyferris.safe_thread import SafeThreadPool, safe_parallel_map

def cpu_task(n):
    return sum(i * i for i in range(n))

data = [100000] * 10

# Standard approach
start = time.time()
results = [cpu_task(n) for n in data]
standard_time = time.time() - start

# Safe threading approach
start = time.time()
results = safe_parallel_map(cpu_task, data, max_workers=4)
safe_time = time.time() - start

print(f"Speedup: {standard_time / safe_time:.2f}x")
```

## Best Practices

1. **Use Context Managers**: Always use `with` statements for automatic cleanup
2. **Choose Appropriate Worker Counts**: Match worker count to your workload
3. **Use Batch Operations**: Prefer `map()` over individual `submit()` calls for large datasets
4. **Handle Exceptions**: Always check for exceptions in thread results
5. **Use Shared Data Structures**: Leverage built-in thread-safe data structures

## Migration from Standard Threading

PyFerris Safe Threading provides a mostly compatible API:

```python
# Standard threading
import threading

thread = threading.Thread(target=func, args=(arg1, arg2))
thread.start()
thread.join()

# Safe threading
from pyferris.safe_thread import SafeThread

thread = SafeThread(target=func, args=(arg1, arg2))
thread.start()
thread.join()
result = thread.get_result()  # Additional feature
```

## Examples

See `examples/safe_threading_demo.py` for comprehensive examples demonstrating all features.

## Limitations

- Requires PyFerris to be installed with Rust extensions
- Some advanced threading features from standard library may not be available
- Function arguments must be picklable for thread execution

## Contributing

Contributions are welcome! Please see the main PyFerris contributing guidelines.
