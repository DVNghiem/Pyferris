# Troubleshooting

This guide helps you diagnose and solve common issues when using PyFerris, from installation problems to performance optimization and debugging parallel code.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Common Runtime Errors](#common-runtime-errors)
3. [Performance Problems](#performance-problems)
4. [Memory Issues](#memory-issues)
5. [Debugging Parallel Code](#debugging-parallel-code)
6. [Platform-Specific Issues](#platform-specific-issues)
7. [Integration Problems](#integration-problems)
8. [FAQ](#frequently-asked-questions)

## Installation Issues

### ImportError: No module named '_pyferris'

**Problem**: Python cannot find the compiled Rust extension.

**Solutions**:

```bash
# Solution 1: Reinstall PyFerris
pip uninstall pyferris
pip install pyferris

# Solution 2: Build from source if precompiled wheel isn't available
pip install maturin
git clone https://github.com/DVNghiem/Pyferris.git
cd Pyferris
maturin develop

# Solution 3: Check Python version compatibility
python --version  # Should be 3.10+
```

### Build Errors on Installation

**Problem**: Compilation fails when building from source.

**Requirements Check**:
```bash
# Check Rust installation
rustc --version  # Should be 1.70+
cargo --version

# Install Rust if missing
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Check Python development headers
# Ubuntu/Debian:
sudo apt-get install python3-dev

# CentOS/RHEL:
sudo yum install python3-devel

# macOS:
xcode-select --install
```

### Version Compatibility Issues

**Problem**: PyFerris doesn't work with your Python version.

**Check Compatibility**:
```python
import sys
print(f"Python version: {sys.version}")

# PyFerris requires Python 3.10+
if sys.version_info < (3, 10):
    print("Please upgrade to Python 3.10 or higher")
```

## Common Runtime Errors

### "Cannot pickle function" Error

**Problem**: Functions passed to parallel operations cannot be serialized.

**Incorrect**:
```python
from pyferris import parallel_map

# This will fail - lambda functions can't be pickled
data = range(1000)
results = parallel_map(lambda x: x * 2, data)  # Error!
```

**Correct**:
```python
from pyferris import parallel_map

# Solution 1: Use regular function
def multiply_by_two(x):
    return x * 2

results = parallel_map(multiply_by_two, data)  # Works!

# Solution 2: Use functools.partial for parameterized functions
from functools import partial

def multiply_by_n(x, n):
    return x * n

multiply_by_three = partial(multiply_by_n, n=3)
results = parallel_map(multiply_by_three, data)  # Works!
```

### "RuntimeError: No workers available"

**Problem**: Worker threads are exhausted or not properly initialized.

**Diagnosis**:
```python
from pyferris import get_worker_count, set_worker_count
import os

print(f"Current worker count: {get_worker_count()}")
print(f"CPU cores: {os.cpu_count()}")

# Reset to default
set_worker_count(os.cpu_count())
```

**Solutions**:
```python
# Solution 1: Explicitly set worker count
from pyferris import set_worker_count
set_worker_count(4)  # Use 4 workers

# Solution 2: Use context manager for executor
from pyferris.executor import Executor

with Executor(max_workers=4) as executor:
    results = executor.map(your_function, data)
```

### "BrokenProcessPool" Error

**Problem**: Worker processes have crashed or become unresponsive.

**Debugging**:
```python
def safe_function_wrapper(func):
    """Wrapper to catch and log errors in parallel functions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import traceback
            print(f"Error in worker: {e}")
            print(traceback.format_exc())
            return None  # Return safe default
    return wrapper

# Usage
from pyferris import parallel_map

@safe_function_wrapper
def risky_function(x):
    if x == 42:
        raise ValueError("Intentional error for testing")
    return x * 2

# This will continue processing even if some items fail
results = parallel_map(risky_function, range(100))
valid_results = [r for r in results if r is not None]
```

### Timeout Errors

**Problem**: Operations are taking longer than expected.

**Solutions**:
```python
from pyferris.executor import Executor
from concurrent.futures import TimeoutError

def long_running_task(x):
    import time
    time.sleep(x)  # Simulate long work
    return x * 2

with Executor(max_workers=4) as executor:
    try:
        # Set timeout for individual tasks
        future = executor.submit(long_running_task, 5)
        result = future.result(timeout=10)  # 10 second timeout
    except TimeoutError:
        print("Task timed out")
        future.cancel()  # Try to cancel if possible
```

## Performance Problems

### Parallel Processing is Slower than Sequential

**Diagnosis Script**:
```python
import time
from pyferris import parallel_map

def benchmark_comparison(func, data, description="function"):
    """Compare sequential vs parallel performance."""
    
    # Sequential benchmark
    start = time.time()
    seq_result = [func(x) for x in data]
    seq_time = time.time() - start
    
    # Parallel benchmark
    start = time.time()
    par_result = list(parallel_map(func, data))
    par_time = time.time() - start
    
    print(f"Benchmarking {description}:")
    print(f"  Data size: {len(data):,} items")
    print(f"  Sequential: {seq_time:.4f}s")
    print(f"  Parallel: {par_time:.4f}s")
    
    if par_time < seq_time:
        speedup = seq_time / par_time
        print(f"  ✓ Speedup: {speedup:.2f}x faster")
    else:
        slowdown = par_time / seq_time
        print(f"  ✗ Slowdown: {slowdown:.2f}x slower")
        
        # Provide recommendations
        print("  Recommendations:")
        if len(data) < 1000:
            print("    - Dataset too small for parallelization")
        
        # Test function complexity
        start = time.time()
        func(data[0])
        single_time = time.time() - start
        
        if single_time < 0.001:  # Less than 1ms
            print("    - Function too simple, overhead exceeds benefits")
            print("    - Consider batching or using sequential processing")
        
        print(f"    - Try increasing chunk size or dataset size")
    
    return seq_time, par_time

# Test with different workloads
def light_work(x):
    return x + 1

def medium_work(x):
    return sum(i * x for i in range(100))

def heavy_work(x):
    return sum(i * x for i in range(1000))

# Small dataset
small_data = list(range(100))
benchmark_comparison(light_work, small_data, "light work (small data)")
benchmark_comparison(medium_work, small_data, "medium work (small data)")

# Large dataset
large_data = list(range(10000))
benchmark_comparison(light_work, large_data, "light work (large data)")
benchmark_comparison(medium_work, large_data, "medium work (large data)")
benchmark_comparison(heavy_work, large_data, "heavy work (large data)")
```

### Poor Scaling with More Workers

**Problem**: Adding more workers doesn't improve performance.

**Diagnostic Tools**:
```python
from pyferris import set_worker_count, parallel_map
import time
import os

def test_worker_scaling(func, data, max_workers=None):
    """Test how performance scales with worker count."""
    
    if max_workers is None:
        max_workers = os.cpu_count() * 2
    
    worker_counts = [1, 2, 4] + list(range(os.cpu_count(), max_workers + 1, 2))
    worker_counts = sorted(set(worker_counts))
    
    print(f"Testing worker scaling (CPU cores: {os.cpu_count()}):")
    print("Workers | Time (s) | Speedup | Efficiency")
    print("-" * 40)
    
    baseline_time = None
    
    for workers in worker_counts:
        set_worker_count(workers)
        
        # Warmup
        list(parallel_map(func, data[:100]))
        
        # Measure
        start = time.time()
        list(parallel_map(func, data))
        execution_time = time.time() - start
        
        if baseline_time is None:
            baseline_time = execution_time
            speedup = 1.0
        else:
            speedup = baseline_time / execution_time
        
        efficiency = speedup / workers * 100
        
        print(f"{workers:7d} | {execution_time:8.3f} | {speedup:7.2f} | {efficiency:8.1f}%")
        
        # Stop if efficiency drops too low
        if efficiency < 25 and workers > 4:
            print("Stopping: efficiency too low")
            break

# Test with CPU-bound work
def cpu_bound_work(x):
    return sum(i * i for i in range(x % 500))

test_data = list(range(5000))
test_worker_scaling(cpu_bound_work, test_data)
```

### Memory Usage Growing Unexpectedly

**Problem**: Memory consumption increases during parallel processing.

**Memory Monitoring**:
```python
import psutil
import os
import gc
from pyferris import parallel_map, BatchProcessor

class MemoryMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.get_memory_mb()
    
    def get_memory_mb(self):
        return self.process.memory_info().rss / (1024 * 1024)
    
    def check_memory_growth(self, description=""):
        current_memory = self.get_memory_mb()
        growth = current_memory - self.initial_memory
        print(f"Memory check{' - ' + description if description else ''}: "
              f"{current_memory:.1f} MB (+{growth:.1f} MB)")
        
        if growth > 1000:  # More than 1GB growth
            print("⚠️  WARNING: High memory usage detected")
            print("   Consider using BatchProcessor or smaller chunk sizes")
        
        return current_memory

def memory_efficient_processing(data, process_func):
    """Process data with memory monitoring and optimization."""
    
    monitor = MemoryMonitor()
    monitor.check_memory_growth("start")
    
    # Determine if we need batch processing
    estimated_item_memory = 1000  # bytes per item (rough estimate)
    total_estimated_memory = len(data) * estimated_item_memory / (1024 * 1024)  # MB
    
    if total_estimated_memory > 500:  # More than 500MB
        print(f"Large dataset detected ({total_estimated_memory:.1f} MB estimated)")
        print("Using batch processing...")
        
        batch_processor = BatchProcessor(
            batch_size=1000,
            max_memory_mb=200,
            progress=True
        )
        
        results = []
        for batch_result in batch_processor.process(data, process_func):
            results.extend(batch_result)
            monitor.check_memory_growth("batch complete")
            gc.collect()  # Force garbage collection
        
        return results
    
    else:
        print("Processing normally...")
        results = list(parallel_map(process_func, data))
        monitor.check_memory_growth("processing complete")
        return results

# Example usage
def memory_intensive_task(x):
    # Simulate memory-intensive work
    temp_data = list(range(x % 1000))
    result = sum(temp_data)
    del temp_data  # Explicit cleanup
    return result

large_dataset = list(range(50000))
results = memory_efficient_processing(large_dataset, memory_intensive_task)
```

## Memory Issues

### Out of Memory Errors

**Problem**: System runs out of memory during processing.

**Solutions**:

```python
from pyferris import BatchProcessor
import gc

def process_with_memory_management(data, process_func, max_memory_mb=1000):
    """Process data with strict memory management."""
    
    # Calculate safe batch size
    import sys
    
    # Estimate memory per item (rough heuristic)
    sample_size = min(100, len(data))
    
    # Process small sample to estimate memory usage
    initial_memory = get_memory_usage()
    sample_results = [process_func(x) for x in data[:sample_size]]
    memory_after_sample = get_memory_usage()
    
    memory_per_item = (memory_after_sample - initial_memory) / sample_size
    safe_batch_size = int(max_memory_mb / memory_per_item) if memory_per_item > 0 else 1000
    safe_batch_size = max(10, min(safe_batch_size, 10000))  # Reasonable bounds
    
    print(f"Estimated memory per item: {memory_per_item:.3f} MB")
    print(f"Using batch size: {safe_batch_size}")
    
    # Process in batches
    def process_batch(batch):
        results = []
        for item in batch:
            try:
                result = process_func(item)
                results.append(result)
            except MemoryError:
                print(f"Memory error processing item: {item}")
                gc.collect()
                # Try again with garbage collection
                try:
                    result = process_func(item)
                    results.append(result)
                except MemoryError:
                    print(f"Skipping item due to memory constraints: {item}")
        return results
    
    batch_processor = BatchProcessor(
        batch_size=safe_batch_size,
        max_memory_mb=max_memory_mb // 2,
        progress=True
    )
    
    all_results = []
    for batch_result in batch_processor.process(data, process_batch):
        all_results.extend(batch_result)
        
        # Force cleanup between batches
        gc.collect()
        
        # Check memory usage
        current_memory = get_memory_usage()
        if current_memory > max_memory_mb:
            print(f"Warning: Memory usage ({current_memory:.1f} MB) exceeds limit")
    
    return all_results

def get_memory_usage():
    """Get current memory usage in MB."""
    import psutil
    return psutil.Process().memory_info().rss / (1024 * 1024)
```

### Memory Leaks in Long-Running Processes

**Problem**: Memory usage grows continuously over time.

**Detection and Prevention**:

```python
import gc
import weakref
from pyferris import parallel_map

class MemoryLeakDetector:
    def __init__(self):
        self.initial_objects = len(gc.get_objects())
        self.snapshots = []
    
    def take_snapshot(self, label=""):
        """Take a memory snapshot."""
        gc.collect()  # Force garbage collection
        
        current_objects = len(gc.get_objects())
        snapshot = {
            'label': label,
            'objects': current_objects,
            'growth': current_objects - self.initial_objects
        }
        self.snapshots.append(snapshot)
        
        print(f"Memory snapshot {label}: {current_objects:,} objects "
              f"(+{snapshot['growth']:,} from start)")
        
        return snapshot
    
    def analyze_leaks(self):
        """Analyze potential memory leaks."""
        if len(self.snapshots) < 2:
            print("Need at least 2 snapshots to analyze")
            return
        
        print("\nMemory Leak Analysis:")
        print("-" * 30)
        
        for i in range(1, len(self.snapshots)):
            prev = self.snapshots[i-1]
            curr = self.snapshots[i]
            growth = curr['objects'] - prev['objects']
            
            print(f"{prev['label']} → {curr['label']}: {growth:+,} objects")
            
            if growth > 1000:
                print(f"  ⚠️  Potential leak detected!")

def leak_safe_processing(data_batches, process_func):
    """Process data in batches with leak detection."""
    
    detector = MemoryLeakDetector()
    detector.take_snapshot("start")
    
    results = []
    
    for i, batch in enumerate(data_batches):
        # Process batch
        batch_results = list(parallel_map(process_func, batch))
        results.extend(batch_results)
        
        # Clear references and force cleanup
        del batch_results
        gc.collect()
        
        # Take snapshot every 10 batches
        if i % 10 == 0:
            detector.take_snapshot(f"batch_{i}")
    
    detector.take_snapshot("end")
    detector.analyze_leaks()
    
    return results

# Example with potential leak
def leaky_function(x):
    # Simulate a function that might leak memory
    global _cache  # Don't do this in real code!
    if '_cache' not in globals():
        _cache = {}
    
    # This creates a memory leak by never cleaning the cache
    _cache[x] = [i * x for i in range(1000)]
    return sum(_cache[x])

def fixed_function(x):
    # Better approach - no global state
    temp_data = [i * x for i in range(1000)]
    result = sum(temp_data)
    del temp_data  # Explicit cleanup
    return result

# Test for leaks
test_batches = [list(range(i*100, (i+1)*100)) for i in range(50)]

print("Testing potentially leaky function:")
leak_safe_processing(test_batches[:10], leaky_function)  # Only test small subset

print("\nTesting fixed function:")
leak_safe_processing(test_batches[:10], fixed_function)
```

## Debugging Parallel Code

### Adding Debug Information

**Problem**: Hard to debug issues in parallel code.

**Solution - Debug Wrapper**:

```python
import time
import threading
import traceback
from functools import wraps

def debug_parallel_function(func):
    """Decorator to add debugging to parallel functions."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread_id = threading.get_ident()
        start_time = time.time()
        
        try:
            print(f"[Thread {thread_id}] Starting {func.__name__} with args: {args[:2]}...")
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"[Thread {thread_id}] {func.__name__} completed in {end_time - start_time:.3f}s")
            return result
            
        except Exception as e:
            print(f"[Thread {thread_id}] ERROR in {func.__name__}: {e}")
            print(f"[Thread {thread_id}] Traceback:")
            traceback.print_exc()
            raise
    
    return wrapper

# Usage example
@debug_parallel_function
def problematic_function(x):
    if x == 42:
        raise ValueError("Answer to everything not allowed!")
    return x * 2

# This will show detailed debugging output
from pyferris import parallel_map
results = list(parallel_map(problematic_function, range(50)))
```

### Logging in Parallel Processes

**Problem**: Logging from parallel workers is messy or lost.

**Solution - Thread-Safe Logging**:

```python
import logging
import queue
import threading
from pyferris import parallel_map

class ParallelLogger:
    def __init__(self, log_file="parallel.log"):
        # Create thread-safe logging setup
        self.log_queue = queue.Queue()
        self.logger = logging.getLogger('PyFerris')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_parallel_function(self, func):
        """Decorator to add logging to parallel functions."""
        def wrapper(*args, **kwargs):
            thread_name = threading.current_thread().name
            self.logger.info(f"Starting {func.__name__} in {thread_name}")
            
            try:
                result = func(*args, **kwargs)
                self.logger.info(f"Completed {func.__name__} successfully")
                return result
            except Exception as e:
                self.logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                raise
        
        return wrapper

# Usage
parallel_logger = ParallelLogger("debug.log")

@parallel_logger.log_parallel_function
def logged_function(x):
    if x % 100 == 0:
        print(f"Processing milestone: {x}")
    
    if x == 250:
        raise ValueError("Simulated error for testing")
    
    return x ** 2

# This will create detailed logs
try:
    results = list(parallel_map(logged_function, range(500)))
except Exception as e:
    print(f"Processing failed: {e}")

print("Check debug.log for detailed execution trace")
```

## Platform-Specific Issues

### Windows-Specific Problems

**Problem**: PyFerris behaves differently on Windows.

**Common Issues and Solutions**:

```python
import platform
import os

def windows_compatibility_check():
    """Check for Windows-specific compatibility issues."""
    
    if platform.system() != 'Windows':
        print("This check is for Windows systems only")
        return
    
    print("Windows Compatibility Check")
    print("=" * 30)
    
    # Check Python version
    python_version = platform.python_version()
    print(f"Python version: {python_version}")
    
    # Check if running in main guard
    print("\nIMPORTANT: Always use if __name__ == '__main__': guard on Windows")
    print("Example:")
    print("""
if __name__ == '__main__':
    from pyferris import parallel_map
    
    def worker_function(x):
        return x * 2
    
    data = range(1000)
    results = list(parallel_map(worker_function, data))
    """)
    
    # Check for multiprocessing issues
    try:
        import multiprocessing
        multiprocessing.set_start_method('spawn', force=True)
        print("\n✓ Multiprocessing start method set to 'spawn' (Windows compatible)")
    except Exception as e:
        print(f"\n✗ Multiprocessing setup issue: {e}")

# Windows-safe main function example
def windows_safe_main():
    """Example of Windows-safe parallel processing."""
    
    if platform.system() == 'Windows':
        import multiprocessing
        multiprocessing.freeze_support()  # Required for Windows executables
    
    from pyferris import parallel_map
    
    def safe_worker(x):
        return x * x
    
    data = range(1000)
    results = list(parallel_map(safe_worker, data))
    print(f"Processed {len(results)} items on Windows")

if __name__ == '__main__':
    windows_compatibility_check()
    windows_safe_main()
```

### macOS-Specific Issues

**Problem**: Performance issues or crashes on macOS.

**Solutions**:

```python
import platform
import os

def macos_optimization():
    """Optimize PyFerris for macOS."""
    
    if platform.system() != 'Darwin':
        print("This optimization is for macOS only")
        return
    
    print("macOS Optimization Guide")
    print("=" * 25)
    
    # Check for Apple Silicon vs Intel
    machine = platform.machine()
    print(f"Architecture: {machine}")
    
    if machine == 'arm64':
        print("Apple Silicon detected:")
        print("• Performance cores and efficiency cores available")
        print("• Consider using fewer workers than total core count")
        
        # Optimal settings for Apple Silicon
        from pyferris import set_worker_count
        set_worker_count(6)  # Conservative for M1/M2
        
    else:
        print("Intel Mac detected:")
        print("• Standard optimization applies")
        
        from pyferris import set_worker_count
        import os
        set_worker_count(os.cpu_count())
    
    # Check for memory pressure
    try:
        import psutil
        memory = psutil.virtual_memory()
        if memory.available < 2 * 1024**3:  # Less than 2GB available
            print("⚠️  Low memory detected, reducing parallel workers")
            from pyferris import set_worker_count
            set_worker_count(2)
    except ImportError:
        print("Install psutil for memory monitoring: pip install psutil")

if __name__ == '__main__':
    macos_optimization()
```

### Linux-Specific Optimizations

**Problem**: Want to optimize for specific Linux configurations.

**Solutions**:

```python
import os
import platform

def linux_optimization():
    """Linux-specific optimizations for PyFerris."""
    
    if platform.system() != 'Linux':
        print("This optimization is for Linux only")
        return
    
    print("Linux System Optimization")
    print("=" * 25)
    
    # Check CPU information
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        
        # Count physical cores
        physical_cores = len(set([
            line.split(':')[1].strip() 
            for line in cpuinfo.split('\n') 
            if 'physical id' in line
        ]))
        
        logical_cores = os.cpu_count()
        
        print(f"Physical cores: {physical_cores}")
        print(f"Logical cores: {logical_cores}")
        
        if logical_cores > physical_cores:
            print("Hyperthreading detected")
            print("Recommendation: Use physical core count for CPU-bound tasks")
            
            from pyferris import set_worker_count
            set_worker_count(physical_cores)
        
    except FileNotFoundError:
        print("Could not read CPU information")
    
    # Check for NUMA
    numa_nodes = []
    for i in range(8):
        try:
            with open(f'/sys/devices/system/node/node{i}/cpulist', 'r') as f:
                numa_nodes.append(i)
        except FileNotFoundError:
            break
    
    if len(numa_nodes) > 1:
        print(f"NUMA system detected: {len(numa_nodes)} nodes")
        print("Consider NUMA-aware process placement for large datasets")
    
    # Check ulimits
    try:
        import resource
        max_files = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
        max_processes = resource.getrlimit(resource.RLIMIT_NPROC)[0]
        
        print(f"Max open files: {max_files}")
        print(f"Max processes: {max_processes}")
        
        if max_files < 4096:
            print("⚠️  Low file descriptor limit may affect I/O performance")
            print("   Consider: ulimit -n 4096")
    except ImportError:
        pass

if __name__ == '__main__':
    linux_optimization()
```

## Integration Problems

### Working with Jupyter Notebooks

**Problem**: PyFerris doesn't work properly in Jupyter notebooks.

**Solutions**:

```python
# Cell 1: Setup for Jupyter
import sys
import warnings

# Suppress numpy warnings that are common in notebooks
warnings.filterwarnings('ignore')

# Check if running in Jupyter
def is_jupyter():
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except ImportError:
        return False

if is_jupyter():
    print("Running in Jupyter - applying notebook optimizations")
    
    # Set up for notebook use
    import os
    os.environ['PYTHONHASHSEED'] = '0'  # For reproducibility
    
    # Reduce worker count in notebooks to avoid overwhelming the kernel
    from pyferris import set_worker_count
    set_worker_count(min(4, os.cpu_count()))
    
    print("✓ PyFerris configured for Jupyter")

# Cell 2: Notebook-safe parallel function
def notebook_safe_parallel_map(func, data, description="Processing"):
    """Jupyter-safe parallel processing with progress."""
    from pyferris import parallel_map, ProgressTracker
    
    # Create progress tracker
    tracker = ProgressTracker(
        total=len(data),
        desc=description,
        update_frequency=max(1, len(data) // 20)  # Update 20 times max
    )
    
    try:
        results = list(parallel_map(func, data, progress=tracker))
        print(f"✓ Completed processing {len(results)} items")
        return results
    except Exception as e:
        print(f"✗ Error during processing: {e}")
        raise

# Cell 3: Example usage
def example_function(x):
    import time
    time.sleep(0.01)  # Simulate work
    return x ** 2

if is_jupyter():
    data = list(range(100))
    results = notebook_safe_parallel_map(example_function, data, "Computing squares")
```

### Integration with Pandas

**Problem**: Using PyFerris with pandas DataFrames.

**Solutions**:

```python
import pandas as pd
from pyferris import parallel_map, parallel_filter

def parallel_apply_to_dataframe(df, func, column=None, n_chunks=None):
    """Apply function to DataFrame using PyFerris parallel processing."""
    
    if n_chunks is None:
        n_chunks = min(10, len(df) // 1000 + 1)
    
    # Split DataFrame into chunks
    chunk_size = len(df) // n_chunks
    chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
    
    def process_chunk(chunk):
        if column:
            return chunk[column].apply(func).tolist()
        else:
            return chunk.apply(func, axis=1).tolist()
    
    # Process chunks in parallel
    results = list(parallel_map(process_chunk, chunks))
    
    # Flatten results
    flattened = []
    for chunk_result in results:
        flattened.extend(chunk_result)
    
    return flattened

# Example usage
def expensive_transform(value):
    # Simulate expensive computation
    import time
    time.sleep(0.001)
    return value * 2 + 1

# Create sample DataFrame
df = pd.DataFrame({
    'values': range(10000),
    'categories': ['A', 'B', 'C'] * 3334
})

print("Processing DataFrame with PyFerris...")
results = parallel_apply_to_dataframe(df, expensive_transform, column='values')

# Add results back to DataFrame
df['processed'] = results
print(f"Processed {len(df)} rows")
```

## Frequently Asked Questions

### Q: Why is my parallel code using 100% CPU but still slow?

**A:** This usually indicates CPU-bound work that's properly utilizing all cores, but the overhead of parallelization might be high. Try:

1. Increasing chunk size
2. Reducing the number of workers
3. Profiling to identify bottlenecks

```python
# Diagnostic code
from pyferris import set_chunk_size, set_worker_count
import time

def profile_settings(func, data):
    settings = [
        (1, 1000),    # 1 worker, 1000 chunk size
        (2, 500),     # 2 workers, 500 chunk size  
        (4, 250),     # 4 workers, 250 chunk size
        (8, 100),     # 8 workers, 100 chunk size
    ]
    
    for workers, chunk_size in settings:
        set_worker_count(workers)
        set_chunk_size(chunk_size)
        
        start = time.time()
        list(parallel_map(func, data))
        duration = time.time() - start
        
        print(f"Workers: {workers}, Chunk: {chunk_size} → {duration:.3f}s")
```

### Q: How do I handle functions that require global state?

**A:** Avoid global state in parallel functions. Instead, use one of these patterns:

```python
# Pattern 1: Pass state as parameters
def stateful_function(item, config_dict):
    # Use config_dict instead of global variables
    return item * config_dict['multiplier']

from functools import partial
from pyferris import parallel_map

config = {'multiplier': 5}
bound_function = partial(stateful_function, config_dict=config)
results = list(parallel_map(bound_function, data))

# Pattern 2: Use class-based approach
class StatefulProcessor:
    def __init__(self, config):
        self.config = config
    
    def process_item(self, item):
        return item * self.config['multiplier']

processor = StatefulProcessor({'multiplier': 5})
results = list(parallel_map(processor.process_item, data))
```

### Q: Can I use PyFerris with async/await code?

**A:** Yes, use the async operations module:

```python
import asyncio
from pyferris import async_parallel_map

async def async_worker(item):
    # Simulate async I/O
    await asyncio.sleep(0.01)
    return item * 2

async def main():
    data = range(100)
    results = await async_parallel_map(async_worker, data)
    print(f"Processed {len(list(results))} items asynchronously")

asyncio.run(main())
```

### Q: How do I optimize for my specific hardware?

**A:** Use the hardware analysis tools:

```python
import os
import psutil
from pyferris import set_worker_count, set_chunk_size

def auto_optimize():
    """Automatically optimize PyFerris for current hardware."""
    
    # Get hardware info
    cpu_count = os.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    # Optimize based on hardware
    if memory_gb < 4:
        # Low memory system
        workers = min(2, cpu_count)
        chunk_size = 100
    elif memory_gb < 8:
        # Medium memory system
        workers = min(4, cpu_count)
        chunk_size = 500
    else:
        # High memory system
        workers = cpu_count
        chunk_size = 1000
    
    set_worker_count(workers)
    set_chunk_size(chunk_size)
    
    print(f"Auto-optimized: {workers} workers, {chunk_size} chunk size")

auto_optimize()
```

## Getting Help

If you're still experiencing issues after trying these solutions:

1. **Check the GitHub Issues**: [PyFerris Issues](https://github.com/DVNghiem/Pyferris/issues)
2. **Create a minimal reproduction**: Simplify your problem to the smallest possible example
3. **Include system information**: OS, Python version, PyFerris version, hardware specs
4. **Provide error messages**: Full stack traces help diagnose issues quickly

### Issue Template

When reporting issues, please include:

```python
import sys
import platform
import pyferris

print("System Information:")
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print(f"PyFerris: {pyferris.__version__}")
print(f"CPU cores: {os.cpu_count()}")

# Minimal reproduction code here
```

This troubleshooting guide should help you resolve most common issues with PyFerris. Remember that parallel processing isn't always faster - profile your specific use case to determine the best approach.
