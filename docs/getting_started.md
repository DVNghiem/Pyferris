# Getting Started with PyFerris

This guide will help you get started with PyFerris, from installation to running your first parallel processing program.

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or poetry package manager

### Install from PyPI

The easiest way to install PyFerris is from PyPI:

```bash
pip install pyferris
```

Or if you're using Poetry:

```bash
poetry add pyferris
```

### Build from Source

If you want to build from source (requires Rust and maturin):

```bash
# Clone the repository
git clone https://github.com/DVNghiem/Pyferris.git
cd Pyferris

# Install dependencies
poetry install

# Build the Rust extension
maturin develop

# Run tests to verify installation
poetry run pytest
```

### Verify Installation

You can verify that PyFerris is installed correctly by running:

```python
import pyferris
print(pyferris.__version__)
```

## Quick Start

Let's start with some simple examples to get you familiar with PyFerris.

### Basic Parallel Map

The most common operation is `parallel_map`, which applies a function to every item in an iterable:

```python
from pyferris import parallel_map

def square(x):
    return x * x

numbers = range(1000000)
results = parallel_map(square, numbers)
print(list(results)[:5])  # [0, 1, 4, 9, 16]
```

### Parallel Filter

Filter elements based on a condition:

```python
from pyferris import parallel_filter

def is_even(x):
    return x % 2 == 0

numbers = range(1000)
even_numbers = parallel_filter(is_even, numbers)
print(list(even_numbers)[:5])  # [0, 2, 4, 6, 8]
```

### Parallel Reduce

Combine all elements into a single result:

```python
from pyferris import parallel_reduce

def add(x, y):
    return x + y

numbers = range(1000)
total = parallel_reduce(add, numbers, initial=0)
print(total)  # 499500
```

### Performance Comparison

Let's compare PyFerris with Python's built-in libraries:

```python
import time
from multiprocessing import Pool
from pyferris import parallel_map

def expensive_operation(x):
    # Simulate CPU-intensive work
    return sum(i * i for i in range(x % 100))

data = range(10000)

# Using PyFerris
start = time.time()
results_pyferris = list(parallel_map(expensive_operation, data))
pyferris_time = time.time() - start

# Using multiprocessing
start = time.time()
with Pool() as pool:
    results_mp = pool.map(expensive_operation, data)
multiprocessing_time = time.time() - start

print(f"PyFerris time: {pyferris_time:.2f}s")
print(f"Multiprocessing time: {multiprocessing_time:.2f}s")
print(f"Speedup: {multiprocessing_time / pyferris_time:.2f}x")
```

## Core Concepts

### Chunk Size

PyFerris automatically determines optimal chunk sizes for parallel operations, but you can configure them:

```python
from pyferris import set_chunk_size, get_chunk_size

# Check current chunk size
current_size = get_chunk_size()
print(f"Current chunk size: {current_size}")

# Set a custom chunk size
set_chunk_size(1000)

# Your parallel operations will now use this chunk size
results = parallel_map(lambda x: x * 2, range(100000))
```

### Worker Count

Control the number of worker threads:

```python
from pyferris import set_worker_count, get_worker_count

# Check current worker count
current_workers = get_worker_count()
print(f"Current workers: {current_workers}")

# Set custom worker count (usually number of CPU cores)
import os
set_worker_count(os.cpu_count())
```

### Progress Tracking

Track progress of long-running operations:

```python
from pyferris import parallel_map, ProgressTracker

def slow_operation(x):
    time.sleep(0.01)  # Simulate slow work
    return x * x

data = range(1000)
tracker = ProgressTracker(total=len(data), desc="Processing data")

results = parallel_map(slow_operation, data, progress=tracker)
```

## Asynchronous Operations

PyFerris also supports asynchronous parallel processing:

```python
import asyncio
from pyferris import async_parallel_map

async def async_operation(x):
    await asyncio.sleep(0.01)  # Simulate async I/O
    return x * 2

async def main():
    data = range(100)
    results = await async_parallel_map(async_operation, data)
    print(list(results)[:5])  # [0, 2, 4, 6, 8]

asyncio.run(main())
```

## File I/O Operations

Process files in parallel:

```python
from pyferris.io import simple_io, csv, json

# Read multiple files in parallel
file_contents = simple_io.read_files_parallel(['file1.txt', 'file2.txt', 'file3.txt'])

# Process CSV files
data = csv.read_csv('large_dataset.csv')
processed_data = parallel_map(lambda row: process_row(row), data)
csv.write_csv('processed_dataset.csv', processed_data)

# Handle JSON files
json_data = json.read_json('input.json')
results = parallel_map(transform_data, json_data)
json.write_json('output.json', results)
```

## Smart Caching

Improve performance with intelligent caching:

```python
from pyferris import SmartCache, EvictionPolicy, cached

# Create a cache with LRU eviction
cache = SmartCache(max_size=1000, policy=EvictionPolicy.LRU)
cache.put("key1", "value1")
value = cache.get("key1")

# Use as a decorator
@cached(max_size=100, policy=EvictionPolicy.ADAPTIVE)
def expensive_computation(n):
    # Expensive operation here
    return n * n * n

result = expensive_computation(42)  # Computed and cached
result = expensive_computation(42)  # Retrieved from cache
```

## Next Steps

Now that you've got the basics, explore more advanced features:

1. **[Core Features](core.md)** - Learn about advanced parallel operations
2. **[Executor](executor.md)** - Master task execution and thread pools
3. **[Shared Memory](shared_memory.md)** - Share data between processes efficiently
4. **[Distributed Computing](distributed.md)** - Scale across multiple machines
5. **[Examples](examples.md)** - See real-world usage examples

## Common Pitfalls

### When NOT to Use Parallel Processing

- **Small datasets**: For datasets with fewer than 1,000 items, sequential processing is often faster
- **Simple operations**: Operations that take microseconds may not benefit from parallelization
- **I/O bound with shared resources**: If all operations access the same file or network resource

### Performance Tips

1. **Profile first**: Always measure performance before and after parallelization
2. **Right-size chunks**: Too small chunks increase overhead, too large chunks reduce parallelism
3. **Consider memory usage**: Parallel operations may use more memory
4. **CPU vs I/O bound**: Different strategies work better for different workload types

### Error Handling

```python
from pyferris import parallel_map

def risky_operation(x):
    if x == 5:
        raise ValueError("Something went wrong!")
    return x * 2

try:
    data = range(10)
    results = list(parallel_map(risky_operation, data))
except Exception as e:
    print(f"Error occurred: {e}")
    # Handle error appropriately
```

## Getting Help

- **Documentation**: Browse the complete [API reference](api_reference.md)
- **Examples**: Check out [practical examples](examples.md)
- **Issues**: Report bugs at [GitHub Issues](https://github.com/DVNghiem/Pyferris/issues)
- **Performance**: Read the [performance guide](performance.md) for optimization tips
