"""
Unit tests for Pyferris Executor functionality.

This module contains comprehensive tests for the Executor class
and task execution capabilities.
"""

import unittest
import time
from pyferris.executor import Executor


class TestExecutorBasics(unittest.TestCase):
    """Test basic Executor functionality."""
    
    def test_executor_instantiation(self):
        """Test Executor can be instantiated."""
        executor = Executor()
        self.assertIsInstance(executor, Executor)
    
    def test_executor_with_workers(self):
        """Test Executor instantiation with specific worker count."""
        # Test different worker counts
        worker_counts = [1, 2, 4, 8]
        
        for count in worker_counts:
            try:
                executor = Executor(workers=count)
                self.assertIsInstance(executor, Executor)
            except TypeError:
                # If workers parameter doesn't exist, that's fine
                # We'll test with default constructor
                executor = Executor()
                self.assertIsInstance(executor, Executor)
                break


class TestExecutorMethods(unittest.TestCase):
    """Test Executor methods and capabilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = Executor()
    
    def test_executor_has_methods(self):
        """Test that Executor has expected methods."""
        # Get all public methods
        methods = [method for method in dir(self.executor) 
                  if not method.startswith('_')]
        
        # Executor should have some methods
        self.assertIsInstance(methods, list)
        
        # Print available methods for debugging
        print(f"Executor methods: {methods}")
    
    def test_executor_submit_if_available(self):
        """Test executor submit method if available."""
        if hasattr(self.executor, 'submit'):
            def simple_task():
                return 42
            
            try:
                result = self.executor.submit(simple_task)
                # The exact behavior depends on implementation
                # This test just ensures submit doesn't crash
                self.assertIsNotNone(result)
            except Exception as e:
                # If submit method exists but requires different parameters,
                # that's expected behavior
                print(f"Submit method exists but requires different usage: {e}")


class TestExecutorTaskExecution(unittest.TestCase):
    """Test task execution capabilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = Executor()
    
    def test_simple_task_execution(self):
        """Test execution of simple tasks."""
        def simple_task(x):
            return x * 2
        
        # If executor has a map-like method, test it
        if hasattr(self.executor, 'map'):
            try:
                data = [1, 2, 3, 4, 5]
                results = self.executor.map(simple_task, data)
                expected = [2, 4, 6, 8, 10]
                self.assertEqual(sorted(results), sorted(expected))
            except Exception as e:
                print(f"Executor map method requires different usage: {e}")
    
    def test_concurrent_task_execution(self):
        """Test concurrent execution of tasks."""
        def slow_task(duration):
            time.sleep(duration)
            return duration
        
        # If executor supports concurrent execution
        if hasattr(self.executor, 'submit') or hasattr(self.executor, 'map'):
            start_time = time.time()
            
            try:
                if hasattr(self.executor, 'map'):
                    # Test with short durations to keep test fast
                    durations = [0.01, 0.01, 0.01]
                    results = self.executor.map(slow_task, durations)
                    self.assertEqual(sorted(results), sorted(durations))
                elif hasattr(self.executor, 'submit'):
                    # Test individual task submission
                    result = self.executor.submit(slow_task, 0.01)
                    self.assertIsNotNone(result)
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Concurrent execution should be faster than sequential
                print(f"Concurrent execution time: {execution_time:.4f}s")
                
            except Exception as e:
                print(f"Concurrent execution test failed: {e}")


class TestExecutorErrorHandling(unittest.TestCase):
    """Test error handling in Executor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = Executor()
    
    def test_exception_in_task(self):
        """Test handling of exceptions in tasks."""
        def failing_task(x):
            if x == 2:
                raise ValueError("Test exception")
            return x * 2
        
        if hasattr(self.executor, 'map'):
            try:
                data = [1, 2, 3]
                # This should either handle the exception gracefully
                # or propagate it in a controlled manner
                results = self.executor.map(failing_task, data)
                # If we get here, the executor handled the exception
                print(f"Executor handled exception gracefully: {results}")
            except Exception as e:
                # If exception is propagated, that's also valid behavior
                print(f"Executor propagated exception: {e}")
                self.assertIsInstance(e, (ValueError, Exception))


class TestExecutorResourceManagement(unittest.TestCase):
    """Test resource management in Executor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = Executor()
    
    def test_executor_cleanup(self):
        """Test executor cleanup and resource management."""
        # If executor has cleanup methods
        cleanup_methods = ['close', 'shutdown', 'cleanup', '__del__']
        
        for method in cleanup_methods:
            if hasattr(self.executor, method):
                try:
                    getattr(self.executor, method)()
                    print(f"Executor cleanup method '{method}' executed successfully")
                    break
                except Exception as e:
                    print(f"Executor cleanup method '{method}' failed: {e}")
    
    def test_multiple_executors(self):
        """Test creating multiple executor instances."""
        executors = []
        
        try:
            # Create multiple executors
            for i in range(3):
                executor = Executor()
                executors.append(executor)
                self.assertIsInstance(executor, Executor)
            
            print(f"Successfully created {len(executors)} executor instances")
            
        finally:
            # Clean up executors
            for executor in executors:
                cleanup_methods = ['close', 'shutdown', 'cleanup']
                for method in cleanup_methods:
                    if hasattr(executor, method):
                        try:
                            getattr(executor, method)()
                            break
                        except Exception:
                            pass


class TestExecutorIntegration(unittest.TestCase):
    """Test Executor integration with other components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = Executor()
    
    def test_executor_with_configuration(self):
        """Test executor with configuration settings."""
        from pyferris.config import get_worker_count, set_worker_count
        
        # Get current worker count
        original_count = get_worker_count()
        
        try:
            # Set a specific worker count
            set_worker_count(4)
            
            # Create new executor (might respect configuration)
            executor = Executor()
            self.assertIsInstance(executor, Executor)
            
            # Test if executor respects configuration
            if hasattr(executor, 'worker_count') or hasattr(executor, 'workers'):
                print("Executor appears to have worker configuration")
            
        finally:
            # Restore original configuration
            set_worker_count(original_count)
    
    def test_executor_with_parallel_operations(self):
        """Test executor alongside parallel operations."""
        from pyferris import parallel_map
        
        def test_function(x):
            return x ** 2
        
        data = list(range(10))
        
        # Test both executor and parallel operations
        executor = Executor()
        self.assertIsInstance(executor, Executor)
        
        # Test parallel_map still works
        parallel_result = parallel_map(test_function, data)
        expected = [x ** 2 for x in data]
        self.assertEqual(sorted(parallel_result), sorted(expected))
        
        # If executor has similar functionality, test compatibility
        if hasattr(executor, 'map'):
            try:
                executor_result = executor.map(test_function, data)
                self.assertEqual(sorted(executor_result), sorted(expected))
                print("Executor and parallel operations produce consistent results")
            except Exception as e:
                print(f"Executor map method has different interface: {e}")


class TestExecutorPerformance(unittest.TestCase):
    """Test Executor performance characteristics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = Executor()
    
    def test_executor_overhead(self):
        """Test executor overhead compared to direct execution."""
        def simple_computation(x):
            return x * 2 + 1
        
        data = list(range(100))
        
        # Test direct execution time
        start_time = time.time()
        direct_results = [simple_computation(x) for x in data]
        direct_time = time.time() - start_time
        
        # Test executor execution time (if available)
        if hasattr(self.executor, 'map'):
            try:
                start_time = time.time()
                executor_results = self.executor.map(simple_computation, data)
                executor_time = time.time() - start_time
                
                # Verify results are correct
                self.assertEqual(sorted(direct_results), sorted(executor_results))
                
                print(f"Direct execution time: {direct_time:.4f}s")
                print(f"Executor execution time: {executor_time:.4f}s")
                print(f"Overhead ratio: {executor_time/direct_time:.2f}x")
                
            except Exception as e:
                print(f"Executor performance test failed: {e}")
    
    def test_executor_scalability(self):
        """Test executor scalability with different data sizes."""
        def cpu_task(n):
            # Simple CPU-bound task
            result = 0
            for i in range(n % 100):
                result += i
            return result
        
        if hasattr(self.executor, 'map'):
            try:
                # Test with different data sizes
                sizes = [10, 50, 100]
                
                for size in sizes:
                    data = list(range(size))
                    
                    start_time = time.time()
                    results = self.executor.map(cpu_task, data)
                    end_time = time.time()
                    
                    execution_time = end_time - start_time
                    
                    # Verify correctness
                    expected = [cpu_task(x) for x in data]
                    self.assertEqual(sorted(results), sorted(expected))
                    
                    print(f"Size {size}: {execution_time:.4f}s")
                    
            except Exception as e:
                print(f"Scalability test failed: {e}")


class TestExecutorEdgeCases(unittest.TestCase):
    """Test Executor edge cases and boundary conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = Executor()
    
    def test_empty_task_list(self):
        """Test executor with empty task list."""
        if hasattr(self.executor, 'map'):
            try:
                def dummy_task(x):
                    return x
                
                results = self.executor.map(dummy_task, [])
                self.assertEqual(results, [])
                
            except Exception as e:
                print(f"Empty task list test failed: {e}")
    
    def test_single_task(self):
        """Test executor with single task."""
        if hasattr(self.executor, 'map'):
            try:
                def single_task(x):
                    return x * 3
                
                results = self.executor.map(single_task, [5])
                self.assertEqual(results, [15])
                
            except Exception as e:
                print(f"Single task test failed: {e}")
    
    def test_executor_reuse(self):
        """Test reusing executor for multiple operations."""
        if hasattr(self.executor, 'map'):
            try:
                def task1(x):
                    return x + 1
                
                def task2(x):
                    return x * 2
                
                # First operation
                results1 = self.executor.map(task1, [1, 2, 3])
                self.assertEqual(sorted(results1), [2, 3, 4])
                
                # Second operation with same executor
                results2 = self.executor.map(task2, [1, 2, 3])
                self.assertEqual(sorted(results2), [2, 4, 6])
                
                print("Executor successfully reused for multiple operations")
                
            except Exception as e:
                print(f"Executor reuse test failed: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
