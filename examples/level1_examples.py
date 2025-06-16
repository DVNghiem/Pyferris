"""
PyFerris Level 1 Examples

This file demonstrates the basic features of PyFerris Level 1:
- Core parallel operations
- Task executor
- Basic configuration
- Error handling
"""

import time
import sys
import os

# Add the project root to Python path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def basic_parallel_operations():
    """Demonstrate core parallel operations."""
    print("=== Basic Parallel Operations ===")
    
    try:
        from pyferris import parallel_map, parallel_filter, parallel_reduce, parallel_starmap
        
        # Parallel map example
        print("\n1. Parallel Map:")
        def square(x):
            return x * x
        
        numbers = list(range(10))
        print(f"Input: {numbers}")
        results = parallel_map(square, numbers)
        print(f"Squares: {list(results)}")
        
        # Parallel filter example
        print("\n2. Parallel Filter:")
        def is_even(x):
            return x % 2 == 0
        
        numbers = list(range(20))
        print(f"Input: {numbers}")
        evens = parallel_filter(is_even, numbers)
        print(f"Even numbers: {list(evens)}")
        
        # Parallel reduce example
        print("\n3. Parallel Reduce:")
        def add(x, y):
            return x + y
        
        numbers = list(range(1, 11))
        print(f"Input: {numbers}")
        total = parallel_reduce(add, numbers)
        print(f"Sum: {total}")
        
        # Parallel starmap example
        print("\n4. Parallel Starmap:")
        def multiply(x, y):
            return x * y
        
        pairs = [(1, 2), (3, 4), (5, 6), (7, 8)]
        print(f"Input pairs: {pairs}")
        products = parallel_starmap(multiply, pairs)
        print(f"Products: {list(products)}")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please build the project first with: maturin develop")

def executor_example():
    """Demonstrate the Executor class."""
    print("\n=== Task Executor Example ===")
    
    try:
        from pyferris import Executor
        
        def expensive_task(x):
            # Simulate some work
            time.sleep(0.1)
            return x ** 2
        
        print("\nUsing Executor with context manager:")
        with Executor(max_workers=4) as executor:
            numbers = list(range(5))
            print(f"Input: {numbers}")
            
            start_time = time.time()
            results = executor.map(expensive_task, numbers)
            end_time = time.time()
            
            print(f"Results: {list(results)}")
            print(f"Time taken: {end_time - start_time:.2f} seconds")
            
    except ImportError as e:
        print(f"Import error: {e}")

def configuration_example():
    """Demonstrate configuration management."""
    print("\n=== Configuration Example ===")
    
    try:
        from pyferris import (
            set_worker_count, get_worker_count, 
            set_chunk_size, get_chunk_size, 
            Config
        )
        
        print(f"Default worker count: {get_worker_count()}")
        print(f"Default chunk size: {get_chunk_size()}")
        
        # Set custom configuration
        set_worker_count(8)
        set_chunk_size(500)
        
        print(f"New worker count: {get_worker_count()}")
        print(f"New chunk size: {get_chunk_size()}")
        
        # Using Config class
        print("\nUsing Config class:")
        config = Config(worker_count=4, chunk_size=1000, error_strategy="raise")
        print(f"Config: {config}")
        config.apply()
        
        print(f"Applied worker count: {get_worker_count()}")
        print(f"Applied chunk size: {get_chunk_size()}")
        
    except ImportError as e:
        print(f"Import error: {e}")

def error_handling_example():
    """Demonstrate error handling."""
    print("\n=== Error Handling Example ===")
    
    try:
        from pyferris import parallel_map, ParallelExecutionError
        
        def problematic_function(x):
            if x == 5:
                raise ValueError(f"Problem with value: {x}")
            return x * 2
        
        print("Testing error handling:")
        numbers = list(range(10))
        
        try:
            results = parallel_map(problematic_function, numbers)
            print(f"Results: {list(results)}")
        except Exception as e:
            print(f"Caught error: {type(e).__name__}: {e}")
            
    except ImportError as e:
        print(f"Import error: {e}")

def performance_comparison():
    """Compare parallel vs sequential performance."""
    print("\n=== Performance Comparison ===")
    
    try:
        from pyferris import parallel_map
        
        def cpu_intensive_task(x):
            # Simulate CPU-intensive work
            total = 0
            for i in range(10000):
                total += i * x
            return total
        
        numbers = list(range(100))
        
        # Sequential processing
        print("Sequential processing...")
        start_time = time.time()
        sequential_results = [cpu_intensive_task(x) for x in numbers]
        sequential_time = time.time() - start_time
        
        # Parallel processing
        print("Parallel processing...")
        start_time = time.time()
        parallel_results = list(parallel_map(cpu_intensive_task, numbers))
        parallel_time = time.time() - start_time
        
        print(f"Sequential time: {sequential_time:.2f} seconds")
        print(f"Parallel time: {parallel_time:.2f} seconds")
        print(f"Speedup: {sequential_time / parallel_time:.2f}x")
        
        # Verify results are the same
        print(f"Results match: {sequential_results == parallel_results}")
        
    except ImportError as e:
        print(f"Import error: {e}")

if __name__ == "__main__":
    print("PyFerris Level 1 Examples")
    print("=" * 50)
    
    basic_parallel_operations()
    executor_example()
    configuration_example()
    error_handling_example()
    performance_comparison()
    
    print("\n" + "=" * 50)
    print("Level 1 examples completed!")
