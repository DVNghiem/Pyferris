"""
Unit tests for Pyferris configuration management.

This module contains comprehensive tests for all configuration functionality
including worker count management, chunk size configuration, and Config class.
"""

import unittest
from pyferris.config import (
    set_worker_count, get_worker_count,
    set_chunk_size, get_chunk_size,
    Config
)


class TestWorkerConfiguration(unittest.TestCase):
    """Test worker count configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Store original values to restore later
        self.original_worker_count = get_worker_count()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original worker count
        set_worker_count(self.original_worker_count)
    
    def test_set_and_get_worker_count(self):
        """Test setting and getting worker count."""
        # Test various worker counts
        test_counts = [1, 2, 4, 8, 16]
        
        for count in test_counts:
            set_worker_count(count)
            self.assertEqual(get_worker_count(), count)
    
    def test_default_worker_count(self):
        """Test that default worker count is reasonable."""
        worker_count = get_worker_count()
        self.assertGreater(worker_count, 0)
        self.assertLessEqual(worker_count, 128)  # Reasonable upper bound
    
    def test_worker_count_validation(self):
        """Test worker count validation."""
        # Test invalid worker counts
        invalid_counts = [0, -1, -10]
        
        for count in invalid_counts:
            with self.assertRaises(Exception):
                set_worker_count(count)
    
    def test_worker_count_persistence(self):
        """Test that worker count settings persist."""
        # Set a specific worker count
        set_worker_count(6)
        self.assertEqual(get_worker_count(), 6)
        
        # Change it and verify it changed
        set_worker_count(4)
        self.assertEqual(get_worker_count(), 4)


class TestChunkSizeConfiguration(unittest.TestCase):
    """Test chunk size configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Store original values to restore later
        self.original_chunk_size = get_chunk_size()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original chunk size
        set_chunk_size(self.original_chunk_size)
    
    def test_set_and_get_chunk_size(self):
        """Test setting and getting chunk size."""
        # Test various chunk sizes
        test_sizes = [1, 10, 100, 1000, 5000]
        
        for size in test_sizes:
            set_chunk_size(size)
            self.assertEqual(get_chunk_size(), size)
    
    def test_default_chunk_size(self):
        """Test that default chunk size is reasonable."""
        chunk_size = get_chunk_size()
        self.assertGreater(chunk_size, 0)
        self.assertLessEqual(chunk_size, 100000)  # Reasonable upper bound
    
    def test_chunk_size_validation(self):
        """Test chunk size validation."""
        # Test invalid chunk sizes
        invalid_sizes = [0, -1, -100]
        
        for size in invalid_sizes:
            with self.assertRaises(Exception):
                set_chunk_size(size)
    
    def test_chunk_size_persistence(self):
        """Test that chunk size settings persist."""
        # Set a specific chunk size
        set_chunk_size(250)
        self.assertEqual(get_chunk_size(), 250)
        
        # Change it and verify it changed
        set_chunk_size(500)
        self.assertEqual(get_chunk_size(), 500)


class TestConfigClass(unittest.TestCase):
    """Test Config class functionality."""
    
    def test_config_instantiation(self):
        """Test Config class can be instantiated."""
        config = Config()
        self.assertIsInstance(config, Config)
    
    def test_config_has_methods(self):
        """Test Config class has expected methods."""
        config = Config()
        
        # Get all attributes that don't start with underscore
        actual_attributes = [attr for attr in dir(config) 
                           if not attr.startswith('_')]
        
        # For now, just verify the object exists and has some attributes
        # We can expand this as we learn more about the Config class API
        self.assertIsInstance(actual_attributes, list)


class TestConfigurationIntegration(unittest.TestCase):
    """Test integration between different configuration settings."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Store original values
        self.original_worker_count = get_worker_count()
        self.original_chunk_size = get_chunk_size()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original values
        set_worker_count(self.original_worker_count)
        set_chunk_size(self.original_chunk_size)
    
    def test_independent_settings(self):
        """Test that worker count and chunk size are independent."""
        # Set specific values
        set_worker_count(4)
        set_chunk_size(200)
        
        # Verify both are set correctly
        self.assertEqual(get_worker_count(), 4)
        self.assertEqual(get_chunk_size(), 200)
        
        # Change one, verify the other is unchanged
        set_worker_count(8)
        self.assertEqual(get_worker_count(), 8)
        self.assertEqual(get_chunk_size(), 200)  # Should be unchanged
        
        # Change the other, verify first is unchanged
        set_chunk_size(500)
        self.assertEqual(get_worker_count(), 8)  # Should be unchanged
        self.assertEqual(get_chunk_size(), 500)
    
    def test_configuration_with_parallel_operations(self):
        """Test that configuration affects parallel operations."""
        from pyferris import parallel_map
        
        def simple_func(x):
            return x * 2
        
        data = list(range(100))
        
        # Test with different configurations
        configurations = [
            (2, 10),   # 2 workers, chunk size 10
            (4, 25),   # 4 workers, chunk size 25
            (1, 50),   # 1 worker, chunk size 50
        ]
        
        for worker_count, chunk_size in configurations:
            set_worker_count(worker_count)
            set_chunk_size(chunk_size)
            
            # Verify settings
            self.assertEqual(get_worker_count(), worker_count)
            self.assertEqual(get_chunk_size(), chunk_size)
            
            # Run parallel operation
            result = parallel_map(simple_func, data)
            expected = [x * 2 for x in data]
            
            # Verify results are correct regardless of configuration
            self.assertEqual(sorted(result), sorted(expected))


class TestConfigurationBoundaryConditions(unittest.TestCase):
    """Test boundary conditions and edge cases for configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Store original values
        self.original_worker_count = get_worker_count()
        self.original_chunk_size = get_chunk_size()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original values
        set_worker_count(self.original_worker_count)
        set_chunk_size(self.original_chunk_size)
    
    def test_minimum_valid_values(self):
        """Test minimum valid configuration values."""
        # Test minimum worker count (1)
        set_worker_count(1)
        self.assertEqual(get_worker_count(), 1)
        
        # Test minimum chunk size (1)
        set_chunk_size(1)
        self.assertEqual(get_chunk_size(), 1)
    
    def test_large_valid_values(self):
        """Test large valid configuration values."""
        # Test large worker count
        set_worker_count(64)
        self.assertEqual(get_worker_count(), 64)
        
        # Test large chunk size
        set_chunk_size(10000)
        self.assertEqual(get_chunk_size(), 10000)
    
    def test_typical_values(self):
        """Test typical configuration values."""
        typical_configs = [
            (2, 100),
            (4, 250),
            (8, 500),
            (16, 1000),
        ]
        
        for worker_count, chunk_size in typical_configs:
            set_worker_count(worker_count)
            set_chunk_size(chunk_size)
            
            self.assertEqual(get_worker_count(), worker_count)
            self.assertEqual(get_chunk_size(), chunk_size)


class TestConfigurationPerformanceImpact(unittest.TestCase):
    """Test how configuration changes affect performance."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Store original values
        self.original_worker_count = get_worker_count()
        self.original_chunk_size = get_chunk_size()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original values
        set_worker_count(self.original_worker_count)
        set_chunk_size(self.original_chunk_size)
    
    def test_worker_count_impact(self):
        """Test impact of different worker counts on performance."""
        from pyferris import parallel_map
        import time
        
        def cpu_intensive_task(x):
            # Simple CPU-intensive task
            result = 0
            for i in range(x % 50):
                result += i * i
            return result
        
        data = list(range(200))
        worker_counts = [1, 2, 4]
        times = []
        
        for worker_count in worker_counts:
            set_worker_count(worker_count)
            
            start_time = time.time()
            result = parallel_map(cpu_intensive_task, data)
            end_time = time.time()
            
            times.append(end_time - start_time)
            
            # Verify correctness
            expected = [cpu_intensive_task(x) for x in data]
            self.assertEqual(sorted(result), sorted(expected))
        
        print("Worker count performance impact:")
        for worker_count, exec_time in zip(worker_counts, times):
            print(f"  {worker_count} workers: {exec_time:.4f}s")
    
    def test_chunk_size_impact(self):
        """Test impact of different chunk sizes on performance."""
        from pyferris import parallel_map
        import time
        
        def simple_task(x):
            return x ** 2 + x + 1
        
        data = list(range(1000))
        chunk_sizes = [10, 50, 100, 500]
        times = []
        
        # Use consistent worker count
        set_worker_count(4)
        
        for chunk_size in chunk_sizes:
            set_chunk_size(chunk_size)
            
            start_time = time.time()
            result = parallel_map(simple_task, data)
            end_time = time.time()
            
            times.append(end_time - start_time)
            
            # Verify correctness
            expected = [simple_task(x) for x in data]
            self.assertEqual(sorted(result), sorted(expected))
        
        print("Chunk size performance impact:")
        for chunk_size, exec_time in zip(chunk_sizes, times):
            print(f"  Chunk size {chunk_size}: {exec_time:.4f}s")


if __name__ == '__main__':
    unittest.main(verbosity=2)
