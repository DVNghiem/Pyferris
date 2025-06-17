"""
Unit tests for Pyferris core parallel operations.

This module contains comprehensive tests for all core parallel functionality
including parallel_map, parallel_filter, parallel_reduce, and parallel_starmap.
"""

import unittest
import time
from pyferris import parallel_map, parallel_filter, parallel_reduce, parallel_starmap


class TestParallelMap(unittest.TestCase):
    """Test parallel_map functionality."""
    
    def test_simple_map(self):
        """Test basic parallel mapping."""
        def square(x):
            return x * x
        
        data = list(range(10))
        result = parallel_map(square, data)
        expected = [x * x for x in data]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_empty_iterable(self):
        """Test parallel_map with empty iterable."""
        def identity(x):
            return x
        
        result = parallel_map(identity, [])
        self.assertEqual(result, [])
    
    def test_single_item(self):
        """Test parallel_map with single item."""
        def double(x):
            return x * 2
        
        result = parallel_map(double, [5])
        self.assertEqual(result, [10])
    
    def test_large_dataset(self):
        """Test parallel_map with large dataset."""
        def increment(x):
            return x + 1
        
        data = list(range(10000))
        result = parallel_map(increment, data)
        expected = [x + 1 for x in data]
        
        self.assertEqual(len(result), len(expected))
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_custom_chunk_size(self):
        """Test parallel_map with custom chunk size."""
        def multiply_by_3(x):
            return x * 3
        
        data = list(range(100))
        result = parallel_map(multiply_by_3, data, chunk_size=10)
        expected = [x * 3 for x in data]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_string_operations(self):
        """Test parallel_map with string operations."""
        def uppercase(s):
            return s.upper()
        
        data = ["hello", "world", "python", "rust"]
        result = parallel_map(uppercase, data)
        expected = [s.upper() for s in data]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_complex_function(self):
        """Test parallel_map with more complex function."""
        def complex_calc(x):
            # Simulate some computational work
            result = 0
            for i in range(x % 100):
                result += i * i
            return result
        
        data = list(range(50, 150))
        result = parallel_map(complex_calc, data)
        expected = [complex_calc(x) for x in data]
        
        self.assertEqual(sorted(result), sorted(expected))


class TestParallelFilter(unittest.TestCase):
    """Test parallel_filter functionality."""
    
    def test_simple_filter(self):
        """Test basic parallel filtering."""
        def is_even(x):
            return x % 2 == 0
        
        data = list(range(20))
        result = parallel_filter(is_even, data)
        expected = [x for x in data if x % 2 == 0]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_empty_iterable(self):
        """Test parallel_filter with empty iterable."""
        def always_true(x):
            return True
        
        result = parallel_filter(always_true, [])
        self.assertEqual(result, [])
    
    def test_no_matches(self):
        """Test parallel_filter with no matching items."""
        def always_false(x):
            return False
        
        data = list(range(10))
        result = parallel_filter(always_false, data)
        self.assertEqual(result, [])
    
    def test_all_matches(self):
        """Test parallel_filter where all items match."""
        def always_true(x):
            return True
        
        data = list(range(10))
        result = parallel_filter(always_true, data)
        self.assertEqual(sorted(result), sorted(data))
    
    def test_string_filter(self):
        """Test parallel_filter with strings."""
        def starts_with_p(s):
            return s.startswith('p')
        
        data = ["python", "rust", "go", "perl", "java", "php"]
        result = parallel_filter(starts_with_p, data)
        expected = ["python", "perl", "php"]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_custom_chunk_size(self):
        """Test parallel_filter with custom chunk size."""
        def is_odd(x):
            return x % 2 == 1
        
        data = list(range(100))
        result = parallel_filter(is_odd, data, chunk_size=15)
        expected = [x for x in data if x % 2 == 1]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_complex_predicate(self):
        """Test parallel_filter with complex predicate."""
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return False
            return True
        
        data = list(range(2, 100))
        result = parallel_filter(is_prime, data)
        expected = [x for x in data if is_prime(x)]
        
        self.assertEqual(sorted(result), sorted(expected))


class TestParallelReduce(unittest.TestCase):
    """Test parallel_reduce functionality."""
    
    def test_simple_reduce(self):
        """Test basic parallel reduction."""
        def add(x, y):
            return x + y
        
        data = list(range(1, 11))  # 1 to 10
        result = parallel_reduce(add, data)
        expected = sum(data)  # 55
        
        self.assertEqual(result, expected)
    
    def test_reduce_with_initializer(self):
        """Test parallel_reduce with initializer."""
        def multiply(x, y):
            return x * y
        
        data = [2, 3, 4]
        result = parallel_reduce(multiply, data, initializer=1)
        expected = 24  # 1 * 2 * 3 * 4
        
        self.assertEqual(result, expected)
    
    def test_single_item(self):
        """Test parallel_reduce with single item."""
        def add(x, y):
            return x + y
        
        result = parallel_reduce(add, [42])
        self.assertEqual(result, 42)
    
    def test_string_concatenation(self):
        """Test parallel_reduce with string concatenation."""
        def concat(x, y):
            return x + y
        
        data = ["hello", " ", "world", "!"]
        result = parallel_reduce(concat, data)
        expected = "hello world!"
        
        self.assertEqual(result, expected)
    
    def test_custom_chunk_size(self):
        """Test parallel_reduce with custom chunk size."""
        def multiply(x, y):
            return x * y
        
        data = [1, 2, 3, 4, 5]
        result = parallel_reduce(multiply, data, chunk_size=2)
        expected = 120  # 1 * 2 * 3 * 4 * 5
        
        self.assertEqual(result, expected)
    
    def test_max_reduction(self):
        """Test parallel_reduce for finding maximum."""
        def maximum(x, y):
            return max(x, y)
        
        data = [3, 7, 2, 9, 1, 8, 4]
        result = parallel_reduce(maximum, data)
        expected = max(data)
        
        self.assertEqual(result, expected)


class TestParallelStarmap(unittest.TestCase):
    """Test parallel_starmap functionality."""
    
    def test_simple_starmap(self):
        """Test basic parallel starmap."""
        def add(x, y):
            return x + y
        
        data = [(1, 2), (3, 4), (5, 6)]
        result = parallel_starmap(add, data)
        expected = [3, 7, 11]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_empty_iterable(self):
        """Test parallel_starmap with empty iterable."""
        def multiply(x, y):
            return x * y
        
        result = parallel_starmap(multiply, [])
        self.assertEqual(result, [])
    
    def test_three_arguments(self):
        """Test parallel_starmap with three arguments."""
        def add_three(x, y, z):
            return x + y + z
        
        data = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
        result = parallel_starmap(add_three, data)
        expected = [6, 15, 24]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_string_operations(self):
        """Test parallel_starmap with string operations."""
        def format_name(first, last):
            return f"{first} {last}"
        
        data = [("John", "Doe"), ("Jane", "Smith"), ("Bob", "Johnson")]
        result = parallel_starmap(format_name, data)
        expected = ["John Doe", "Jane Smith", "Bob Johnson"]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_custom_chunk_size(self):
        """Test parallel_starmap with custom chunk size."""
        def power(base, exp):
            return base ** exp
        
        data = [(2, 3), (3, 2), (4, 2), (5, 2)]
        result = parallel_starmap(power, data, chunk_size=2)
        expected = [8, 9, 16, 25]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_complex_function(self):
        """Test parallel_starmap with complex function."""
        def calculate_distance(x1, y1, x2, y2):
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        
        data = [(0, 0, 3, 4), (1, 1, 4, 5), (2, 2, 5, 6)]
        result = parallel_starmap(calculate_distance, data)
        expected = [5.0, 5.0, 5.0]
        
        for r, e in zip(sorted(result), sorted(expected)):
            self.assertAlmostEqual(r, e, places=10)


class TestPerformanceCharacteristics(unittest.TestCase):
    """Test performance characteristics of parallel operations."""
    
    def setUp(self):
        """Set up performance test fixtures."""
        self.large_data = list(range(10000))
    
    def test_parallel_vs_sequential_map(self):
        """Compare parallel vs sequential map performance."""
        def expensive_operation(x):
            # Simulate some computation
            result = 0
            for i in range(x % 100):
                result += i
            return result
        
        # Test with smaller dataset for reasonable test time
        data = list(range(1000))
        
        # Sequential version
        start_time = time.time()
        sequential_result = [expensive_operation(x) for x in data]
        sequential_time = time.time() - start_time
        
        # Parallel version
        start_time = time.time()
        parallel_result = parallel_map(expensive_operation, data)
        parallel_time = time.time() - start_time
        
        # Results should be equivalent
        self.assertEqual(sorted(sequential_result), sorted(parallel_result))
        
        # Print performance info (parallel might not always be faster for small datasets)
        print(f"Sequential time: {sequential_time:.4f}s")
        print(f"Parallel time: {parallel_time:.4f}s")
    
    def test_chunk_size_impact(self):
        """Test impact of different chunk sizes."""
        def simple_calc(x):
            return x * 2 + 1
        
        data = list(range(1000))
        
        # Test different chunk sizes
        chunk_sizes = [10, 50, 100, 500]
        times = []
        
        for chunk_size in chunk_sizes:
            start_time = time.time()
            result = parallel_map(simple_calc, data, chunk_size=chunk_size)
            end_time = time.time()
            times.append(end_time - start_time)
            
            # Verify correctness
            expected = [x * 2 + 1 for x in data]
            self.assertEqual(sorted(result), sorted(expected))
        
        print("Chunk size performance:")
        for chunk_size, exec_time in zip(chunk_sizes, times):
            print(f"  Chunk size {chunk_size}: {exec_time:.4f}s")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_none_values(self):
        """Test handling of None values."""
        def handle_none(x):
            return x if x is not None else 0
        
        data = [1, None, 3, None, 5]
        result = parallel_map(handle_none, data)
        expected = [1, 0, 3, 0, 5]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_mixed_types(self):
        """Test handling of mixed data types."""
        def to_string(x):
            return str(x)
        
        data = [1, "hello", 3.14, True, None]
        result = parallel_map(to_string, data)
        expected = ["1", "hello", "3.14", "True", "None"]
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_exception_handling(self):
        """Test how exceptions are handled in parallel operations."""
        def divide_by_zero(x):
            return 1 / x
        
        data = [1, 2, 0, 4]
        
        # This should raise an exception due to division by zero
        with self.assertRaises(ZeroDivisionError):
            parallel_map(divide_by_zero, data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
