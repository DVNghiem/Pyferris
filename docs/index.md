# PyFerris Documentation Index

Welcome to the complete PyFerris documentation! This index provides quick access to all documentation resources.

## 📚 Documentation Structure

### Core Documentation
- **[README](README.md)** - Overview and quick start guide
- **[API Reference](api_reference.md)** - Complete API documentation
- **[Examples](examples.md)** - Comprehensive examples and use cases

### Feature Documentation
- **[Core Operations](core.md)** - Parallel map, filter, reduce, and starmap
- **[Executor](executor.md)** - Task execution and thread pool management  
- **[I/O Operations](io.md)** - File processing and parallel I/O

## 🚀 Quick Navigation

### By Use Case
- **Data Processing** → [Core Operations](core.md) + [Examples](examples.md#data-science-pipeline)
- **File Processing** → [I/O Operations](io.md) + [Examples](examples.md#file-processing-examples)
- **Task Management** → [Executor](executor.md) + [Examples](examples.md#executor-examples)
- **Performance Optimization** → [Examples](examples.md#performance-comparisons)

### By Experience Level
- **Beginner** → [README](README.md) → [Core Operations](core.md)
- **Intermediate** → [Executor](executor.md) → [I/O Operations](io.md)
- **Advanced** → [Examples](examples.md) → [API Reference](api_reference.md)

## 📖 Documentation Contents

### [Core Operations](core.md)
- `parallel_map()` - Transform data in parallel
- `parallel_filter()` - Filter data in parallel
- `parallel_reduce()` - Aggregate data in parallel
- `parallel_starmap()` - Apply functions to argument tuples
- Performance characteristics and best practices
- Error handling and optimization tips

### [Executor](executor.md)
- `Executor` class for task management
- Future objects and result handling
- Context managers and resource cleanup
- Priority scheduling and work stealing
- Performance monitoring and statistics
- Integration with asyncio

### [I/O Operations](io.md)
- **Simple I/O**: Text file operations
- **CSV Processing**: High-performance CSV reading/writing
- **JSON Operations**: JSON and JSON Lines support
- **Parallel I/O**: Batch file processing
- File utilities and directory operations
- Memory-efficient large file handling

### [Examples](examples.md)
- **Basic Operations**: Core functionality demonstrations
- **Real-World Use Cases**: Data science pipelines, log processing
- **Performance Comparisons**: PyFerris vs standard Python
- **Integration Examples**: NumPy, Pandas, async workflows

### [API Reference](api_reference.md)
- Complete function signatures and parameters
- Return types and error conditions
- Type hints and IDE support
- Exception handling reference

## 🔍 Quick Reference

### Core Functions
```python
from pyferris import parallel_map, parallel_filter, parallel_reduce, parallel_starmap

# Transform data
results = parallel_map(func, data)

# Filter data  
filtered = parallel_filter(predicate, data)

# Aggregate data
total = parallel_reduce(binary_func, data)

# Apply function to argument tuples
results = parallel_starmap(func, arg_tuples)
```

### Executor Usage
```python
from pyferris import Executor

with Executor(max_workers=4) as executor:
    future = executor.submit(function, args)
    result = future.result()
```

### File I/O
```python
from pyferris.io import simple_io, csv, json

# Simple file operations
content = simple_io.read_file('file.txt')
simple_io.write_file('output.txt', content)

# CSV operations
data = csv.read_csv('data.csv')
csv.write_csv('output.csv', processed_data)

# JSON operations
data = json.read_json('data.json')
json.write_jsonl('output.jsonl', records)
```

## 🎯 Common Patterns

### Data Processing Pipeline
```python
# 1. Load data in parallel
data = parallel_map(load_data_source, data_sources)

# 2. Filter valid records
valid_data = parallel_filter(is_valid, data)

# 3. Transform data
processed = parallel_map(transform_record, valid_data)

# 4. Aggregate results
summary = parallel_reduce(combine_results, processed)
```

### Batch File Processing
```python
from pyferris.io.parallel_io import ParallelFileProcessor

processor = ParallelFileProcessor(max_workers=8)
results = processor.process_files(file_list, process_function)
```

### Task Queue Processing
```python
with Executor(max_workers=6) as executor:
    # Submit all tasks
    futures = [executor.submit(process_task, task) for task in tasks]
    
    # Collect results as they complete
    for future in executor.as_completed(futures):
        result = future.result()
        handle_result(result)
```

## 💡 Tips for Success

1. **Start Simple**: Begin with basic `parallel_map()` before moving to advanced features
2. **Check Examples**: Look at [examples.md](examples.md) for patterns similar to your use case
3. **Performance**: Use [performance comparisons](examples.md#performance-comparisons) to validate improvements
4. **Error Handling**: Review error handling patterns in each module's documentation
5. **Resource Management**: Always use context managers (`with` statements) for executors

## 🛠️ Development Resources

- **Source Code**: Explore the `pyferris/` directory for implementation details
- **Examples**: Check the `examples/` directory for additional code samples
- **Tests**: Review the `tests/` directory for usage patterns

## 📞 Getting Help

- **Documentation Issues**: Check if your question is covered in the relevant section
- **Performance Questions**: See [performance comparisons](examples.md#performance-comparisons)
- **Integration Help**: Review [real-world examples](examples.md#real-world-use-cases)
- **API Questions**: Consult the [API reference](api_reference.md)

---

*This documentation covers PyFerris core, executor, and I/O features. For additional features and advanced functionality, refer to the main project documentation.*
