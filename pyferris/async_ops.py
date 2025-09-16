"""
This module provides asynchronous parallel processing capabilities,
allowing for efficient handling of I/O-bound and CPU-bound tasks.
Optimized for use with asyncio.loop.run_in_executor for better performance than ThreadPoolExecutor.
"""

import asyncio
import inspect
from typing import Any, List, Callable
from concurrent.futures import Executor
from ._pyferris import (
    AsyncExecutor as _AsyncExecutor,
    AsyncTask as _AsyncTask
)


class AsyncExecutor(Executor):
    """
    An asynchronous executor for parallel task processing, optimized for asyncio.
    
    AsyncExecutor provides efficient async/await-style parallel processing
    for both I/O-bound and CPU-bound tasks with controlled concurrency.
    Implements the Executor interface for use with loop.run_in_executor.
    
    Args:
        max_workers (int): Maximum number of concurrent workers.
    
    Example:
        >>> async def main():
        ...     executor = AsyncExecutor(max_workers=4)
        ...     loop = asyncio.get_event_loop()
        ...     
        ...     def cpu_bound_task(x):
        ...         # Simulate CPU-intensive work
        ...         result = sum(i * i for i in range(x * 1000))
        ...         return result
        ...     
        ...     # Use with loop.run_in_executor for async execution
        ...     result = await loop.run_in_executor(executor, cpu_bound_task, 100)
        ...     print(f"Result: {result}")
        >>> 
        >>> asyncio.run(main())
    """
    
    def __init__(self, max_workers: int):
        """Initialize an AsyncExecutor with specified maximum workers."""
        self._executor = _AsyncExecutor(max_workers)
        self._shutdown = False
    
    def submit(self, fn, *args, **kwargs):
        """
        Submit a callable to be executed with the given arguments.
        
        This method is required by the Executor interface and enables
        use with asyncio.loop.run_in_executor. Uses the optimized Rust backend
        with tokio runtime for true async execution.
        
        Args:
            fn: A callable object.
            *args: Arguments to pass to fn.
            **kwargs: Keyword arguments to pass to fn.
        
        Returns:
            A Future object representing the execution of the callable.
        
        Example:
            >>> import asyncio
            >>> async def main():
            ...     executor = AsyncExecutor(max_workers=2)
            ...     loop = asyncio.get_event_loop()
            ...     
            ...     def slow_function(x):
            ...         time.sleep(0.1)
            ...         return x * 2
            ...     
            ...     result = await loop.run_in_executor(executor, slow_function, 5)
            ...     print(f"Result: {result}")
        """
        if self._shutdown:
            raise RuntimeError('Executor has been shutdown')
        
        # OPTIMIZED: Use the high-performance submit_task_optimized method
        from concurrent.futures import Future
        import threading
        
        future = Future()
        
        def execute_optimized():
            """Execute using the optimized Rust submit_task_optimized method."""
            try:
                # Create a wrapper function that includes the arguments
                def task_wrapper():
                    return fn(*args, **kwargs)
                
                # Try the optimized method first, fallback to regular submit_task
                try:
                    result = self._executor.submit_task_optimized(task_wrapper, None)
                except AttributeError:
                    # Fallback for compatibility
                    result = self._executor.submit_task(task_wrapper, None)
                    
                if not future.cancelled():
                    future.set_result(result)
            except Exception as e:
                if not future.cancelled():
                    future.set_exception(e)
        
        # Execute asynchronously with optimized Rust backend
        thread = threading.Thread(target=execute_optimized)
        thread.start()
        
        return future

    def submit_batch(self, tasks):
        """
        Submit multiple tasks as a batch for maximum throughput.
        
        This method provides superior performance when submitting many tasks
        by reducing overhead through batch processing in the Rust backend.
        
        Args:
            tasks: List of (function, args) tuples where args is a tuple of positional arguments
            
        Returns:
            List of results in the same order as input tasks
            
        Example:
            >>> executor = AsyncExecutor(max_workers=4)
            >>> 
            >>> def square(x):
            ...     return x * x
            >>> 
            >>> def cube(x):
            ...     return x * x * x
            >>> 
            >>> tasks = [(square, (2,)), (cube, (3,)), (square, (4,))]
            >>> results = executor.submit_batch(tasks)
            >>> print(results)  # [4, 27, 16]
        """
        if self._shutdown:
            raise RuntimeError('Executor has been shutdown')
            
        try:
            # Convert tasks to format expected by Rust backend
            batch_tasks = []
            for fn, args in tasks:
                def task_wrapper():
                    return fn(*args) if args else fn()
                batch_tasks.append((task_wrapper, None))
            
            # Use optimized batch submission in Rust
            return self._executor.submit_batch(batch_tasks)
        except AttributeError:
            # Fallback to individual submissions if batch method not available
            return [self.submit(fn, *args if args else ()) for fn, args in tasks]

    def shutdown(self, wait=True):
        """
        Shutdown the executor.
        
        Args:
            wait: If True, shutdown will not return until all running tasks complete.
        """
        self._shutdown = True
        self._executor.shutdown()

    def get_stats(self):
        """
        Get runtime statistics for performance monitoring.
        
        Returns:
            Dictionary containing executor statistics and optimization features.
        """
        try:
            return self._executor.get_stats()
        except AttributeError:
            # Fallback stats if method not available in Rust backend
            return {
                'max_workers': getattr(self._executor, 'max_workers', 'unknown'),
                'optimization_features': ['python_wrapper'],
                'runtime_type': 'fallback'
            }

    def health_check(self):
        """
        Check if the executor is healthy and responsive.
        
        Returns:
            Boolean indicating executor health status.
        """
        try:
            return self._executor.health_check()
        except AttributeError:
            # Fallback health check
            return not self._shutdown

    def map_async(self, func: Callable[[Any], Any], data: List[Any]) -> List[Any]:
        """
        Apply a function to data asynchronously with full concurrency.
        
        This method provides better performance than ThreadPoolExecutor by using
        Rust's tokio runtime for true async execution with minimal overhead.
        
        Args:
            func: A function to apply to each element.
            data: A list of input data.
        
        Returns:
            A list containing the results of applying func to each element.
        
        Example:
            >>> def expensive_computation(x):
            ...     # Simulate heavy computation
            ...     time.sleep(0.1)
            ...     return x ** 2
            >>> 
            >>> executor = AsyncExecutor(max_workers=4)
            >>> data = list(range(10))
            >>> results = executor.map_async(expensive_computation, data)
            >>> print(f"Computed squares: {results}")
        """
        if self._shutdown:
            raise RuntimeError('Executor has been shutdown')
        return self._executor.map_async(func, data)
    
    def map_async_limited(self, func: Callable[[Any], Any], data: List[Any]) -> List[Any]:
        """
        Apply a function to data asynchronously with concurrency limits.
        
        Args:
            func: A function to apply to each element.
            data: A list of input data.
        
        Returns:
            A list containing the results of applying func to each element.
        
        Example:
            >>> def limited_task(x):
            ...     # This will respect the max_workers limit
            ...     time.sleep(0.1)
            ...     return x ** 2
            >>> 
            >>> executor = AsyncExecutor(max_workers=2)
            >>> data = list(range(10))
            >>> results = executor.map_async_limited(limited_task, data)
            >>> print(f"Computed squares: {results}")
        """
        return self._executor.map_async_limited(func, data)
    
    def submit_async(self, func: Callable[..., Any], *args) -> 'AsyncTask':
        """
        Submit a single async task for execution.
        
        Args:
            func: The function to execute.
            *args: Arguments to pass to the function.
        
        Returns:
            An AsyncTask object representing the submitted task.
        
        Example:
            >>> executor = AsyncExecutor(max_workers=2)
            >>> task = executor.submit_async(lambda x: x * 2, 5)
            >>> print(f"Task result: {task.result()}")
        """
        return AsyncTask(self._executor.submit_async(func(*args)))
    
    @property
    def max_workers(self) -> int:
        """Get the maximum number of workers."""
        return self._executor.max_workers


class AsyncTask:
    """
    Represents an asynchronous task with result tracking.
    
    AsyncTask provides a Future-like interface for tracking the completion
    and result of asynchronous operations.
    
    Example:
        >>> task = AsyncTask()
        >>> # Task will be executed by AsyncExecutor
        >>> if task.done():
        ...     result = task.result()
        ...     print(f"Task completed with result: {result}")
    """
    
    def __init__(self, rust_task=None):
        """Initialize an AsyncTask."""
        self._task = rust_task or _AsyncTask()
    
    def done(self) -> bool:
        """
        Check if the task has completed.
        
        Returns:
            True if the task is finished, False otherwise.
        """
        return self._task.done()
    
    def result(self) -> Any:
        """
        Get the result of the task (blocking if not done).
        
        Returns:
            The result of the task execution.
        
        Raises:
            RuntimeError: If the task hasn't completed yet.
        """
        return self._task.result()


async def async_parallel_map(func: Callable[[Any], Any], data: List[Any]) -> List[Any]:
    """
    Apply an async function to data in parallel using optimized AsyncExecutor.
    
    Executes the function asynchronously across all data elements,
    with better performance than ThreadPoolExecutor by leveraging
    Rust's tokio runtime and proper GIL management.
    
    Args:
        func: An async function to apply to each element.
        data: A list of input data to process.
    
    Returns:
        A list containing the results of applying func to each element.
    
    Example:
        >>> async def slow_operation(x):
        ...     # Simulate async I/O operation
        ...     await asyncio.sleep(0.01)
        ...     return x * 2
        >>> 
        >>> data = list(range(20))
        >>> results = await async_parallel_map(slow_operation, data)
        >>> print(results)  # [0, 2, 4, 6, 8, ..., 38]
    """
    if not data:
        return []
    
    if inspect.iscoroutinefunction(func):
        # Create tasks for all data elements
        tasks = [func(item) for item in data]
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        return list(results)
    else:
        # For non-async functions, use our optimized AsyncExecutor
        executor = AsyncExecutor(max_workers=min(len(data), 8))
        try:
            loop = asyncio.get_event_loop()
            
            # Use run_in_executor with our optimized executor
            tasks = [
                loop.run_in_executor(executor, func, item)
                for item in data
            ]
            results = await asyncio.gather(*tasks)
            return list(results)
        finally:
            executor.shutdown()


async def async_parallel_filter(predicate: Callable[[Any], bool], data: List[Any]) -> List[Any]:
    """
    Filter data using asynchronous parallel processing with optimized executor.
    
    Applies a predicate function to data in parallel and returns only
    the elements for which the predicate returns True. Uses the optimized
    AsyncExecutor for better performance than standard ThreadPoolExecutor.
    
    Args:
        predicate: An async function that returns True/False for each element.
        data: A list of input data to filter.
    
    Returns:
        A list containing only elements that satisfy the predicate.
    
    Example:
        >>> async def is_prime_slow(n):
        ...     # Simulate expensive async primality test
        ...     await asyncio.sleep(0.01)
        ...     if n < 2:
        ...         return False
        ...     for i in range(2, int(n**0.5) + 1):
        ...         if n % i == 0:
        ...             return False
        ...     return True
        >>> 
        >>> numbers = list(range(2, 100))
        >>> primes = await async_parallel_filter(is_prime_slow, numbers)
        >>> print(f"Found {len(primes)} prime numbers")
    """
    if not data:
        return []
    
    if inspect.iscoroutinefunction(predicate):
        # Create tasks for all data elements
        tasks = [predicate(item) for item in data]
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Filter based on results
        return [item for item, result in zip(data, results) if result]
    else:
        # For non-async predicates, use our optimized AsyncExecutor
        executor = AsyncExecutor(max_workers=min(len(data), 8))
        try:
            loop = asyncio.get_event_loop()
            
            # Use run_in_executor with our optimized executor
            tasks = [
                loop.run_in_executor(executor, predicate, item)
                for item in data
            ]
            results = await asyncio.gather(*tasks)
            
            # Filter based on results
            return [item for item, result in zip(data, results) if result]
        finally:
            executor.shutdown()


async def run_in_executor_optimized(func: Callable, *args, max_workers: int = None) -> Any:
    """
    Run a function in an optimized AsyncExecutor.
    
    This is a convenience function that provides better performance than
    using the default ThreadPoolExecutor with loop.run_in_executor.
    
    Args:
        func: The function to execute.
        *args: Arguments to pass to the function.
        max_workers: Maximum number of workers (defaults to optimal value).
    
    Returns:
        The result of the function execution.
    
    Example:
        >>> def cpu_intensive_task(n):
        ...     return sum(i * i for i in range(n))
        >>> 
        >>> result = await run_in_executor_optimized(cpu_intensive_task, 10000)
        >>> print(f"Result: {result}")
    """
    executor = AsyncExecutor(max_workers=max_workers or 4)
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, func, *args)
    finally:
        executor.shutdown()


__all__ = [
    'AsyncExecutor', 
    'AsyncTask', 
    'async_parallel_map', 
    'async_parallel_filter',
    'run_in_executor_optimized'
]
