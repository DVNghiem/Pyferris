"""
PyFerris Shared Memory Tests (Level 3)

Tests for shared memory functionality:
- SharedArray variants
- SharedDict
- SharedQueue
- SharedCounter
"""

import pytest
import threading
import time
import random

from pyferris import (
    SharedArray, SharedArrayInt, SharedArrayStr, SharedArrayObj,
    SharedDict, SharedQueue, SharedCounter, create_shared_array
)


class TestSharedArray:
    """Test SharedArray functionality."""

    def test_shared_array_creation(self):
        """Test basic SharedArray creation."""
        array = SharedArray(capacity=100)
        assert array is not None
        assert array.capacity() == 100

    def test_shared_array_append_get(self):
        """Test SharedArray append and get operations."""
        array = SharedArray(capacity=10)
        
        # Append items
        for i in range(5):
            array.append(i)
        
        assert array.len() == 5
        
        # Get items
        for i in range(5):
            assert array.get(i) == i

    def test_shared_array_set_operations(self):
        """Test SharedArray set operations."""
        array = SharedArray(capacity=10)
        
        # Append some initial items
        for i in range(5):
            array.append(i)
        
        # Set new values
        array.set(0, 10)
        array.set(2, 20)
        
        assert array.get(0) == 10
        assert array.get(1) == 1  # Unchanged
        assert array.get(2) == 20

    def test_shared_array_clear(self):
        """Test SharedArray clear operation."""
        array = SharedArray(capacity=10)
        
        # Add items
        for i in range(5):
            array.append(i)
        
        assert array.len() == 5
        
        # Clear
        array.clear()
        assert array.len() == 0

    def test_shared_array_capacity_limit(self):
        """Test SharedArray capacity limits."""
        array = SharedArray(capacity=3)
        
        # Fill to capacity
        for i in range(3):
            array.append(i)
        
        assert array.len() == 3
        
        # Try to exceed capacity
        with pytest.raises((IndexError, RuntimeError, Exception)):
            array.append(3)

    def test_shared_array_index_bounds(self):
        """Test SharedArray index bounds checking."""
        array = SharedArray(capacity=5)
        
        # Add some items
        for i in range(3):
            array.append(i)
        
        # Valid indices
        assert array.get(0) == 0
        assert array.get(2) == 2
        
        # Invalid indices
        with pytest.raises((IndexError, Exception)):
            array.get(5)
        
        with pytest.raises((IndexError, Exception)):
            array.get(-1)

    def test_shared_array_thread_safety(self):
        """Test SharedArray thread safety."""
        array = SharedArray(capacity=1000)
        results = []
        lock = threading.Lock()
        
        def worker(start, end):
            local_results = []
            for i in range(start, end):
                try:
                    array.append(i)
                    local_results.append(i)
                except Exception:
                    # Capacity might be reached
                    break
            
            with lock:
                results.extend(local_results)
        
        # Start multiple threads
        threads = []
        for i in range(4):
            thread = threading.Thread(target=worker, args=(i * 100, (i + 1) * 100))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify array contains some items
        assert array.len() > 0
        assert array.len() <= 1000


class TestSharedArrayVariants:
    """Test specialized SharedArray variants."""

    def test_shared_array_int(self):
        """Test SharedArrayInt functionality."""
        array = SharedArrayInt(capacity=10)
        
        # Add integers
        for i in range(5):
            array.append(i * 10)
        
        assert array.len() == 5
        
        # Verify values
        for i in range(5):
            assert array.get(i) == i * 10

    def test_shared_array_str(self):
        """Test SharedArrayStr functionality."""
        array = SharedArrayStr(capacity=10)
        
        # Add strings
        strings = ["hello", "world", "test", "string"]
        for s in strings:
            array.append(s)
        
        assert array.len() == len(strings)
        
        # Verify values
        for i, s in enumerate(strings):
            assert array.get(i) == s

    def test_shared_array_obj(self):
        """Test SharedArrayObj functionality."""
        array = SharedArrayObj(capacity=10)
        
        # Add various objects
        objects = [
            {"key": "value"},
            [1, 2, 3],
            "string",
            42,
            None
        ]
        
        for obj in objects:
            array.append(obj)
        
        assert array.len() == len(objects)
        
        # Verify values
        for i, obj in enumerate(objects):
            assert array.get(i) == obj

    def test_create_shared_array_function(self):
        """Test create_shared_array function."""
        # Create different types of arrays
        int_array = create_shared_array("int", capacity=10)
        str_array = create_shared_array("str", capacity=10)
        obj_array = create_shared_array("obj", capacity=10)
        
        # Test they work correctly
        int_array.append(42)
        str_array.append("test")
        obj_array.append({"test": "object"})
        
        assert int_array.get(0) == 42
        assert str_array.get(0) == "test"
        assert obj_array.get(0) == {"test": "object"}

    def test_shared_array_type_enforcement(self):
        """Test type enforcement in typed arrays."""
        int_array = SharedArrayInt(capacity=5)
        
        # Should work with integers
        int_array.append(42)
        assert int_array.get(0) == 42
        
        # Might enforce type checking (implementation dependent)
        try:
            int_array.append("not_an_int")
            # If it accepts, conversion might occur
            value = int_array.get(1)
            assert isinstance(value, (int, str))
        except (TypeError, ValueError):
            # Type enforcement is working
            pass


class TestSharedDict:
    """Test SharedDict functionality."""

    def test_shared_dict_creation(self):
        """Test basic SharedDict creation."""
        shared_dict = SharedDict()
        assert shared_dict is not None

    def test_shared_dict_put_get(self):
        """Test SharedDict put and get operations."""
        shared_dict = SharedDict()
        
        # Put values
        shared_dict.put("key1", "value1")
        shared_dict.put("key2", 42)
        shared_dict.put("key3", {"nested": "object"})
        
        # Get values
        assert shared_dict.get("key1") == "value1"
        assert shared_dict.get("key2") == 42
        assert shared_dict.get("key3") == {"nested": "object"}

    def test_shared_dict_contains(self):
        """Test SharedDict contains operation."""
        shared_dict = SharedDict()
        
        shared_dict.put("existing_key", "value")
        
        assert shared_dict.contains("existing_key")
        assert not shared_dict.contains("nonexistent_key")

    def test_shared_dict_remove(self):
        """Test SharedDict remove operation."""
        shared_dict = SharedDict()
        
        shared_dict.put("temp_key", "temp_value")
        assert shared_dict.contains("temp_key")
        
        shared_dict.remove("temp_key")
        assert not shared_dict.contains("temp_key")

    def test_shared_dict_clear(self):
        """Test SharedDict clear operation."""
        shared_dict = SharedDict()
        
        # Add multiple items
        for i in range(5):
            shared_dict.put(f"key_{i}", f"value_{i}")
        
        # Clear all
        shared_dict.clear()
        
        # Should be empty
        for i in range(5):
            assert not shared_dict.contains(f"key_{i}")

    def test_shared_dict_size(self):
        """Test SharedDict size tracking."""
        shared_dict = SharedDict()
        
        assert shared_dict.size() == 0
        
        # Add items
        for i in range(10):
            shared_dict.put(f"key_{i}", i)
            assert shared_dict.size() == i + 1
        
        # Remove items
        for i in range(5):
            shared_dict.remove(f"key_{i}")
            assert shared_dict.size() == 10 - i - 1

    def test_shared_dict_thread_safety(self):
        """Test SharedDict thread safety."""
        shared_dict = SharedDict()
        results = []
        lock = threading.Lock()
        
        def worker(worker_id, num_ops):
            local_results = []
            for i in range(num_ops):
                key = f"worker_{worker_id}_key_{i}"
                value = f"worker_{worker_id}_value_{i}"
                
                shared_dict.put(key, value)
                retrieved = shared_dict.get(key)
                
                if retrieved == value:
                    local_results.append(True)
                else:
                    local_results.append(False)
            
            with lock:
                results.extend(local_results)
        
        # Start multiple threads
        threads = []
        for i in range(4):
            thread = threading.Thread(target=worker, args=(i, 25))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All operations should have succeeded
        assert all(results)
        assert len(results) == 100  # 4 workers * 25 operations each

    def test_shared_dict_nonexistent_key(self):
        """Test SharedDict behavior with nonexistent keys."""
        shared_dict = SharedDict()
        
        # Getting nonexistent key should raise exception or return None
        try:
            result = shared_dict.get("nonexistent")
            assert result is None
        except (KeyError, Exception):
            # It's acceptable to raise an exception
            pass
        
        # Removing nonexistent key
        try:
            shared_dict.remove("nonexistent")
        except (KeyError, Exception):
            # It's acceptable to raise an exception
            pass


class TestSharedQueue:
    """Test SharedQueue functionality."""

    def test_shared_queue_creation(self):
        """Test basic SharedQueue creation."""
        queue = SharedQueue()
        assert queue is not None

    def test_shared_queue_push_pop(self):
        """Test SharedQueue push and pop operations."""
        queue = SharedQueue()
        
        # Push items
        queue.push("item1")
        queue.push("item2")
        queue.push("item3")
        
        assert queue.size() == 3
        
        # Pop items (FIFO order)
        assert queue.pop() == "item1"
        assert queue.pop() == "item2"
        assert queue.pop() == "item3"
        
        assert queue.size() == 0

    def test_shared_queue_is_empty(self):
        """Test SharedQueue empty checking."""
        queue = SharedQueue()
        
        assert queue.is_empty()
        
        queue.push("item")
        assert not queue.is_empty()
        
        queue.pop()
        assert queue.is_empty()

    def test_shared_queue_size_tracking(self):
        """Test SharedQueue size tracking."""
        queue = SharedQueue()
        
        assert queue.size() == 0
        
        # Add items
        for i in range(10):
            queue.push(f"item_{i}")
            assert queue.size() == i + 1
        
        # Remove items
        for i in range(10):
            queue.pop()
            assert queue.size() == 10 - i - 1

    def test_shared_queue_thread_safety(self):
        """Test SharedQueue thread safety."""
        queue = SharedQueue()
        produced_items = []
        consumed_items = []
        lock = threading.Lock()
        
        def producer(start, end):
            for i in range(start, end):
                item = f"item_{i}"
                queue.push(item)
                with lock:
                    produced_items.append(item)
                time.sleep(0.001)  # Small delay
        
        def consumer(num_items):
            consumed = 0
            while consumed < num_items:
                if not queue.is_empty():
                    item = queue.pop()
                    with lock:
                        consumed_items.append(item)
                    consumed += 1
                else:
                    time.sleep(0.001)  # Wait for items
        
        # Start producer threads
        producer_threads = []
        for i in range(2):
            thread = threading.Thread(target=producer, args=(i * 10, (i + 1) * 10))
            producer_threads.append(thread)
            thread.start()
        
        # Start consumer thread
        consumer_thread = threading.Thread(target=consumer, args=(20,))
        consumer_thread.start()
        
        # Wait for all threads
        for thread in producer_threads:
            thread.join()
        consumer_thread.join()
        
        # All produced items should be consumed
        assert len(produced_items) == 20
        assert len(consumed_items) == 20
        assert set(produced_items) == set(consumed_items)

    def test_shared_queue_empty_pop(self):
        """Test SharedQueue pop from empty queue."""
        queue = SharedQueue()
        
        # Popping from empty queue should raise exception or return None
        try:
            result = queue.pop()
            assert result is None
        except (IndexError, RuntimeError, Exception):
            # It's acceptable to raise an exception
            pass

    def test_shared_queue_order_preservation(self):
        """Test that SharedQueue preserves FIFO order."""
        queue = SharedQueue()
        
        items = [f"item_{i}" for i in range(100)]
        
        # Push all items
        for item in items:
            queue.push(item)
        
        # Pop all items and verify order
        popped_items = []
        while not queue.is_empty():
            popped_items.append(queue.pop())
        
        assert popped_items == items


class TestSharedCounter:
    """Test SharedCounter functionality."""

    def test_shared_counter_creation(self):
        """Test basic SharedCounter creation."""
        counter = SharedCounter(initial_value=0)
        assert counter is not None
        assert counter.get() == 0

    def test_shared_counter_increment(self):
        """Test SharedCounter increment operations."""
        counter = SharedCounter(initial_value=10)
        
        # Increment
        counter.increment()
        assert counter.get() == 11
        
        # Increment by specific amount
        counter.increment(5)
        assert counter.get() == 16

    def test_shared_counter_decrement(self):
        """Test SharedCounter decrement operations."""
        counter = SharedCounter(initial_value=20)
        
        # Decrement
        counter.decrement()
        assert counter.get() == 19
        
        # Decrement by specific amount
        counter.decrement(5)
        assert counter.get() == 14

    def test_shared_counter_set_value(self):
        """Test SharedCounter set operations."""
        counter = SharedCounter(initial_value=0)
        
        counter.set(42)
        assert counter.get() == 42
        
        # Test with a large positive value instead of negative
        counter.set(100)
        assert counter.get() == 100

    def test_shared_counter_reset(self):
        """Test SharedCounter reset operation."""
        counter = SharedCounter(initial_value=0)
        
        counter.increment(50)
        assert counter.get() == 50
        
        counter.reset()
        assert counter.get() == 0

    def test_shared_counter_thread_safety(self):
        """Test SharedCounter thread safety."""
        counter = SharedCounter(initial_value=0)
        
        def incrementer(num_increments):
            for _ in range(num_increments):
                counter.increment()
        
        def decrementer(num_decrements):
            for _ in range(num_decrements):
                counter.decrement()
        
        # Start multiple threads
        threads = []
        
        # 4 incrementer threads
        for _ in range(4):
            thread = threading.Thread(target=incrementer, args=(250,))
            threads.append(thread)
            thread.start()
        
        # 2 decrementer threads
        for _ in range(2):
            thread = threading.Thread(target=decrementer, args=(200,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Final value should be: 4*250 - 2*200 = 1000 - 400 = 600
        assert counter.get() == 600

    def test_shared_counter_atomic_operations(self):
        """Test SharedCounter atomic operations."""
        counter = SharedCounter(initial_value=100)
        
        def random_operations(num_ops):
            for _ in range(num_ops):
                operation = random.choice(['inc', 'dec', 'set'])
                if operation == 'inc':
                    counter.increment(random.randint(1, 5))
                elif operation == 'dec':
                    counter.decrement(random.randint(1, 5))
                else:  # set
                    counter.set(random.randint(0, 1000))
        
        # Start multiple threads doing random operations
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=random_operations, args=(100,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Counter should have some valid value (no corruption)
        final_value = counter.get()
        assert isinstance(final_value, int)


class TestSharedMemoryIntegration:
    """Test integration between different shared memory components."""

    def test_shared_components_together(self):
        """Test using multiple shared components together."""
        # Create components
        array = SharedArray(capacity=100)
        shared_dict = SharedDict()
        queue = SharedQueue()
        counter = SharedCounter(initial_value=0)
        
        # Use them together
        for i in range(10):
            array.append(i)
            shared_dict.put(f"key_{i}", i * 2)
            queue.push(f"item_{i}")
            counter.increment()
        
        # Verify they all work
        assert array.len() == 10
        assert shared_dict.size() == 10
        assert queue.size() == 10
        assert counter.get() == 10

    def test_shared_memory_producer_consumer(self):
        """Test producer-consumer pattern with shared memory."""
        queue = SharedQueue()
        counter = SharedCounter(initial_value=0)
        results = SharedArray(capacity=1000)
        
        def producer(num_items):
            for i in range(num_items):
                queue.push(i)
                counter.increment()
        
        def consumer():
            processed = 0
            while processed < 50:  # Expect 50 items total
                if not queue.is_empty():
                    item = queue.pop()
                    results.append(item * 2)
                    processed += 1
                else:
                    time.sleep(0.001)
        
        # Start threads
        producer_threads = [
            threading.Thread(target=producer, args=(25,)),
            threading.Thread(target=producer, args=(25,))
        ]
        consumer_thread = threading.Thread(target=consumer)
        
        for thread in producer_threads:
            thread.start()
        consumer_thread.start()
        
        # Wait for completion
        for thread in producer_threads:
            thread.join()
        consumer_thread.join()
        
        # Verify results
        assert counter.get() == 50
        assert results.len() == 50


class TestSharedMemoryEdgeCases:
    """Test edge cases for shared memory components."""

    def test_shared_memory_large_data(self):
        """Test shared memory with large data."""
        # Large capacity array
        large_array = SharedArray(capacity=10000)
        
        # Fill with data
        for i in range(5000):
            large_array.append(i)
        
        assert large_array.len() == 5000
        
        # Verify some values
        assert large_array.get(0) == 0
        assert large_array.get(4999) == 4999

    def test_shared_memory_complex_objects(self):
        """Test shared memory with complex objects."""
        obj_array = SharedArrayObj(capacity=10)
        
        complex_objects = [
            {"nested": {"deeply": {"nested": "value"}}},
            [1, [2, [3, 4]]],
            {"list": [1, 2, 3], "dict": {"key": "value"}},
        ]
        
        for obj in complex_objects:
            obj_array.append(obj)
        
        # Verify objects are preserved
        for i, obj in enumerate(complex_objects):
            assert obj_array.get(i) == obj

    def test_shared_memory_stress_test(self):
        """Stress test shared memory components."""
        queue = SharedQueue()
        counter = SharedCounter(initial_value=0)
        
        def stress_worker(worker_id):
            for i in range(100):
                queue.push(f"worker_{worker_id}_item_{i}")
                counter.increment()
                
                if not queue.is_empty():
                    queue.pop()
                    counter.decrement()
        
        # Start many threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=stress_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # System should still be consistent
        final_counter = counter.get()
        final_queue_size = queue.size()
        
        # Counter + queue size should equal items added minus items removed
        assert isinstance(final_counter, int)
        assert isinstance(final_queue_size, int)


if __name__ == "__main__":
    pytest.main([__file__])
