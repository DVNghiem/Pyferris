# Core Features

PyFerris provides a comprehensive set of core parallel operations that form the foundation of high-performance parallel processing. These operations are optimized for large datasets and CPU-intensive tasks.

## Basic Parallel Operations

### parallel_map

Apply a function to every item in an iterable in parallel.

```python
from pyferris import parallel_map

def square(x):
    return x * x

numbers = range(1000000)
results = parallel_map(square, numbers)
print(list(results)[:5])  # [0, 1, 4, 9, 16]
```

**Advanced Usage:**

```python
from pyferris import parallel_map, ProgressTracker

def complex_calculation(x):
    # Simulate complex CPU-intensive work
    result = 0
    for i in range(x % 1000):
        result += i * i
    return result

data = range(10000)
tracker = ProgressTracker(total=len(data), desc="Computing")

# With progress tracking
results = parallel_map(complex_calculation, data, progress=tracker)

# With custom chunk size
results = parallel_map(complex_calculation, data, chunk_size=100)
```

### parallel_filter

Filter elements based on a predicate function in parallel.

```python
from pyferris import parallel_filter

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

numbers = range(1000)
primes = parallel_filter(is_prime, numbers)
print(list(primes)[:10])  # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

### parallel_reduce

Combine all elements into a single result using a reduction function.

```python
from pyferris import parallel_reduce

def multiply(x, y):
    return x * y

numbers = range(1, 11)  # [1, 2, 3, ..., 10]
factorial_10 = parallel_reduce(multiply, numbers, initial=1)
print(factorial_10)  # 3628800 (10!)

# String concatenation
words = ["Hello", " ", "parallel", " ", "world", "!"]
sentence = parallel_reduce(lambda x, y: x + y, words, initial="")
print(sentence)  # "Hello parallel world!"
```

### parallel_starmap

Apply a function to arguments unpacked from tuples in parallel.

```python
from pyferris import parallel_starmap

def power(base, exponent):
    return base ** exponent

# List of (base, exponent) tuples
calculations = [(2, 3), (4, 2), (5, 3), (3, 4)]
results = parallel_starmap(power, calculations)
print(list(results))  # [8, 16, 125, 81]

# Real-world example: distance calculations
import math

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

points = [(0, 0, 3, 4), (1, 1, 4, 5), (2, 2, 5, 6)]
distances = parallel_starmap(distance, points)
print(list(distances))  # [5.0, 5.0, 5.0]
```

## Advanced Parallel Operations

### parallel_sort

Sort large datasets in parallel using merge sort algorithm.

```python
from pyferris import parallel_sort
import random

# Generate random data
data = [random.randint(1, 1000) for _ in range(100000)]

# Sort in ascending order
sorted_data = parallel_sort(data)

# Sort with custom key function
people = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
sorted_by_age = parallel_sort(people, key=lambda person: person[1])
print(sorted_by_age)  # [("Bob", 25), ("Alice", 30), ("Charlie", 35)]

# Sort in descending order
sorted_desc = parallel_sort(data, reverse=True)
```

### parallel_group_by

Group elements by a key function in parallel.

```python
from pyferris import parallel_group_by

# Group numbers by their remainder when divided by 3
numbers = range(20)
groups = parallel_group_by(numbers, key=lambda x: x % 3)
print(groups)
# {0: [0, 3, 6, 9, 12, 15, 18], 1: [1, 4, 7, 10, 13, 16, 19], 2: [2, 5, 8, 11, 14, 17]}

# Group words by length
words = ["apple", "pie", "banana", "cat", "elephant", "dog"]
by_length = parallel_group_by(words, key=len)
print(by_length)
# {5: ['apple'], 3: ['pie', 'cat', 'dog'], 6: ['banana'], 8: ['elephant']}
```

### parallel_unique

Remove duplicates from a large dataset in parallel.

```python
from pyferris import parallel_unique

# Remove duplicates from large list
data = [1, 2, 3, 2, 4, 3, 5, 1, 6, 4] * 10000
unique_values = parallel_unique(data)
print(sorted(unique_values))  # [1, 2, 3, 4, 5, 6]

# With custom key function
people = [("Alice", 30), ("Bob", 25), ("Alice", 30), ("Charlie", 35)]
unique_people = parallel_unique(people, key=lambda person: person[0])
print(unique_people)  # [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
```

### parallel_partition

Partition data into two groups based on a predicate.

```python
from pyferris import parallel_partition

numbers = range(100)
evens, odds = parallel_partition(numbers, lambda x: x % 2 == 0)
print(f"Evens: {len(evens)}, Odds: {len(odds)}")  # Evens: 50, Odds: 50

# Partition by value range
values = range(1000)
small, large = parallel_partition(values, lambda x: x < 500)
print(f"Small values: {len(small)}, Large values: {len(large)}")
```

### parallel_chunks

Split data into chunks for batch processing.

```python
from pyferris import parallel_chunks

data = range(100)
chunks = parallel_chunks(data, chunk_size=10)
print(f"Number of chunks: {len(chunks)}")  # 10
print(f"First chunk: {chunks[0]}")  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Process each chunk
def process_chunk(chunk):
    return sum(chunk)

chunk_sums = parallel_map(process_chunk, chunks)
print(f"Total sum: {sum(chunk_sums)}")  # 4950
```

## Batch Processing

### BatchProcessor

Process large datasets in configurable batches with automatic memory management.

```python
from pyferris import BatchProcessor, ProgressTracker

def process_batch(batch):
    """Process a batch of data and return results."""
    return [x * x for x in batch]

# Create batch processor
processor = BatchProcessor(
    batch_size=1000,
    max_memory_mb=100,  # Limit memory usage
    progress=True
)

# Large dataset
large_dataset = range(1000000)

# Process in batches
results = []
for batch_result in processor.process(large_dataset, process_batch):
    results.extend(batch_result)

print(f"Processed {len(results)} items")
```

**Advanced Batch Processing:**

```python
from pyferris import BatchProcessor

class CustomBatchProcessor:
    def __init__(self):
        self.batch_processor = BatchProcessor(
            batch_size=5000,
            max_memory_mb=200,
            progress=True
        )
    
    def process_file_data(self, filename):
        """Process large file in batches."""
        def read_file_lines():
            with open(filename, 'r') as f:
                for line in f:
                    yield line.strip()
        
        def process_batch(lines):
            # Process each batch of lines
            return [line.upper() for line in lines if line]
        
        results = []
        for batch_result in self.batch_processor.process(read_file_lines(), process_batch):
            results.extend(batch_result)
        
        return results

# Usage
processor = CustomBatchProcessor()
processed_lines = processor.process_file_data('large_file.txt')
```

## Progress Tracking

### ProgressTracker

Monitor the progress of long-running parallel operations.

```python
from pyferris import parallel_map, ProgressTracker
import time

def slow_operation(x):
    time.sleep(0.1)  # Simulate slow work
    return x * x

data = range(100)

# Basic progress tracking
tracker = ProgressTracker(total=len(data), desc="Processing")
results = parallel_map(slow_operation, data, progress=tracker)

# Advanced progress tracking with custom update frequency
tracker = ProgressTracker(
    total=len(data),
    desc="Complex processing",
    update_frequency=10,  # Update every 10 items
    show_eta=True,  # Show estimated time of arrival
    show_speed=True  # Show items per second
)
results = parallel_map(slow_operation, data, progress=tracker)
```

**Custom Progress Callback:**

```python
from pyferris import parallel_map

def progress_callback(completed, total, elapsed_time):
    percentage = (completed / total) * 100
    speed = completed / elapsed_time if elapsed_time > 0 else 0
    print(f"Progress: {percentage:.1f}% ({completed}/{total}) - {speed:.1f} items/sec")

def long_computation(x):
    time.sleep(0.05)
    return x ** 3

data = range(200)
results = parallel_map(
    long_computation, 
    data, 
    progress_callback=progress_callback
)
```

## Result Collection

### ResultCollector

Collect and manage results from parallel operations efficiently.

```python
from pyferris import ResultCollector, parallel_map

def generate_data(x):
    return {
        'id': x,
        'value': x * x,
        'category': 'even' if x % 2 == 0 else 'odd'
    }

# Create result collector
collector = ResultCollector(
    max_size=10000,  # Maximum number of results to keep in memory
    auto_save=True,  # Automatically save to disk when full
    save_path='results.json'
)

data = range(1000)
results = parallel_map(generate_data, data)

# Collect results
for result in results:
    collector.add(result)

# Get collected results
all_results = collector.get_results()
print(f"Collected {len(all_results)} results")

# Filter results
even_results = collector.filter(lambda r: r['category'] == 'even')
print(f"Even results: {len(even_results)}")

# Save to file
collector.save_to_file('processed_results.json')
```

## Performance Considerations

### Choosing the Right Operation

```python
# For simple transformations on large datasets
results = parallel_map(transform_function, large_dataset)

# For filtering with expensive predicates
filtered = parallel_filter(expensive_predicate, dataset)

# For reductions that can be parallelized
total = parallel_reduce(combine_function, dataset)

# For sorting large datasets
sorted_data = parallel_sort(large_unsorted_dataset)
```

### Optimal Chunk Sizes

```python
from pyferris import set_chunk_size

# For CPU-intensive operations
set_chunk_size(100)  # Smaller chunks for better load balancing

# For I/O-intensive operations
set_chunk_size(1000)  # Larger chunks to reduce overhead

# For memory-intensive operations
set_chunk_size(50)  # Very small chunks to manage memory usage
```

### Memory Management

```python
import gc
from pyferris import parallel_map, BatchProcessor

# For very large datasets, use batch processing
def process_large_dataset(data):
    batch_processor = BatchProcessor(
        batch_size=10000,
        max_memory_mb=500
    )
    
    results = []
    for batch_result in batch_processor.process(data, transform_function):
        results.extend(batch_result)
        
        # Periodic garbage collection for long-running processes
        if len(results) % 100000 == 0:
            gc.collect()
    
    return results
```

## Error Handling

```python
from pyferris import parallel_map
import logging

def safe_operation(x):
    try:
        if x < 0:
            raise ValueError("Negative values not allowed")
        return x * x
    except Exception as e:
        logging.error(f"Error processing {x}: {e}")
        return None  # Return None for failed operations

def filter_none(x):
    return x is not None

data = range(-10, 11)  # Includes negative numbers
results = parallel_map(safe_operation, data)
valid_results = parallel_filter(filter_none, results)
print(list(valid_results))
```

## Best Practices

1. **Profile Before Parallelizing**: Always measure sequential performance first
2. **Right-size Your Data**: Parallel operations excel with datasets > 1,000 items
3. **Consider Memory Usage**: Parallel operations may use more memory
4. **Use Progress Tracking**: For long-running operations, always show progress
5. **Handle Errors Gracefully**: Plan for failures in parallel execution
6. **Batch Large Datasets**: Use BatchProcessor for very large datasets
7. **Choose Appropriate Chunk Sizes**: Balance between overhead and parallelism

## Next Steps

- Learn about [Executor](executor.md) for advanced task management
- Explore [Async Operations](async_ops.md) for asynchronous parallel processing
- Check out [Examples](examples.md) for real-world usage patterns
