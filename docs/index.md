# PyFerris Documentation Index

PyFerris is a high-performance parallel processing library for Python, powered by Rust and PyO3. It provides powerful tools for parallel computation, data processing, and workflow management with excellent performance and ease of use.

## Getting Started

- **[User Guide](user_guide.md)** - Complete getting started guide with examples and best practices

## Core Features

### Parallel Processing
- **[Core Operations](core.md)** - Basic parallel operations (map, filter, reduce)
- **[Advanced Operations](advanced.md)** - Advanced parallel algorithms and batch processing

### Data Management
- **[Shared Memory Arrays](shared_memory_arrays.md)** - Thread-safe arrays supporting multiple data types
- **[I/O Operations](io.md)** - Efficient file reading, writing, and parallel I/O

### Workflow Management
- **[Pipeline Processing](pipeline_processing.md)** - Chain operations together for complex workflows
- **[Async Operations](async_operations.md)** - Efficient concurrent execution for I/O-bound tasks
- **[Custom Schedulers](custom_schedulers.md)** - Control how tasks are distributed and executed

### Configuration and Execution
- **[Executor](executor.md)** - Task execution management and configuration
- **[Configuration](README.md)** - Global configuration and performance tuning

## Examples and Use Cases

- **[Examples](examples.md)** - Comprehensive examples and real-world use cases

## API Reference

- **[API Reference](api_reference.md)** - Complete API documentation

## Quick Reference

### Basic Parallel Operations

```python
import pyferris

# Parallel map
results = pyferris.parallel_map(lambda x: x ** 2, [1, 2, 3, 4, 5])

# Parallel filter
evens = pyferris.parallel_filter(lambda x: x % 2 == 0, range(100))

# Parallel reduce
total = pyferris.parallel_reduce(lambda a, b: a + b, range(1000), initial=0)
```

### Shared Memory Arrays

```python
# Automatic type detection
int_array = pyferris.create_shared_array([1, 2, 3])        # → SharedArrayInt
float_array = pyferris.create_shared_array([1.0, 2.0])     # → SharedArray
string_array = pyferris.create_shared_array(['a', 'b'])    # → SharedArrayStr
object_array = pyferris.create_shared_array([1, 'mixed'])  # → SharedArrayObj

# All arrays support the same operations
int_array.append(4)
float_array.extend([3.0, 4.0])
result = int_array.parallel_map(lambda x: x * 2)
```

### Pipeline Processing

```python
# Create processing pipeline
pipeline = pyferris.Pipeline()
pipeline.add_stage(lambda data: [x.upper() for x in data])
pipeline.add_stage(lambda data: [x + "!" for x in data])
pipeline.add_stage(lambda data: sorted(data))

# Execute pipeline
result = pipeline.execute(["hello", "world"])
```

### Async Operations

```python
import asyncio

async def fetch_data(url):
    await asyncio.sleep(0.1)
    return f"Data from {url}"

# Parallel async execution
urls = ["api1.com", "api2.com", "api3.com"]
results = await pyferris.async_parallel_map(fetch_data, urls)
```

### Custom Schedulers

```python
# Work-stealing scheduler for dynamic load balancing
scheduler = pyferris.WorkStealingScheduler(num_workers=4)
results = scheduler.execute_tasks(compute_function, task_data)

# Priority-based scheduling
task = pyferris.create_priority_task(
    lambda: important_operation(),
    pyferris.TaskPriority.HIGH
)
result = pyferris.execute_with_priority([task])
```

## Feature Overview

| Feature | Description | Best Use Cases |
|---------|-------------|----------------|
| **Parallel Operations** | Core parallel map/filter/reduce | CPU-intensive data transformations |
| **Shared Memory Arrays** | Thread-safe multi-type arrays | Data sharing, concurrent access |
| **Pipeline Processing** | Multi-stage data workflows | ETL processes, data cleaning |
| **Async Operations** | Concurrent I/O processing | Network requests, file operations |
| **Custom Schedulers** | Task execution control | Load balancing, priority handling |
| **I/O Operations** | Parallel file processing | Large file handling, CSV/JSON processing |

## Performance Characteristics

PyFerris is designed for high performance:

- **Rust-powered backend** for maximum speed
- **Zero-copy operations** where possible
- **Thread-safe data structures** with minimal overhead
- **Intelligent work distribution** across CPU cores
- **Memory-efficient algorithms** for large datasets

## Common Use Cases

1. **Data Processing** - Transform large datasets in parallel
2. **ETL Pipelines** - Extract, transform, and load data efficiently  
3. **Web Scraping** - Concurrent HTTP requests and data extraction
4. **File Processing** - Parallel processing of large files
5. **Scientific Computing** - High-performance numerical computations
6. **Batch Processing** - Process large batches of tasks efficiently

## Integration

PyFerris integrates well with popular Python libraries:

- **Pandas** - Process DataFrames with parallel operations
- **NumPy** - Accelerate numerical computations
- **AsyncIO** - Combine with native async/await patterns
- **Requests** - Parallel HTTP requests for web APIs
- **JSON/CSV** - Built-in support for common data formats

## Architecture

PyFerris uses a hybrid Python/Rust architecture:

```
Python API Layer
      ↓
PyO3 Bindings
      ↓  
Rust Core (Performance-Critical Operations)
      ↓
System Resources (CPU, Memory, I/O)
```

This design provides:
- **Python ease of use** with familiar APIs
- **Rust performance** for computational kernels
- **Memory safety** and thread safety guarantees
- **Seamless integration** with existing Python codebases

## Documentation Navigation

### By Feature Type
- **Core Features**: [Core](core.md), [Advanced](advanced.md), [Executor](executor.md)
- **Data Structures**: [Shared Memory Arrays](shared_memory_arrays.md), [I/O](io.md)
- **Workflows**: [Pipelines](pipeline_processing.md), [Async](async_operations.md), [Schedulers](custom_schedulers.md)

### By Use Case
- **Getting Started**: [User Guide](user_guide.md)
- **Performance Optimization**: [Executor](executor.md), [Custom Schedulers](custom_schedulers.md)
- **Real-World Examples**: [Examples](examples.md)
- **Complete Reference**: [API Reference](api_reference.md)

### By Experience Level
- **Beginner**: [User Guide](user_guide.md) → [Core](core.md) → [Examples](examples.md)
- **Intermediate**: [Shared Memory Arrays](shared_memory_arrays.md) → [Pipelines](pipeline_processing.md) → [Advanced](advanced.md)
- **Advanced**: [Async Operations](async_operations.md) → [Custom Schedulers](custom_schedulers.md) → [API Reference](api_reference.md)

---

**Next Steps**: Start with the [User Guide](user_guide.md) for a comprehensive introduction to PyFerris, or jump directly to a specific feature documentation based on your needs.
