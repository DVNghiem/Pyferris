# User Guide - Getting Started with PyFerris

Welcome to PyFerris! This guide will help you get started with PyFerris's high-performance parallel processing capabilities. PyFerris combines the speed of Rust with the ease of Python to provide powerful tools for data processing, concurrent operations, and workflow management.

## Installation

```bash
pip install pyferris
```

## Core Concepts

PyFerris is organized around several key feature areas:

- **Parallel Processing** - High-speed parallel operations for data transformation
- **Shared Memory Arrays** - Thread-safe arrays supporting multiple data types
- **Pipeline Processing** - Chain operations together for complex workflows
- **Async Operations** - Efficient concurrent execution for I/O-bound tasks
- **Custom Schedulers** - Control how tasks are distributed and executed

## Quick Start Examples

### Basic Parallel Processing

```python
import pyferris

# Parallel map operation
numbers = list(range(10000))
squared = pyferris.parallel_map(lambda x: x ** 2, numbers)
print(f"Processed {len(squared)} numbers in parallel")

# Parallel filtering
evens = pyferris.parallel_filter(lambda x: x % 2 == 0, numbers)
print(f"Found {len(evens)} even numbers")

# Parallel reduction
total = pyferris.parallel_reduce(lambda a, b: a + b, numbers, initial=0)
print(f"Sum of all numbers: {total}")
```

### Shared Memory Arrays

```python
import pyferris

# Automatic type detection
int_array = pyferris.create_shared_array([1, 2, 3, 4, 5])
float_array = pyferris.create_shared_array([1.1, 2.2, 3.3])
string_array = pyferris.create_shared_array(['hello', 'world'])

# All arrays support the same operations
int_array.append(6)
float_array.extend([4.4, 5.5])
string_array.append('!')

print(f"Int array: {int_array.to_list()}")
print(f"Float array: {float_array.to_list()}")
print(f"String array: {string_array.to_list()}")
```

### Pipeline Processing

```python
import pyferris

# Create a data processing pipeline
pipeline = pyferris.Pipeline()
pipeline.add_stage(lambda data: [x.upper() for x in data])  # Uppercase
pipeline.add_stage(lambda data: [x + "!" for x in data])    # Add exclamation
pipeline.add_stage(lambda data: sorted(data))               # Sort

# Execute pipeline
words = ["hello", "world", "python"]
result = pipeline.execute(words)
print(f"Pipeline result: {result}")  # ['HELLO!', 'PYTHON!', 'WORLD!']
```

### Async Operations

```python
import pyferris
import asyncio

async def async_example():
    # Define async function
    async def fetch_data(url):
        await asyncio.sleep(0.1)  # Simulate network request
        return f"Data from {url}"
    
    # Parallel async execution
    urls = ["api1.com", "api2.com", "api3.com"]
    results = await pyferris.async_parallel_map(fetch_data, urls)
    print(f"Fetched data from {len(results)} URLs")

# Run async example
asyncio.run(async_example())
```

### Custom Schedulers

```python
import pyferris

# Work-stealing scheduler for load balancing
scheduler = pyferris.WorkStealingScheduler(num_workers=4)

def compute_task(n):
    return sum(i * i for i in range(n))

# Execute with custom scheduling
tasks = [1000, 2000, 500, 1500]
results = scheduler.execute_tasks(compute_task, tasks)
print(f"Computed {len(results)} results with work stealing")
```

## Common Patterns

### Data Processing Workflow

```python
import pyferris

def complete_data_workflow():
    """Complete data processing workflow example"""
    
    # 1. Start with raw data
    raw_data = [f"  item_{i}  " for i in range(1000)]
    
    # 2. Create shared array for efficient processing
    shared_data = pyferris.create_shared_array(raw_data)
    
    # 3. Build processing pipeline
    pipeline = pyferris.Pipeline()
    
    # Stage 1: Clean data
    pipeline.add_stage(lambda data: [item.strip().lower() for item in data])
    
    # Stage 2: Parallel transformation
    pipeline.add_stage(lambda data: pyferris.parallel_map(lambda x: x.replace('_', ' '), data))
    
    # Stage 3: Filter results
    pipeline.add_stage(lambda data: pyferris.parallel_filter(lambda x: 'item' in x, data))
    
    # 4. Execute workflow
    clean_data = pipeline.execute(shared_data.to_list())
    
    # 5. Final aggregation
    result_count = len(clean_data)
    sample_items = clean_data[:5]
    
    return {
        'total_processed': result_count,
        'sample_results': sample_items,
        'processing_stages': 3
    }

# Run complete workflow
workflow_result = complete_data_workflow()
print("Workflow completed:")
print(f"  Processed: {workflow_result['total_processed']} items")
print(f"  Sample: {workflow_result['sample_results']}")
```

### High-Performance Computing

```python
import pyferris
import time

def hpc_example():
    """High-performance computing example"""
    
    # Large dataset
    data = list(range(100000))
    
    # CPU-intensive function
    def complex_calculation(x):
        return sum(i ** 2 + i for i in range(x % 100 + 1))
    
    # Sequential vs Parallel comparison
    start_time = time.time()
    sequential_results = [complex_calculation(x) for x in data[:1000]]
    sequential_time = time.time() - start_time
    
    start_time = time.time()
    parallel_results = pyferris.parallel_map(complex_calculation, data[:1000])
    parallel_time = time.time() - start_time
    
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    
    print(f"Sequential time: {sequential_time:.3f}s")
    print(f"Parallel time: {parallel_time:.3f}s")
    print(f"Speedup: {speedup:.2f}x")
    
    return parallel_results

hpc_results = hpc_example()
```

### Concurrent I/O Processing

```python
import pyferris
import asyncio

async def concurrent_io_example():
    """Concurrent I/O processing example"""
    
    # Simulate file processing
    async def process_file(filename):
        # Simulate I/O delay
        await asyncio.sleep(0.1)
        return f"Processed {filename}"
    
    async def validate_result(result):
        # Simulate validation
        await asyncio.sleep(0.05)
        return "Processed" in result
    
    # File list
    files = [f"file_{i}.txt" for i in range(20)]
    
    # Process files concurrently
    processed = await pyferris.async_parallel_map(process_file, files)
    
    # Validate results concurrently
    valid_results = await pyferris.async_parallel_filter(validate_result, processed)
    
    return {
        'files_processed': len(processed),
        'valid_results': len(valid_results),
        'success_rate': len(valid_results) / len(processed) * 100
    }

# Run concurrent I/O example
io_result = asyncio.run(concurrent_io_example())
print(f"I/O Processing: {io_result['files_processed']} files, "
      f"{io_result['success_rate']:.1f}% success rate")
```

## Performance Tips

### 1. Choose the Right Tool

- **parallel_map/filter/reduce** for CPU-intensive tasks
- **async_parallel_map/filter** for I/O-bound tasks
- **SharedArray** for data sharing between operations
- **Pipeline** for multi-stage processing
- **Custom Schedulers** for specialized workload patterns

### 2. Optimize Data Structures

```python
import pyferris

# Use shared arrays for repeated operations
data = list(range(10000))
shared_data = pyferris.create_shared_array(data)

# Efficient: operate on shared array
result1 = shared_data.parallel_map(lambda x: x * 2)
result2 = shared_data.parallel_map(lambda x: x + 1)

# Less efficient: recreate arrays each time
# result1 = pyferris.parallel_map(lambda x: x * 2, data)
# result2 = pyferris.parallel_map(lambda x: x + 1, data)
```

### 3. Pipeline Optimization

```python
import pyferris

# Efficient: combine related operations
efficient_pipeline = pyferris.Pipeline()
efficient_pipeline.add_stage(lambda data: [x.strip().lower().replace(' ', '_') for x in data])

# Less efficient: separate stages for each operation
# inefficient_pipeline = pyferris.Pipeline()
# inefficient_pipeline.add_stage(lambda data: [x.strip() for x in data])
# inefficient_pipeline.add_stage(lambda data: [x.lower() for x in data])
# inefficient_pipeline.add_stage(lambda data: [x.replace(' ', '_') for x in data])
```

### 4. Memory Management

```python
import pyferris

def memory_efficient_processing(large_dataset):
    """Process large datasets efficiently"""
    
    # Process in chunks to manage memory
    chunk_size = 1000
    results = []
    
    for i in range(0, len(large_dataset), chunk_size):
        chunk = large_dataset[i:i + chunk_size]
        
        # Process chunk
        chunk_result = pyferris.parallel_map(lambda x: x * x, chunk)
        
        # Aggregate immediately to free memory
        chunk_sum = sum(chunk_result)
        results.append(chunk_sum)
        
        # chunk_result goes out of scope and can be garbage collected
    
    return results

# Use for very large datasets
# large_data = list(range(1000000))
# chunk_sums = memory_efficient_processing(large_data)
```

## Error Handling

### Graceful Error Handling

```python
import pyferris

def safe_parallel_processing(data):
    """Parallel processing with error handling"""
    
    def safe_operation(item):
        try:
            # Operation that might fail
            if item < 0:
                raise ValueError(f"Negative value: {item}")
            return item ** 2
        except Exception as e:
            # Return error indicator instead of crashing
            return f"ERROR: {e}"
    
    # Process all items, errors won't stop the whole operation
    results = pyferris.parallel_map(safe_operation, data)
    
    # Separate successful results from errors
    successes = [r for r in results if not str(r).startswith("ERROR")]
    errors = [r for r in results if str(r).startswith("ERROR")]
    
    return {
        'successes': successes,
        'errors': errors,
        'success_rate': len(successes) / len(results) * 100
    }

# Test with mixed data
test_data = [1, 2, -3, 4, -5, 6]
result = safe_parallel_processing(test_data)
print(f"Success rate: {result['success_rate']:.1f}%")
print(f"Errors: {result['errors']}")
```

### Pipeline Error Recovery

```python
import pyferris

def resilient_pipeline():
    """Pipeline with error recovery"""
    
    pipeline = pyferris.Pipeline()
    
    def stage_with_recovery(data):
        """Pipeline stage that handles errors gracefully"""
        good_items = []
        error_count = 0
        
        for item in data:
            try:
                # Processing that might fail
                processed = item.upper()
                good_items.append(processed)
            except AttributeError:
                # Handle non-string items
                good_items.append(str(item).upper())
                error_count += 1
        
        print(f"Stage processed {len(good_items)} items, {error_count} with errors")
        return good_items
    
    pipeline.add_stage(stage_with_recovery)
    pipeline.add_stage(lambda data: [item + "!" for item in data])
    
    # Mixed data types that might cause errors
    mixed_data = ["hello", 123, "world", None, "python"]
    result = pipeline.execute(mixed_data)
    
    return result

resilient_result = resilient_pipeline()
print(f"Resilient pipeline result: {resilient_result}")
```

## Integration Examples

### With Popular Libraries

```python
import pyferris
# import pandas as pd  # Uncomment if pandas is available
# import numpy as np   # Uncomment if numpy is available

def integrate_with_pandas():
    """Example integration with pandas (conceptual)"""
    
    # Simulate pandas DataFrame
    data = {
        'values': list(range(1000)),
        'categories': ['A', 'B', 'C'] * 334  # Cycling categories
    }
    
    # PyFerris can process pandas data efficiently
    processed_values = pyferris.parallel_map(lambda x: x ** 2, data['values'])
    
    # Create new dataset with processed values
    result = {
        'original': data['values'][:10],
        'processed': processed_values[:10],
        'categories': data['categories'][:10]
    }
    
    return result

# pandas_integration = integrate_with_pandas()
# print("Pandas integration:", pandas_integration)

def integrate_with_numpy():
    """Example integration with numpy (conceptual)"""
    
    # Simulate numpy array operations
    data = list(range(10000))
    
    # PyFerris parallel operations on numpy-like data
    squared = pyferris.parallel_map(lambda x: x ** 2, data)
    filtered = pyferris.parallel_filter(lambda x: x > 5000, squared)
    
    return {
        'original_size': len(data),
        'after_square': len(squared),
        'after_filter': len(filtered),
        'sample': filtered[:5]
    }

numpy_integration = integrate_with_numpy()
print("NumPy-like integration:", numpy_integration)
```

## Next Steps

### Advanced Features

1. **Explore Custom Schedulers** - Learn about WorkStealingScheduler, PriorityScheduler, and AdaptiveScheduler
2. **Master Async Operations** - Dive deeper into concurrent processing with async_parallel_map and AsyncExecutor
3. **Build Complex Pipelines** - Create multi-stage data processing workflows
4. **Optimize Performance** - Use profiling and benchmarking to optimize your applications

### Feature-Specific Guides

- [Shared Memory Arrays](shared_memory_arrays.md) - Complete guide to multi-type arrays
- [Pipeline Processing](pipeline_processing.md) - Build complex data workflows
- [Async Operations](async_operations.md) - Master concurrent programming
- [Custom Schedulers](custom_schedulers.md) - Control task execution strategies

### Best Practices

1. **Start Simple** - Begin with basic parallel_map/filter operations
2. **Profile Performance** - Measure before optimizing
3. **Handle Errors Gracefully** - Always plan for failure cases
4. **Choose Appropriate Tools** - Match the tool to your workload characteristics
5. **Monitor Resource Usage** - Keep an eye on CPU and memory consumption

## Community and Support

PyFerris is designed to be intuitive and powerful. As you explore the library:

- Start with simple examples and gradually build complexity
- Experiment with different features to find what works best for your use case
- Combine multiple features (pipelines + shared arrays + schedulers) for maximum efficiency
- Always test performance improvements to ensure they provide real benefits

Happy parallel processing with PyFerris!
