"""
Core parallel operations for PyFerris.
"""

from ._pyferris import (
    parallel_map as _parallel_map,
    parallel_starmap as _parallel_starmap,
    parallel_filter as _parallel_filter,
    parallel_reduce as _parallel_reduce,
)

def parallel_map(func, iterable, chunk_size=None):
    """
    Apply a function to every item of an iterable in parallel.
    
    Args:
        func: Function to apply to each item
        iterable: Iterable to process
        chunk_size: Size of chunks to process (optional)
    
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
    return _parallel_map(func, iterable, chunk_size)

def parallel_starmap(func, iterable, chunk_size=None):
    """
    Apply a function to arguments unpacked from tuples in parallel.
    
    Args:
        func: Function to apply
        iterable: Iterable of argument tuples
        chunk_size: Size of chunks to process (optional)
    
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
    return _parallel_starmap(func, iterable, chunk_size)

def parallel_filter(predicate, iterable, chunk_size=None):
    """
    Filter items from an iterable in parallel using a predicate function.
    
    Args:
        predicate: Function that returns True for items to keep
        iterable: Iterable to filter
        chunk_size: Size of chunks to process (optional)
    
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
    return _parallel_filter(predicate, iterable, chunk_size)

def parallel_reduce(func, iterable, initializer=None, chunk_size=None):
    """
    Apply a function of two arguments cumulatively to items in parallel.
    
    Args:
        func: Function of two arguments
        iterable: Iterable to reduce
        initializer: Initial value (optional)
        chunk_size: Size of chunks to process (optional)
    
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
    return _parallel_reduce(func, iterable, initializer, chunk_size)

__all__ = [
    "parallel_map",
    "parallel_starmap", 
    "parallel_filter",
    "parallel_reduce",
]