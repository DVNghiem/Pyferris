"""
Level 3 Features - Async Support

This module provides asynchronous parallel processing capabilities,
allowing for efficient handling of I/O-bound and CPU-bound tasks.
"""

from typing import Any, List, Callable
from ._pyferris import (
    AsyncExecutor as _AsyncExecutor,
    AsyncTask as _AsyncTask, 
    async_parallel_map as _async_parallel_map,
    async_parallel_filter as _async_parallel_filter
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
            A list of results in the same order as input data.
        
        Example:
            >>> executor = AsyncExecutor(max_workers=4)
            >>> results = executor.map_async(lambda x: x ** 2, [1, 2, 3, 4, 5])
            >>> print(results)  # [1, 4, 9, 16, 25]
        """
        return self._executor.map_async(func, data)
    
    def map_async_limited(self, func: Callable[[Any], Any], data: List[Any]) -> List[Any]:
        """
        Apply a function to data with limited concurrency.
        
        Args:
            func: A function to apply to each element.
            data: A list of input data.
        
        Returns:
            A list of results in the same order as input data.
        
        Example:
            >>> executor = AsyncExecutor(max_workers=8)
            >>> # Limit to 3 concurrent executions even though we have 8 workers
            >>> results = executor.map_async_limited(
            ...     lambda x: expensive_operation(x), 
            ...     large_dataset, 
            ... )
        
        Note:
            This is useful when you want to limit resource usage or
            respect rate limits on external services.
        """
        return self._executor.map_async_limited(func, data)
    
    def submit_task(self, func: Callable[[], Any]) -> 'AsyncTask':
        """
        Submit a single task for asynchronous execution.
        
        Args:
            func: A callable function with no arguments.
        
        Returns:
            An AsyncTask object that can be used to retrieve the result.
        
        Example:
            >>> executor = AsyncExecutor(max_workers=2)
            >>> task = executor.submit_task(lambda: expensive_computation())
            >>> # Do other work...
            >>> result = task.get_result()
        """
        rust_task = self._executor.submit_task(func)
        return AsyncTask._from_rust(rust_task)


class AsyncTask:
    """
    Represents an asynchronous task with result retrieval capabilities.
    
    AsyncTask provides a handle to a task that is executing asynchronously,
    allowing you to check its status and retrieve the result when ready.
    
    Note:
        AsyncTask objects are typically created by AsyncExecutor.submit_task()
        rather than instantiated directly.
    """
    
    def __init__(self):
        """Initialize an AsyncTask (typically not called directly)."""
        self._task = _AsyncTask()
    
    @classmethod
    def _from_rust(cls, rust_task):
        """Create an AsyncTask from a Rust AsyncTask object."""
        instance = cls.__new__(cls)
        instance._task = rust_task
        return instance
    
    def get_result(self) -> Any:
        """
        Get the result of the async task.
        
        Returns:
            The result of the task execution.
        
        Note:
            This method will block until the task completes if it hasn't finished yet.
        """
        return self._task.get_result()
    
    def is_ready(self) -> bool:
        """
        Check if the task has completed.
        
        Returns:
            True if the task is complete, False if still running.
        """
        return self._task.is_ready()


def async_parallel_map(func: Callable[[Any], Any], data: List[Any]) -> List[Any]:
    """
    Apply a function to data using asynchronous parallel processing.
    
    Convenience function for async mapping without creating an AsyncExecutor.
    
    Args:
        func: A function to apply to each element.
        data: A list of input data.
    
    Returns:
        A list of results in the same order as input data.
    
    Example:
        >>> def slow_operation(x):
        ...     time.sleep(0.1)  # Simulate I/O or slow computation
        ...     return x * 2
        >>> 
        >>> data = list(range(20))
        >>> results = async_parallel_map(slow_operation, data)
        >>> print(results)  # [0, 2, 4, 6, 8, ..., 38]
    """
    return _async_parallel_map(func, data)


def async_parallel_filter(predicate: Callable[[Any], bool], data: List[Any]) -> List[Any]:
    """
    Filter data using asynchronous parallel processing.
    
    Applies a predicate function to data in parallel and returns only
    the elements for which the predicate returns True.
    
    Args:
        predicate: A function that returns True/False for each element.
        data: A list of input data to filter.
    
    Returns:
        A list containing only elements that satisfy the predicate.
    
    Example:
        >>> def is_prime_slow(n):
        ...     # Simulate expensive primality test
        ...     time.sleep(0.01)
        ...     if n < 2:
        ...         return False
        ...     for i in range(2, int(n**0.5) + 1):
        ...         if n % i == 0:
        ...             return False
        ...     return True
        >>> 
        >>> numbers = list(range(2, 100))
        >>> primes = async_parallel_filter(is_prime_slow, numbers)
        >>> print(f"Found {len(primes)} prime numbers")
    """
    return _async_parallel_filter(predicate, data)

__all__ = ['AsyncExecutor', 'AsyncTask', 'async_parallel_map', 'async_parallel_filter']
