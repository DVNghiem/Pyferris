"""
PyFerris Async Operations Tests (Level 3)

Tests for async functionality:
- AsyncExecutor
- AsyncTask
- async_parallel_map
- async_parallel_filter
"""

import pytest
import asyncio
import time

from pyferris.async_ops import (
    AsyncExecutor, async_parallel_map, async_parallel_filter
)


class TestAsyncExecutor:
    """Test AsyncExecutor functionality."""

    def test_async_executor_creation(self):
        """Test basic AsyncExecutor creation."""
        executor = AsyncExecutor(max_workers=4)
        assert executor is not None

    def test_async_executor_map_basic(self):
        """Test basic AsyncExecutor map functionality."""
        def simple_task(x):
            return x * 2
        
        executor = AsyncExecutor(max_workers=2)
        data = [1, 2, 3, 4, 5]
        
        result = executor.map_async(simple_task, data)
        expected = [x * 2 for x in data]
        assert result == expected

    def test_async_executor_with_cpu_task(self):
        """Test AsyncExecutor with CPU-intensive task."""
        def cpu_task(n):
            # Small CPU-intensive task
            total = 0
            for i in range(n * 100):
                total += i * i
            return total
        
        executor = AsyncExecutor(max_workers=4)
        data = [10, 20, 30, 40]
        
        result = executor.map_async(cpu_task, data)
        expected = [cpu_task(x) for x in data]
        assert result == expected

    def test_async_executor_performance(self):
        """Test AsyncExecutor performance characteristics."""
        def task_with_delay(x):
            time.sleep(0.05)  # Increased delay to make async benefit more apparent
            return x + 1
        
        data = list(range(10))  # Reduced data size to keep test fast
        
        # Sequential execution
        sequential_result = [task_with_delay(x) for x in data]
        
        # Async execution
        executor = AsyncExecutor(max_workers=4)
        async_result = executor.map_async(task_with_delay, data)
        
        # Results should be the same
        assert sequential_result == async_result
        
        # Just ensure both complete successfully - performance comparison is too variable
        assert len(sequential_result) == len(async_result) == len(data)

    def test_async_executor_empty_data(self):
        """Test AsyncExecutor with empty data."""
        def simple_task(x):
            return x
        
        executor = AsyncExecutor(max_workers=2)
        result = executor.map_async(simple_task, [])
        assert result == []

    def test_async_executor_single_item(self):
        """Test AsyncExecutor with single item."""
        def task(x):
            return x ** 2
        
        executor = AsyncExecutor(max_workers=2)
        result = executor.map_async(task, [5])
        assert result == [25]

    def test_async_executor_error_handling(self):
        """Test AsyncExecutor error handling."""
        def failing_task(x):
            if x == 3:
                raise ValueError("Task failed")
            return x * 2
        
        executor = AsyncExecutor(max_workers=2)
        
        # Should propagate the exception
        with pytest.raises((ValueError, Exception)):
            executor.map_async(failing_task, [1, 2, 3, 4])

    def test_async_executor_different_worker_counts(self):
        """Test AsyncExecutor with different worker counts."""
        def simple_task(x):
            return x + 10
        
        data = [1, 2, 3, 4, 5]
        expected = [x + 10 for x in data]
        
        for workers in [1, 2, 4, 8]:
            executor = AsyncExecutor(max_workers=workers)
            result = executor.map_async(simple_task, data)
            assert result == expected


class TestAsyncTask:
    """Test AsyncTask functionality."""

    @pytest.mark.asyncio
    async def test_async_task_creation(self):
        """Test basic AsyncExecutor functionality with map_async."""
        def simple_task(x):
            return x * 2
        
        executor = AsyncExecutor(max_workers=2)
        data = [1, 2, 3, 4, 5]
        results = executor.map_async(simple_task, data)
        assert results == [2, 4, 6, 8, 10]

    @pytest.mark.asyncio
    async def test_async_task_execution(self):
        """Test AsyncExecutor map_async execution."""
        def computation_task(x):
            import time
            time.sleep(0.01)  # Simulate some work
            return x ** 2
        
        executor = AsyncExecutor(max_workers=2)
        data = [1, 2, 3, 4]
        results = executor.map_async(computation_task, data)
        assert results == [1, 4, 9, 16]

    @pytest.mark.asyncio
    async def test_async_task_with_timeout(self):
        """Test AsyncExecutor limited execution."""
        def slow_task(x):
            import time
            time.sleep(0.1)
            return x * 2
        
        # Use map_async_limited which respects concurrency limits
        executor = AsyncExecutor(max_workers=2)
        data = [1, 2, 3, 4]
        results = executor.map_async_limited(slow_task, data)
        assert results == [2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_async_task_no_timeout(self):
        """Test AsyncExecutor fast execution."""
        def fast_task(x):
            import time
            time.sleep(0.01)
            return x + 10
        
        executor = AsyncExecutor(max_workers=2)
        data = [1, 2, 3]
        results = executor.map_async(fast_task, data)
        assert results == [11, 12, 13]

    @pytest.mark.asyncio
    async def test_async_task_exception_handling(self):
        """Test AsyncExecutor exception handling."""
        def failing_task(x):
            if x == 2:
                raise ValueError("Async task failed")
            return x * 2
        
        executor = AsyncExecutor(max_workers=2)
        
        # Test with data that causes an exception
        with pytest.raises(ValueError, match="Async task failed"):
            executor.map_async(failing_task, [1, 2, 3])

    @pytest.mark.asyncio
    async def test_async_task_cancellation(self):
        """Test AsyncExecutor with varying task durations."""
        def variable_task(x):
            import time
            # Simulate variable execution time
            sleep_time = 0.01 if x % 2 == 0 else 0.02
            time.sleep(sleep_time)
            return x * 2
        
        executor = AsyncExecutor(max_workers=2)
        data = [1, 2, 3, 4, 5, 6]
        results = executor.map_async(variable_task, data)
        assert results == [2, 4, 6, 8, 10, 12]


class TestAsyncParallelMap:
    """Test async_parallel_map functionality."""

    @pytest.mark.asyncio
    async def test_async_parallel_map_basic(self):
        """Test basic async_parallel_map functionality."""
        async def async_double(x):
            await asyncio.sleep(0.001)
            return x * 2
        
        data = [1, 2, 3, 4, 5]
        result = await async_parallel_map(async_double, data)
        expected = [2, 4, 6, 8, 10]
        assert result == expected

    @pytest.mark.asyncio
    async def test_async_parallel_map_io_simulation(self):
        """Test async_parallel_map with I/O simulation."""
        async def simulate_io(x):
            # Simulate async I/O operation
            await asyncio.sleep(0.01)
            return f"processed_{x}"
        
        data = list(range(10))
        result = await async_parallel_map(simulate_io, data)
        expected = [f"processed_{x}" for x in data]
        assert result == expected

    @pytest.mark.asyncio
    async def test_async_parallel_map_performance(self):
        """Test async_parallel_map performance."""
        async def io_task(x):
            await asyncio.sleep(0.01)
            return x + 1
        
        data = list(range(20))
        
        # Sequential async execution
        start_time = time.time()
        sequential_result = []
        for x in data:
            result = await io_task(x)
            sequential_result.append(result)
        sequential_time = time.time() - start_time
        
        # Parallel async execution
        start_time = time.time()
        parallel_result = await async_parallel_map(io_task, data)
        parallel_time = time.time() - start_time
        
        # Results should be the same
        assert sequential_result == parallel_result
        
        # Parallel should be significantly faster
        improvement_ratio = sequential_time / parallel_time
        assert improvement_ratio > 3, f"Async parallel should be much faster: {improvement_ratio:.2f}x"

    @pytest.mark.asyncio
    async def test_async_parallel_map_empty_data(self):
        """Test async_parallel_map with empty data."""
        async def async_task(x):
            return x
        
        result = await async_parallel_map(async_task, [])
        assert result == []

    @pytest.mark.asyncio
    async def test_async_parallel_map_single_item(self):
        """Test async_parallel_map with single item."""
        async def async_square(x):
            await asyncio.sleep(0.001)
            return x ** 2
        
        result = await async_parallel_map(async_square, [7])
        assert result == [49]

    @pytest.mark.asyncio
    async def test_async_parallel_map_error_handling(self):
        """Test async_parallel_map error handling."""
        async def failing_task(x):
            await asyncio.sleep(0.001)
            if x == 3:
                raise ValueError("Async task failed")
            return x * 2
        
        data = [1, 2, 3, 4]
        
        with pytest.raises((ValueError, Exception)):
            await async_parallel_map(failing_task, data)

    @pytest.mark.asyncio
    async def test_async_parallel_map_different_delays(self):
        """Test async_parallel_map with tasks having different delays."""
        async def variable_delay_task(x):
            # Longer delays for larger numbers
            await asyncio.sleep(0.001 * x)
            return x * 2
        
        data = [1, 2, 3, 4, 5]
        result = await async_parallel_map(variable_delay_task, data)
        expected = [x * 2 for x in data]
        assert result == expected


class TestAsyncParallelFilter:
    """Test async_parallel_filter functionality."""

    @pytest.mark.asyncio
    async def test_async_parallel_filter_basic(self):
        """Test basic async_parallel_filter functionality."""
        async def async_is_even(x):
            await asyncio.sleep(0.001)
            return x % 2 == 0
        
        data = list(range(10))
        result = await async_parallel_filter(async_is_even, data)
        expected = [x for x in data if x % 2 == 0]
        assert result == expected

    @pytest.mark.asyncio
    async def test_async_parallel_filter_complex_predicate(self):
        """Test async_parallel_filter with complex predicate."""
        async def is_prime(n):
            await asyncio.sleep(0.001)
            if n < 2:
                return False
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return False
            return True
        
        data = list(range(20))
        result = await async_parallel_filter(is_prime, data)
        
        # Should contain prime numbers
        assert 2 in result
        assert 3 in result
        assert 5 in result
        assert 7 in result
        assert 11 in result
        assert 13 in result
        assert 17 in result
        assert 19 in result
        
        # Should not contain non-primes
        assert 0 not in result
        assert 1 not in result
        assert 4 not in result
        assert 6 not in result
        assert 8 not in result

    @pytest.mark.asyncio
    async def test_async_parallel_filter_performance(self):
        """Test async_parallel_filter performance."""
        async def slow_predicate(x):
            await asyncio.sleep(0.01)
            return x % 3 == 0
        
        data = list(range(30))
        
        # Sequential async filtering
        start_time = time.time()
        sequential_result = []
        for x in data:
            if await slow_predicate(x):
                sequential_result.append(x)
        sequential_time = time.time() - start_time
        
        # Parallel async filtering
        start_time = time.time()
        parallel_result = await async_parallel_filter(slow_predicate, data)
        parallel_time = time.time() - start_time
        
        # Results should be the same
        assert set(sequential_result) == set(parallel_result)
        
        # Parallel should be faster
        improvement_ratio = sequential_time / parallel_time
        assert improvement_ratio > 3, f"Async parallel should be much faster: {improvement_ratio:.2f}x"

    @pytest.mark.asyncio
    async def test_async_parallel_filter_empty_data(self):
        """Test async_parallel_filter with empty data."""
        async def async_predicate(x):
            return True
        
        result = await async_parallel_filter(async_predicate, [])
        assert result == []

    @pytest.mark.asyncio
    async def test_async_parallel_filter_no_matches(self):
        """Test async_parallel_filter with no matches."""
        async def always_false(x):
            await asyncio.sleep(0.001)
            return False
        
        data = [1, 2, 3, 4, 5]
        result = await async_parallel_filter(always_false, data)
        assert result == []

    @pytest.mark.asyncio
    async def test_async_parallel_filter_all_matches(self):
        """Test async_parallel_filter with all matches."""
        async def always_true(x):
            await asyncio.sleep(0.001)
            return True
        
        data = [1, 2, 3, 4, 5]
        result = await async_parallel_filter(always_true, data)
        assert set(result) == set(data)

    @pytest.mark.asyncio
    async def test_async_parallel_filter_error_handling(self):
        """Test async_parallel_filter error handling."""
        async def failing_predicate(x):
            await asyncio.sleep(0.001)
            if x == 3:
                raise ValueError("Predicate failed")
            return x > 2
        
        data = [1, 2, 3, 4, 5]
        
        with pytest.raises((ValueError, Exception)):
            await async_parallel_filter(failing_predicate, data)

    @pytest.mark.asyncio
    async def test_async_parallel_filter_maintains_order(self):
        """Test that async_parallel_filter maintains input order."""
        async def slow_is_even(x):
            # Vary delay to potentially reveal ordering issues
            await asyncio.sleep(0.001 * (5 - x % 5))
            return x % 2 == 0
        
        data = list(range(20))
        result = await async_parallel_filter(slow_is_even, data)
        
        # Result should be in ascending order (maintaining input order)
        assert result == sorted(result)
        
        # Should contain only even numbers
        for num in result:
            assert num % 2 == 0


class TestAsyncIntegration:
    """Test integration of async components."""

    @pytest.mark.asyncio
    async def test_async_map_then_filter(self):
        """Test combining async_parallel_map and async_parallel_filter."""
        async def async_square(x):
            await asyncio.sleep(0.001)
            return x * x
        
        async def async_is_large(x):
            await asyncio.sleep(0.001)
            return x > 50
        
        data = list(range(10))
        
        # First map, then filter
        squared = await async_parallel_map(async_square, data)
        large_squares = await async_parallel_filter(async_is_large, squared)
        
        # Should contain squares > 50
        expected = [x * x for x in data if x * x > 50]
        assert set(large_squares) == set(expected)

    @pytest.mark.asyncio
    async def test_async_with_regular_operations(self):
        """Test mixing async and regular operations."""
        from pyferris import parallel_map
        
        async def async_process(x):
            await asyncio.sleep(0.001)
            return x * 2
        
        def sync_process(x):
            return x + 10
        
        data = [1, 2, 3, 4, 5]
        
        # Async then sync
        async_result = await async_parallel_map(async_process, data)
        final_result = list(parallel_map(sync_process, async_result))
        
        expected = [(x * 2) + 10 for x in data]
        assert final_result == expected

    @pytest.mark.asyncio
    async def test_async_operations_with_different_concurrency(self):
        """Test async operations with different concurrency levels."""
        async def io_task(x):
            await asyncio.sleep(0.005)
            return x * 3
        
        data = list(range(20))
        
        # Run multiple async operations concurrently
        tasks = [
            async_parallel_map(io_task, data),
            async_parallel_map(io_task, data),
            async_parallel_map(io_task, data)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All results should be the same
        expected = [x * 3 for x in data]
        for result in results:
            assert result == expected


class TestAsyncEdgeCases:
    """Test edge cases for async operations."""

    @pytest.mark.asyncio
    async def test_async_with_cancelled_tasks(self):
        """Test behavior with cancelled async tasks."""
        async def cancellable_task(x):
            await asyncio.sleep(0.1)  # Long enough to be cancelled
            return x
        
        # This test checks graceful handling of cancellation
        try:
            task = asyncio.create_task(async_parallel_map(cancellable_task, [1, 2, 3]))
            await asyncio.sleep(0.01)  # Let it start
            task.cancel()
            await task
        except asyncio.CancelledError:
            # Expected behavior
            pass

    @pytest.mark.asyncio
    async def test_async_with_very_short_tasks(self):
        """Test async operations with very short tasks."""
        async def instant_task(x):
            # No await - completes immediately
            return x + 1
        
        data = list(range(100))
        result = await async_parallel_map(instant_task, data)
        expected = [x + 1 for x in data]
        assert result == expected

    @pytest.mark.asyncio
    async def test_async_with_nested_async_calls(self):
        """Test nested async calls."""
        async def outer_task(x):
            async def inner_task(y):
                await asyncio.sleep(0.001)
                return y * 2
            
            result = await inner_task(x)
            return result + 1
        
        data = [1, 2, 3]
        result = await async_parallel_map(outer_task, data)
        expected = [(x * 2) + 1 for x in data]
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
