"""
Level 4 Features - Performance Profiling

This module provides detailed profiling capabilities for analyzing CPU usage, 
memory consumption, and identifying performance bottlenecks in parallel operations.
"""

from typing import Any, Dict, List, Optional, Callable
import functools
from ._pyferris import (
    Profiler as _Profiler,
    auto_tune_workers as _auto_tune_workers,
)


class Profiler:
    """
    A comprehensive profiler for monitoring CPU, memory, and performance bottlenecks.
    
    Provides detailed timing information, memory usage tracking, and performance counters
    to help identify and optimize bottlenecks in parallel processing applications.
    
    Example:
        >>> from pyferris import Profiler, parallel_map
        >>> import time
        >>> 
        >>> profiler = Profiler()
        >>> profiler.start()
        >>> 
        >>> def cpu_intensive_task(x):
        ...     profiler.start_timer("computation")
        ...     # Simulate CPU work
        ...     result = sum(i * i for i in range(x * 100))
        ...     profiler.stop_timer("computation")
        ...     profiler.increment_counter("tasks_completed")
        ...     return result
        >>> 
        >>> # Profile parallel execution
        >>> data = range(1000)
        >>> results = parallel_map(cpu_intensive_task, data)
        >>> 
        >>> elapsed = profiler.stop()
        >>> report = profiler.get_report()
        >>> 
        >>> print(f"Total time: {elapsed:.2f}s")
        >>> print(f"Timings: {report['timings']}")
        >>> print(f"Counters: {report['counters']}")
    """
    
    def __init__(self):
        """Initialize a new profiler instance."""
        self._profiler = _Profiler()
        self._context_stack = []
    
    def start(self) -> None:
        """Start profiling."""
        self._profiler.start()
    
    def stop(self) -> Optional[float]:
        """
        Stop profiling and return total elapsed time.
        
        Returns:
            Total elapsed time in seconds, or None if not started.
        """
        return self._profiler.stop()
    
    def start_timer(self, name: str) -> None:
        """
        Start timing a specific operation.
        
        Args:
            name: Name of the operation to time.
        """
        self._profiler.start_timer(name)
    
    def stop_timer(self, name: str) -> float:
        """
        Stop timing a specific operation.
        
        Args:
            name: Name of the operation to stop timing.
            
        Returns:
            Elapsed time for the operation in seconds.
        """
        return self._profiler.stop_timer(name)
    
    def record_memory(self, name: str, bytes_used: int) -> None:
        """
        Record memory usage for a specific operation.
        
        Args:
            name: Name of the operation.
            bytes_used: Number of bytes used.
        """
        self._profiler.record_memory(name, bytes_used)
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """
        Increment a counter.
        
        Args:
            name: Name of the counter.
            value: Value to increment by (default: 1).
        """
        self._profiler.increment_counter(name, value)
    
    def get_timings(self) -> Dict[str, float]:
        """
        Get timing results.
        
        Returns:
            Dictionary mapping operation names to elapsed times in seconds.
        """
        return self._profiler.get_timings()
    
    def get_memory_usage(self) -> Dict[str, int]:
        """
        Get memory usage results.
        
        Returns:
            Dictionary mapping operation names to memory usage in bytes.
        """
        return self._profiler.get_memory_usage()
    
    def get_counters(self) -> Dict[str, int]:
        """
        Get counter results.
        
        Returns:
            Dictionary mapping counter names to their values.
        """
        return self._profiler.get_counters()
    
    def get_report(self) -> Dict[str, Any]:
        """
        Get comprehensive profiling report.
        
        Returns:
            Dictionary containing all profiling data including:
            - timings: Operation timing data
            - memory_usage: Memory usage data  
            - counters: Counter data
            - total_elapsed: Total profiling time
        """
        return self._profiler.get_report()
    
    def clear(self) -> None:
        """Clear all profiling data."""
        self._profiler.clear()
    
    def timer(self, name: str):
        """
        Context manager for timing operations.
        
        Args:
            name: Name of the operation to time.
            
        Example:
            >>> profiler = Profiler()
            >>> with profiler.timer("data_processing"):
            ...     # Your code here
            ...     time.sleep(0.1)
            >>> print(profiler.get_timings())
        """
        return TimerContext(self, name)
    
    def profile_function(self, name: Optional[str] = None):
        """
        Decorator for profiling function execution.
        
        Args:
            name: Optional name for the operation (defaults to function name).
            
        Example:
            >>> profiler = Profiler()
            >>> 
            >>> @profiler.profile_function("math_operation")
            >>> def expensive_calculation(n):
            ...     return sum(i * i for i in range(n))
            >>> 
            >>> result = expensive_calculation(10000)
            >>> print(profiler.get_timings())
        """
        def decorator(func):
            operation_name = name or func.__name__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                self.start_timer(operation_name)
                try:
                    result = func(*args, **kwargs)
                    self.increment_counter(f"{operation_name}_success")
                    return result
                except Exception:
                    self.increment_counter(f"{operation_name}_error")
                    raise
                finally:
                    self.stop_timer(operation_name)
            
            return wrapper
        return decorator
    
    def __repr__(self) -> str:
        """String representation."""
        return self._profiler.__repr__()
    
    def __str__(self) -> str:
        """String representation."""
        return self._profiler.__str__()


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, profiler: Profiler, name: str):
        self.profiler = profiler
        self.name = name
    
    def __enter__(self):
        self.profiler.start_timer(self.name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        del exc_type, exc_val, exc_tb  # Unused parameters
        self.profiler.stop_timer(self.name)


def auto_tune_workers(
    task_function: Callable,
    sample_data: List[Any],
    min_workers: Optional[int] = None,
    max_workers: Optional[int] = None,
    test_duration: float = 1.0,
) -> Dict[str, Any]:
    """
    Automatically determine the optimal number of workers for a given task.
    
    Benchmarks the task function with different worker counts to find the
    configuration that provides the best throughput.
    
    Args:
        task_function: The function to benchmark.
        sample_data: Sample data to use for benchmarking.
        min_workers: Minimum number of workers to test (default: 1).
        max_workers: Maximum number of workers to test (default: CPU count).
        test_duration: How long to test each configuration in seconds (default: 1.0).
    
    Returns:
        Dictionary containing:
        - optimal_workers: The optimal number of workers
        - best_throughput: The best throughput achieved (items/second)
        - tested_workers: Number of different worker counts tested
    
    Example:
        >>> from pyferris import auto_tune_workers
        >>> 
        >>> def cpu_task(x):
        ...     return sum(i * i for i in range(x * 100))
        >>> 
        >>> sample_data = list(range(50, 150))
        >>> result = auto_tune_workers(cpu_task, sample_data, test_duration=2.0)
        >>> 
        >>> print(f"Optimal workers: {result['optimal_workers']}")
        >>> print(f"Best throughput: {result['best_throughput']:.2f} items/sec")
        >>> 
        >>> # Use the result to configure your parallel operations
        >>> from pyferris import set_worker_count
        >>> set_worker_count(result['optimal_workers'])
    """
    return _auto_tune_workers(task_function, sample_data, min_workers, max_workers, test_duration)


def profile_parallel_operation(
    operation_func: Callable,
    *args,
    profiler: Optional[Profiler] = None,
    operation_name: str = "parallel_operation",
    **kwargs
) -> tuple:
    """
    Profile a parallel operation and return both results and profiling data.
    
    Args:
        operation_func: The parallel operation function to profile.
        *args: Arguments to pass to the operation function.
        profiler: Optional profiler instance (creates new one if not provided).
        operation_name: Name for the profiling operation.
        **kwargs: Keyword arguments to pass to the operation function.
    
    Returns:
        Tuple of (results, profiling_report).
    
    Example:
        >>> from pyferris import profile_parallel_operation, parallel_map
        >>> 
        >>> def square(x):
        ...     return x * x
        >>> 
        >>> data = range(10000)
        >>> results, report = profile_parallel_operation(
        ...     parallel_map, square, data, operation_name="square_operation"
        ... )
        >>> 
        >>> print(f"Results count: {len(list(results))}")
        >>> print(f"Profiling report: {report}")
    """
    if profiler is None:
        profiler = Profiler()
    
    profiler.start()
    profiler.start_timer(operation_name)
    
    try:
        results = operation_func(*args, **kwargs)
        profiler.increment_counter(f"{operation_name}_success")
    except Exception:
        profiler.increment_counter(f"{operation_name}_error")
        raise
    finally:
        profiler.stop_timer(operation_name)
        profiler.stop()
    
    return results, profiler.get_report()


__all__ = [
    'Profiler',
    'auto_tune_workers',
    'profile_parallel_operation'
]