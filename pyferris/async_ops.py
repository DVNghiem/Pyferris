"""
Level 3 Features - Async Support

This module provides asynchronous parallel processing capabilities,
allowing for efficient handling of I/O-bound and CPU-bound tasks.
"""

import asyncio
import inspect
from typing import Any, List, Callable
from ._pyferris import (
    AsyncExecutor as _AsyncExecutor,
    AsyncTask as _AsyncTask
)


class AsyncExecutor:
    """
    An asynchronous executor for parallel task processing.
    
    AsyncExecutor provides efficient async/await-style parallel processing
    for both I/O-bound and CPU-bound tasks with controlled concurrency.
    
    Args:
        max_workers (int): Maximum number of concurrent workers.
    
    Example:
        >>> async_executor = AsyncExecutor(max_workers=4)
        >>> 
        >>> def cpu_bound_task(x):
        ...     # Simulate CPU-intensive work
        ...     result = sum(i * i for i in range(x * 1000))
        ...     return result
        >>> 
        >>> data = [10, 20, 30, 40, 50]
        >>> results = async_executor.map_async(cpu_bound_task, data)
        >>> print(f"Processed {len(results)} tasks asynchronously")
    """
    
    def __init__(self, max_workers: int):
        """Initialize an AsyncExecutor with specified maximum workers."""
        self._executor = _AsyncExecutor(max_workers)
    
    def map_async(self, func: Callable[[Any], Any], data: List[Any]) -> List[Any]:
        """
        Apply a function to data asynchronously with full concurrency.
        
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
    
    def shutdown(self):
        """Shutdown the async executor."""
        self._executor.shutdown()


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
    Apply an async function to data in parallel.
    
    Executes the function asynchronously across all data elements,
    with proper concurrent execution for I/O-bound operations.
    
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
        # For non-async functions, just apply normally
        return [func(item) for item in data]


async def async_parallel_filter(predicate: Callable[[Any], bool], data: List[Any]) -> List[Any]:
    """
    Filter data using asynchronous parallel processing.
    
    Applies a predicate function to data in parallel and returns only
    the elements for which the predicate returns True.
    
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
        # For non-async predicates, just filter normally
        return [item for item in data if predicate(item)]


__all__ = ['AsyncExecutor', 'AsyncTask', 'async_parallel_map', 'async_parallel_filter']
