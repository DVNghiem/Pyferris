"""
Core parallel operations for PyFerris with performance optimizations.
"""

import gc
from typing import Callable, Iterable, Any, Optional

from ._pyferris import (
    parallel_map as _parallel_map,
    parallel_starmap as _parallel_starmap,
    parallel_filter as _parallel_filter,
    parallel_reduce as _parallel_reduce,
)

# Performance optimization: Pre-calculate optimal chunk sizes for common patterns
_CHUNK_SIZE_CACHE = {}

def _calculate_optimal_chunk_size(iterable_size: int, operation_type: str = 'default') -> int:
    """Calculate optimal chunk size based on dataset size and operation type."""
    cache_key = (iterable_size, operation_type)
    if cache_key in _CHUNK_SIZE_CACHE:
        return _CHUNK_SIZE_CACHE[cache_key]
    
    import multiprocessing
    cpu_count = multiprocessing.cpu_count()
    
    if iterable_size < 1000:
        chunk_size = max(1, iterable_size // cpu_count)
    elif iterable_size < 10000:
        chunk_size = max(100, iterable_size // (cpu_count * 2))
    else:
        chunk_size = max(500, iterable_size // (cpu_count * 4))
    
    # Cache the result for future use
    if len(_CHUNK_SIZE_CACHE) < 100:  # Prevent memory leak
        _CHUNK_SIZE_CACHE[cache_key] = chunk_size
    
    return chunk_size

def parallel_map(func: Callable, iterable: Iterable, chunk_size: Optional[int] = None) -> list:
    """
    Apply a function to every item of an iterable in parallel with optimized performance.
    
    Args:
        func: Function to apply to each item
        iterable: Iterable to process
        chunk_size: Size of chunks to process (auto-calculated if None)
    
    Returns:
        List of results
    
    Example:
        >>> from pyferris import parallel_map
        >>> def square(x):
        ...     return x * x
        >>> results = parallel_map(square, range(10))
        >>> list(results)
        [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    """
    # Convert to list once if needed for size calculation
    if not hasattr(iterable, '__len__'):
        iterable = list(iterable)
    
    if chunk_size is None and hasattr(iterable, '__len__'):
        chunk_size = _calculate_optimal_chunk_size(len(iterable), 'map')
    
    try:
        result = _parallel_map(func, iterable, chunk_size)
        return result
    except Exception as e:
        # Enhanced error handling
        if "memory" in str(e).lower():
            gc.collect()  # Force garbage collection on memory errors
            # Retry with smaller chunk size
            if chunk_size and chunk_size > 10:
                return parallel_map(func, iterable, chunk_size // 2)
        raise

def parallel_starmap(func: Callable, iterable: Iterable, chunk_size: Optional[int] = None) -> list:
    """
    Apply a function to arguments unpacked from tuples in parallel with optimized performance.
    
    Args:
        func: Function to apply
        iterable: Iterable of argument tuples
        chunk_size: Size of chunks to process (auto-calculated if None)
    
    Returns:
        List of results
    
    Example:
        >>> from pyferris import parallel_starmap
        >>> def add(x, y):
        ...     return x + y
        >>> args = [(1, 2), (3, 4), (5, 6)]
        >>> results = parallel_starmap(add, args)
        >>> list(results)
        [3, 7, 11]
    """
    # Convert to list once if needed for size calculation
    if not hasattr(iterable, '__len__'):
        iterable = list(iterable)
    
    if chunk_size is None and hasattr(iterable, '__len__'):
        chunk_size = _calculate_optimal_chunk_size(len(iterable), 'starmap')
    
    try:
        result = _parallel_starmap(func, iterable, chunk_size)
        return result
    except Exception as e:
        # Enhanced error handling
        if "memory" in str(e).lower():
            gc.collect()  # Force garbage collection on memory errors
            # Retry with smaller chunk size
            if chunk_size and chunk_size > 10:
                return parallel_starmap(func, iterable, chunk_size // 2)
        raise

def parallel_filter(predicate: Callable, iterable: Iterable, chunk_size: Optional[int] = None) -> list:
    """
    Filter items from an iterable in parallel using a predicate function with optimized performance.
    
    Args:
        predicate: Function that returns True for items to keep
        iterable: Iterable to filter
        chunk_size: Size of chunks to process (auto-calculated if None)
    
    Returns:
        List of filtered items
    
    Example:
        >>> from pyferris import parallel_filter
        >>> def is_even(x):
        ...     return x % 2 == 0
        >>> results = parallel_filter(is_even, range(10))
        >>> list(results)
        [0, 2, 4, 6, 8]
    """
    # Convert to list once if needed for size calculation
    if not hasattr(iterable, '__len__'):
        iterable = list(iterable)
    
    if chunk_size is None and hasattr(iterable, '__len__'):
        chunk_size = _calculate_optimal_chunk_size(len(iterable), 'filter')
    
    try:
        result = _parallel_filter(predicate, iterable, chunk_size)
        return result
    except Exception as e:
        # Enhanced error handling
        if "memory" in str(e).lower():
            gc.collect()  # Force garbage collection on memory errors
            # Retry with smaller chunk size
            if chunk_size and chunk_size > 10:
                return parallel_filter(predicate, iterable, chunk_size // 2)
        raise

def parallel_reduce(func: Callable, iterable: Iterable, initializer: Any = None, chunk_size: Optional[int] = None) -> Any:
    """
    Apply a function of two arguments cumulatively to items in parallel with optimized performance.
    
    Args:
        func: Function of two arguments
        iterable: Iterable to reduce
        initializer: Initial value (optional)
        chunk_size: Size of chunks to process (auto-calculated if None)
    
    Returns:
        Reduced result
    
    Example:
        >>> from pyferris import parallel_reduce
        >>> def add(x, y):
        ...     return x + y
        >>> result = parallel_reduce(add, range(10))
        >>> result
        45
    """
    # Convert to list once if needed for size calculation
    if not hasattr(iterable, '__len__'):
        iterable = list(iterable)
    
    if chunk_size is None and hasattr(iterable, '__len__'):
        chunk_size = _calculate_optimal_chunk_size(len(iterable), 'reduce')
    
    try:
        result = _parallel_reduce(func, iterable, initializer, chunk_size)
        return result
    except Exception as e:
        # Enhanced error handling
        if "memory" in str(e).lower():
            gc.collect()  # Force garbage collection on memory errors
            # Retry with smaller chunk size
            if chunk_size and chunk_size > 10:
                return parallel_reduce(func, iterable, initializer, chunk_size // 2)
        raise

__all__ = [
    "parallel_map",
    "parallel_starmap", 
    "parallel_filter",
    "parallel_reduce",
]