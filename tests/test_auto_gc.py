"""
Tests for the Auto Garbage Collection System

This module provides comprehensive tests for the automatic garbage collection
system, including memory management, resource cleanup, and performance optimization.
"""

import unittest
import threading
import time
import tempfile
import os
import gc

from pyferris.gc import (
    AutoGCConfig, AutoGarbageCollector, MemoryTracker, ResourceManager,
    ManagedMemoryPool, get_auto_gc, enable_auto_gc, disable_auto_gc, force_gc,
    gc_stats, track_allocation, track_deallocation, register_memory_pool,
    register_mmap_file, register_cleanup_callback, managed_memory, 
    auto_gc_decorator, create_managed_mmap
)
from pyferris.memory import MemoryPool


class TestAutoGCConfig(unittest.TestCase):
    """Test AutoGCConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = AutoGCConfig()
        
        self.assertTrue(config.enabled)
        self.assertFalse(config.aggressive_mode)
        self.assertEqual(config.memory_threshold_mb, 512)
        self.assertEqual(config.memory_threshold_percent, 80)
        self.assertEqual(config.cleanup_interval, 5.0)
        self.assertEqual(config.generation_thresholds, (700, 10, 10))
        self.assertTrue(config.track_allocations)
        self.assertTrue(config.profile_gc)
        self.assertTrue(config.auto_optimize)
        self.assertTrue(config.weak_ref_cleanup)
        self.assertTrue(config.memory_pool_management)
        self.assertTrue(config.mmap_file_cleanup)
        self.assertTrue(config.thread_safe)
        self.assertEqual(config.emergency_threshold_mb, 1024)
        self.assertEqual(config.max_cleanup_time, 10.0)
        
    def test_custom_config(self):
        """Test custom configuration values."""
        config = AutoGCConfig()
        config.enabled = False
        config.aggressive_mode = True
        config.memory_threshold_mb = 256
        config.cleanup_interval = 10.0
        
        self.assertFalse(config.enabled)
        self.assertTrue(config.aggressive_mode)
        self.assertEqual(config.memory_threshold_mb, 256)
        self.assertEqual(config.cleanup_interval, 10.0)


class TestMemoryTracker(unittest.TestCase):
    """Test MemoryTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = MemoryTracker()
        
    def test_track_allocation(self):
        """Test allocation tracking."""
        self.tracker.track_allocation("test_object", 1024)
        
        stats = self.tracker.get_memory_stats()
        self.assertEqual(stats['allocations_by_type']['test_object'], 1024)
        self.assertEqual(stats['total_allocations'], 1)
        
    def test_track_deallocation(self):
        """Test deallocation tracking."""
        self.tracker.track_allocation("test_object", 1024)
        self.tracker.track_deallocation("test_object", 512)
        
        stats = self.tracker.get_memory_stats()
        self.assertEqual(stats['allocations_by_type']['test_object'], 1024)
        self.assertEqual(stats['deallocations_by_type']['test_object'], 512)
        self.assertEqual(stats['total_allocations'], 1)
        self.assertEqual(stats['total_deallocations'], 1)
        self.assertEqual(stats['net_allocations'], 0)
        
    def test_memory_stats(self):
        """Test memory statistics."""
        self.tracker.track_allocation("object1", 512)
        self.tracker.track_allocation("object2", 1024)
        self.tracker.track_deallocation("object1", 256)
        
        stats = self.tracker.get_memory_stats()
        
        self.assertIn('current_memory_mb', stats)
        self.assertIn('peak_memory_mb', stats)
        self.assertIn('total_allocations', stats)
        self.assertIn('total_deallocations', stats)
        self.assertIn('net_allocations', stats)
        self.assertIn('allocations_by_type', stats)
        self.assertIn('deallocations_by_type', stats)
        self.assertIn('memory_timeline', stats)
        self.assertIn('gc_stats', stats)
        self.assertIn('gc_counts', stats)
        
        self.assertEqual(stats['total_allocations'], 2)
        self.assertEqual(stats['total_deallocations'], 1)
        self.assertEqual(stats['net_allocations'], 1)
        self.assertEqual(stats['allocations_by_type']['object1'], 512)
        self.assertEqual(stats['allocations_by_type']['object2'], 1024)
        self.assertEqual(stats['deallocations_by_type']['object1'], 256)
        
    def test_thread_safety(self):
        """Test thread safety of memory tracker."""
        def track_allocations():
            for i in range(100):
                self.tracker.track_allocation(f"thread_object_{i}", 1024)
                
        def track_deallocations():
            for i in range(100):
                self.tracker.track_deallocation(f"thread_object_{i}", 512)
                
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=track_allocations))
            threads.append(threading.Thread(target=track_deallocations))
            
        for thread in threads:
            thread.start()
            
        for thread in threads:
            thread.join()
            
        stats = self.tracker.get_memory_stats()
        self.assertEqual(stats['total_allocations'], 500)
        self.assertEqual(stats['total_deallocations'], 500)


class TestResourceManager(unittest.TestCase):
    """Test ResourceManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = ResourceManager()
        
    def test_memory_pool_management(self):
        """Test memory pool registration and cleanup."""
        pool = MemoryPool(1024, 10)
        
        # Register pool
        self.manager.register_memory_pool(pool)
        self.assertIn(pool, self.manager.memory_pools)
        
        # Allocate some blocks
        blocks = [pool.allocate() for _ in range(5)]
        
        # Deallocate some blocks back to pool
        for block in blocks[:3]:
            pool.deallocate(block)
            
        # Cleanup pools
        freed_blocks = self.manager.cleanup_memory_pools()
        self.assertGreater(freed_blocks, 0)
        
        # Unregister pool
        self.manager.unregister_memory_pool(pool)
        self.assertNotIn(pool, self.manager.memory_pools)
        
    def test_mmap_file_management(self):
        """Test memory-mapped file registration."""
        test_file = "/tmp/test_mmap.dat"
        
        # Register file
        self.manager.register_mmap_file(test_file)
        self.assertIn(test_file, self.manager.mmap_files)
        
        # Unregister file
        self.manager.unregister_mmap_file(test_file)
        self.assertNotIn(test_file, self.manager.mmap_files)
        
    def test_cleanup_callbacks(self):
        """Test cleanup callback registration and execution."""
        callback_called = []
        
        def test_callback():
            callback_called.append(True)
            
        # Register callback
        self.manager.register_cleanup_callback(test_callback)
        
        # Run callbacks
        self.manager.run_cleanup_callbacks()
        
        self.assertTrue(callback_called)
        
    def test_weak_ref_cleanup(self):
        """Test weak reference cleanup."""
        import weakref
        
        # Create test objects that can have weak references
        class TestObject:
            def __init__(self, value):
                self.value = value
        
        test_objects = [TestObject(i) for i in range(10)]
        
        # Create weak references
        weak_refs = [weakref.ref(obj) for obj in test_objects]
        
        # Register weak references
        for ref in weak_refs:
            self.manager.register_weak_ref(ref)
            
        # Delete some objects
        del test_objects[:5]
        
        # Force garbage collection
        gc.collect()
        
        # Clean up weak references
        cleaned_refs = self.manager.cleanup_weak_refs()
        
        # Should have cleaned up dead references
        self.assertGreater(cleaned_refs, 0)


class TestAutoGarbageCollector(unittest.TestCase):
    """Test AutoGarbageCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = AutoGCConfig()
        self.config.cleanup_interval = 0.1  # Fast cleanup for testing
        self.config.memory_threshold_mb = 1  # Low threshold for testing
        self.collector = AutoGarbageCollector(self.config)
        
    def tearDown(self):
        """Clean up after tests."""
        self.collector.stop()
        
    def test_start_stop(self):
        """Test starting and stopping the collector."""
        self.assertFalse(self.collector._running)
        
        self.collector.start()
        self.assertTrue(self.collector._running)
        
        self.collector.stop()
        self.assertFalse(self.collector._running)
        
    def test_context_manager(self):
        """Test using collector as context manager."""
        with AutoGarbageCollector(self.config) as collector:
            self.assertTrue(collector._running)
            
        self.assertFalse(collector._running)
        
    def test_force_cleanup(self):
        """Test forced cleanup."""
        self.collector.start()
        
        # Track some allocations
        self.collector.memory_tracker.track_allocation("test", 1024)
        
        # Force cleanup
        self.collector.force_cleanup()
        
        # Should have some cleanup stats
        stats = self.collector.get_stats()
        self.assertIn('cleanup_stats', stats)
        
    def test_configuration(self):
        """Test dynamic configuration."""
        self.collector.configure(
            aggressive_mode=True,
            memory_threshold_mb=256
        )
        
        self.assertTrue(self.collector.config.aggressive_mode)
        self.assertEqual(self.collector.config.memory_threshold_mb, 256)
        
    def test_stats(self):
        """Test statistics collection."""
        stats = self.collector.get_stats()
        
        required_keys = [
            'enabled', 'running', 'emergency_cleanups', 'cleanup_stats',
            'memory_stats', 'gc_thresholds', 'gc_counts', 'gc_stats',
            'resource_counts'
        ]
        
        for key in required_keys:
            self.assertIn(key, stats)
            
    def test_memory_threshold_cleanup(self):
        """Test cleanup based on memory threshold."""
        # Set very low threshold
        self.collector.config.memory_threshold_mb = 0.001  # Very low threshold
        
        # Check current memory first
        current_memory = self.collector.memory_tracker.get_current_memory_mb()
        
        if current_memory > 0:
            # Should trigger cleanup (current memory should be above 0.001 MB)
            self.assertTrue(self.collector._should_cleanup())
        else:
            # If psutil is not available and memory is 0, test time-based cleanup
            # Set last cleanup to a time in the past
            self.collector._last_cleanup = time.time() - (self.collector.config.cleanup_interval * 3)
            self.assertTrue(self.collector._should_cleanup())
        
    def test_gc_optimization(self):
        """Test automatic GC optimization."""
        # Simulate high allocation rate
        for i in range(1500):
            self.collector.memory_tracker.track_allocation(f"obj_{i}", 1024)
            
        # Run optimization
        self.collector._optimize_gc_settings()
        
        # Should have adjusted thresholds
        thresholds = gc.get_threshold()
        self.assertIsInstance(thresholds, tuple)
        self.assertEqual(len(thresholds), 3)


class TestManagedMemoryPool(unittest.TestCase):
    """Test ManagedMemoryPool class."""
    
    def test_auto_registration(self):
        """Test automatic registration with resource manager."""
        pool = ManagedMemoryPool(1024, 10)
        
        # Should be automatically registered
        auto_gc = get_auto_gc()
        self.assertIn(pool, auto_gc.resource_manager.memory_pools)
        
    def test_allocation_deallocation(self):
        """Test allocation and deallocation."""
        pool = ManagedMemoryPool(1024, 10)
        
        # Test allocation
        block = pool.allocate()
        self.assertEqual(len(block), 1024)
        
        # Test deallocation
        pool.deallocate(block)
        
        # Test stats
        stats = pool.stats()
        self.assertIn('block_size', stats)
        self.assertIn('max_blocks', stats)


class TestGlobalFunctions(unittest.TestCase):
    """Test global functions."""
    
    def test_get_auto_gc(self):
        """Test get_auto_gc function."""
        auto_gc = get_auto_gc()
        self.assertIsInstance(auto_gc, AutoGarbageCollector)
        
        # Should return same instance
        auto_gc2 = get_auto_gc()
        self.assertIs(auto_gc, auto_gc2)
        
    def test_enable_disable_auto_gc(self):
        """Test enable/disable auto GC."""
        disable_auto_gc()
        auto_gc = get_auto_gc()
        self.assertFalse(auto_gc._running)
        
        enable_auto_gc()
        auto_gc = get_auto_gc()
        self.assertTrue(auto_gc._running)
        
        disable_auto_gc()
        
    def test_force_gc(self):
        """Test force GC function."""
        # Should not raise an exception
        force_gc()
        
    def test_gc_stats(self):
        """Test GC stats function."""
        stats = gc_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('memory_stats', stats)
        
    def test_track_allocation_deallocation(self):
        """Test allocation/deallocation tracking."""
        track_allocation("test_object", 1024)
        track_deallocation("test_object", 512)
        
        stats = gc_stats()
        memory_stats = stats['memory_stats']
        
        self.assertIn('allocations_by_type', memory_stats)
        self.assertIn('deallocations_by_type', memory_stats)
        self.assertEqual(memory_stats['allocations_by_type']['test_object'], 1024)
        self.assertEqual(memory_stats['deallocations_by_type']['test_object'], 512)
        
    def test_register_memory_pool(self):
        """Test memory pool registration."""
        pool = MemoryPool(1024, 10)
        register_memory_pool(pool)
        
        auto_gc = get_auto_gc()
        self.assertIn(pool, auto_gc.resource_manager.memory_pools)
        
    def test_register_mmap_file(self):
        """Test memory-mapped file registration."""
        test_file = "/tmp/test_mmap.dat"
        register_mmap_file(test_file)
        
        auto_gc = get_auto_gc()
        self.assertIn(test_file, auto_gc.resource_manager.mmap_files)
        
    def test_register_cleanup_callback(self):
        """Test cleanup callback registration."""
        callback_called = []
        
        def test_callback():
            callback_called.append(True)
            
        register_cleanup_callback(test_callback)
        
        auto_gc = get_auto_gc()
        auto_gc.resource_manager.run_cleanup_callbacks()
        
        self.assertTrue(callback_called)


class TestManagedMemoryContext(unittest.TestCase):
    """Test managed memory context manager."""
    
    def test_managed_memory_context(self):
        """Test managed memory context manager."""
        with managed_memory() as auto_gc:
            self.assertIsInstance(auto_gc, AutoGarbageCollector)
            self.assertTrue(auto_gc._running)
            
        # Should have performed cleanup
        # (can't easily test if cleanup was performed, but it should run)
        
    def test_auto_gc_decorator(self):
        """Test auto GC decorator."""
        @auto_gc_decorator
        def test_function():
            # Allocate some memory
            data = [i for i in range(1000)]
            return len(data)
            
        result = test_function()
        self.assertEqual(result, 1000)
        
        # Should have managed GC automatically
        # (can't easily test if GC was managed, but it should work)


class TestCreateManagedMmap(unittest.TestCase):
    """Test create_managed_mmap function."""
    
    def test_create_managed_mmap(self):
        """Test creating managed memory-mapped array."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            filepath = f.name
            
        try:
            # Create managed mmap
            arr = create_managed_mmap(filepath, size=1000, dtype="float32", mode="w+")
            
            # Should be registered
            auto_gc = get_auto_gc()
            self.assertIn(filepath, auto_gc.resource_manager.mmap_files)
            
            # Test basic operations
            self.assertEqual(arr.shape, (1000,))
            self.assertEqual(str(arr.dtype), 'float32')
            
            # Write some data
            arr[0:10] = range(10)
            
            # Verify data
            self.assertEqual(list(arr[0:5]), [0.0, 1.0, 2.0, 3.0, 4.0])
            
        finally:
            # Clean up
            del arr
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in auto GC system."""
    
    def test_collector_with_invalid_config(self):
        """Test collector with invalid configuration."""
        config = AutoGCConfig()
        config.cleanup_interval = -1  # Invalid interval
        
        # Should still work with invalid config
        collector = AutoGarbageCollector(config)
        collector.start()
        collector.stop()
        
    def test_cleanup_with_exceptions(self):
        """Test cleanup when callbacks raise exceptions."""
        def failing_callback():
            raise ValueError("Test error")
            
        auto_gc = get_auto_gc()
        auto_gc.resource_manager.register_cleanup_callback(failing_callback)
        
        # Should not raise exception
        auto_gc.resource_manager.run_cleanup_callbacks()
        
    def test_memory_pool_cleanup_with_invalid_pool(self):
        """Test memory pool cleanup with invalid pool."""
        class InvalidPool:
            def stats(self):
                raise ValueError("Invalid pool")
                
        auto_gc = get_auto_gc()
        auto_gc.resource_manager.register_memory_pool(InvalidPool())
        
        # Should not raise exception
        freed_blocks = auto_gc.resource_manager.cleanup_memory_pools()
        self.assertEqual(freed_blocks, 0)


class TestPerformance(unittest.TestCase):
    """Test performance characteristics."""
    
    def test_memory_tracker_performance(self):
        """Test memory tracker performance."""
        tracker = MemoryTracker()
        
        start_time = time.time()
        
        # Track many allocations
        for i in range(10000):
            tracker.track_allocation(f"obj_{i % 100}", 1024)
            
        end_time = time.time()
        
        # Should be reasonably fast
        self.assertLess(end_time - start_time, 1.0)
        
    def test_concurrent_access(self):
        """Test concurrent access to auto GC."""
        def worker():
            for i in range(100):
                track_allocation(f"thread_obj_{i}", 1024)
                force_gc()
                
        threads = [threading.Thread(target=worker) for _ in range(10)]
        
        start_time = time.time()
        
        for thread in threads:
            thread.start()
            
        for thread in threads:
            thread.join()
            
        end_time = time.time()
        
        # Should handle concurrent access reasonably well
        self.assertLess(end_time - start_time, 10.0)


if __name__ == '__main__':
    # Clean up any existing auto GC state
    disable_auto_gc()
    
    # Run tests
    unittest.main(verbosity=2)
