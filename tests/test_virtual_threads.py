"""
Tests for Virtual Thread functionality in PyFerris
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from pyferris.virtual_thread import (
    VirtualThreadPool, AsyncVirtualThreadPool,
    run_in_virtual_thread, virtual_map, virtual_thread_benchmark,
    create_virtual_thread_executor
)


class TestVirtualThreads:
    """Test Virtual Thread functionality."""

    def test_basic_virtual_thread_execution(self):
        """Test basic virtual thread execution."""
        def simple_task(x):
            return x * 2
        
        result = run_in_virtual_thread(simple_task, 5)
        assert result == 10

    def test_virtual_thread_with_kwargs(self):
        """Test virtual thread execution with keyword arguments."""
        def task_with_kwargs(x, multiplier=2):
            return x * multiplier
        
        result = run_in_virtual_thread(task_with_kwargs, 5, multiplier=3)
        assert result == 15

    def test_virtual_thread_pool_context_manager(self):
        """Test virtual thread pool as context manager."""
        def simple_task(x):
            time.sleep(0.01)  # Small delay to test concurrency
            return x * 2
        
        with VirtualThreadPool(max_platform_threads=2) as pool:
            futures = [pool.submit(simple_task, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        expected = [i * 2 for i in range(10)]
        assert results == expected

    def test_virtual_thread_pool_map(self):
        """Test virtual thread pool map functionality."""
        def square(x):
            return x * x
        
        with VirtualThreadPool() as pool:
            results = pool.map(square, range(10))
        
        expected = [i * i for i in range(10)]
        assert results == expected

    def test_virtual_thread_pool_starmap(self):
        """Test virtual thread pool starmap functionality."""
        def add(a, b):
            return a + b
        
        args_list = [(1, 2), (3, 4), (5, 6)]
        
        with VirtualThreadPool() as pool:
            results = pool.starmap(add, args_list)
        
        expected = [3, 7, 11]
        assert results == expected

    def test_virtual_thread_priorities(self):
        """Test virtual thread priority handling."""
        def timed_task(delay, value):
            time.sleep(delay)
            return value
        
        with VirtualThreadPool(max_platform_threads=1) as pool:
            # Submit tasks with different priorities
            high_priority = pool.submit(timed_task, 0.1, "high", priority=50)
            low_priority = pool.submit(timed_task, 0.1, "low", priority=200)
            
            results = [high_priority.result(), low_priority.result()]
        
        # Both should complete successfully regardless of priority
        assert "high" in results
        assert "low" in results

    def test_blocking_tasks(self):
        """Test handling of blocking tasks."""
        def blocking_task(duration):
            time.sleep(duration)
            return "completed"
        
        start_time = time.time()
        
        with VirtualThreadPool(max_platform_threads=2) as pool:
            futures = [
                pool.submit(blocking_task, 0.1, is_blocking=True)
                for _ in range(4)
            ]
            results = [future.result() for future in futures]
        
        elapsed = time.time() - start_time
        
        # Should complete in less time than sequential execution
        assert all(r == "completed" for r in results)
        assert elapsed < 0.4  # Should be less than 4 * 0.1 seconds

    def test_virtual_thread_stats(self):
        """Test virtual thread statistics."""
        def simple_task(x):
            return x
        
        with VirtualThreadPool() as pool:
            # Submit some tasks
            futures = [pool.submit(simple_task, i) for i in range(5)]
            
            # Get stats before completion
            stats = pool.get_stats()
            assert stats['is_running'] is True
            assert stats['total_threads_created'] >= 5
            
            # Wait for completion
            _ = [f.result() for f in futures]
            
            # Get final stats
            final_stats = pool.get_stats()
            assert final_stats['completed_threads'] >= 5

    def test_virtual_map_convenience_function(self):
        """Test virtual_map convenience function."""
        def double(x):
            return x * 2
        
        results = virtual_map(double, range(5))
        expected = [i * 2 for i in range(5)]
        assert results == expected

    def test_virtual_thread_executor_direct(self):
        """Test direct VirtualThreadExecutor usage."""
        executor = create_virtual_thread_executor(None, 2)
        executor.start()
        
        def simple_task(x):
            return x + 1
        
        # Submit a task
        thread_id = executor.submit_virtual_task(simple_task, (5,))
        result = executor.join(thread_id)
        
        assert result == 6
        
        executor.shutdown()

    def test_concurrent_virtual_threads(self):
        """Test high concurrency with virtual threads."""
        def cpu_task(n):
            # Simple computation task
            total = 0
            for i in range(n):
                total += i
            return total
        
        start_time = time.time()
        
        with VirtualThreadPool(max_platform_threads=4) as pool:
            futures = [pool.submit(cpu_task, 1000) for _ in range(100)]
            results = [f.result() for f in futures]
        
        elapsed = time.time() - start_time
        
        # All tasks should complete successfully
        assert len(results) == 100
        assert all(isinstance(r, int) for r in results)
        
        # Should complete reasonably quickly
        assert elapsed < 5.0

    def test_virtual_thread_future_interface(self):
        """Test VirtualThreadFuture interface."""
        def slow_task():
            time.sleep(0.1)
            return "done"
        
        with VirtualThreadPool() as pool:
            future = pool.submit(slow_task)
            
            # Test done() method
            assert not future.done()
            
            # Test result() method
            result = future.result()
            assert result == "done"
            assert future.done()
            
            # Test cancelled methods
            assert not future.cancelled()
            assert not future.cancel()

    def test_exception_handling(self):
        """Test exception handling in virtual threads."""
        def failing_task():
            raise ValueError("Test exception")
        
        with VirtualThreadPool() as pool:
            future = pool.submit(failing_task)
            
            with pytest.raises(ValueError, match="Test exception"):
                future.result()

    @pytest.mark.asyncio
    async def test_async_virtual_thread_pool(self):
        """Test async virtual thread pool."""
        def simple_task(x):
            return x * 2
        
        async with AsyncVirtualThreadPool() as pool:
            result = await pool.submit(simple_task, 5)
            assert result == 10
            
            # Test map
            results = await pool.map(simple_task, range(5))
            expected = [i * 2 for i in range(5)]
            assert results == expected

    def test_virtual_thread_benchmark(self):
        """Test virtual thread benchmarking utility."""
        def compute_task(n):
            return sum(range(n))
        
        args_list = [(100,), (200,), (300,)]
        
        benchmark_results = virtual_thread_benchmark(
            compute_task,
            args_list,
            traditional_threads=True,
            max_platform_threads=2
        )
        
        assert 'virtual_threads' in benchmark_results
        assert 'traditional_threads' in benchmark_results
        assert 'speedup' in benchmark_results
        
        # Verify results are correct
        vt_results = benchmark_results['virtual_threads']['results']
        tt_results = benchmark_results['traditional_threads']['results']
        
        assert vt_results == tt_results  # Should produce same results
        assert len(vt_results) == 3

    def test_memory_efficiency(self):
        """Test memory efficiency of virtual threads."""
        def minimal_task(x):
            return x
        
        # Create many virtual threads to test memory usage
        with VirtualThreadPool(max_virtual_threads=10000, max_platform_threads=2) as pool:
            futures = [pool.submit(minimal_task, i) for i in range(1000)]
            results = [f.result() for f in futures]
        
        # All tasks should complete successfully
        assert len(results) == 1000
        assert results == list(range(1000))

    def test_virtual_thread_vs_regular_threads_performance(self):
        """Compare virtual threads vs regular threads for I/O-bound tasks."""
        def io_simulation(duration):
            time.sleep(duration)
            return threading.current_thread().ident
        
        num_tasks = 20
        task_duration = 0.05
        
        # Test virtual threads
        start_time = time.time()
        with VirtualThreadPool(max_platform_threads=4) as pool:
            vt_futures = [pool.submit(io_simulation, task_duration, is_blocking=True) 
                         for _ in range(num_tasks)]
            vt_results = [f.result() for f in vt_futures]
        vt_time = time.time() - start_time
        
        # Test regular threads
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            tt_futures = [executor.submit(io_simulation, task_duration) 
                         for _ in range(num_tasks)]
            tt_results = [f.result() for f in tt_futures]
        tt_time = time.time() - start_time
        
        # Virtual threads should be competitive or better
        assert len(vt_results) == num_tasks
        assert len(tt_results) == num_tasks
        
        # Both should complete in reasonable time (much less than sequential)
        sequential_time = num_tasks * task_duration
        assert vt_time < sequential_time * 0.3
        assert tt_time < sequential_time * 0.3

    def test_error_conditions(self):
        """Test error handling and edge cases."""
        # Test invalid thread ID
        executor = create_virtual_thread_executor()
        executor.start()
        
        with pytest.raises(Exception):  # Should raise an error for invalid thread ID
            executor.join(99999)
        
        executor.shutdown()
        
        # Test shutdown behavior
        with VirtualThreadPool() as pool:
            def simple_task():
                return "test"
            
            future = pool.submit(simple_task)
            result = future.result()
            assert result == "test"
        
        # Pool should be shutdown after context exit
        stats = pool.get_stats()
        assert not stats['is_running']

    def test_large_scale_virtual_threads(self):
        """Test creating and managing a large number of virtual threads."""
        def quick_task(x):
            return x % 1000
        
        num_threads = 5000  # Large number of virtual threads
        
        start_time = time.time()
        with VirtualThreadPool(max_virtual_threads=10000, max_platform_threads=4) as pool:
            futures = [pool.submit(quick_task, i) for i in range(num_threads)]
            results = [f.result() for f in futures]
        elapsed = time.time() - start_time
        
        # All tasks should complete
        assert len(results) == num_threads
        assert all(isinstance(r, int) for r in results)
        
        # Should complete in reasonable time
        assert elapsed < 10.0  # Should not take more than 10 seconds
        
        # Verify correctness
        expected = [i % 1000 for i in range(num_threads)]
        assert results == expected
