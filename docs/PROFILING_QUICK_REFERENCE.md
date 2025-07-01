# Pyferris Profiling Quick Reference

## Quick Start

```python
from pyferris import Profiler, auto_tune_workers

# Basic profiling
profiler = Profiler()
profiler.start()
# ... your code ...
elapsed = profiler.stop()
```

## Core Functions

### Basic Timing
```python
# Manual timing
profiler.start_timer("operation")
result = some_operation()
elapsed = profiler.stop_timer("operation")

# Context manager
with profiler.timer("operation"):
    result = some_operation()

# Decorator
@profiler.profile_function("operation")
def some_operation():
    # ... code ...
```

### Memory Tracking
```python
# Record memory usage
profiler.record_memory("dataset", 1024 * 1024)  # bytes

# Track memory with psutil
import psutil, os
process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
profiler.record_memory("current", int(memory_mb))
```

### Counters
```python
# Increment counters
profiler.increment_counter("items_processed")
profiler.increment_counter("errors", 5)
```

### Getting Results
```python
# Individual results
timings = profiler.get_timings()
memory = profiler.get_memory_usage()
counters = profiler.get_counters()

# Complete report
report = profiler.get_report()
print(f"Total time: {report['total_elapsed']:.2f}s")
print(f"Timings: {report['timings']}")
```

## Auto-Tuning Workers

### Basic Usage
```python
def my_task(item):
    return process_item(item)

sample_data = [1, 2, 3, 4, 5]
result = auto_tune_workers(my_task, sample_data)

optimal_workers = result['optimal_workers']
throughput = result['best_throughput']
```

### Advanced Tuning
```python
result = auto_tune_workers(
    my_task, 
    sample_data,
    min_workers=2,
    max_workers=16,
    test_duration=5.0
)

# Apply the result
from pyferris import set_worker_count
set_worker_count(result['optimal_workers'])
```

## Common Patterns

### Profile Parallel Operations
```python
from pyferris import profile_parallel_operation, parallel_map

results, report = profile_parallel_operation(
    parallel_map, my_function, data,
    operation_name="parallel_processing"
)
```

### Comparative Benchmarking
```python
def benchmark_implementations():
    implementations = {
        'method_a': lambda d: method_a(d),
        'method_b': lambda d: method_b(d)
    }
    
    results = {}
    for name, impl in implementations.items():
        profiler = Profiler()
        profiler.start()
        result = impl(test_data)
        elapsed = profiler.stop()
        results[name] = elapsed
    
    best = min(results, key=results.get)
    print(f"Best: {best} ({results[best]:.3f}s)")
```

### Memory Usage Analysis
```python
import psutil, os

def track_memory_usage():
    profiler = Profiler()
    process = psutil.Process(os.getpid())
    
    # Track at different points
    profiler.record_memory("start", process.memory_info().rss)
    
    data = create_large_dataset()
    profiler.record_memory("after_creation", process.memory_info().rss)
    
    results = process_data(data)
    profiler.record_memory("after_processing", process.memory_info().rss)
    
    return profiler.get_memory_usage()
```

### Bottleneck Identification
```python
def find_bottlenecks():
    profiler = Profiler()
    
    with profiler.timer("step_1"):
        step_1()
    with profiler.timer("step_2"):
        step_2()
    with profiler.timer("step_3"):
        step_3()
    
    timings = profiler.get_timings()
    bottleneck = max(timings, key=timings.get)
    print(f"Slowest step: {bottleneck} ({timings[bottleneck]:.2f}s)")
```

## Error Handling

### Safe Profiling
```python
profiler = Profiler()

try:
    profiler.start_timer("risky_operation")
    risky_operation()
    profiler.increment_counter("success")
except Exception as e:
    profiler.increment_counter("errors")
    raise
finally:
    profiler.stop_timer("risky_operation")
```

### Context Manager Safety
```python
# Automatically handles exceptions
with profiler.timer("operation"):
    potentially_failing_operation()
```

## Performance Tips

### Minimize Overhead
```python
# Group operations to reduce profiling calls
profiler.start_timer("batch_processing")
for item in batch:
    process_item(item)
profiler.stop_timer("batch_processing")

# Instead of timing each item individually
```

### Hierarchical Profiling
```python
profiler.start_timer("total_operation")

profiler.start_timer("sub_operation_1")
# ... code ...
profiler.stop_timer("sub_operation_1")

profiler.start_timer("sub_operation_2")
# ... code ...
profiler.stop_timer("sub_operation_2")

profiler.stop_timer("total_operation")
```

### Smart Sampling
```python
# Profile every Nth operation for long-running processes
counter = 0
for item in large_dataset:
    if counter % 100 == 0:  # Profile every 100th item
        with profiler.timer("sample_operation"):
            result = process_item(item)
    else:
        result = process_item(item)
    counter += 1
```

## Integration Examples

### With Parallel Processing
```python
from pyferris import parallel_map, Profiler

profiler = Profiler()

@profiler.profile_function("worker_task")
def worker_task(item):
    # This will be profiled for each call
    return complex_processing(item)

results = parallel_map(worker_task, data)
print(profiler.get_counters())  # Shows call counts
```

### With Custom Schedulers
```python
from pyferris import CustomScheduler, Profiler

class ProfiledScheduler(CustomScheduler):
    def __init__(self):
        super().__init__()
        self.profiler = Profiler()
    
    def schedule_task(self, task, *args):
        with self.profiler.timer("task_scheduling"):
            return super().schedule_task(task, *args)
    
    def get_performance_report(self):
        return self.profiler.get_report()
```

---

**Key Points:**
- Always call `profiler.start()` before profiling
- Use context managers for automatic cleanup
- Group operations to minimize overhead
- Clear profiling data with `profiler.clear()` when needed
- Use `auto_tune_workers()` to optimize parallel performance
