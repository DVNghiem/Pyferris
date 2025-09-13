"""
Unit tests for PyFerris Safe Threading module.
"""

from pyferris.safe_thread import (
    SafeThread, SafeThreadPool, SafeLock,
    safe_thread_decorator, safe_parallel_map, create_safe_shared_data
)


class TestSafeThread:
    """Test cases for SafeThread class."""

    def test_thread_creation(self):
        """Test basic thread creation."""
        def dummy_task():
            return 42

        thread = SafeThread(target=dummy_task, name="TestThread")
        
        assert thread.name == "TestThread"
        assert not thread.is_alive()

    def test_thread_execution(self):
        """Test basic thread execution."""
        def simple_task(x):
            return x * 2

        thread = SafeThread(target=simple_task, args=(21,))
        thread.start()
        thread.join()
        
        result = thread.get_result()
        assert result == 42

    def test_thread_with_exception(self):
        """Test thread exception handling."""
        def failing_task():
            raise ValueError("Test exception")

        thread = SafeThread(target=failing_task)
        thread.start()
        thread.join()
        
        exception = thread.get_exception()
        assert exception is not None
        assert isinstance(exception, ValueError)


class TestSafeThreadPool:
    """Test cases for SafeThreadPool class."""

    def test_pool_submit(self):
        """Test submitting tasks to the pool."""
        def multiply_task(x, y):
            return x * y

        with SafeThreadPool(max_workers=2) as pool:
            future = pool.submit(multiply_task, 6, 7)
            result = future.result()
            assert result == 42

    def test_pool_map(self):
        """Test map operation on the pool."""
        def square_task(x):
            return x * x

        data = [1, 2, 3, 4, 5]
        expected = [1, 4, 9, 16, 25]

        with SafeThreadPool(max_workers=2) as pool:
            results = pool.map(square_task, data)
            assert results == expected


class TestSafeLock:
    """Test cases for SafeLock class."""

    def test_lock_basic_operations(self):
        """Test basic lock acquire and release."""
        lock = SafeLock()
        
        assert not lock.locked()
        
        lock.acquire()
        assert lock.locked()
        
        lock.release()
        assert not lock.locked()

    def test_lock_context_manager(self):
        """Test lock as context manager."""
        lock = SafeLock()
        
        with lock:
            assert lock.locked()
        
        assert not lock.locked()

    def test_lock_thread_safety(self):
        """Test lock thread safety with multiple threads."""
        lock = SafeLock()
        shared_data = [0]
        
        def worker():
            for _ in range(100):
                with lock:
                    current = shared_data[0]
                    shared_data[0] = current + 1

        # Create multiple threads
        threads = []
        for i in range(3):
            thread = SafeThread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Check results
        assert shared_data[0] == 300  # 3 threads * 100 increments


class TestSafeParallelMap:
    """Test cases for safe_parallel_map function."""

    def test_basic_parallel_map(self):
        """Test basic parallel map functionality."""
        def square(x):
            return x * x

        data = [1, 2, 3, 4, 5]
        expected = [1, 4, 9, 16, 25]
        
        result = safe_parallel_map(square, data, max_workers=2)
        assert result == expected

    def test_parallel_map_empty_input(self):
        """Test parallel map with empty input."""
        def square(x):
            return x * x

        result = safe_parallel_map(square, [], max_workers=2)
        assert result == []


class TestSharedDataStructures:
    """Test cases for thread-safe shared data structures."""

    def test_shared_counter(self):
        """Test shared counter operations."""
        counter = create_safe_shared_data("counter", 0)
        
        counter.increment()
        assert counter.get() == 1
        
        counter.increment()
        assert counter.get() == 2
        
        counter.decrement()
        assert counter.get() == 1

    def test_shared_dict(self):
        """Test shared dictionary operations."""
        shared_dict = create_safe_shared_data("dict")
        
        shared_dict.put("key1", "value1")
        value = shared_dict.get("key1")
        assert value == "value1"
        
        # Test non-existent key
        value = shared_dict.get("nonexistent")
        assert value is None

    def test_shared_array(self):
        """Test shared array operations."""
        initial_data = [1.0, 2.0, 3.0, 4.0, 5.0]
        shared_array = create_safe_shared_data("array", initial_data)
        
        # Test that array was populated correctly
        assert shared_array.len() == len(initial_data)
        
        # Test accessing elements by converting to list
        result = shared_array.to_list()
        assert result == initial_data

    def test_shared_queue(self):
        """Test shared queue operations."""
        shared_queue = create_safe_shared_data("queue")
        
        shared_queue.push("item1")
        shared_queue.push("item2")
        
        item = shared_queue.pop()
        assert item == "item1"
        
        item = shared_queue.pop()
        assert item == "item2"


class TestSafeThreadDecorator:
    """Test cases for safe_thread_decorator."""

    def test_decorator_basic_usage(self):
        """Test basic decorator usage."""
        @safe_thread_decorator(max_workers=2)
        def multiply_by_two(x):
            return x * 2

        future = multiply_by_two(21)
        result = future.result()
        assert result == 42


def test_integration_workflow():
    """Test a simple integration workflow."""
    # Create shared data
    shared_counter = create_safe_shared_data("counter", 0)
    lock = SafeLock()

    def worker():
        for _ in range(10):
            with lock:
                current = shared_counter.get()
                shared_counter.set(current + 1)

    # Use thread pool to run workers
    with SafeThreadPool(max_workers=2) as pool:
        futures = []
        for _ in range(3):
            future = pool.submit(worker)
            futures.append(future)
        
        # Wait for all workers
        for future in futures:
            future.result()

    # Check final result
    assert shared_counter.get() == 30  # 3 workers * 10 increments each


def test_non_blocking_behavior():
    """Test that SafeThread and SafeThreadPool don't block when starting tasks."""
    import time
    
    def long_task(duration):
        time.sleep(duration)
        return f"completed after {duration}s"
    
    # Test SafeThread non-blocking behavior
    start_time = time.time()
    threads = []
    
    for i in range(3):
        thread = SafeThread(target=long_task, args=(1,))
        threads.append(thread)
        thread.start()  # This should not block
    
    # All threads should start within a short time
    start_duration = time.time() - start_time
    assert start_duration < 0.5, f"Starting threads took too long: {start_duration}s"
    
    # Wait for completion
    for thread in threads:
        result = thread.get_result(timeout=2)
        assert result == "completed after 1s"
    
    total_duration = time.time() - start_time
    assert total_duration < 1.5, f"Parallel execution took too long: {total_duration}s"
    
    # Test SafeThreadPool non-blocking behavior
    start_time = time.time()
    
    with SafeThreadPool(max_workers=3) as pool:
        futures = []
        for i in range(3):
            future = pool.submit(long_task, 1)
            futures.append(future)
        
        # Submitting should be fast
        submit_duration = time.time() - start_time
        assert submit_duration < 0.5, f"Submitting tasks took too long: {submit_duration}s"
        
        # Wait for results
        results = [future.result(timeout=2) for future in futures]
        assert all(result == "completed after 1s" for result in results)
    
    total_duration = time.time() - start_time
    assert total_duration < 1.5, f"Pool execution took too long: {total_duration}s"
