# PyFerris Level 2: Advanced Features Documentation

## Overview

PyFerris Level 2 introduces intermediate-level parallel processing capabilities that build upon the core Level 1 features. These advanced operations provide more sophisticated data processing patterns, batch processing capabilities, and enhanced result management.

## Features Summary

### Advanced Parallel Operations

- **`parallel_sort`**: Sort data in parallel with optional key functions and reverse ordering
- **`parallel_group_by`**: Group elements by key function in parallel  
- **`parallel_unique`**: Extract unique elements with optional key-based uniqueness
- **`parallel_partition`**: Split data into two groups based on a predicate function

### Batch Processing

- **`BatchProcessor`**: Process large datasets in configurable batches
- **`parallel_chunks`**: Process data in parallel chunks with custom functions

### Progress Tracking

- **`ProgressTracker`**: Monitor task progress with customizable display
- **Result Collection**: Ordered, unordered, and as-completed collection modes

## Advanced Parallel Operations

### parallel_sort

Sort an iterable in parallel with optional key function and reverse ordering.

```python
from pyferris import parallel_sort

# Basic sorting
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
sorted_numbers = parallel_sort(numbers)
# Result: [1, 1, 2, 3, 4, 5, 6, 9]

# Sort with key function
words = ['apple', 'pie', 'banana', 'cherry']
sorted_by_length = parallel_sort(words, key=len)
# Result: ['pie', 'apple', 'banana', 'cherry']

# Reverse sorting
descending = parallel_sort(numbers, reverse=True)
# Result: [9, 6, 5, 4, 3, 2, 1, 1]
```

**Parameters:**
- `iterable`: Input data to sort
- `key`: Optional function to compute sort key for each element
- `reverse`: Sort in descending order if True

**Performance Notes:**
- Uses parallel merge sort algorithm
- Efficient for large datasets (>1000 elements)
- Key function is applied in parallel

### parallel_group_by

Group elements by a key function in parallel.

```python
from pyferris import parallel_group_by

# Group numbers by remainder
data = list(range(1, 21))
groups = parallel_group_by(data, lambda x: x % 3)
# Result: {0: [3, 6, 9, 12, 15, 18], 1: [1, 4, 7, 10, 13, 16, 19], 2: [2, 5, 8, 11, 14, 17, 20]}

# Group strings by first letter
words = ['apple', 'apricot', 'banana', 'blueberry', 'cherry']
letter_groups = parallel_group_by(words, lambda w: w[0])
# Result: {'a': ['apple', 'apricot'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
```

**Parameters:**
- `iterable`: Input data to group
- `key_func`: Function to compute grouping key for each element
- `chunk_size`: Optional chunk size for parallel processing

**Returns:**
- Dictionary mapping keys to lists of grouped elements

### parallel_unique

Get unique elements from an iterable in parallel.

```python
from pyferris import parallel_unique

# Basic uniqueness
data = [1, 2, 2, 3, 3, 3, 4, 4, 5]
unique_items = parallel_unique(data)
# Result: [1, 2, 3, 4, 5]

# Unique with key function (case-insensitive)
words = ['Apple', 'APPLE', 'banana', 'BANANA']
unique_words = parallel_unique(words, key=str.lower)
# Result: ['Apple', 'banana'] (first occurrence preserved)
```

**Parameters:**
- `iterable`: Input data
- `key`: Optional function to compute uniqueness key for each element

**Returns:**
- List of unique elements (first occurrence preserved)

### parallel_partition

Partition elements based on a predicate function in parallel.

```python
from pyferris import parallel_partition

# Partition numbers into even/odd
numbers = list(range(10))
evens, odds = parallel_partition(lambda x: x % 2 == 0, numbers)
# evens: [0, 2, 4, 6, 8]
# odds: [1, 3, 5, 7, 9]

# Partition strings by length
words = ['cat', 'dog', 'elephant', 'mouse']
short, long = parallel_partition(lambda w: len(w) <= 4, words)
# short: ['cat', 'dog']
# long: ['elephant', 'mouse']
```

**Parameters:**
- `predicate`: Function that returns True/False for each element
- `iterable`: Input data to partition
- `chunk_size`: Optional chunk size for parallel processing

**Returns:**
- Tuple of (true_elements, false_elements)

## Batch Processing

### BatchProcessor

Process large datasets in configurable batches with parallel execution.

```python
from pyferris import BatchProcessor

# Initialize with custom parameters
bp = BatchProcessor(batch_size=100, max_workers=4)

# Process data in batches
def process_batch(batch_idx, batch_data):
    return {
        'batch': batch_idx,
        'sum': sum(batch_data),
        'count': len(batch_data),
        'average': sum(batch_data) / len(batch_data)
    }

data = list(range(1000))
results = bp.process_batches(data, process_batch)

# Results contain one entry per batch
print(f"Processed {len(results)} batches")
```

**Constructor Parameters:**
- `batch_size`: Size of each processing batch (default: 1000)
- `max_workers`: Maximum number of worker threads (default: auto)

**Methods:**
- `process_batches(data, processor_func)`: Process data in batches
- Properties: `batch_size`, `max_workers`

### parallel_chunks

Process data in parallel chunks with a custom function.

```python
from pyferris import parallel_chunks

def analyze_chunk(chunk_idx, chunk_data):
    return {
        'chunk': chunk_idx,
        'size': len(chunk_data),
        'sum': sum(chunk_data),
        'min': min(chunk_data),
        'max': max(chunk_data)
    }

data = list(range(100))
results = parallel_chunks(data, chunk_size=10, processor_func=analyze_chunk)

# Results contain analysis for each chunk
for result in results:
    print(f"Chunk {result['chunk']}: {result['size']} items, sum={result['sum']}")
```

**Parameters:**
- `iterable`: Input data to process
- `chunk_size`: Size of each chunk
- `processor_func`: Function to process each chunk (receives chunk_index, chunk_data)

## Progress Tracking

### ProgressTracker

Monitor task progress with customizable display.

```python
from pyferris import ProgressTracker

# Initialize progress tracker
tracker = ProgressTracker(total=100, desc="Processing data")

# Update progress during processing
for i in range(100):
    # Do some work
    process_item(i)
    
    # Update progress
    tracker.update(1)

# Close tracker and show final stats
tracker.close()
```

**Constructor Parameters:**
- `total`: Total number of items to process (optional)
- `desc`: Description for progress display

**Methods:**
- `update(n=1)`: Update progress by n items
- `close()`: Close tracker and display final statistics

**Features:**
- Automatic progress bar display
- Rate calculation (items/second)
- Elapsed time tracking
- Works with or without known total

### Result Collection Modes

Utility class for collecting results in different modes.

```python
from pyferris import ResultCollector

# Ordered collection (preserves original order)
ordered_results = ResultCollector.ordered(results)

# Unordered collection (may be faster)
unordered_results = ResultCollector.unordered(results)

# As-completed collection (for concurrent.futures integration)
for result in ResultCollector.as_completed(futures):
    handle_result(result)
```

## Data Processing Pipelines

Level 2 features excel at building sophisticated data processing pipelines:

```python
from pyferris import (
    parallel_sort, parallel_group_by, parallel_unique, parallel_partition,
    BatchProcessor, ProgressTracker
)

def data_processing_pipeline(raw_data):
    """Complete data processing pipeline using Level 2 features."""
    
    # Step 1: Filter valid data
    valid_data, invalid_data = parallel_partition(
        lambda item: item.get('valid', False),
        raw_data
    )
    
    # Step 2: Remove duplicates
    unique_data = parallel_unique(valid_data, key=lambda item: item['id'])
    
    # Step 3: Group by category
    category_groups = parallel_group_by(unique_data, lambda item: item['category'])
    
    # Step 4: Process each group in batches
    bp = BatchProcessor(batch_size=50)
    processed_groups = {}
    
    for category, items in category_groups.items():
        # Sort items by priority
        sorted_items = parallel_sort(items, key=lambda item: item['priority'], reverse=True)
        
        # Process in batches
        def process_category_batch(batch_idx, batch_data):
            # Custom processing logic
            return {
                'batch': batch_idx,
                'category': category,
                'processed_count': len(batch_data),
                'total_value': sum(item['value'] for item in batch_data)
            }
        
        batch_results = bp.process_batches(sorted_items, process_category_batch)
        processed_groups[category] = batch_results
    
    return processed_groups
```

## Performance Guidelines

### Choosing the Right Operation

1. **Use `parallel_sort`** when:
   - Dataset size > 1000 elements
   - Custom key functions are computationally expensive
   - Stable sorting is not required

2. **Use `parallel_group_by`** when:
   - Key function computation is expensive
   - Large number of groups expected
   - Dataset size > 10,000 elements

3. **Use `parallel_unique`** when:
   - Dataset has many duplicates
   - Key-based uniqueness checking is expensive
   - Dataset size > 1,000 elements

4. **Use `BatchProcessor`** when:
   - Processing very large datasets (>100,000 items)
   - Individual item processing is expensive
   - Memory usage needs to be controlled

### Optimization Tips

1. **Chunk Size Tuning:**
   ```python
   # For CPU-intensive operations, use smaller chunks
   results = parallel_group_by(data, expensive_key_func, chunk_size=100)
   
   # For simple operations, use larger chunks
   results = parallel_sort(data, chunk_size=10000)
   ```

2. **Memory Management:**
   ```python
   # Process very large datasets in batches to control memory
   bp = BatchProcessor(batch_size=1000)  # Adjust based on available memory
   
   # Use streaming for extremely large datasets
   for batch in data_stream:
       results = bp.process_batches(batch, process_func)
       save_results(results)  # Save immediately to free memory
   ```

3. **Progress Tracking for Long Operations:**
   ```python
   # Use progress tracking for operations taking >1 second
   tracker = ProgressTracker(total=len(large_dataset), desc="Processing data")
   
   for item in large_dataset:
       process_item(item)
       tracker.update(1)
   
   tracker.close()
   ```

## Integration Examples

### With NumPy

```python
import numpy as np
from pyferris import parallel_sort, parallel_group_by

# Sort arrays by their norms
arrays = [np.random.rand(100) for _ in range(1000)]
sorted_arrays = parallel_sort(arrays, key=lambda arr: np.linalg.norm(arr))

# Group arrays by their mean values
groups = parallel_group_by(arrays, lambda arr: int(np.mean(arr) * 10))
```

### With Pandas

```python
import pandas as pd
from pyferris import parallel_group_by, BatchProcessor

# Group DataFrames by computed statistics
dataframes = [pd.DataFrame(np.random.rand(100, 5)) for _ in range(100)]
groups = parallel_group_by(dataframes, lambda df: df.mean().sum() // 1)

# Process large datasets in batches
def process_df_batch(batch_idx, batch_dfs):
    combined = pd.concat(batch_dfs, ignore_index=True)
    return combined.describe().to_dict()

bp = BatchProcessor(batch_size=10)
results = bp.process_batches(dataframes, process_df_batch)
```

## Error Handling

Level 2 operations include robust error handling:

```python
from pyferris import parallel_sort, ParallelExecutionError

try:
    # This might fail if comparison is not supported
    mixed_data = [1, 'hello', 3.14, None]
    result = parallel_sort(mixed_data)
except ParallelExecutionError as e:
    print(f"Parallel operation failed: {e}")
    # Fallback to sequential processing
    result = sorted(mixed_data, key=lambda x: str(x))
```

## Best Practices

1. **Profile Before Optimizing:**
   ```python
   import time
   
   # Measure sequential vs parallel performance
   start = time.time()
   sequential_result = sorted(data, key=expensive_key)
   sequential_time = time.time() - start
   
   start = time.time()
   parallel_result = parallel_sort(data, key=expensive_key)
   parallel_time = time.time() - start
   
   print(f"Speedup: {sequential_time / parallel_time:.2f}x")
   ```

2. **Use Appropriate Data Structures:**
   ```python
   # Use lists for operations that preserve order
   ordered_data = parallel_sort(input_list)
   
   # Use sets for uniqueness operations when order doesn't matter
   unique_items = set(parallel_unique(input_data))
   ```

3. **Combine Operations for Efficiency:**
   ```python
   # Instead of multiple passes:
   # unique_data = parallel_unique(data)
   # sorted_data = parallel_sort(unique_data)
   # groups = parallel_group_by(sorted_data, key_func)
   
   # Use a single pipeline:
   pipeline_result = parallel_group_by(
       parallel_sort(parallel_unique(data)),
       key_func
   )
   ```

This comprehensive Level 2 feature set provides the foundation for building sophisticated, high-performance data processing applications with PyFerris.
