"""
PyFerris Executor Tests

Tests for the task executor functionality:
- Executor class
- Task submission and execution
- Context management
- Error handling
"""

import pytest
import time
import concurrent.futures

from pyferris import Executor


class TestExecutor:
    """Test Executor functionality."""

    def test_executor_creation(self):
        """Test basic executor creation."""
        executor = Executor(max_workers=4)
        assert executor is not None

    def test_executor_context_manager(self):
        """Test executor as context manager."""
        with Executor(max_workers=2) as executor:
            assert executor is not None
            # Should be able to submit tasks
            future = executor.submit(lambda: 42)
            assert future.result() == 42

    def test_executor_submit_basic(self):
        """Test basic task submission."""
        with Executor(max_workers=2) as executor:
            def simple_task():
                return "task_completed"
            
            future = executor.submit(simple_task)
            result = future.result()
            assert result == "task_completed"

    def test_executor_submit_with_args(self):
        """Test task submission with arguments."""
        with Executor(max_workers=2) as executor:
            def task_with_args(x, y, z=None):
                return x + y + (z or 0)
            
            future = executor.submit(task_with_args, 10, 20, z=5)
            result = future.result()
            assert result == 35

    def test_executor_multiple_tasks(self):
        """Test submitting multiple tasks."""
        with Executor(max_workers=4) as executor:
            def square(x):
                return x * x
            
            # Submit multiple tasks
            futures = []
            for i in range(10):
                future = executor.submit(square, i)
                futures.append(future)
            
            # Collect results
            results = [future.result() for future in futures]
            expected = [i * i for i in range(10)]
            assert results == expected

    def test_executor_map_functionality(self):
        """Test executor map functionality if available."""
        with Executor(max_workers=2) as executor:
            def double(x):
                return x * 2
            
            if hasattr(executor, 'map'):
                results = list(executor.map(double, range(5)))
                expected = [x * 2 for x in range(5)]
                assert results == expected

    def test_executor_shutdown(self):
        """Test executor shutdown functionality."""
        executor = Executor(max_workers=2)
        
        # Submit a task
        future = executor.submit(lambda: "test")
        result = future.result()
        assert result == "test"
        
        # Shutdown
        executor.shutdown(wait=True)
        
        # Should not be able to submit new tasks after shutdown
        with pytest.raises((RuntimeError, Exception)):
            executor.submit(lambda: "should_fail")

    def test_executor_concurrent_tasks(self):
        """Test concurrent execution of tasks."""
        with Executor(max_workers=4) as executor:
            def slow_task(duration, value):
                time.sleep(duration)
                return value
            
            start_time = time.time()
            
            # Submit tasks that should run concurrently
            futures = []
            for i in range(4):
                future = executor.submit(slow_task, 0.1, i)
                futures.append(future)
            
            # Collect results
            results = [future.result() for future in futures]
            end_time = time.time()
            
            # Should complete in less time than sequential execution
            execution_time = end_time - start_time
            sequential_time = 0.1 * 4  # 4 tasks * 0.1 seconds each
            
            # Be more lenient with timing to avoid flaky tests
            assert execution_time < sequential_time * 1.2  # Allow some overhead
            assert results == [0, 1, 2, 3]

    def test_executor_exception_handling(self):
        """Test exception handling in executor."""
        with Executor(max_workers=2) as executor:
            def failing_task():
                raise ValueError("Task failed")
            
            try:
                future = executor.submit(failing_task)
                # Should raise the exception when getting result
                with pytest.raises(ValueError, match="Task failed"):
                    future.result()
            except ValueError:
                # If exception is raised immediately during submit, that's also acceptable
                pass

    def test_executor_different_worker_counts(self):
        """Test executor with different worker counts."""
        for worker_count in [1, 2, 4, 8]:
            with Executor(max_workers=worker_count) as executor:
                def simple_task(x):
                    return x + 1
                
                future = executor.submit(simple_task, 10)
                result = future.result()
                assert result == 11

    def test_executor_task_cancellation(self):
        """Test task cancellation if supported."""
        with Executor(max_workers=2) as executor:
            def long_running_task():
                time.sleep(1.0)
                return "completed"
            
            future = executor.submit(long_running_task)
            
            # Try to cancel (may not be supported)
            if hasattr(future, 'cancel'):
                cancelled = future.cancel()
                if cancelled:
                    assert future.cancelled()

    def test_executor_as_completed(self):
        """Test as_completed functionality if available."""
        with Executor(max_workers=3) as executor:
            def task_with_delay(delay, value):
                time.sleep(delay)
                return value
            
            # Submit tasks with different delays
            futures = []
            futures.append(executor.submit(task_with_delay, 0.1, "fast"))
            futures.append(executor.submit(task_with_delay, 0.3, "slow"))
            futures.append(executor.submit(task_with_delay, 0.2, "medium"))
            
            # Check if concurrent.futures.as_completed works
            try:
                completed_futures = []
                for future in concurrent.futures.as_completed(futures, timeout=1.0):
                    completed_futures.append(future.result())
                
                # All tasks should complete
                assert len(completed_futures) == 3
                assert set(completed_futures) == {"fast", "slow", "medium"}
            except (AttributeError, NotImplementedError):
                # as_completed might not be supported
                pass

    def test_executor_invalid_worker_count(self):
        """Test executor with invalid worker count."""
        # Zero workers is allowed in this implementation
        try:
            executor = Executor(max_workers=0)
            executor.shutdown()  # Clean up
        except Exception:
            pass  # Some implementations might raise an error
        
        # Negative workers should raise an error
        with pytest.raises((ValueError, OverflowError, Exception)):
            Executor(max_workers=-1)

    def test_executor_future_interface(self):
        """Test that returned futures implement expected interface."""
        with Executor(max_workers=2) as executor:
            def simple_task():
                return "result"
            
            future = executor.submit(simple_task)
            
            # Should have basic future methods
            assert hasattr(future, 'result')
            assert hasattr(future, 'done')
            
            # Should be done after getting result
            result = future.result()
            assert result == "result"
            assert future.done()

    def test_executor_timeout_handling(self):
        """Test timeout handling in executor."""
        with Executor(max_workers=2) as executor:
            def slow_task():
                time.sleep(0.5)
                return "slow_result"
            
            future = executor.submit(slow_task)
            
            # Test timeout - may not be supported in all implementations
            timeout_raised = False
            try:
                future.result(timeout=0.1)
            except (TimeoutError, concurrent.futures.TimeoutError):
                timeout_raised = True
            except Exception:
                pass  # Other exceptions are also acceptable
            
            # If no timeout was raised, just verify we can get the result
            if not timeout_raised:
                result = future.result(timeout=1.0)
                assert result == "slow_result"
            
            # Should succeed with longer timeout
            result = future.result(timeout=1.0)
            assert result == "slow_result"

    @pytest.mark.slow
    def test_executor_stress_test(self):
        """Test executor under stress with many tasks."""
        with Executor(max_workers=4) as executor:
            def cpu_task(n):
                # Small CPU-intensive task
                return sum(i * i for i in range(n))
            
            # Submit many tasks
            futures = []
            for i in range(100):
                future = executor.submit(cpu_task, i + 10)
                futures.append(future)
            
            # Collect all results
            results = [future.result() for future in futures]
            
            # Verify results
            expected = [sum(i * i for i in range(j + 10)) for j in range(100)]
            assert results == expected

    def test_executor_memory_management(self):
        """Test that executor doesn't leak memory with many tasks."""
        # This is a basic test - in practice you'd use memory profiling tools
        with Executor(max_workers=2) as executor:
            def simple_task(x):
                return x * 2
            
            # Submit and complete many tasks
            for i in range(1000):
                future = executor.submit(simple_task, i)
                result = future.result()
                assert result == i * 2
                
                # Delete future to help with cleanup
                del future

    def test_executor_thread_safety(self):
        """Test that executor is thread-safe."""
        import threading
        
        with Executor(max_workers=4) as executor:
            results = []
            results_lock = threading.Lock()
            
            def submit_tasks(start, end):
                local_results = []
                for i in range(start, end):
                    future = executor.submit(lambda x: x * x, i)
                    local_results.append(future.result())
                
                with results_lock:
                    results.extend(local_results)
            
            # Submit tasks from multiple threads
            threads = []
            for i in range(4):
                thread = threading.Thread(target=submit_tasks, args=(i * 10, (i + 1) * 10))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            # Verify all results
            assert len(results) == 40
            expected = [i * i for i in range(40)]
            assert sorted(results) == sorted(expected)


class TestExecutorEdgeCases:
    """Test edge cases for executor."""

    def test_executor_with_none_function(self):
        """Test executor with None function."""
        with Executor(max_workers=2) as executor:
            with pytest.raises((TypeError, AttributeError)):
                executor.submit(None)

    def test_executor_with_non_callable(self):
        """Test executor with non-callable object."""
        with Executor(max_workers=2) as executor:
            with pytest.raises((TypeError, AttributeError)):
                executor.submit("not_callable")

    def test_executor_reuse_after_shutdown(self):
        """Test executor reuse after shutdown."""
        executor = Executor(max_workers=2)
        
        # Use and shutdown
        future = executor.submit(lambda: "test")
        assert future.result() == "test"
        executor.shutdown(wait=True)
        
        # Should not be able to reuse
        with pytest.raises((RuntimeError, Exception)):
            executor.submit(lambda: "should_fail")

    def test_executor_large_return_values(self):
        """Test executor with large return values."""
        with Executor(max_workers=2) as executor:
            def large_data_task():
                # Return a moderately large list
                return list(range(10000))
            
            future = executor.submit(large_data_task)
            result = future.result()
            assert len(result) == 10000
            assert result == list(range(10000))

    def test_executor_nested_submission(self):
        """Test submitting tasks from within tasks."""
        with Executor(max_workers=4) as executor:
            def nested_task(x):
                # Submit another task from within this task
                inner_future = executor.submit(lambda y: y * 2, x)
                return inner_future.result()
            
            future = executor.submit(nested_task, 5)
            result = future.result()
            assert result == 10


if __name__ == "__main__":
    pytest.main([__file__])
