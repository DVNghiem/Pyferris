# Pyferris Profiling Documentation

## Overview

The Pyferris profiling module provides comprehensive tools for analyzing performance, identifying bottlenecks, and optimizing parallel processing applications. This module includes detailed timing analysis, memory usage tracking, performance counters, and automatic worker tuning capabilities.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Classes](#core-classes)
3. [Functions](#functions)
4. [Usage Patterns](#usage-patterns)
5. [Performance Optimization](#performance-optimization)
6. [Best Practices](#best-practices)
7. [Examples](#examples)
8. [API Reference](#api-reference)

## Quick Start

```python
from pyferris import Profiler, auto_tune_workers, parallel_map
import time

# Basic profiling
profiler = Profiler()
profiler.start()

# Your code here
data = range(1000)
results = parallel_map(lambda x: x * x, data)

elapsed = profiler.stop()
print(f"Total execution time: {elapsed:.2f}s")
```

## Core Classes

### Profiler

The `Profiler` class is the main tool for performance analysis, providing:
- **Timing Analysis**: Measure execution time of operations
- **Memory Tracking**: Monitor memory usage patterns
- **Performance Counters**: Track custom metrics and events
- **Comprehensive Reporting**: Generate detailed performance reports

#### Key Features

- **Thread-safe**: Can be used safely in multi-threaded applications
- **Context managers**: Convenient timing with `with` statements
- **Decorators**: Profile functions with decorators
- **Hierarchical timing**: Track nested operations
- **Memory profiling**: Monitor memory allocation patterns

#### Basic Usage

```python
from pyferris import Profiler

# Create profiler instance
profiler = Profiler()

# Start overall profiling
profiler.start()

# Time specific operations
profiler.start_timer("data_processing")
# ... your code ...
profiler.stop_timer("data_processing")

# Track memory usage
profiler.record_memory("dataset_size", 1024 * 1024)

# Increment counters
profiler.increment_counter("items_processed", 100)

# Get results
total_time = profiler.stop()
report = profiler.get_report()
```

## Functions

### auto_tune_workers()

Automatically determines the optimal number of workers for a given task by benchmarking different configurations.

```python
def auto_tune_workers(
    task_function: Callable,
    sample_data: List[Any],
    min_workers: Optional[int] = None,
    max_workers: Optional[int] = None,
    test_duration: float = 1.0,
) -> Dict[str, Any]
```

**Parameters:**
- `task_function`: The function to benchmark
- `sample_data`: Sample data to use for benchmarking
- `min_workers`: Minimum number of workers to test (default: 1)
- `max_workers`: Maximum number of workers to test (default: CPU count)
- `test_duration`: How long to test each configuration in seconds

**Returns:**
- Dictionary with `optimal_workers`, `best_throughput`, and `tested_workers`

### profile_parallel_operation()

Profiles a parallel operation and returns both results and profiling data.

```python
def profile_parallel_operation(
    operation_func: Callable,
    *args,
    profiler: Optional[Profiler] = None,
    operation_name: str = "parallel_operation",
    **kwargs
) -> tuple
```

## Usage Patterns

### 1. Context Manager Pattern

```python
profiler = Profiler()

with profiler.timer("data_loading"):
    data = load_large_dataset()

with profiler.timer("processing"):
    results = process_data(data)

print(profiler.get_timings())
```

### 2. Decorator Pattern

```python
profiler = Profiler()

@profiler.profile_function("expensive_calculation")
def compute_results(data):
    return [complex_operation(x) for x in data]

results = compute_results(my_data)
print(profiler.get_report())
```

### 3. Manual Timing Pattern

```python
profiler = Profiler()
profiler.start()

for batch in data_batches:
    profiler.start_timer("batch_processing")
    process_batch(batch)
    elapsed = profiler.stop_timer("batch_processing")
    
    profiler.record_memory("batch_memory", get_memory_usage())
    profiler.increment_counter("batches_processed")

total_time = profiler.stop()
```

### 4. Parallel Operation Profiling

```python
from pyferris import profile_parallel_operation, parallel_map

def cpu_intensive_task(x):
    return sum(i * i for i in range(x * 100))

data = range(1000)
results, report = profile_parallel_operation(
    parallel_map, cpu_intensive_task, data,
    operation_name="parallel_squares"
)

print(f"Processing time: {report['timings']['parallel_squares']:.2f}s")
print(f"Total time: {report['total_elapsed']:.2f}s")
```

## Performance Optimization

### Worker Count Optimization

```python
from pyferris import auto_tune_workers, set_worker_count

def my_task(item):
    # Your processing logic
    return process_item(item)

# Automatically find optimal worker count
sample_data = generate_sample_data(100)
tuning_result = auto_tune_workers(
    my_task, 
    sample_data,
    test_duration=5.0
)

optimal_workers = tuning_result['optimal_workers']
print(f"Optimal workers: {optimal_workers}")

# Apply the optimization
set_worker_count(optimal_workers)
```

### Memory Usage Analysis

```python
import psutil
import os

profiler = Profiler()

def track_memory(operation_name):
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    profiler.record_memory(operation_name, int(memory_mb))

profiler.start()

# Track memory at different points
track_memory("startup")

large_data = create_large_dataset()
track_memory("after_data_creation")

results = parallel_process(large_data)
track_memory("after_processing")

memory_report = profiler.get_memory_usage()
print(f"Memory usage: {memory_report}")
```

### Bottleneck Identification

```python
profiler = Profiler()
profiler.start()

# Profile different components
with profiler.timer("data_loading"):
    data = load_data()

with profiler.timer("preprocessing"):
    preprocessed = preprocess(data)

with profiler.timer("parallel_processing"):
    results = parallel_map(complex_function, preprocessed)

with profiler.timer("postprocessing"):
    final_results = postprocess(results)

# Analyze bottlenecks
timings = profiler.get_timings()
bottleneck = max(timings, key=timings.get)
print(f"Bottleneck: {bottleneck} ({timings[bottleneck]:.2f}s)")
```

## Best Practices

### 1. Hierarchical Profiling

```python
profiler = Profiler()

def process_with_profiling(data_batch):
    profiler.start_timer("total_batch")
    
    profiler.start_timer("validation")
    validate_data(data_batch)
    profiler.stop_timer("validation")
    
    profiler.start_timer("transformation")
    transformed = transform_data(data_batch)
    profiler.stop_timer("transformation")
    
    profiler.start_timer("computation")
    result = compute_results(transformed)
    profiler.stop_timer("computation")
    
    profiler.stop_timer("total_batch")
    profiler.increment_counter("batches_completed")
    
    return result
```

### 2. Resource Monitoring

```python
class ResourceProfiler:
    def __init__(self):
        self.profiler = Profiler()
        self.start_cpu = None
        self.start_memory = None
    
    def start_monitoring(self):
        self.profiler.start()
        process = psutil.Process()
        self.start_cpu = process.cpu_percent()
        self.start_memory = process.memory_info().rss
    
    def stop_monitoring(self):
        process = psutil.Process()
        end_cpu = process.cpu_percent()
        end_memory = process.memory_info().rss
        
        self.profiler.record_memory("peak_memory", end_memory)
        self.profiler.record_memory("memory_delta", end_memory - self.start_memory)
        
        elapsed = self.profiler.stop()
        
        return {
            'elapsed_time': elapsed,
            'cpu_usage': end_cpu,
            'memory_used': end_memory - self.start_memory,
            'profiling_data': self.profiler.get_report()
        }
```

### 3. Comparative Analysis

```python
def compare_implementations(implementations, test_data):
    """Compare different implementations using profiling."""
    results = {}
    
    for name, impl_func in implementations.items():
        profiler = Profiler()
        
        # Profile the implementation
        results_data, report = profile_parallel_operation(
            impl_func, test_data, 
            operation_name=name,
            profiler=profiler
        )
        
        results[name] = {
            'timing': report['timings'][name],
            'memory': report.get('memory_usage', {}),
            'total_time': report['total_elapsed']
        }
    
    # Find the best implementation
    best = min(results.items(), key=lambda x: x[1]['timing'])
    print(f"Best implementation: {best[0]} ({best[1]['timing']:.2f}s)")
    
    return results
```

## Examples

### Example 1: Basic Profiling

```python
from pyferris import Profiler, parallel_map
import time

def simulate_work(item):
    """Simulate some CPU-intensive work."""
    time.sleep(0.01)  # Simulate I/O
    return sum(i * i for i in range(item * 10))  # CPU work

# Create and start profiler
profiler = Profiler()
profiler.start()

# Profile data preparation
profiler.start_timer("data_preparation")
data = list(range(100))
profiler.stop_timer("data_preparation")

# Profile parallel processing
profiler.start_timer("parallel_processing")
results = parallel_map(simulate_work, data)
profiler.stop_timer("parallel_processing")

# Get comprehensive report
total_time = profiler.stop()
report = profiler.get_report()

print(f"Total execution time: {total_time:.2f}s")
print(f"Data preparation: {report['timings']['data_preparation']:.4f}s")
print(f"Parallel processing: {report['timings']['parallel_processing']:.2f}s")
```

### Example 2: Auto-Tuning Workers

```python
from pyferris import auto_tune_workers, set_worker_count, parallel_map

def cpu_intensive_task(n):
    """CPU-intensive task for benchmarking."""
    return sum(i * i for i in range(n * 100))

# Generate sample data for tuning
sample_data = list(range(50, 150))

# Auto-tune worker count
print("Auto-tuning worker count...")
tuning_result = auto_tune_workers(
    cpu_intensive_task,
    sample_data,
    min_workers=1,
    max_workers=8,
    test_duration=2.0
)

print(f"Optimal workers: {tuning_result['optimal_workers']}")
print(f"Best throughput: {tuning_result['best_throughput']:.2f} items/sec")
print(f"Tested configurations: {tuning_result['tested_workers']}")

# Apply the optimized setting
set_worker_count(tuning_result['optimal_workers'])

# Run with optimized settings
large_dataset = list(range(1000))
results = parallel_map(cpu_intensive_task, large_dataset)
print(f"Processed {len(list(results))} items with {tuning_result['optimal_workers']} workers")
```

### Example 3: Memory Usage Tracking

```python
import psutil
import os
from pyferris import Profiler

class MemoryTracker:
    def __init__(self, profiler):
        self.profiler = profiler
        self.process = psutil.Process(os.getpid())
    
    def record_memory(self, label):
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        self.profiler.record_memory(label, int(memory_mb))
        return memory_mb

# Example usage
profiler = Profiler()
tracker = MemoryTracker(profiler)

profiler.start()

# Track memory at different stages
tracker.record_memory("startup")

# Create large data structure
large_list = [i * i for i in range(1000000)]
tracker.record_memory("after_data_creation")

# Process data
results = [x * 2 for x in large_list if x % 2 == 0]
tracker.record_memory("after_processing")

# Clean up
del large_list
tracker.record_memory("after_cleanup")

# Get memory report
memory_usage = profiler.get_memory_usage()
print("Memory usage throughout execution:")
for stage, memory_mb in memory_usage.items():
    print(f"  {stage}: {memory_mb} MB")
```

### Example 4: Performance Comparison

```python
from pyferris import Profiler, parallel_map, parallel_filter
import time

def compare_parallel_operations():
    """Compare different parallel operations."""
    
    # Test data
    data = list(range(10000))
    
    # Different operations to compare
    operations = {
        'map_square': lambda d: list(parallel_map(lambda x: x * x, d)),
        'map_cube': lambda d: list(parallel_map(lambda x: x * x * x, d)),
        'filter_even': lambda d: list(parallel_filter(lambda x: x % 2 == 0, d)),
        'filter_prime': lambda d: list(parallel_filter(is_prime, d)),
    }
    
    results = {}
    
    for name, operation in operations.items():
        profiler = Profiler()
        
        # Profile the operation
        start_time = time.time()
        profiler.start()
        
        result = operation(data)
        
        elapsed = profiler.stop()
        total_time = time.time() - start_time
        
        results[name] = {
            'profiled_time': elapsed,
            'wall_time': total_time,
            'result_count': len(result),
            'throughput': len(data) / total_time
        }
        
        print(f"{name}:")
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Throughput: {results[name]['throughput']:.0f} items/sec")
        print(f"  Results: {len(result)} items")
    
    return results

def is_prime(n):
    """Simple prime check for testing."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

# Run comparison
comparison_results = compare_parallel_operations()
```

## API Reference

### Profiler Class

#### Constructor
```python
Profiler()
```
Creates a new profiler instance.

#### Methods

##### start()
```python
start() -> None
```
Start overall profiling timer.

##### stop()
```python
stop() -> Optional[float]
```
Stop profiling and return total elapsed time in seconds.

##### start_timer(name)
```python
start_timer(name: str) -> None
```
Start timing a specific operation.

##### stop_timer(name)
```python
stop_timer(name: str) -> float
```
Stop timing an operation and return elapsed time.

##### record_memory(name, bytes_used)
```python
record_memory(name: str, bytes_used: int) -> None
```
Record memory usage for an operation.

##### increment_counter(name, value)
```python
increment_counter(name: str, value: int = 1) -> None
```
Increment a counter by the specified value.

##### get_timings()
```python
get_timings() -> Dict[str, float]
```
Get all timing measurements.

##### get_memory_usage()
```python
get_memory_usage() -> Dict[str, int]
```
Get all memory usage measurements.

##### get_counters()
```python
get_counters() -> Dict[str, int]
```
Get all counter values.

##### get_report()
```python
get_report() -> Dict[str, Any]
```
Get comprehensive profiling report with all measurements.

##### clear()
```python
clear() -> None
```
Clear all profiling data.

##### timer(name)
```python
timer(name: str) -> TimerContext
```
Context manager for timing operations.

##### profile_function(name)
```python
profile_function(name: Optional[str] = None) -> Callable
```
Decorator for profiling function execution.

### Functions

#### auto_tune_workers()
```python
auto_tune_workers(
    task_function: Callable,
    sample_data: List[Any],
    min_workers: Optional[int] = None,
    max_workers: Optional[int] = None,
    test_duration: float = 1.0,
) -> Dict[str, Any]
```

#### profile_parallel_operation()
```python
profile_parallel_operation(
    operation_func: Callable,
    *args,
    profiler: Optional[Profiler] = None,
    operation_name: str = "parallel_operation",
    **kwargs
) -> tuple
```

---

*This documentation covers the comprehensive profiling capabilities in Pyferris. For more examples and advanced usage patterns, see the examples directory and test files.*
