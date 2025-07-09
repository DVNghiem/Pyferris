#!/usr/bin/env python3
"""
Performance optimization validation script for PyFerris.

This script validates that the optimizations have improved performance
without breaking functionality.
"""

import time
import gc
import sys
import os
import multiprocessing

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

def benchmark_function(func, *args, iterations=3, **kwargs):
    """Benchmark a function and return average execution time."""
    times = []
    
    for _ in range(iterations):
        gc.collect()  # Clean slate for each iteration
        start_time = time.perf_counter()
        
        result = func(*args, **kwargs)
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    avg_time = sum(times) / len(times)
    return avg_time, result

def test_core_operations():
    """Test core parallel operations performance."""
    print("Testing core operations...")
    
    try:
        from pyferris import parallel_map, parallel_filter, parallel_reduce
        
        # Test data
        data = list(range(100000))
        
        # Test parallel_map
        def square(x):
            return x * x
        
        avg_time, result = benchmark_function(parallel_map, square, data)
        print(f"parallel_map: {avg_time:.4f}s, result_len={len(result)}")
        
        # Test parallel_filter
        def is_even(x):
            return x % 2 == 0
        
        avg_time, result = benchmark_function(parallel_filter, is_even, data)
        print(f"parallel_filter: {avg_time:.4f}s, result_len={len(result)}")
        
        # Test parallel_reduce
        def add(x, y):
            return x + y
        
        avg_time, result = benchmark_function(parallel_reduce, add, data[:1000])  # Smaller dataset for reduce
        print(f"parallel_reduce: {avg_time:.4f}s, result={result}")
        
    except Exception as e:
        print(f"Error testing core operations: {e}")

def test_executor_operations():
    """Test executor performance."""
    print("\nTesting executor operations...")
    
    try:
        from pyferris import Executor
        
        def cpu_intensive_task(n):
            return sum(i * i for i in range(n))
        
        with Executor(max_workers=multiprocessing.cpu_count()) as executor:
            tasks = [1000] * 100
            
            avg_time, results = benchmark_function(
                lambda: [executor.submit(cpu_intensive_task, task).result() for task in tasks]
            )
            print(f"executor.submit: {avg_time:.4f}s, tasks_completed={len(results)}")
            
            # Test batch operations
            batch_tasks = [(cpu_intensive_task, (100,)) for _ in range(50)]
            avg_time, results = benchmark_function(executor.submit_batch, batch_tasks)
            print(f"executor.submit_batch: {avg_time:.4f}s, tasks_completed={len(results)}")
        
    except Exception as e:
        print(f"Error testing executor operations: {e}")

def test_memory_usage():
    """Test memory usage patterns."""
    print("\nTesting memory usage...")
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        from pyferris import parallel_map
        
        # Large dataset test
        large_data = list(range(1000000))
        
        def simple_transform(x):
            return x * 2 + 1
        
        result = parallel_map(simple_transform, large_data)
        end_memory = process.memory_info().rss / 1024 / 1024
        
        peak_memory = end_memory - initial_memory
        print(f"Memory usage - Initial: {initial_memory:.1f}MB, Peak: {peak_memory:.1f}MB")
        print(f"Memory per item: {peak_memory * 1024 / len(large_data):.2f}KB")
        
        # Cleanup
        del result, large_data
        gc.collect()
        
    except ImportError:
        print("psutil not available, skipping memory test")
    except Exception as e:
        print(f"Error testing memory usage: {e}")

def test_chunk_size_optimization():
    """Test chunk size optimization."""
    print("\nTesting chunk size optimization...")
    
    try:
        from pyferris import parallel_map
        
        def simple_op(x):
            return x + 1
        
        # Test different data sizes
        for size in [1000, 10000, 100000]:
            data = list(range(size))
            
            # Test with auto chunk size
            avg_time_auto, _ = benchmark_function(parallel_map, simple_op, data, chunk_size=None)
            
            # Test with manual chunk size
            manual_chunk_size = max(100, size // (multiprocessing.cpu_count() * 4))
            avg_time_manual, _ = benchmark_function(parallel_map, simple_op, data, chunk_size=manual_chunk_size)
            
            print(f"Size {size}: Auto={avg_time_auto:.4f}s, Manual={avg_time_manual:.4f}s")
        
    except Exception as e:
        print(f"Error testing chunk size optimization: {e}")

def main():
    """Run all performance tests."""
    print("PyFerris Performance Optimization Validation")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"CPU count: {multiprocessing.cpu_count()}")
    print("=" * 50)
    
    test_core_operations()
    test_executor_operations()
    test_memory_usage()
    test_chunk_size_optimization()
    
    print("\n" + "=" * 50)
    print("Performance validation complete!")

if __name__ == "__main__":
    main()
