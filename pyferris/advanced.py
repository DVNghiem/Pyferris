"""
Advanced parallel operations for PyFerris Level 2.

This module provides intermediate-level parallel processing capabilities
including advanced operations, batch processing, and result collection.

Note on Performance:
    These parallel operations are optimized for specific use cases:
    - Large datasets (>10,000 items) where parallel processing overhead is justified
    - CPU-intensive key functions or comparisons
    - I/O-bound operations within processing functions
    
    For small datasets, sequential operations may be faster due to parallel overhead.
    The parallel operations excel when used with complex key functions or when
    processing large amounts of data.
"""

from ._pyferris import (
    parallel_sort as _parallel_sort,
    parallel_group_by as _parallel_group_by,
    parallel_unique as _parallel_unique,
    parallel_partition as _parallel_partition,
    parallel_chunks as _parallel_chunks,
    BatchProcessor as _BatchProcessor,
)

import time


def parallel_sort(iterable, key=None, reverse=False):
    """
    Sort an iterable in parallel.
    
    Args:
        iterable: Input data to sort
        key: Optional function to compute sort key for each element
        reverse: Sort in descending order if True
        
    Returns:
        list: Sorted list
        
    Example:
        >>> numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        >>> parallel_sort(numbers)
        [1, 1, 2, 3, 4, 5, 5, 6, 9]
        
        >>> words = ['apple', 'pie', 'banana', 'cherry']
        >>> parallel_sort(words, key=len)
        ['pie', 'apple', 'banana', 'cherry']
    """
    return _parallel_sort(iterable, key, reverse)


def parallel_group_by(iterable, key_func, chunk_size=None):
    """
    Group elements by a key function in parallel.
    
    Args:
        iterable: Input data to group
        key_func: Function to compute grouping key for each element
        chunk_size: Optional chunk size for parallel processing
        
    Returns:
        dict: Dictionary mapping keys to lists of grouped elements
        
    Example:
        >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> groups = parallel_group_by(data, lambda x: x % 3)
        >>> groups
        {0: [3, 6, 9], 1: [1, 4, 7, 10], 2: [2, 5, 8]}
    """
    return _parallel_group_by(iterable, key_func, chunk_size)


def parallel_unique(iterable, key=None):
    """
    Get unique elements from an iterable in parallel.
    
    Args:
        iterable: Input data
        key: Optional function to compute uniqueness key for each element
        
    Returns:
        list: List of unique elements (order preserved)
        
    Example:
        >>> data = [1, 2, 2, 3, 3, 3, 4, 4, 5]
        >>> parallel_unique(data)
        [1, 2, 3, 4, 5]
        
        >>> words = ['apple', 'APPLE', 'banana', 'BANANA']
        >>> parallel_unique(words, key=str.lower)
        ['apple', 'banana']
    """
    return _parallel_unique(iterable, key)


def parallel_partition(predicate, iterable, chunk_size=None):
    """
    Partition elements based on a predicate function in parallel.
    
    Args:
        predicate: Function that returns True/False for each element
        iterable: Input data to partition
        chunk_size: Optional chunk size for parallel processing
        
    Returns:
        tuple: (true_elements, false_elements)
        
    Example:
        >>> numbers = range(10)
        >>> evens, odds = parallel_partition(lambda x: x % 2 == 0, numbers)
        >>> evens
        [0, 2, 4, 6, 8]
        >>> odds
        [1, 3, 5, 7, 9]
    """
    return _parallel_partition(predicate, iterable, chunk_size)


def parallel_chunks(iterable, chunk_size, processor_func):
    """
    Process data in parallel chunks.
    
    Args:
        iterable: Input data to process
        chunk_size: Size of each chunk
        processor_func: Function to process each chunk (receives chunk_index, chunk_data)
        
    Returns:
        list: List of chunk processing results
        
    Example:
        >>> data = range(100)
        >>> def sum_chunk(chunk_idx, chunk_data):
        ...     return sum(chunk_data)
        >>> results = parallel_chunks(data, 10, sum_chunk)
        >>> len(results)
        10
    """
    return _parallel_chunks(iterable, chunk_size, processor_func)


class BatchProcessor:
    """
    Batch processor for handling large datasets efficiently.
    
    This class provides methods to process large datasets in configurable
    batch sizes with parallel execution.
    """
    
    def __init__(self, batch_size=1000, max_workers=0):
        """
        Initialize BatchProcessor.
        
        Args:
            batch_size: Size of each processing batch
            max_workers: Maximum number of worker threads (0 = auto)
        """
        self._processor = _BatchProcessor(batch_size, max_workers)
    
    def process_batches(self, data, processor_func):
        """
        Process data in batches with a custom function.
        
        Args:
            data: Input data to process
            processor_func: Function to process each batch (receives batch_index, batch_data)
            
        Returns:
            list: List of batch processing results
            
        Example:
            >>> bp = BatchProcessor(batch_size=100)
            >>> data = range(1000)
            >>> def process_batch(batch_idx, batch_data):
            ...     return {"batch": batch_idx, "sum": sum(batch_data)}
            >>> results = bp.process_batches(data, process_batch)
            >>> len(results)
            10
        """
        return self._processor.process_batches(data, processor_func)
    
    @property
    def batch_size(self):
        """Get the batch size."""
        return self._processor.batch_size
    
    @property
    def max_workers(self):
        """Get the maximum number of workers."""
        return self._processor.max_workers


class ProgressTracker:
    """
    Simple progress tracker for monitoring task completion.
    
    This provides basic progress tracking functionality. For advanced
    progress bars, consider using tqdm directly.
    """
    
    def __init__(self, total=None, desc="Processing"):
        """
        Initialize progress tracker.
        
        Args:
            total: Total number of items to process
            desc: Description for the progress display
        """
        self.total = total
        self.desc = desc
        self.completed = 0
        self.start_time = time.time()
        self._last_update = 0
    
    def update(self, n=1):
        """Update progress by n items."""
        self.completed += n
        current_time = time.time()
        
        # Update display every 0.1 seconds to avoid spam
        if current_time - self._last_update > 0.1:
            self._display_progress()
            self._last_update = current_time
    
    def close(self):
        """Close the progress tracker and display final stats."""
        self._display_progress()
        elapsed = time.time() - self.start_time
        rate = self.completed / elapsed if elapsed > 0 else 0
        print(f"\n{self.desc} complete: {self.completed} items in {elapsed:.2f}s ({rate:.1f} items/s)")
    
    def _display_progress(self):
        """Display current progress."""
        if self.total:
            percentage = (self.completed / self.total) * 100
            bar_length = 30
            filled_length = int(bar_length * self.completed / self.total)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f"\r{self.desc}: |{bar}| {self.completed}/{self.total} ({percentage:.1f}%)", end='', flush=True)
        else:
            elapsed = time.time() - self.start_time
            rate = self.completed / elapsed if elapsed > 0 else 0
            print(f"\r{self.desc}: {self.completed} items ({rate:.1f} items/s)", end='', flush=True)


# Result collection modes
class ResultCollector:
    """
    Utility class for collecting results in different modes.
    """
    
    @staticmethod
    def ordered(results):
        """Return results in original order."""
        return list(results)
    
    @staticmethod
    def unordered(results):
        """Return results in any order (potentially faster)."""
        # For now, just return as-is since our implementations maintain order
        # In a real implementation, this could use different collection strategies
        return list(results)
    
    @staticmethod
    def as_completed(futures, timeout=None):
        """
        Return results as they complete (for use with concurrent.futures).
        
        This is a placeholder implementation. In practice, you'd want to
        integrate with concurrent.futures or similar.
        """
        # This is a simple implementation - in practice you'd want
        # proper integration with concurrent.futures
        for future in futures:
            yield future


__all__ = [
    "parallel_sort",
    "parallel_group_by", 
    "parallel_unique",
    "parallel_partition",
    "parallel_chunks",
    "BatchProcessor",
    "ProgressTracker",
    "ResultCollector",
]
