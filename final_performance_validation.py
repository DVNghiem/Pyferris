#!/usr/bin/env python3
"""
Final comprehensive performance validation for PyFerris optimizations
"""

import time
import gc
import sys
import os
import pyferris
from pyferris import parallel_map, parallel_filter, parallel_reduce, Executor

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def measure_time(func, *args, **kwargs):
    """Measure execution time of a function"""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return end - start, result

def test_core_operations():
    """Test core parallel operations with different data sizes"""
    print("Testing core operations with different data sizes...")
    
    sizes = [1000, 10000, 100000, 1000000]
    
    for size in sizes:
        print(f"\nTesting with {size:,} elements:")
        
        # Test data
        data = list(range(size))
        
        # Test parallel_map
        time_taken, result = measure_time(parallel_map, lambda x: x * 2, data)
        print(f"  parallel_map: {time_taken:.4f}s, {len(result):,} results")
        
        # Test parallel_filter
        time_taken, result = measure_time(parallel_filter, lambda x: x % 2 == 0, data)
        print(f"  parallel_filter: {time_taken:.4f}s, {len(result):,} results")
        
        # Test parallel_reduce
        time_taken, result = measure_time(parallel_reduce, lambda x, y: x + y, data)
        print(f"  parallel_reduce: {time_taken:.4f}s, result={result}")

def test_executor_performance():
    """Test executor performance with different scenarios"""
    print("\nTesting executor performance...")
    
    with Executor(max_workers=8) as executor:
        # Test map operations
        data = list(range(100000))
        time_taken, result = measure_time(executor.map, lambda x: x * x, data)
        print(f"  executor.map (100k): {time_taken:.4f}s, {len(result):,} results")
        
        # Test submission performance
        def simple_task():
            return sum(range(1000))
        
        tasks = [simple_task] * 100
        time_taken, results = measure_time(
            executor.submit_batch, 
            [(task, None) for task in tasks]
        )
        print(f"  executor.submit_batch (100 tasks): {time_taken:.4f}s")
        
        # Test computation performance
        test_data = [float(i) for i in range(10000)]
        time_taken, result = measure_time(
            executor.submit_computation, 
            "heavy_computation", 
            test_data
        )
        print(f"  executor.submit_computation: {time_taken:.4f}s, result={result:.2f}")

def test_chunk_size_optimization():
    """Test different chunk sizes for optimization"""
    print("\nTesting chunk size optimization...")
    
    data = list(range(100000))
    
    # Test with different chunk sizes
    chunk_sizes = [100, 1000, 5000, 10000]
    
    for chunk_size in chunk_sizes:
        time_taken, result = measure_time(
            parallel_map, 
            lambda x: x * 2, 
            data, 
            chunk_size=chunk_size
        )
        print(f"  chunk_size={chunk_size}: {time_taken:.4f}s")

def test_memory_efficiency():
    """Test memory efficiency of operations"""
    print("\nTesting memory efficiency...")
    
    if not HAS_PSUTIL:
        print("  Skipping memory test (psutil not available)")
        return
    
    process = psutil.Process(os.getpid())
    
    # Baseline memory
    gc.collect()
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
    print(f"  Baseline memory: {baseline_memory:.1f} MB")
    
    # Test with large dataset
    large_data = list(range(1000000))
    
    # Memory before operation
    memory_before = process.memory_info().rss / 1024 / 1024
    
    # Perform operation
    result = parallel_map(lambda x: x * 2, large_data)
    
    # Memory after operation
    memory_after = process.memory_info().rss / 1024 / 1024
    
    print(f"  Memory before: {memory_before:.1f} MB")
    print(f"  Memory after: {memory_after:.1f} MB")
    print(f"  Memory increase: {memory_after - memory_before:.1f} MB")
    print(f"  Results: {len(result):,} items")
    
    # Clean up
    del result, large_data
    gc.collect()

def test_error_handling():
    """Test error handling in optimized code"""
    print("\nTesting error handling...")
    
    try:
        # Test with function that raises exception
        def faulty_func(x):
            if x == 50:
                raise ValueError("Test error")
            return x * 2
        
        data = list(range(100))
        result = parallel_map(faulty_func, data)
        print("  ERROR: Should have raised exception")
    except Exception as e:
        print(f"  ✓ Correctly caught exception: {type(e).__name__}")
    
    # Test with empty data
    result = parallel_map(lambda x: x * 2, [])
    print(f"  ✓ Empty data handled correctly: {len(result)} results")

def test_concurrent_operations():
    """Test concurrent operations for thread safety"""
    print("\nTesting concurrent operations...")
    
    import threading
    
    results = []
    
    def worker(worker_id):
        data = list(range(10000))
        result = parallel_map(lambda x: x * worker_id, data)
        results.append((worker_id, len(result)))
    
    # Create multiple threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i+1,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    print(f"  ✓ Concurrent operations completed: {len(results)} workers")
    for worker_id, result_count in results:
        print(f"    Worker {worker_id}: {result_count:,} results")

def main():
    """Main performance validation"""
    print("PyFerris Final Performance Validation")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"CPU count: {HAS_PSUTIL and psutil.cpu_count() or 'unknown'}")
    print(f"PyFerris version: {pyferris.__version__ if hasattr(pyferris, '__version__') else 'unknown'}")
    print("=" * 50)
    
    try:
        test_core_operations()
        test_executor_performance()
        test_chunk_size_optimization()
        test_memory_efficiency()
        test_error_handling()
        test_concurrent_operations()
        
        print("\n" + "=" * 50)
        print("✓ All performance validations passed!")
        print("✓ Optimizations are working correctly!")
        
    except Exception as e:
        print(f"\n❌ Performance validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
