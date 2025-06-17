# Core Features

The PyFerris core module provides fundamental parallel processing operations that bypass Python's Global Interpreter Lock (GIL) for true parallelism. All operations are implemented in Rust for maximum performance.

## Overview

The core module includes four main parallel operations:
- `parallel_map` - Apply a function to each element in parallel
- `parallel_starmap` - Apply a function to unpacked argument tuples in parallel
- `parallel_filter` - Filter elements using a predicate function in parallel
- `parallel_reduce` - Reduce elements using a binary function in parallel

## API Reference

### `parallel_map(func, iterable, chunk_size=None)`

Apply a function to every item of an iterable in parallel.

**Parameters:**
- `func` (callable): Function to apply to each item
- `iterable` (iterable): Input data to process
- `chunk_size` (int, optional): Size of work chunks for load balancing

**Returns:**
- `list`: Results in the same order as input

**Example:**
```python
from pyferris import parallel_map

def square(x):
    return x * x

# Process 1 million numbers in parallel
numbers = range(1000000)
results = parallel_map(square, numbers)
print(f"First 10 results: {list(results)[:10]}")
# Output: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

**Performance Tips:**
- Use larger chunk sizes for simple functions to reduce overhead
- Use smaller chunk sizes for computationally expensive functions
- Let PyFerris auto-determine chunk size by omitting the parameter

### `parallel_starmap(func, iterable, chunk_size=None)`

Apply a function to arguments unpacked from tuples in parallel.

**Parameters:**
- `func` (callable): Function to apply to unpacked arguments
- `iterable` (iterable): Iterable of argument tuples
- `chunk_size` (int, optional): Size of work chunks

**Returns:**
- `list`: Results in the same order as input

**Example:**
```python
from pyferris import parallel_starmap

def multiply(x, y):
    return x * y

# Process pairs of numbers
pairs = [(1, 2), (3, 4), (5, 6), (7, 8)]
results = parallel_starmap(multiply, pairs)
print(results)
# Output: [2, 12, 30, 56]

# More complex example with different argument counts
def calculate(base, exponent, multiplier=1):
    return (base ** exponent) * multiplier

args = [(2, 3, 1), (3, 2, 2), (4, 2, 0.5)]
results = parallel_starmap(calculate, args)
print(results)
# Output: [8.0, 18.0, 8.0]
```

### `parallel_filter(predicate, iterable, chunk_size=None)`

Filter items from an iterable in parallel using a predicate function.

**Parameters:**
- `predicate` (callable): Function that returns True for items to keep
- `iterable` (iterable): Input data to filter
- `chunk_size` (int, optional): Size of work chunks

**Returns:**
- `list`: Filtered items that satisfy the predicate

**Example:**
```python
from pyferris import parallel_filter

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

# Find prime numbers up to 1000
numbers = range(1000)
primes = parallel_filter(is_prime, numbers)
print(f"Found {len(primes)} primes")
print(f"First 10 primes: {primes[:10]}")
# Output: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

### `parallel_reduce(func, iterable, initializer=None, chunk_size=None)`

Apply a function of two arguments cumulatively to items in parallel.

**Parameters:**
- `func` (callable): Binary function to apply cumulatively
- `iterable` (iterable): Input data to reduce
- `initializer` (any, optional): Initial value for the reduction
- `chunk_size` (int, optional): Size of work chunks

**Returns:**
- `any`: Single reduced result

**Example:**
```python
from pyferris import parallel_reduce

def add(x, y):
    return x + y

# Sum numbers from 1 to 1000
numbers = range(1, 1001)
total = parallel_reduce(add, numbers)
print(f"Sum: {total}")
# Output: 500500

# Find maximum with initializer
def max_func(x, y):
    return max(x, y)

numbers = [3, 7, 2, 9, 1, 5]
maximum = parallel_reduce(max_func, numbers, initializer=0)
print(f"Maximum: {maximum}")
# Output: 9

# Complex reduction: compute product of squares
def multiply(x, y):
    return x * y

def square(x):
    return x * x

numbers = range(1, 6)
squares = parallel_map(square, numbers)  # [1, 4, 9, 16, 25]
product = parallel_reduce(multiply, squares)
print(f"Product of squares: {product}")
# Output: 14400
```

## Performance Characteristics

### Threading Model
- Uses Rust's Rayon library for work-stealing parallelism
- Automatically determines optimal number of threads based on CPU cores
- No Python GIL limitations - true parallel execution

### Memory Usage
- Minimal memory overhead compared to sequential processing
- Efficient memory layout for cache optimization
- Automatic garbage collection of intermediate results

### Scalability
- Linear speedup for CPU-bound tasks
- Efficient load balancing across available cores
- Optimal performance on systems with 2-64 cores

## Best Practices

### Choosing the Right Operation

1. **Use `parallel_map`** when:
   - You need to transform each element independently
   - Order of results matters
   - Function is pure (no side effects)

2. **Use `parallel_filter`** when:
   - You need to select subset of data based on criteria
   - Predicate function is computationally expensive
   - You want to maintain order of filtered elements

3. **Use `parallel_reduce`** when:
   - You need to aggregate data into a single result
   - Reduction function is associative and commutative
   - You want to leverage parallel tree reduction

4. **Use `parallel_starmap`** when:
   - Each input is a tuple of arguments
   - Function takes multiple parameters
   - You need argument unpacking behavior

### Optimization Tips

1. **Chunk Size Tuning:**
   ```python
   # For simple operations, use larger chunks
   results = parallel_map(simple_func, data, chunk_size=10000)
   
   # For complex operations, use smaller chunks
   results = parallel_map(complex_func, data, chunk_size=100)
   ```

2. **Function Design:**
   ```python
   # Good: Pure function without side effects
   def process_item(x):
       return x ** 2 + x ** 0.5
   
   # Avoid: Functions with side effects
   def bad_process_item(x):
       print(f"Processing {x}")  # Side effect
       return x ** 2
   ```

3. **Memory Considerations:**
   ```python
   # Process large datasets in batches
   def process_large_dataset(data):
       batch_size = 100000
       results = []
       for i in range(0, len(data), batch_size):
           batch = data[i:i + batch_size]
           batch_results = parallel_map(process_func, batch)
           results.extend(batch_results)
       return results
   ```

## Error Handling

PyFerris provides robust error handling for parallel operations:

```python
from pyferris import parallel_map

def risky_operation(x):
    if x == 13:  # Unlucky number!
        raise ValueError("Unlucky number encountered")
    return x ** 2

try:
    # This will raise an exception when it encounters 13
    results = parallel_map(risky_operation, range(20))
except ValueError as e:
    print(f"Error occurred: {e}")
    # Handle error appropriately
```

## Integration Examples

### With NumPy
```python
import numpy as np
from pyferris import parallel_map

def numpy_operation(arr):
    return np.sum(arr ** 2)

# Process multiple arrays in parallel
arrays = [np.random.rand(1000) for _ in range(100)]
results = parallel_map(numpy_operation, arrays)
```

### With Pandas
```python
import pandas as pd
from pyferris import parallel_map

def process_group(group_data):
    df = pd.DataFrame(group_data)
    return df.groupby('category').sum()

# Process multiple data groups in parallel
data_groups = [generate_data() for _ in range(50)]
results = parallel_map(process_group, data_groups)
```

## Comparison with Built-in `map()`

| Feature | `map()` | `parallel_map()` |
|---------|---------|------------------|
| Execution | Sequential | Parallel |
| GIL Impact | Limited by GIL | GIL-free |
| Memory | Lazy evaluation | Eager evaluation |
| Performance | O(n) time | O(n/cores) time |
| Order | Preserved | Preserved |
| Error Handling | Standard Python | Enhanced with context |

## Advanced Usage

### Custom Chunk Size Strategy
```python
def adaptive_chunk_size(data_size, item_complexity):
    """Calculate optimal chunk size based on data characteristics."""
    base_chunk_size = max(1, data_size // (os.cpu_count() * 4))
    
    if item_complexity == 'simple':
        return base_chunk_size * 10
    elif item_complexity == 'complex':
        return max(1, base_chunk_size // 10)
    else:
        return base_chunk_size

# Use adaptive chunking
chunk_size = adaptive_chunk_size(len(data), 'complex')
results = parallel_map(complex_function, data, chunk_size=chunk_size)
```

### Nested Parallel Operations
```python
from pyferris import parallel_map

def process_matrix_row(row):
    # Each row is processed in parallel
    return parallel_map(lambda x: x ** 2, row)

# Process 2D matrix with nested parallelism
matrix = [[i + j for j in range(100)] for i in range(100)]
results = parallel_map(process_matrix_row, matrix)
```

This comprehensive core API provides the foundation for all parallel processing in PyFerris, offering both simplicity and high performance for a wide range of use cases.
