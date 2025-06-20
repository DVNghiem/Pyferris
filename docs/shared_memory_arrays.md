# Shared Memory Arrays

PyFerris provides high-performance shared memory arrays that support multiple data types with thread-safe operations. These arrays are designed for efficient parallel processing and data sharing across multiple threads.

## Overview

The shared memory array system includes:
- **SharedArray** - High-performance arrays for floating-point numbers
- **SharedArrayInt** - Optimized arrays for integers
- **SharedArrayStr** - Efficient arrays for strings
- **SharedArrayObj** - Generic arrays for any Python objects
- **create_shared_array()** - Smart factory function for automatic type detection

## Quick Start

```python
import pyferris

# Automatic type detection with factory function
float_array = pyferris.create_shared_array([1.0, 2.5, 3.14])     # → SharedArray
int_array = pyferris.create_shared_array([1, 2, 3, 4, 5])        # → SharedArrayInt
string_array = pyferris.create_shared_array(['hello', 'world'])   # → SharedArrayStr
mixed_array = pyferris.create_shared_array([1, 'text', [1,2]])   # → SharedArrayObj

# All arrays support the same operations
float_array.append(4.2)
int_array.extend([6, 7, 8])
string_array.append('!')

print(f"Float array: {float_array.to_list()}")
print(f"Int array: {int_array.to_list()}")
print(f"String array: {string_array.to_list()}")
```

## Array Types

### SharedArray (Float64)

Optimized for 64-bit floating-point numbers with high-performance mathematical operations.

```python
from pyferris import SharedArray

# Create with capacity
arr = SharedArray(capacity=100)

# Create from existing data
arr = SharedArray.from_data([1.1, 2.2, 3.3, 4.4])

# Mathematical operations
result = arr.parallel_map(lambda x: x * x)  # Parallel square operation
```

### SharedArrayInt (Integer64)

Specialized for 64-bit signed integers with optimized storage and operations.

```python
from pyferris import SharedArrayInt

# Create with capacity
arr = SharedArrayInt(capacity=1000)

# Create from existing data
arr = SharedArrayInt.from_data([10, 20, 30, 40, 50])

# Integer operations
arr.append(60)
arr.extend([70, 80, 90])
total_length = len(arr)
```

### SharedArrayStr (String)

Efficient storage and manipulation of string data with UTF-8 support.

```python
from pyferris import SharedArrayStr

# Create with capacity
arr = SharedArrayStr(capacity=50)

# Create from existing data
arr = SharedArrayStr.from_data(['apple', 'banana', 'cherry'])

# String operations
arr.append('date')
arr.set(0, 'avocado')  # Replace first element
fruits = arr.to_list()
```

### SharedArrayObj (Generic Objects)

Universal array type that can store any Python objects including mixed types.

```python
from pyferris import SharedArrayObj

# Create with capacity
arr = SharedArrayObj(capacity=20)

# Create from existing data
arr = SharedArrayObj.from_data([1, 'text', [1, 2, 3], {'key': 'value'}])

# Mixed type operations
arr.append(True)
arr.append(None)
arr.append(lambda x: x + 1)
objects = arr.to_list()
```

## Factory Function

The `create_shared_array()` function automatically detects the most appropriate array type based on your data.

```python
from pyferris import create_shared_array

# Type detection examples
arr1 = create_shared_array([1, 2, 3])           # → SharedArrayInt
arr2 = create_shared_array([1.0, 2.0, 3.0])     # → SharedArray
arr3 = create_shared_array(['a', 'b', 'c'])     # → SharedArrayStr
arr4 = create_shared_array([1, 'mixed', None])  # → SharedArrayObj

# Empty arrays default to integer type
empty_arr = create_shared_array([])             # → SharedArrayInt
```

### Type Detection Rules

1. **Integer** - If all elements are integers: `[1, 2, 3]`
2. **Float** - If all elements are numbers with decimals: `[1.0, 2.5, 3.14]`
3. **String** - If all elements are strings: `['hello', 'world']`
4. **Object** - If elements are mixed types: `[1, 'text', [1, 2]]`

## Common Operations

### Basic Operations

All array types support the same core operations:

```python
# Create array
arr = create_shared_array([1, 2, 3, 4, 5])

# Get array length
length = len(arr)

# Get element by index
value = arr.get(0)

# Set element by index
arr.set(1, 99)

# Add single element
arr.append(6)

# Add multiple elements
arr.extend([7, 8, 9])

# Convert to Python list
data = arr.to_list()

# Array slicing
subset = arr[1:4]  # Get elements from index 1 to 3
```

### Advanced Operations

#### Parallel Processing

```python
# Parallel map operation (available for numeric arrays)
numbers = create_shared_array([1.0, 2.0, 3.0, 4.0, 5.0])
squared = numbers.parallel_map(lambda x: x * x)
print(squared)  # [1.0, 4.0, 9.0, 16.0, 25.0]

# Works with integers too
integers = create_shared_array([1, 2, 3, 4, 5])
doubled = integers.parallel_map(lambda x: x * 2)
print(doubled)  # [2, 4, 6, 8, 10]
```

#### Thread-Safe Access

```python
import threading
from pyferris import create_shared_array

# Shared array accessible from multiple threads
shared_data = create_shared_array([0] * 1000)

def worker_thread(thread_id):
    for i in range(100):
        index = thread_id * 100 + i
        shared_data.set(index, thread_id)

# Create multiple threads
threads = []
for i in range(10):
    t = threading.Thread(target=worker_thread, args=(i,))
    threads.append(t)
    t.start()

# Wait for completion
for t in threads:
    t.join()

print(f"Processed {len(shared_data)} elements")
```

## Performance Characteristics

### Memory Efficiency

- **SharedArray**: 8 bytes per float64 element
- **SharedArrayInt**: 8 bytes per int64 element  
- **SharedArrayStr**: Variable length with UTF-8 encoding
- **SharedArrayObj**: Python object overhead + reference storage

### Thread Safety

All arrays use read-write locks (RwLock) for thread safety:
- Multiple readers can access simultaneously
- Writers have exclusive access
- No data races or corruption possible

### Capacity Management

Arrays automatically include buffer capacity for growth:
- Initial capacity: 150% of input data size (minimum +10)
- Efficient append/extend operations without frequent reallocations
- Capacity can be specified manually for optimal performance

## Error Handling

```python
from pyferris import create_shared_array

arr = create_shared_array([1, 2, 3])

try:
    # Index out of bounds
    value = arr.get(10)
except IndexError as e:
    print(f"Index error: {e}")

try:
    # Capacity exceeded (when full)
    while True:
        arr.append(1)  # Will eventually raise RuntimeError
except RuntimeError as e:
    print(f"Capacity error: {e}")
```

## Best Practices

### Choosing Array Types

1. **Use SharedArray** for mathematical computations with floats
2. **Use SharedArrayInt** for counters, indices, and integer calculations  
3. **Use SharedArrayStr** for text processing and string collections
4. **Use SharedArrayObj** for heterogeneous data or complex objects
5. **Use create_shared_array()** when type is determined at runtime

### Performance Optimization

```python
# Pre-allocate capacity for better performance
arr = SharedArrayInt(capacity=10000)  # Avoids reallocations

# Use parallel_map for CPU-intensive operations
large_array = create_shared_array(list(range(1000000)))
results = large_array.parallel_map(lambda x: x * x + 1)

# Batch operations are more efficient
arr.extend([1, 2, 3, 4, 5])  # Better than multiple append() calls
```

### Memory Management

```python
# Arrays are automatically freed when no longer referenced
def process_data():
    temp_array = create_shared_array(large_dataset)
    # Process temp_array
    return temp_array.to_list()
    # temp_array is automatically freed here
```

## Integration Examples

### With Other PyFerris Features

```python
import pyferris

# Combine with parallel processing
data = list(range(1000))
shared_array = pyferris.create_shared_array(data)

# Use with Pipeline
pipeline = pyferris.Pipeline()
pipeline.add_stage(lambda x: shared_array.parallel_map(lambda i: i * 2))
result = pipeline.execute(data)

# Use with AsyncExecutor
async_executor = pyferris.AsyncExecutor()
# Process array data asynchronously
```

### Data Science Workflows

```python
# Load and process large datasets
import pyferris

# Create shared arrays for different data types
ids = pyferris.create_shared_array(list(range(100000)))
scores = pyferris.create_shared_array([random.random() for _ in range(100000)])
labels = pyferris.create_shared_array([f"item_{i}" for i in range(100000)])

# Parallel processing
normalized_scores = scores.parallel_map(lambda x: (x - 0.5) * 2)
scaled_ids = ids.parallel_map(lambda x: x / 1000.0)

# Combine results
results = []
for i in range(len(ids)):
    results.append({
        'id': scaled_ids[i],
        'score': normalized_scores[i], 
        'label': labels.get(i)
    })
```

## API Reference

### Constructor Methods

```python
# Manual construction with capacity
SharedArray(capacity: int)
SharedArrayInt(capacity: int)  
SharedArrayStr(capacity: int)
SharedArrayObj(capacity: int)

# Construction from existing data
SharedArray.from_data(data: List[float])
SharedArrayInt.from_data(data: List[int])
SharedArrayStr.from_data(data: List[str]) 
SharedArrayObj.from_data(data: List[Any])

# Factory function
create_shared_array(data: List[Any]) -> Union[SharedArray, SharedArrayInt, SharedArrayStr, SharedArrayObj]
```

### Instance Methods

```python
# Core operations (all array types)
get(index: int) -> Any
set(index: int, value: Any) -> None
append(value: Any) -> None
extend(values: List[Any]) -> None
to_list() -> List[Any]
len() -> int

# Slicing (all array types)
__getitem__(slice) -> List[Any]

# Parallel operations (numeric arrays only)
parallel_map(func: Callable[[Any], Any]) -> List[Any]
```

This documentation provides comprehensive coverage of PyFerris shared memory arrays, focusing on practical usage patterns and real-world examples while maintaining technical accuracy.
