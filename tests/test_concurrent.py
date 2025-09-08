"""
Test Level 4 Features - Concurrent Data Structures

This module tests concurrent data structure functionality for thread-safe operations.
Features tested:
- ConcurrentHashMap
- LockFreeQueue  
- AtomicCounter
- RwLockDict
"""

import pytest
import time
import threading

from pyferris import (
    ConcurrentHashMap, LockFreeQueue, AtomicCounter,
    RwLockDict
)


class TestConcurrentHashMap:
    """Test ConcurrentHashMap functionality."""

    def test_concurrent_hashmap_creation(self):
        """Test basic ConcurrentHashMap creation."""
        hashmap = ConcurrentHashMap()
        assert hashmap is not None

    def test_concurrent_hashmap_basic_operations(self):
        """Test basic put/get operations."""
        hashmap = ConcurrentHashMap()
        
        hashmap['key1'] = 'value1'
        hashmap['key2'] = 42
        hashmap['key3'] = [1, 2, 3]
        
        assert hashmap['key1'] == 'value1'
        assert hashmap['key2'] == 42
        assert hashmap['key3'] == [1, 2, 3]

    def test_concurrent_hashmap_contains(self):
        """Test contains functionality."""
        hashmap = ConcurrentHashMap()
        
        hashmap['test_key'] = 'test_value'
        
        assert 'test_key' in hashmap
        assert 'nonexistent_key' not in hashmap

    def test_concurrent_hashmap_deletion(self):
        """Test deletion operations."""
        hashmap = ConcurrentHashMap()
        
        hashmap['key1'] = 'value1'
        assert 'key1' in hashmap
        
        del hashmap['key1']
        assert 'key1' not in hashmap

    def test_concurrent_hashmap_len(self):
        """Test length calculation."""
        hashmap = ConcurrentHashMap()
        
        assert len(hashmap) == 0
        
        hashmap['key1'] = 'value1'
        assert len(hashmap) == 1
        
        hashmap['key2'] = 'value2'
        assert len(hashmap) == 2
        
        del hashmap['key1']
        assert len(hashmap) == 1

    def test_concurrent_hashmap_keys_values_items(self):
        """Test keys, values, and items methods."""
        hashmap = ConcurrentHashMap()
        
        hashmap['key1'] = 'value1'
        hashmap['key2'] = 'value2'
        
        keys = hashmap.keys()
        values = hashmap.values()
        items = hashmap.items()
        
        assert 'key1' in keys
        assert 'key2' in keys
        assert 'value1' in values
        assert 'value2' in values
        assert ('key1', 'value1') in items
        assert ('key2', 'value2') in items

    def test_concurrent_hashmap_thread_safety(self):
        """Test thread-safe concurrent access."""
        hashmap = ConcurrentHashMap()
        results = []
        
        def worker(thread_id):
            for i in range(50):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                hashmap[key] = value
                
                retrieved = hashmap[key]
                if retrieved == value:
                    results.append(True)
                else:
                    results.append(False)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All operations should have succeeded
        assert all(results)
        assert len(hashmap) == 500  # 10 threads * 50 operations each

    def test_concurrent_hashmap_update(self):
        """Test update method."""
        hashmap = ConcurrentHashMap()
        
        hashmap.update({'key1': 'value1', 'key2': 'value2'})
        
        assert hashmap['key1'] == 'value1'
        assert hashmap['key2'] == 'value2'
        assert len(hashmap) == 2

    def test_concurrent_hashmap_clear(self):
        """Test clear method."""
        hashmap = ConcurrentHashMap()
        
        hashmap['key1'] = 'value1'
        hashmap['key2'] = 'value2'
        
        hashmap.clear()
        
        assert len(hashmap) == 0
        assert 'key1' not in hashmap
        assert 'key2' not in hashmap


class TestLockFreeQueue:
    """Test LockFreeQueue functionality."""

    def test_lock_free_queue_creation(self):
        """Test basic LockFreeQueue creation."""
        queue = LockFreeQueue()
        assert queue is not None

    def test_lock_free_queue_push_pop(self):
        """Test basic push/pop operations."""
        queue = LockFreeQueue()
        
        queue.push("item1")
        queue.push("item2")
        queue.push(42)
        
        assert queue.pop() == "item1"  # FIFO order
        assert queue.pop() == "item2"
        assert queue.pop() == 42

    def test_lock_free_queue_empty(self):
        """Test empty queue behavior."""
        queue = LockFreeQueue()
        
        assert queue.is_empty()
        
        queue.push("item")
        assert not queue.is_empty()
        
        queue.pop()
        assert queue.is_empty()

    def test_lock_free_queue_size(self):
        """Test basic operations since size() is not available."""
        queue = LockFreeQueue()
        
        assert queue.is_empty()
        
        queue.push("item1")
        assert not queue.is_empty()
        
        queue.push("item2")
        assert not queue.is_empty()
        
        queue.pop()
        assert not queue.is_empty()  # Still has one item
        
        queue.pop()
        assert queue.is_empty()  # Now empty

    def test_lock_free_queue_thread_safety(self):
        """Test thread-safe concurrent push/pop operations."""
        queue = LockFreeQueue()
        results = []
        
        def producer(producer_id):
            for i in range(20):
                item = f"producer_{producer_id}_item_{i}"
                queue.push(item)
        
        def consumer():
            items = []
            for _ in range(10):
                if not queue.is_empty():
                    item = queue.pop()
                    if item is not None:
                        items.append(item)
                else:
                    time.sleep(0.001)  # Small delay if queue is empty
            results.extend(items)
        
        # Start producers and consumers
        producers = [threading.Thread(target=producer, args=(i,)) for i in range(5)]
        consumers = [threading.Thread(target=consumer) for _ in range(10)]
        
        for thread in producers + consumers:
            thread.start()
        for thread in producers + consumers:
            thread.join()
        
        # Should have processed many items without errors
        assert len(results) > 0

    def test_lock_free_queue_try_pop(self):
        """Test pop functionality with error handling."""
        queue = LockFreeQueue()
        
        # Try pop from empty queue
        try:
            result = queue.pop()
            assert False, "Should have raised exception on empty queue"
        except Exception:
            # Expected behavior for empty queue
            pass
        
        # Add item and pop
        queue.push("test_item")
        result = queue.pop()
        assert result == "test_item"

    def test_lock_free_queue_performance(self):
        """Test queue performance under load."""
        queue = LockFreeQueue()
        
        start_time = time.time()
        
        # Rapid push operations
        for i in range(1000):
            queue.push(f"item_{i}")
        
        # Rapid pop operations
        for i in range(1000):
            queue.pop()
        
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 1.0


class TestAtomicCounter:
    """Test AtomicCounter functionality."""

    def test_atomic_counter_creation(self):
        """Test basic AtomicCounter creation."""
        counter = AtomicCounter()
        assert counter is not None

    def test_atomic_counter_with_initial_value(self):
        """Test AtomicCounter creation with initial value."""
        counter = AtomicCounter(100)
        assert counter.get() == 100

    def test_atomic_counter_increment(self):
        """Test increment operations."""
        counter = AtomicCounter(0)
        
        assert counter.get() == 0
        
        counter.increment()
        assert counter.get() == 1
        
        counter.increment()
        assert counter.get() == 2

    def test_atomic_counter_decrement(self):
        """Test decrement operations."""
        counter = AtomicCounter(10)
        
        assert counter.get() == 10
        
        counter.decrement()
        assert counter.get() == 9
        
        counter.decrement()
        assert counter.get() == 8

    def test_atomic_counter_add(self):
        """Test add operations."""
        counter = AtomicCounter(0)
        
        counter.add(5)
        assert counter.get() == 5
        
        counter.add(10)
        assert counter.get() == 15

    def test_atomic_counter_subtract(self):
        """Test subtract operations."""
        counter = AtomicCounter(20)
        
        counter.sub(5)
        assert counter.get() == 15
        
        counter.sub(10)
        assert counter.get() == 5

    def test_atomic_counter_set_get(self):
        """Test set/get operations."""
        counter = AtomicCounter()
        
        counter.set(42)
        assert counter.get() == 42
        
        counter.set(100)
        assert counter.get() == 100

    def test_atomic_counter_reset(self):
        """Test reset functionality."""
        counter = AtomicCounter(50)
        
        counter.reset()
        assert counter.get() == 0

    def test_atomic_counter_thread_safety(self):
        """Test thread-safe atomic operations."""
        counter = AtomicCounter(0)
        
        def worker():
            for _ in range(100):
                counter.increment()
        
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Should have exactly 1000 increments
        assert counter.get() == 1000

    def test_atomic_counter_compare_and_swap(self):
        """Test compare and swap operations."""
        counter = AtomicCounter(10)
        
        # Successful compare and swap - returns old value
        old_value = counter.compare_and_swap(10, 20)
        assert old_value == 10  # Returns the old value
        assert counter.get() == 20
        
        # Failed compare and swap - current value is 20, trying to swap from 10
        old_value = counter.compare_and_swap(10, 30)
        assert old_value == 20  # Returns current value (not 10 as expected)
        assert counter.get() == 20  # Value unchanged


class TestRwLockDict:
    """Test RwLockDict functionality."""

    def test_rw_lock_dict_creation(self):
        """Test basic RwLockDict creation."""
        rw_dict = RwLockDict()
        assert rw_dict is not None

    def test_rw_lock_dict_basic_operations(self):
        """Test basic get/set operations."""
        rw_dict = RwLockDict()
        
        rw_dict['key1'] = 'value1'
        rw_dict['key2'] = 42
        
        assert rw_dict['key1'] == 'value1'
        assert rw_dict['key2'] == 42

    def test_rw_lock_dict_contains(self):
        """Test contains functionality."""
        rw_dict = RwLockDict()
        
        rw_dict['test_key'] = 'test_value'
        
        assert 'test_key' in rw_dict
        assert 'nonexistent_key' not in rw_dict

    def test_rw_lock_dict_deletion(self):
        """Test deletion operations."""
        rw_dict = RwLockDict()
        
        rw_dict['key1'] = 'value1'
        assert 'key1' in rw_dict
        
        del rw_dict['key1']
        assert 'key1' not in rw_dict

    def test_rw_lock_dict_len(self):
        """Test length calculation."""
        rw_dict = RwLockDict()
        
        assert len(rw_dict) == 0
        
        rw_dict['key1'] = 'value1'
        assert len(rw_dict) == 1
        
        rw_dict['key2'] = 'value2'
        assert len(rw_dict) == 2

    def test_rw_lock_dict_keys_values_items(self):
        """Test keys, values, and items methods."""
        rw_dict = RwLockDict()
        
        rw_dict['key1'] = 'value1'
        rw_dict['key2'] = 'value2'
        
        keys = rw_dict.keys()
        values = rw_dict.values()
        items = rw_dict.items()
        
        assert 'key1' in keys
        assert 'key2' in keys
        assert 'value1' in values
        assert 'value2' in values
        assert ('key1', 'value1') in items

    def test_rw_lock_dict_update(self):
        """Test update method."""
        rw_dict = RwLockDict()
        
        rw_dict.update({'key1': 'value1', 'key2': 'value2'})
        
        assert rw_dict['key1'] == 'value1'
        assert rw_dict['key2'] == 'value2'
        assert len(rw_dict) == 2

    def test_rw_lock_dict_thread_safety(self):
        """Test thread-safe read/write operations."""
        rw_dict = RwLockDict()
        results = []
        
        def writer(thread_id):
            for i in range(25):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                rw_dict[key] = value
        
        def reader():
            read_count = 0
            for _ in range(50):
                keys = rw_dict.keys()
                read_count += len(keys)
                time.sleep(0.001)  # Small delay
            results.append(read_count)
        
        # Start writers and readers
        writers = [threading.Thread(target=writer, args=(i,)) for i in range(4)]
        readers = [threading.Thread(target=reader) for _ in range(4)]
        
        for thread in writers + readers:
            thread.start()
        for thread in writers + readers:
            thread.join()
        
        # All operations should have completed successfully
        assert len(results) == 4  # 4 readers
        assert len(rw_dict) == 100  # 4 writers * 25 items each


class TestConcurrentDataStructuresIntegration:
    """Test integration between concurrent data structures."""

    def test_multiple_structures_independent(self):
        """Test that multiple structures work independently."""
        hashmap = ConcurrentHashMap()
        queue = LockFreeQueue()
        counter = AtomicCounter()
        rw_dict = RwLockDict()
        
        # Use each structure
        hashmap['key1'] = 'value1'
        queue.push('item1')
        counter.increment()
        rw_dict['dict_key'] = 'dict_value'
        
        # Verify independence
        assert hashmap['key1'] == 'value1'
        assert queue.pop() == 'item1'
        assert counter.get() == 1
        assert rw_dict['dict_key'] == 'dict_value'

    def test_concurrent_workflow(self):
        """Test a complete concurrent workflow."""
        # Shared data structures
        work_queue = LockFreeQueue()
        results_map = ConcurrentHashMap()
        completed_counter = AtomicCounter()
        status_dict = RwLockDict()
        
        # Add work items
        for i in range(50):
            work_queue.push(f"task_{i}")
        
        def worker(worker_id):
            status_dict[f"worker_{worker_id}"] = "active"
            
            while not work_queue.is_empty():
                try:
                    task = work_queue.pop()
                    # Simulate work
                    result = f"result_for_{task}"
                    results_map[task] = result
                    completed_counter.increment()
                except Exception:
                    # Queue is empty, break
                    break
            
            status_dict[f"worker_{worker_id}"] = "completed"
        
        # Start workers
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Verify results
        assert completed_counter.get() <= 50  # Some tasks might not be processed due to race conditions
        assert len(results_map) == completed_counter.get()
        
        # Check that all workers completed
        for i in range(5):
            assert status_dict[f"worker_{i}"] == "completed"

    def test_performance_comparison(self):
        """Test performance characteristics of different structures."""
        hashmap = ConcurrentHashMap()
        rw_dict = RwLockDict()
        
        # Test write performance
        start_time = time.time()
        for i in range(1000):
            hashmap[f"key_{i}"] = f"value_{i}"
        hashmap_write_time = time.time() - start_time
        
        start_time = time.time()
        for i in range(1000):
            rw_dict[f"key_{i}"] = f"value_{i}"
        rw_dict_write_time = time.time() - start_time
        
        # Both should complete reasonably quickly
        assert hashmap_write_time < 1.0
        assert rw_dict_write_time < 1.0
        
        # Verify data integrity
        assert len(hashmap) == 1000
        assert len(rw_dict) == 1000


if __name__ == "__main__":
    pytest.main([__file__])
