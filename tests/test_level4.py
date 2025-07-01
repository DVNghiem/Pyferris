"""
Test Level 4 Features - Expert Features

Test concurrent data structures, memory management, and performance profiling.
"""

import unittest
import tempfile
import os
import threading
import time
from pyferris import (
    # Concurrent data structures
    ConcurrentHashMap, LockFreeQueue, AtomicCounter, RwLockDict,
    # Memory management
    MemoryPool, memory_mapped_array, memory_mapped_array_2d, memory_mapped_info, create_temp_mmap,
    # Performance profiling
    Profiler, auto_tune_workers, profile_parallel_operation,
    # Core functions for testing
    parallel_map
)


class TestConcurrentDataStructures(unittest.TestCase):
    """Test concurrent data structures."""
    
    def test_concurrent_hashmap(self):
        """Test ConcurrentHashMap basic operations."""
        cmap = ConcurrentHashMap()
        
        # Test basic operations
        cmap['key1'] = 'value1'
        cmap['key2'] = 42
        
        self.assertEqual(cmap['key1'], 'value1')
        self.assertEqual(cmap['key2'], 42)
        self.assertTrue('key1' in cmap)
        self.assertFalse('key3' in cmap)
        self.assertEqual(len(cmap), 2)
        
        # Test get with default
        self.assertEqual(cmap.get('key1'), 'value1')
        self.assertEqual(cmap.get('nonexistent', 'default'), 'default')
        
        # Test removal
        self.assertEqual(cmap.remove('key1'), 'value1')
        self.assertIsNone(cmap.remove('nonexistent'))
        
        # Test clear
        cmap.clear()
        self.assertTrue(cmap.is_empty())
        self.assertEqual(len(cmap), 0)
    
    def test_concurrent_hashmap_threading(self):
        """Test ConcurrentHashMap with multiple threads."""
        cmap = ConcurrentHashMap()
        
        def worker(thread_id):
            for i in range(100):
                cmap[f'thread_{thread_id}_item_{i}'] = thread_id * 1000 + i
        
        # Start multiple threads
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify all items were inserted
        self.assertEqual(len(cmap), 500)  # 5 threads * 100 items each
        
        # Verify some specific values
        self.assertEqual(cmap['thread_0_item_0'], 0)
        self.assertEqual(cmap['thread_4_item_99'], 4099)
    
    def test_lockfree_queue(self):
        """Test LockFreeQueue basic operations."""
        queue = LockFreeQueue()
        
        # Test basic operations
        self.assertTrue(queue.is_empty())
        self.assertEqual(len(queue), 0)
        
        # Test push and pop
        queue.push('item1')
        queue.push('item2')
        queue.push(42)
        
        self.assertFalse(queue.is_empty())
        self.assertEqual(len(queue), 3)
        
        # Pop items (FIFO order)
        self.assertEqual(queue.pop(), 'item1')
        self.assertEqual(queue.pop(), 'item2')
        self.assertEqual(queue.pop(), 42)
        
        # Queue should be empty now
        self.assertTrue(queue.is_empty())
        self.assertIsNone(queue.pop())
    
    def test_lockfree_queue_threading(self):
        """Test LockFreeQueue with multiple threads."""
        queue = LockFreeQueue()
        items_produced = 0
        items_consumed = 0
        
        def producer():
            nonlocal items_produced
            for i in range(100):
                queue.push(f'item_{i}')
                items_produced += 1
                time.sleep(0.001)
        
        def consumer():
            nonlocal items_consumed
            while items_consumed < 200:  # 2 producers * 100 items
                item = queue.pop()
                if item is not None:
                    items_consumed += 1
                time.sleep(0.001)
        
        # Start producers and consumer
        producers = [threading.Thread(target=producer) for _ in range(2)]
        consumer_thread = threading.Thread(target=consumer)
        
        for p in producers:
            p.start()
        consumer_thread.start()
        
        for p in producers:
            p.join()
        consumer_thread.join()
        
        self.assertEqual(items_produced, 200)
        self.assertEqual(items_consumed, 200)
    
    def test_atomic_counter(self):
        """Test AtomicCounter basic operations."""
        counter = AtomicCounter(10)
        
        # Test basic operations
        self.assertEqual(counter.get(), 10)
        self.assertEqual(int(counter), 10)
        
        # Test increment/decrement
        self.assertEqual(counter.increment(), 11)
        self.assertEqual(counter.decrement(), 10)
        
        # Test add/sub
        self.assertEqual(counter.add(5), 15)
        self.assertEqual(counter.sub(3), 12)
        
        # Test compare and swap
        result = counter.compare_and_swap(12, 20)
        self.assertEqual(result, 12)  # Should return old value
        self.assertEqual(counter.get(), 20)
        
        # Failed compare and swap
        result = counter.compare_and_swap(12, 30)  # Expected 12 but actual is 20
        self.assertEqual(result, 20)  # Should return actual value
        self.assertEqual(counter.get(), 20)  # Value unchanged
        
        # Test reset
        counter.reset()
        self.assertEqual(counter.get(), 0)
    
    def test_atomic_counter_threading(self):
        """Test AtomicCounter with multiple threads."""
        counter = AtomicCounter(0)
        
        def increment_worker():
            for _ in range(1000):
                counter.increment()
        
        # Start multiple threads
        threads = [threading.Thread(target=increment_worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All increments should be counted
        self.assertEqual(counter.get(), 10000)
    
    def test_rwlock_dict(self):
        """Test RwLockDict basic operations."""
        rw_dict = RwLockDict()
        
        # Test basic operations
        rw_dict['key1'] = 'value1'
        rw_dict['key2'] = 42
        
        self.assertEqual(rw_dict['key1'], 'value1')
        self.assertEqual(rw_dict['key2'], 42)
        self.assertTrue(rw_dict.contains_key('key1'))
        self.assertFalse(rw_dict.contains_key('key3'))
        self.assertEqual(len(rw_dict), 2)
        
        # Test get with default
        self.assertEqual(rw_dict.get('key1'), 'value1')
        self.assertEqual(rw_dict.get('nonexistent', 'default'), 'default')
        
        # Test removal
        self.assertEqual(rw_dict.remove('key1'), 'value1')
        self.assertIsNone(rw_dict.remove('nonexistent'))
        
        # Test clear
        rw_dict.clear()
        self.assertTrue(rw_dict.is_empty())
        self.assertEqual(len(rw_dict), 0)


class TestMemoryManagement(unittest.TestCase):
    """Test memory management features."""
    
    def test_memory_pool(self):
        """Test MemoryPool basic operations."""
        pool = MemoryPool(block_size=1024, max_blocks=10)
        
        # Test properties
        self.assertEqual(pool.block_size, 1024)
        self.assertEqual(pool.max_blocks, 10)
        self.assertEqual(pool.allocated_blocks(), 0)
        self.assertEqual(pool.available_blocks(), 0)
        
        # Test allocation
        block1 = pool.allocate()
        self.assertEqual(len(block1), 1024)
        self.assertEqual(pool.allocated_blocks(), 1)
        
        block2 = pool.allocate()
        self.assertEqual(len(block2), 1024)
        self.assertEqual(pool.allocated_blocks(), 2)
        
        # Test deallocation
        pool.deallocate(block1)
        self.assertEqual(pool.available_blocks(), 1)
        
        # Test reuse
        block3 = pool.allocate()
        self.assertEqual(len(block3), 1024)
        self.assertEqual(pool.available_blocks(), 0)  # Block was reused
        
        # Test stats
        stats = pool.stats()
        self.assertEqual(stats['block_size'], 1024)
        self.assertEqual(stats['max_blocks'], 10)
        self.assertIsInstance(stats['allocated_blocks'], int)
        self.assertIsInstance(stats['available_blocks'], int)
    
    def test_memory_mapped_array(self):
        """Test memory-mapped array creation."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            filepath = f.name
        
        try:
            # Create memory-mapped array
            arr = memory_mapped_array(filepath, size=1000, dtype="float32", mode="w+")
            
            # Test basic operations
            self.assertEqual(arr.shape, (1000,))
            self.assertEqual(str(arr.dtype), 'float32')
            
            # Write some data
            arr[0:10] = range(10)
            arr[10:20] = [x * 2 for x in range(10)]
            
            # Verify data
            self.assertEqual(list(arr[0:5]), [0.0, 1.0, 2.0, 3.0, 4.0])
            self.assertEqual(list(arr[10:15]), [0.0, 2.0, 4.0, 6.0, 8.0])
            
        finally:
            # Clean up
            del arr
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_memory_mapped_array_2d(self):
        """Test 2D memory-mapped array creation."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            filepath = f.name
        
        try:
            # Create 2D memory-mapped array
            arr = memory_mapped_array_2d(filepath, shape=(100, 50), dtype="int32", mode="w+")
            
            # Test basic operations
            self.assertEqual(arr.shape, (100, 50))
            self.assertEqual(str(arr.dtype), 'int32')
            
            # Write some data
            arr[0, :] = range(50)
            arr[:, 0] = range(100)
            
            # Verify data
            self.assertEqual(list(arr[0, 0:5]), [0, 1, 2, 3, 4])
            self.assertEqual(list(arr[0:5, 0]), [0, 1, 2, 3, 4])
            
        finally:
            # Clean up
            del arr
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_memory_mapped_info(self):
        """Test memory-mapped file info."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            filepath = f.name
            f.write(b'0' * 1024)  # Write 1KB of data
        
        try:
            info = memory_mapped_info(filepath)
            
            self.assertEqual(info['filepath'], filepath)
            self.assertEqual(info['size_bytes'], 1024)
            self.assertAlmostEqual(info['size_mb'], 1024 / (1024 * 1024), places=6)
            self.assertTrue(info['is_file'])
            self.assertIsInstance(info['is_readonly'], bool)
            
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_create_temp_mmap(self):
        """Test temporary memory-mapped file creation."""
        result = create_temp_mmap(size=1000, dtype="float64", prefix="test_")
        
        try:
            arr = result['array']
            filepath = result['filepath']
            
            # Test array properties
            self.assertEqual(arr.shape, (1000,))
            self.assertEqual(str(arr.dtype), 'float64')
            
            # Test file exists
            self.assertTrue(os.path.exists(filepath))
            self.assertTrue(filepath.endswith('.tmp') or 'test_' in filepath)
            
            # Write and read data
            arr[0:10] = range(10)
            self.assertEqual(list(arr[0:5]), [0.0, 1.0, 2.0, 3.0, 4.0])
            
        finally:
            # Clean up
            del arr
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestPerformanceProfiling(unittest.TestCase):
    """Test performance profiling features."""
    
    def test_profiler_basic(self):
        """Test Profiler basic operations."""
        profiler = Profiler()
        
        # Test timing
        profiler.start_timer("test_operation")
        time.sleep(0.01)  # Small delay
        elapsed = profiler.stop_timer("test_operation")
        
        self.assertGreater(elapsed, 0)
        self.assertLess(elapsed, 1.0)  # Should be much less than 1 second
        
        # Test counters
        profiler.increment_counter("test_counter")
        profiler.increment_counter("test_counter", 5)
        
        counters = profiler.get_counters()
        self.assertEqual(counters["test_counter"], 6)
        
        # Test memory recording
        profiler.record_memory("test_memory", 1024)
        memory_usage = profiler.get_memory_usage()
        self.assertEqual(memory_usage["test_memory"], 1024)
        
        # Test report
        report = profiler.get_report()
        self.assertIn("timings", report)
        self.assertIn("counters", report)
        self.assertIn("memory_usage", report)
        
        # Test clear
        profiler.clear()
        self.assertEqual(len(profiler.get_timings()), 0)
        self.assertEqual(len(profiler.get_counters()), 0)
        self.assertEqual(len(profiler.get_memory_usage()), 0)
    
    def test_profiler_context_manager(self):
        """Test Profiler context manager."""
        profiler = Profiler()
        
        with profiler.timer("context_test"):
            time.sleep(0.01)
        
        timings = profiler.get_timings()
        self.assertIn("context_test", timings)
        self.assertGreater(timings["context_test"], 0)
    
    def test_profiler_decorator(self):
        """Test Profiler decorator."""
        profiler = Profiler()
        
        @profiler.profile_function("decorated_function")
        def test_function(x):
            time.sleep(0.001)
            return x * 2
        
        result = test_function(5)
        self.assertEqual(result, 10)
        
        timings = profiler.get_timings()
        counters = profiler.get_counters()
        
        self.assertIn("decorated_function", timings)
        self.assertIn("decorated_function_success", counters)
        self.assertEqual(counters["decorated_function_success"], 1)
    
    def test_auto_tune_workers(self):
        """Test auto_tune_workers function."""
        def simple_task(x):
            return x * x
        
        sample_data = list(range(10, 50))
        
        result = auto_tune_workers(
            simple_task, 
            sample_data, 
            min_workers=1, 
            max_workers=4, 
            test_duration=0.1
        )
        
        self.assertIn("optimal_workers", result)
        self.assertIn("best_throughput", result)
        self.assertIn("tested_workers", result)
        
        self.assertGreaterEqual(result["optimal_workers"], 1)
        self.assertLessEqual(result["optimal_workers"], 4)
        self.assertGreater(result["best_throughput"], 0)
        self.assertGreaterEqual(result["tested_workers"], 1)
    
    def test_profile_parallel_operation(self):
        """Test profile_parallel_operation function."""
        def square(x):
            return x * x
        
        data = range(100)
        
        results, report = profile_parallel_operation(
            parallel_map, 
            square, 
            data, 
            operation_name="square_operation"
        )
        
        # Check results
        results_list = list(results)
        self.assertEqual(len(results_list), 100)
        self.assertEqual(results_list[0], 0)
        self.assertEqual(results_list[5], 25)
        
        # Check profiling report
        self.assertIn("timings", report)
        self.assertIn("counters", report)
        self.assertIn("square_operation", report["timings"])
        self.assertIn("square_operation_success", report["counters"])


if __name__ == '__main__':
    unittest.main()
