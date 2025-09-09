# Performance Guide

This guide provides comprehensive information on optimizing PyFerris performance, understanding when to use parallel processing, and getting the most out of your hardware resources.

## Table of Contents

1. [Understanding Performance](#understanding-performance)
2. [When to Use Parallel Processing](#when-to-use-parallel-processing)
3. [Configuration and Tuning](#configuration-and-tuning)
4. [Memory Optimization](#memory-optimization)
5. [CPU vs I/O Bound Workloads](#cpu-vs-io-bound-workloads)
6. [Benchmarking and Profiling](#benchmarking-and-profiling)
7. [Common Performance Pitfalls](#common-performance-pitfalls)
8. [Hardware Considerations](#hardware-considerations)
9. [Real-world Optimization Examples](#real-world-optimization-examples)

## Understanding Performance

### Parallel Processing Overhead

Every parallel operation has overhead costs:

- **Thread creation and management**
- **Data serialization/deserialization**
- **Inter-thread communication**
- **Result collection and merging**

Understanding these costs helps you make informed decisions about when parallelization will provide benefits.

```python
from pyferris import parallel_map, set_chunk_size
import time

def measure_overhead():
    """Measure the overhead of parallel processing for different workloads."""
    
    def light_work(x):
        return x * 2
    
    def medium_work(x):
        total = 0
        for i in range(100):
            total += i * x
        return total
    
    def heavy_work(x):
        total = 0
        for i in range(10000):
            total += i * x
        return total
    
    data_sizes = [100, 1000, 10000, 100000]
    work_types = [('light', light_work), ('medium', medium_work), ('heavy', heavy_work)]
    
    print("Overhead Analysis: Sequential vs Parallel")
    print("=" * 50)
    
    for work_name, work_func in work_types:
        print(f"\n{work_name.upper()} WORK:")
        print("-" * 20)
        
        for size in data_sizes:
            data = list(range(size))
            
            # Sequential execution
            start = time.time()
            seq_result = [work_func(x) for x in data]
            seq_time = time.time() - start
            
            # Parallel execution
            start = time.time()
            par_result = list(parallel_map(work_func, data))
            par_time = time.time() - start
            
            speedup = seq_time / par_time if par_time > 0 else 0
            overhead = ((par_time - seq_time) / seq_time * 100) if seq_time > 0 else 0
            
            print(f"Size {size:6d}: Sequential={seq_time:.4f}s, Parallel={par_time:.4f}s, "
                  f"Speedup={speedup:.2f}x, Overhead={overhead:+.1f}%")

measure_overhead()
```

### Performance Metrics

Key metrics to monitor:

- **Throughput**: Items processed per second
- **Latency**: Time to process a single item
- **Resource utilization**: CPU, memory, I/O usage
- **Scalability**: Performance change with data size
- **Efficiency**: Speedup relative to number of cores

## When to Use Parallel Processing

### Decision Matrix

```python
def should_use_parallel_processing(data_size, work_complexity, available_cores):
    """
    Decision helper for when to use parallel processing.
    
    Args:
        data_size: Number of items to process
        work_complexity: 'light', 'medium', 'heavy'
        available_cores: Number of CPU cores available
    
    Returns:
        Recommendation and reasoning
    """
    
    # Complexity scoring
    complexity_scores = {
        'light': 1,      # Simple arithmetic, basic operations
        'medium': 5,     # Function calls, basic algorithms
        'heavy': 20      # Complex computations, nested loops
    }
    
    score = data_size * complexity_scores.get(work_complexity, 1)
    
    # Decision thresholds
    if score < 1000:
        return "Sequential", "Overhead likely exceeds benefits for small/light workload"
    elif score < 10000:
        return "Consider Parallel", "May benefit from parallelization with proper tuning"
    else:
        return "Parallel", "Strong candidate for parallel processing"

# Examples
print("Decision Matrix Examples:")
examples = [
    (100, 'light', 4),      # Small dataset, light work
    (10000, 'light', 4),    # Large dataset, light work
    (1000, 'heavy', 4),     # Medium dataset, heavy work
    (100000, 'medium', 8),  # Large dataset, medium work
]

for data_size, complexity, cores in examples:
    recommendation, reason = should_use_parallel_processing(data_size, complexity, cores)
    print(f"Data: {data_size:6d}, Work: {complexity:6s}, Cores: {cores} → {recommendation:15s} ({reason})")
```

### Workload Classification

```python
import time
import math

# Light workloads (avoid parallelization for small datasets)
def light_examples():
    """Examples of light computational workloads."""
    
    # Simple arithmetic
    def add_numbers(x):
        return x + 1
    
    # String operations
    def process_string(s):
        return s.upper().strip()
    
    # List comprehensions
    def simple_transform(data):
        return [x * 2 for x in data]
    
    return [add_numbers, process_string, simple_transform]

# Medium workloads (good candidates for parallelization)
def medium_examples():
    """Examples of medium computational workloads."""
    
    # Data parsing and validation
    def parse_record(record):
        # Simulate parsing a complex record
        fields = record.split(',')
        return {
            'id': int(fields[0]),
            'name': fields[1].strip(),
            'value': float(fields[2]),
            'processed_at': time.time()
        }
    
    # Regular expression processing
    def extract_patterns(text):
        import re
        patterns = [r'\d+', r'[A-Z][a-z]+', r'\w+@\w+\.\w+']
        results = {}
        for pattern in patterns:
            results[pattern] = re.findall(pattern, text)
        return results
    
    return [parse_record, extract_patterns]

# Heavy workloads (excellent candidates for parallelization)
def heavy_examples():
    """Examples of heavy computational workloads."""
    
    # Mathematical computations
    def prime_check(n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    # Cryptographic operations
    def hash_computation(data):
        import hashlib
        result = data
        for _ in range(1000):  # Simulate expensive hashing
            result = hashlib.sha256(str(result).encode()).hexdigest()
        return result
    
    # Simulation/modeling
    def monte_carlo_step(iterations):
        import random
        inside_circle = 0
        for _ in range(iterations):
            x, y = random.random(), random.random()
            if x*x + y*y <= 1:
                inside_circle += 1
        return inside_circle
    
    return [prime_check, hash_computation, monte_carlo_step]
```

## Configuration and Tuning

### Optimal Chunk Size

```python
from pyferris import parallel_map, set_chunk_size
import time

def find_optimal_chunk_size(func, data, chunk_sizes=None):
    """Find the optimal chunk size for a given function and dataset."""
    
    if chunk_sizes is None:
        data_size = len(data)
        chunk_sizes = [
            1,
            max(1, data_size // 1000),
            max(1, data_size // 100),
            max(1, data_size // 10),
            max(1, data_size // 4),
            max(1, data_size // 2)
        ]
        chunk_sizes = list(set(chunk_sizes))  # Remove duplicates
        chunk_sizes.sort()
    
    results = []
    
    print(f"Testing chunk sizes for {len(data)} items...")
    print("Chunk Size | Execution Time | Throughput (items/sec)")
    print("-" * 55)
    
    for chunk_size in chunk_sizes:
        set_chunk_size(chunk_size)
        
        # Warmup run
        list(parallel_map(func, data[:100]))
        
        # Actual measurement
        start_time = time.time()
        result = list(parallel_map(func, data))
        end_time = time.time()
        
        execution_time = end_time - start_time
        throughput = len(data) / execution_time
        
        results.append((chunk_size, execution_time, throughput))
        print(f"{chunk_size:9d} | {execution_time:13.3f} | {throughput:21.1f}")
    
    # Find optimal chunk size
    optimal = min(results, key=lambda x: x[1])
    print(f"\nOptimal chunk size: {optimal[0]} (execution time: {optimal[1]:.3f}s)")
    
    return optimal[0]

# Example usage
def sample_computation(x):
    return sum(i*i for i in range(x % 100))

test_data = list(range(10000))
optimal_chunk = find_optimal_chunk_size(sample_computation, test_data)
set_chunk_size(optimal_chunk)
```

### Worker Thread Configuration

```python
from pyferris import set_worker_count, get_worker_count
import os
import time

def benchmark_worker_counts(func, data, max_workers=None):
    """Benchmark different worker thread configurations."""
    
    if max_workers is None:
        max_workers = os.cpu_count() * 2
    
    worker_counts = [1, 2, 4] + list(range(os.cpu_count(), max_workers + 1, 2))
    worker_counts = list(set(worker_counts))  # Remove duplicates
    worker_counts.sort()
    
    original_count = get_worker_count()
    
    results = []
    
    print(f"Testing worker counts (CPU cores: {os.cpu_count()})...")
    print("Workers | Execution Time | Speedup | Efficiency")
    print("-" * 45)
    
    baseline_time = None
    
    for worker_count in worker_counts:
        set_worker_count(worker_count)
        
        # Warmup
        list(parallel_map(func, data[:100]))
        
        # Measurement
        start_time = time.time()
        result = list(parallel_map(func, data))
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        if baseline_time is None:
            baseline_time = execution_time
            speedup = 1.0
        else:
            speedup = baseline_time / execution_time
        
        efficiency = speedup / worker_count * 100
        
        results.append((worker_count, execution_time, speedup, efficiency))
        print(f"{worker_count:7d} | {execution_time:13.3f} | {speedup:7.2f} | {efficiency:9.1f}%")
    
    # Restore original setting
    set_worker_count(original_count)
    
    # Find optimal configuration
    optimal = max(results, key=lambda x: x[2])  # Best speedup
    print(f"\nOptimal worker count: {optimal[0]} (speedup: {optimal[2]:.2f}x)")
    
    return optimal[0]

# Example usage
def cpu_intensive_task(n):
    return sum(i * i for i in range(n % 1000))

test_data = list(range(10000))
optimal_workers = benchmark_worker_counts(cpu_intensive_task, test_data)
```

## Memory Optimization

### Memory-Efficient Processing

```python
from pyferris import BatchProcessor, parallel_map
from pyferris.memory import MemoryPool
import psutil
import os
import gc

class MemoryEfficientProcessor:
    def __init__(self, max_memory_mb=1000):
        self.max_memory_mb = max_memory_mb
        self.memory_pool = MemoryPool(block_size=1024*1024)  # 1MB blocks
    
    def get_memory_usage(self):
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def process_large_dataset(self, data, process_func):
        """Process large dataset with memory management."""
        
        initial_memory = self.get_memory_usage()
        print(f"Initial memory usage: {initial_memory:.1f} MB")
        
        # Calculate optimal batch size based on memory limit
        estimated_item_size = 1000  # bytes per item (estimate)
        max_batch_size = (self.max_memory_mb * 1024 * 1024) // estimated_item_size
        batch_size = min(1000, max_batch_size)
        
        print(f"Using batch size: {batch_size}")
        
        batch_processor = BatchProcessor(
            batch_size=batch_size,
            max_memory_mb=self.max_memory_mb // 2,  # Reserve memory for processing
            progress=True
        )
        
        results = []
        peak_memory = initial_memory
        
        for batch_result in batch_processor.process(data, process_func):
            results.extend(batch_result)
            
            # Monitor memory usage
            current_memory = self.get_memory_usage()
            peak_memory = max(peak_memory, current_memory)
            
            # Force garbage collection if memory usage is high
            if current_memory > self.max_memory_mb * 0.8:
                gc.collect()
                print(f"Memory cleanup: {current_memory:.1f} → {self.get_memory_usage():.1f} MB")
        
        final_memory = self.get_memory_usage()
        
        print(f"Peak memory usage: {peak_memory:.1f} MB")
        print(f"Final memory usage: {final_memory:.1f} MB")
        print(f"Memory increase: {final_memory - initial_memory:.1f} MB")
        
        return results

def memory_intensive_function(data_item):
    """Simulate memory-intensive processing."""
    # Create temporary large data structure
    temp_data = [data_item * i for i in range(1000)]
    result = sum(temp_data)
    del temp_data  # Explicit cleanup
    return result

# Example usage
processor = MemoryEfficientProcessor(max_memory_mb=500)
large_dataset = list(range(100000))

print("Processing large dataset with memory management...")
results = processor.process_large_dataset(large_dataset, memory_intensive_function)
print(f"Processed {len(results)} items successfully")
```

### Memory-Mapped Arrays for Large Datasets

```python
from pyferris.memory import memory_mapped_array, memory_mapped_array_2d
from pyferris import parallel_map
import numpy as np
import time

def demonstrate_memory_mapping():
    """Demonstrate memory-mapped arrays for processing large datasets."""
    
    # Create large memory-mapped array
    size = 10_000_000  # 10 million elements
    print(f"Creating memory-mapped array with {size:,} elements...")
    
    # Create memory-mapped array (doesn't allocate all memory immediately)
    mmap_array = memory_mapped_array(size, dtype='float64')
    
    # Initialize array in parallel chunks
    def init_chunk(chunk_info):
        start, end = chunk_info
        for i in range(start, end):
            mmap_array[i] = i * 0.5 + 10
    
    # Divide initialization work
    chunk_size = 100_000
    chunks = [(i, min(i + chunk_size, size)) for i in range(0, size, chunk_size)]
    
    print("Initializing array in parallel...")
    start_time = time.time()
    list(parallel_map(init_chunk, chunks))
    init_time = time.time() - start_time
    
    print(f"Initialization completed in {init_time:.2f} seconds")
    
    # Process array in parallel
    def process_chunk(chunk_info):
        start, end = chunk_info
        chunk_sum = 0
        for i in range(start, end):
            chunk_sum += mmap_array[i] ** 2
        return chunk_sum
    
    print("Processing array in parallel...")
    start_time = time.time()
    chunk_results = list(parallel_map(process_chunk, chunks))
    total_sum = sum(chunk_results)
    process_time = time.time() - start_time
    
    print(f"Processing completed in {process_time:.2f} seconds")
    print(f"Total sum: {total_sum:.2e}")
    
    # Memory usage comparison
    estimated_memory = size * 8 / (1024**3)  # 8 bytes per float64, convert to GB
    print(f"Estimated memory usage: {estimated_memory:.2f} GB")

demonstrate_memory_mapping()
```

## CPU vs I/O Bound Workloads

### Identifying Workload Types

```python
import time
import os
from pyferris import parallel_map, set_worker_count

def profile_workload_type(func, sample_data, duration=5):
    """
    Profile a function to determine if it's CPU or I/O bound.
    
    Returns:
        str: 'cpu_bound', 'io_bound', or 'mixed'
    """
    
    def measure_with_workers(worker_count):
        """Measure performance with specific worker count."""
        original_count = set_worker_count(worker_count)
        
        start_time = time.time()
        processed = 0
        
        while time.time() - start_time < duration:
            list(parallel_map(func, sample_data))
            processed += len(sample_data)
        
        total_time = time.time() - start_time
        throughput = processed / total_time
        
        set_worker_count(original_count)
        return throughput
    
    # Test with different worker counts
    cpu_cores = os.cpu_count()
    single_thread_throughput = measure_with_workers(1)
    multi_thread_throughput = measure_with_workers(cpu_cores)
    high_thread_throughput = measure_with_workers(cpu_cores * 4)
    
    # Analyze scaling behavior
    cpu_scaling = multi_thread_throughput / single_thread_throughput
    io_scaling = high_thread_throughput / multi_thread_throughput
    
    print(f"Single thread: {single_thread_throughput:.1f} items/sec")
    print(f"Multi thread ({cpu_cores}): {multi_thread_throughput:.1f} items/sec")
    print(f"High thread ({cpu_cores*4}): {high_thread_throughput:.1f} items/sec")
    print(f"CPU scaling: {cpu_scaling:.2f}x")
    print(f"I/O scaling: {io_scaling:.2f}x")
    
    # Classification logic
    if cpu_scaling > 2.0 and io_scaling < 1.2:
        return 'cpu_bound'
    elif cpu_scaling < 1.5 and io_scaling > 1.5:
        return 'io_bound'
    else:
        return 'mixed'

# Example workloads
def cpu_bound_task(n):
    """CPU-intensive task."""
    total = 0
    for i in range(n % 1000):
        total += i * i
    return total

def io_bound_task(filename):
    """I/O-intensive task (simulated)."""
    time.sleep(0.01)  # Simulate I/O wait
    return len(filename)

def mixed_task(data):
    """Mixed CPU and I/O task."""
    # Some CPU work
    result = sum(i*i for i in range(50))
    # Some I/O simulation
    time.sleep(0.001)
    return result + len(str(data))

# Profile different workload types
sample_data = list(range(100))

print("CPU-bound workload profile:")
workload_type = profile_workload_type(cpu_bound_task, sample_data)
print(f"Classification: {workload_type}\n")

print("I/O-bound workload profile:")
io_sample_data = [f"file_{i}.txt" for i in range(100)]
workload_type = profile_workload_type(io_bound_task, io_sample_data)
print(f"Classification: {workload_type}\n")

print("Mixed workload profile:")
workload_type = profile_workload_type(mixed_task, sample_data)
print(f"Classification: {workload_type}")
```

### Optimization Strategies by Workload Type

```python
from pyferris import set_worker_count, set_chunk_size

class WorkloadOptimizer:
    def __init__(self):
        self.cpu_cores = os.cpu_count()
    
    def optimize_for_cpu_bound(self):
        """Optimize configuration for CPU-bound workloads."""
        # Use number of CPU cores for worker count
        set_worker_count(self.cpu_cores)
        
        # Smaller chunk size for better load balancing
        set_chunk_size(1)
        
        print(f"CPU-bound optimization:")
        print(f"  Worker count: {self.cpu_cores}")
        print(f"  Chunk size: 1")
        print(f"  Strategy: Maximize CPU utilization, minimize overhead")
    
    def optimize_for_io_bound(self):
        """Optimize configuration for I/O-bound workloads."""
        # Use more workers than CPU cores (2-4x)
        worker_count = min(self.cpu_cores * 3, 64)  # Cap at reasonable limit
        set_worker_count(worker_count)
        
        # Larger chunk size to reduce coordination overhead
        set_chunk_size(100)
        
        print(f"I/O-bound optimization:")
        print(f"  Worker count: {worker_count}")
        print(f"  Chunk size: 100")
        print(f"  Strategy: Overlap I/O waits with more threads")
    
    def optimize_for_mixed(self):
        """Optimize configuration for mixed workloads."""
        # Balance between CPU cores and I/O concurrency
        worker_count = int(self.cpu_cores * 1.5)
        set_worker_count(worker_count)
        
        # Medium chunk size
        set_chunk_size(10)
        
        print(f"Mixed workload optimization:")
        print(f"  Worker count: {worker_count}")
        print(f"  Chunk size: 10")
        print(f"  Strategy: Balance CPU usage and I/O concurrency")

optimizer = WorkloadOptimizer()

# Apply different optimizations based on workload type
def apply_optimization(workload_type):
    if workload_type == 'cpu_bound':
        optimizer.optimize_for_cpu_bound()
    elif workload_type == 'io_bound':
        optimizer.optimize_for_io_bound()
    else:
        optimizer.optimize_for_mixed()
```

## Benchmarking and Profiling

### Comprehensive Benchmarking Framework

```python
import time
import statistics
from dataclasses import dataclass
from typing import List, Callable, Any
from pyferris import parallel_map

@dataclass
class BenchmarkResult:
    name: str
    execution_times: List[float]
    mean_time: float
    std_time: float
    min_time: float
    max_time: float
    throughput: float
    data_size: int

class PerformanceBenchmark:
    def __init__(self, warmup_runs=2, measurement_runs=5):
        self.warmup_runs = warmup_runs
        self.measurement_runs = measurement_runs
    
    def benchmark_function(self, func: Callable, data: List[Any], name: str) -> BenchmarkResult:
        """Benchmark a function with multiple runs."""
        
        print(f"Benchmarking {name}...")
        
        # Warmup runs
        for _ in range(self.warmup_runs):
            list(func(data))
        
        # Measurement runs
        execution_times = []
        for run in range(self.measurement_runs):
            start_time = time.perf_counter()
            result = list(func(data))
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            print(f"  Run {run + 1}: {execution_time:.4f}s")
        
        # Calculate statistics
        mean_time = statistics.mean(execution_times)
        std_time = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        min_time = min(execution_times)
        max_time = max(execution_times)
        throughput = len(data) / mean_time
        
        return BenchmarkResult(
            name=name,
            execution_times=execution_times,
            mean_time=mean_time,
            std_time=std_time,
            min_time=min_time,
            max_time=max_time,
            throughput=throughput,
            data_size=len(data)
        )
    
    def compare_implementations(self, implementations: List[tuple], data: List[Any]) -> None:
        """Compare multiple implementations of the same functionality."""
        
        results = []
        for name, func in implementations:
            result = self.benchmark_function(func, data, name)
            results.append(result)
        
        # Print comparison
        print("\n" + "=" * 80)
        print("BENCHMARK COMPARISON")
        print("=" * 80)
        
        print(f"{'Implementation':<20} {'Mean Time':<12} {'Std Dev':<10} {'Throughput':<15} {'Speedup':<10}")
        print("-" * 80)
        
        baseline_time = results[0].mean_time
        
        for result in results:
            speedup = baseline_time / result.mean_time
            print(f"{result.name:<20} {result.mean_time:<12.4f} {result.std_time:<10.4f} "
                  f"{result.throughput:<15.1f} {speedup:<10.2f}x")
        
        # Find best performer
        best_result = min(results, key=lambda r: r.mean_time)
        print(f"\nBest performer: {best_result.name} ({best_result.throughput:.1f} items/sec)")

# Example usage
def create_benchmark_suite():
    """Create a comprehensive benchmark suite."""
    
    def heavy_computation(x):
        """Heavy computational task for benchmarking."""
        total = 0
        for i in range(x % 1000):
            total += i * i * i
        return total
    
    # Test data
    test_data = list(range(10000))
    
    # Different implementations to compare
    implementations = [
        ("Sequential", lambda data: [heavy_computation(x) for x in data]),
        ("PyFerris parallel_map", lambda data: parallel_map(heavy_computation, data)),
        ("PyFerris chunked", lambda data: parallel_map(heavy_computation, data, chunk_size=100)),
    ]
    
    # Run benchmark
    benchmark = PerformanceBenchmark(warmup_runs=2, measurement_runs=5)
    benchmark.compare_implementations(implementations, test_data)

create_benchmark_suite()
```

### Memory Profiling

```python
import psutil
import os
import time
from pyferris import parallel_map

class MemoryProfiler:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = self.get_memory_usage()
    
    def get_memory_usage(self):
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def profile_memory_usage(self, func, data, name="Function"):
        """Profile memory usage during function execution."""
        
        print(f"Memory profiling: {name}")
        print("-" * 40)
        
        initial_memory = self.get_memory_usage()
        print(f"Initial memory: {initial_memory:.1f} MB")
        
        # Track memory during execution
        peak_memory = initial_memory
        memory_samples = []
        
        def memory_monitor():
            nonlocal peak_memory
            while memory_monitor.running:
                current_memory = self.get_memory_usage()
                peak_memory = max(peak_memory, current_memory)
                memory_samples.append(current_memory)
                time.sleep(0.1)
        
        # Start memory monitoring
        import threading
        memory_monitor.running = True
        monitor_thread = threading.Thread(target=memory_monitor)
        monitor_thread.start()
        
        # Execute function
        start_time = time.time()
        result = list(func(data))
        execution_time = time.time() - start_time
        
        # Stop monitoring
        memory_monitor.running = False
        monitor_thread.join()
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        peak_increase = peak_memory - initial_memory
        
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Final memory: {final_memory:.1f} MB")
        print(f"Peak memory: {peak_memory:.1f} MB")
        print(f"Memory increase: {memory_increase:.1f} MB")
        print(f"Peak increase: {peak_increase:.1f} MB")
        print(f"Memory efficiency: {len(data) / max(1, peak_increase):.1f} items/MB")
        
        return {
            'execution_time': execution_time,
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'peak_memory': peak_memory,
            'memory_increase': memory_increase,
            'peak_increase': peak_increase,
            'memory_samples': memory_samples
        }

# Example usage
def memory_intensive_task(n):
    """Create temporary large data structure."""
    temp_list = list(range(n % 1000))
    result = sum(x * x for x in temp_list)
    del temp_list
    return result

profiler = MemoryProfiler()
test_data = list(range(50000))

# Profile sequential execution
seq_profile = profiler.profile_memory_usage(
    lambda data: [memory_intensive_task(x) for x in data],
    test_data,
    "Sequential execution"
)

print("\n")

# Profile parallel execution
par_profile = profiler.profile_memory_usage(
    lambda data: parallel_map(memory_intensive_task, data),
    test_data,
    "Parallel execution"
)

# Compare memory efficiency
print(f"\nMemory Efficiency Comparison:")
print(f"Sequential: {seq_profile['peak_increase']:.1f} MB peak")
print(f"Parallel: {par_profile['peak_increase']:.1f} MB peak")
print(f"Memory overhead: {par_profile['peak_increase'] - seq_profile['peak_increase']:.1f} MB")
```

## Common Performance Pitfalls

### Anti-patterns to Avoid

```python
from pyferris import parallel_map
import time

def demonstrate_antipatterns():
    """Demonstrate common performance anti-patterns and their solutions."""
    
    print("PERFORMANCE ANTI-PATTERNS")
    print("=" * 50)
    
    # Anti-pattern 1: Parallelizing trivial operations
    print("\n1. Trivial Operations (ANTI-PATTERN)")
    trivial_data = list(range(1000))
    
    def trivial_operation(x):
        return x + 1
    
    # Bad: Parallel overhead exceeds benefits
    start = time.time()
    bad_result = list(parallel_map(trivial_operation, trivial_data))
    bad_time = time.time() - start
    
    # Good: Sequential for trivial operations
    start = time.time()
    good_result = [trivial_operation(x) for x in trivial_data]
    good_time = time.time() - start
    
    print(f"  Parallel (bad): {bad_time:.4f}s")
    print(f"  Sequential (good): {good_time:.4f}s")
    print(f"  Overhead penalty: {bad_time/good_time:.2f}x slower")
    
    # Anti-pattern 2: Processing tiny datasets
    print("\n2. Tiny Datasets (ANTI-PATTERN)")
    tiny_data = list(range(10))
    
    def medium_operation(x):
        return sum(i * x for i in range(100))
    
    # Bad: Parallel overhead for small dataset
    start = time.time()
    bad_result = list(parallel_map(medium_operation, tiny_data))
    bad_time = time.time() - start
    
    # Good: Sequential for small datasets
    start = time.time()
    good_result = [medium_operation(x) for x in tiny_data]
    good_time = time.time() - start
    
    print(f"  Parallel (bad): {bad_time:.4f}s")
    print(f"  Sequential (good): {good_time:.4f}s")
    print(f"  Recommendation: Use parallel for datasets > 1000 items")
    
    # Anti-pattern 3: Incorrect chunk size
    print("\n3. Incorrect Chunk Size (ANTI-PATTERN)")
    large_data = list(range(100000))
    
    def cpu_operation(x):
        return sum(i * x for i in range(x % 100))
    
    # Bad: Chunk size too small (high overhead)
    from pyferris import set_chunk_size
    set_chunk_size(1)
    start = time.time()
    bad_result = list(parallel_map(cpu_operation, large_data))
    bad_time = time.time() - start
    
    # Good: Optimal chunk size
    set_chunk_size(1000)
    start = time.time()
    good_result = list(parallel_map(cpu_operation, large_data))
    good_time = time.time() - start
    
    print(f"  Small chunks (bad): {bad_time:.4f}s")
    print(f"  Optimal chunks (good): {good_time:.4f}s")
    print(f"  Improvement: {bad_time/good_time:.2f}x faster")
    
    # Anti-pattern 4: Memory inefficient processing
    print("\n4. Memory Inefficient Processing (ANTI-PATTERN)")
    
    def memory_wasteful(x):
        # Bad: Create unnecessary large temporary objects
        waste = [i * x for i in range(10000)]
        return sum(waste)  # Don't clean up
    
    def memory_efficient(x):
        # Good: Process incrementally without large temporaries
        return sum(i * x for i in range(10000))
    
    test_data = list(range(1000))
    
    # Compare memory usage
    import psutil
    process = psutil.Process()
    
    initial_memory = process.memory_info().rss / 1024 / 1024
    list(parallel_map(memory_wasteful, test_data))
    wasteful_memory = process.memory_info().rss / 1024 / 1024
    
    initial_memory = process.memory_info().rss / 1024 / 1024
    list(parallel_map(memory_efficient, test_data))
    efficient_memory = process.memory_info().rss / 1024 / 1024
    
    print(f"  Memory wasteful: {wasteful_memory:.1f} MB")
    print(f"  Memory efficient: {efficient_memory:.1f} MB")

demonstrate_antipatterns()
```

## Hardware Considerations

### CPU Architecture Optimization

```python
import os
import platform
from pyferris import set_worker_count

def analyze_hardware_configuration():
    """Analyze hardware and provide optimization recommendations."""
    
    print("HARDWARE ANALYSIS")
    print("=" * 40)
    
    # Basic system information
    cpu_count = os.cpu_count()
    system = platform.system()
    machine = platform.machine()
    
    print(f"System: {system} {machine}")
    print(f"CPU cores: {cpu_count}")
    
    # Try to get more detailed CPU information
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            
        # Extract CPU model
        for line in cpuinfo.split('\n'):
            if 'model name' in line:
                cpu_model = line.split(':')[1].strip()
                print(f"CPU model: {cpu_model}")
                break
        
        # Count physical cores vs logical cores
        physical_cores = len(set([line.split(':')[1].strip() 
                                for line in cpuinfo.split('\n') 
                                if 'physical id' in line]))
        if physical_cores > 0:
            logical_cores = cpu_count
            hyperthreading = logical_cores > physical_cores
            print(f"Physical cores: {physical_cores}")
            print(f"Logical cores: {logical_cores}")
            print(f"Hyperthreading: {'Yes' if hyperthreading else 'No'}")
    
    except FileNotFoundError:
        print("Detailed CPU info not available on this system")
    
    # Memory information
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"Total memory: {memory.total / (1024**3):.1f} GB")
        print(f"Available memory: {memory.available / (1024**3):.1f} GB")
    except ImportError:
        print("Memory information requires psutil package")
    
    # Provide optimization recommendations
    print(f"\nOPTIMIZATION RECOMMENDATIONS")
    print("-" * 40)
    
    if cpu_count <= 2:
        print("• Low core count: Use sequential processing for small datasets")
        print("• Consider I/O optimization over parallelization")
        recommended_workers = cpu_count
    elif cpu_count <= 8:
        print("• Medium core count: Good for moderate parallel workloads")
        print("• Use chunk size optimization for best performance")
        recommended_workers = cpu_count
    else:
        print("• High core count: Excellent for parallel processing")
        print("• Consider NUMA topology for very large datasets")
        recommended_workers = min(cpu_count, 32)  # Cap for diminishing returns
    
    print(f"• Recommended worker count: {recommended_workers}")
    
    # Workload-specific recommendations
    print(f"\nWORKLOAD-SPECIFIC SETTINGS")
    print("-" * 40)
    print(f"CPU-bound workloads:")
    print(f"  Workers: {cpu_count}")
    print(f"  Chunk size: 1-10")
    
    print(f"I/O-bound workloads:")
    print(f"  Workers: {cpu_count * 2}-{cpu_count * 4}")
    print(f"  Chunk size: 50-500")
    
    print(f"Memory-intensive workloads:")
    print(f"  Workers: {max(1, cpu_count // 2)}")
    print(f"  Use batch processing")

analyze_hardware_configuration()
```

### NUMA Awareness

```python
def numa_optimization_guide():
    """Guide for NUMA (Non-Uniform Memory Access) optimization."""
    
    print("NUMA OPTIMIZATION GUIDE")
    print("=" * 40)
    
    try:
        # Check if system has NUMA topology
        numa_nodes = []
        for i in range(8):  # Check up to 8 NUMA nodes
            try:
                with open(f'/sys/devices/system/node/node{i}/cpulist', 'r') as f:
                    cpulist = f.read().strip()
                    numa_nodes.append((i, cpulist))
            except FileNotFoundError:
                break
        
        if numa_nodes:
            print(f"NUMA topology detected ({len(numa_nodes)} nodes):")
            for node_id, cpulist in numa_nodes:
                print(f"  Node {node_id}: CPUs {cpulist}")
            
            print(f"\nNUMA Optimization Tips:")
            print("• Bind worker threads to specific NUMA nodes")
            print("• Allocate data on the same NUMA node as processing")
            print("• Use memory-mapped files for large datasets")
            print("• Consider process-based parallelism for NUMA systems")
            
        else:
            print("No NUMA topology detected (single node system)")
            print("Standard parallel processing optimization applies")
    
    except Exception as e:
        print(f"Could not detect NUMA topology: {e}")
        print("Assuming single-node system")

numa_optimization_guide()
```

## Real-world Optimization Examples

### E-commerce Data Processing

```python
from pyferris import parallel_map, parallel_filter, BatchProcessor
import time
import json

class EcommerceDataProcessor:
    def __init__(self):
        self.batch_processor = BatchProcessor(
            batch_size=5000,
            max_memory_mb=500,
            progress=True
        )
    
    def optimize_for_scale(self, data_size):
        """Optimize configuration based on data size."""
        from pyferris import set_chunk_size, set_worker_count
        import os
        
        if data_size < 10000:
            # Small dataset: conservative settings
            set_worker_count(min(4, os.cpu_count()))
            set_chunk_size(100)
        elif data_size < 100000:
            # Medium dataset: balanced settings
            set_worker_count(os.cpu_count())
            set_chunk_size(500)
        else:
            # Large dataset: aggressive parallelization
            set_worker_count(os.cpu_count())
            set_chunk_size(1000)
    
    def process_orders(self, orders):
        """Process e-commerce orders with optimized parallel pipeline."""
        
        print(f"Processing {len(orders):,} orders...")
        self.optimize_for_scale(len(orders))
        
        start_time = time.time()
        
        # Step 1: Data validation and cleaning
        def validate_order(order):
            try:
                return {
                    'order_id': str(order['order_id']),
                    'customer_id': str(order['customer_id']),
                    'amount': float(order['amount']),
                    'items': len(order.get('items', [])),
                    'date': order['date'],
                    'status': order.get('status', 'pending').lower()
                }
            except (KeyError, ValueError, TypeError):
                return None
        
        # Step 2: Business rule filtering
        def is_valid_order(order):
            return (order is not None and 
                   order['amount'] > 0 and 
                   order['items'] > 0 and
                   order['status'] in ['pending', 'processing', 'completed'])
        
        # Step 3: Enrichment with calculated fields
        def enrich_order(order):
            order['avg_item_value'] = order['amount'] / order['items']
            order['value_category'] = (
                'high' if order['amount'] > 500 else
                'medium' if order['amount'] > 100 else
                'low'
            )
            order['processing_timestamp'] = time.time()
            return order
        
        # Execute pipeline with batching for memory efficiency
        def process_batch(batch):
            # Validate batch
            validated = list(parallel_map(validate_order, batch))
            # Filter valid orders
            filtered = list(parallel_filter(is_valid_order, validated))
            # Enrich orders
            enriched = list(parallel_map(enrich_order, filtered))
            return enriched
        
        # Process in batches
        all_processed_orders = []
        for batch_result in self.batch_processor.process(orders, process_batch):
            all_processed_orders.extend(batch_result)
        
        processing_time = time.time() - start_time
        
        print(f"Processed {len(all_processed_orders):,} valid orders")
        print(f"Processing time: {processing_time:.2f} seconds")
        print(f"Throughput: {len(all_processed_orders)/processing_time:.1f} orders/second")
        
        return all_processed_orders

# Generate sample e-commerce data
def generate_ecommerce_data(num_orders=100000):
    """Generate sample e-commerce order data."""
    import random
    from datetime import datetime, timedelta
    
    orders = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_orders):
        order = {
            'order_id': f'ORD-{i:06d}',
            'customer_id': f'CUST-{random.randint(1000, 9999)}',
            'amount': round(random.uniform(10, 1000), 2),
            'items': random.randint(1, 10),
            'date': (base_date + timedelta(days=random.randint(0, 30))).isoformat(),
            'status': random.choice(['pending', 'processing', 'completed', 'cancelled'])
        }
        
        # Introduce some invalid data for testing
        if random.random() < 0.05:  # 5% invalid data
            if random.random() < 0.5:
                order['amount'] = -order['amount']  # Invalid amount
            else:
                del order['items']  # Missing field
        
        orders.append(order)
    
    return orders

# Example usage
processor = EcommerceDataProcessor()

# Generate test data
print("Generating sample e-commerce data...")
sample_orders = generate_ecommerce_data(50000)

# Process with optimization
processed_orders = processor.process_orders(sample_orders)

# Analyze results
valid_rate = len(processed_orders) / len(sample_orders) * 100
print(f"Data quality: {valid_rate:.1f}% valid orders")

# Performance analysis by value category
from pyferris import parallel_group_by
value_categories = parallel_group_by(processed_orders, key=lambda o: o['value_category'])

print("\nOrder distribution by value:")
for category, orders in value_categories.items():
    avg_value = sum(o['amount'] for o in orders) / len(orders)
    print(f"  {category.capitalize()}: {len(orders):,} orders (avg: ${avg_value:.2f})")
```

This comprehensive performance guide covers all aspects of optimizing PyFerris for various use cases. The key takeaways are:

1. **Measure first**: Always profile before optimizing
2. **Consider workload type**: CPU vs I/O bound requires different strategies
3. **Right-size resources**: Match worker count and chunk size to your data and hardware
4. **Monitor memory**: Use batch processing for large datasets
5. **Avoid anti-patterns**: Don't parallelize trivial operations or tiny datasets

## Next Steps

- Review the [API Reference](api_reference.md) for detailed parameter information
- Check out [Examples](examples.md) for more real-world optimization patterns
- Explore [Hardware-specific optimizations](troubleshooting.md) for your platform
