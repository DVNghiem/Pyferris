"""
Level 4 Features - Memory Management

This module provides efficient memory management utilities including memory pools
and memory-mapped arrays for high-performance data processing.
"""

from typing import Any, Dict, Optional, Tuple, Union
from ._pyferris import (
    MemoryPool as _MemoryPool,
    memory_mapped_array as _memory_mapped_array,
    memory_mapped_array_2d as _memory_mapped_array_2d,
    memory_mapped_info as _memory_mapped_info,
    create_temp_mmap as _create_temp_mmap,
)


class MemoryPool:
    """
    A memory pool for efficient allocation and reuse of memory blocks.
    
    Reduces memory allocation overhead by reusing pre-allocated blocks.
    Ideal for scenarios with frequent allocation/deallocation of similar-sized objects.
    
    Args:
        block_size (int): Size of each memory block in bytes.
        max_blocks (Optional[int]): Maximum number of blocks to maintain (default: 1000).
    
    Example:
        >>> from pyferris import MemoryPool
        >>> import threading
        >>> 
        >>> # Create a memory pool for 1KB blocks
        >>> pool = MemoryPool(block_size=1024, max_blocks=100)
        >>> 
        >>> def worker():
        ...     # Allocate a block
        ...     block = pool.allocate()
        ...     
        ...     # Use the block for some computation
        ...     # ... process data ...
        ...     
        ...     # Return the block to the pool
        ...     pool.deallocate(block)
        >>> 
        >>> # Run multiple workers
        >>> threads = [threading.Thread(target=worker) for _ in range(10)]
        >>> for t in threads:
        ...     t.start()
        >>> for t in threads:
        ...     t.join()
        >>> 
        >>> print(f"Pool stats: {pool.stats()}")
    """
    
    def __init__(self, block_size: int, max_blocks: Optional[int] = None):
        """Initialize a memory pool with specified block size and maximum blocks."""
        self._pool = _MemoryPool(block_size, max_blocks)
    
    def allocate(self) -> bytearray:
        """
        Allocate a memory block from the pool.
        
        Returns:
            A bytearray of the specified block size.
            
        Raises:
            MemoryError: If the pool is exhausted.
        """
        block = self._pool.allocate()
        return bytearray(block)
    
    def deallocate(self, block: Union[bytearray, bytes, list]) -> None:
        """
        Return a memory block to the pool.
        
        Args:
            block: The memory block to return (must match the pool's block size).
            
        Raises:
            ValueError: If the block size doesn't match.
        """
        if isinstance(block, (bytearray, bytes)):
            block_list = list(block)
        else:
            block_list = block
        self._pool.deallocate(block_list)
    
    def available_blocks(self) -> int:
        """Get the number of available blocks in the pool."""
        return self._pool.available_blocks()
    
    def allocated_blocks(self) -> int:
        """Get the total number of allocated blocks."""
        return self._pool.allocated_blocks()
    
    @property
    def block_size(self) -> int:
        """Get the block size in bytes."""
        return self._pool.block_size()
    
    @property
    def max_blocks(self) -> int:
        """Get the maximum number of blocks."""
        return self._pool.max_blocks()
    
    def clear(self) -> None:
        """Clear all blocks from the pool."""
        self._pool.clear()
    
    def stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics.
        
        Returns:
            A dictionary containing pool statistics including:
            - block_size: Size of each block in bytes
            - max_blocks: Maximum number of blocks
            - allocated_blocks: Currently allocated blocks
            - available_blocks: Blocks available in the pool
            - total_memory_bytes: Total memory allocated
            - pool_memory_bytes: Memory held in the pool
        """
        return self._pool.stats()
    
    def __repr__(self) -> str:
        """String representation."""
        return self._pool.__repr__()
    
    def __str__(self) -> str:
        """String representation."""
        return self._pool.__str__()


def memory_mapped_array(
    filepath: str,
    size: int,
    dtype: str = "float64",
    mode: str = "r+",
) -> Any:
    """
    Create a memory-mapped array backed by a file.
    
    Memory-mapped arrays allow working with large datasets that don't fit in memory
    by mapping file contents directly to memory addresses.
    
    Args:
        filepath (str): Path to the file backing the array.
        size (int): Number of elements in the array.
        dtype (str): Data type (default: "float64").
        mode (str): Access mode - "r" (read), "w+" (write), "r+" (read/write).
    
    Returns:
        A numpy memory-mapped array.
    
    Example:
        >>> from pyferris import memory_mapped_array
        >>> import tempfile
        >>> import os
        >>> 
        >>> # Create a temporary file
        >>> with tempfile.NamedTemporaryFile(delete=False) as f:
        ...     filepath = f.name
        >>> 
        >>> # Create a memory-mapped array
        >>> arr = memory_mapped_array(filepath, size=1000000, dtype="float32", mode="w+")
        >>> 
        >>> # Use like a regular numpy array
        >>> arr[0:100] = range(100)
        >>> arr[100:200] = [x * 2 for x in range(100)]
        >>> 
        >>> # Changes are automatically written to disk
        >>> print(f"Array shape: {arr.shape}")
        >>> print(f"First 10 elements: {arr[:10]}")
        >>> 
        >>> # Clean up
        >>> del arr
        >>> os.unlink(filepath)
    """
    return _memory_mapped_array(filepath, size, dtype, mode)


def memory_mapped_array_2d(
    filepath: str,
    shape: Tuple[int, int],
    dtype: str = "float64",
    mode: str = "r+",
) -> Any:
    """
    Create a 2D memory-mapped array backed by a file.
    
    Args:
        filepath (str): Path to the file backing the array.
        shape (Tuple[int, int]): Shape of the 2D array (rows, columns).
        dtype (str): Data type (default: "float64").
        mode (str): Access mode - "r" (read), "w+" (write), "r+" (read/write).
    
    Returns:
        A numpy 2D memory-mapped array.
    
    Example:
        >>> from pyferris import memory_mapped_array_2d
        >>> import tempfile
        >>> import os
        >>> 
        >>> # Create a temporary file
        >>> with tempfile.NamedTemporaryFile(delete=False) as f:
        ...     filepath = f.name
        >>> 
        >>> # Create a 2D memory-mapped array
        >>> arr = memory_mapped_array_2d(filepath, shape=(1000, 500), dtype="int32", mode="w+")
        >>> 
        >>> # Use like a regular 2D numpy array
        >>> arr[0, :] = range(500)
        >>> arr[:, 0] = range(1000)
        >>> 
        >>> print(f"Array shape: {arr.shape}")
        >>> print(f"First row: {arr[0, :10]}")
        >>> 
        >>> # Clean up
        >>> del arr
        >>> os.unlink(filepath)
    """
    return _memory_mapped_array_2d(filepath, shape, dtype, mode)


def memory_mapped_info(filepath: str) -> Dict[str, Any]:
    """
    Get information about a memory-mapped file.
    
    Args:
        filepath (str): Path to the file.
    
    Returns:
        A dictionary containing file information including:
        - filepath: The file path
        - size_bytes: File size in bytes
        - size_mb: File size in megabytes
        - is_file: Whether it's a regular file
        - is_readonly: Whether the file is read-only
        - modified_timestamp: Last modification time (if available)
    
    Example:
        >>> from pyferris import memory_mapped_info
        >>> 
        >>> info = memory_mapped_info("/path/to/data.mmap")
        >>> print(f"File size: {info['size_mb']:.2f} MB")
        >>> print(f"Read-only: {info['is_readonly']}")
    """
    return _memory_mapped_info(filepath)


def create_temp_mmap(
    size: int,
    dtype: str = "float64",
    prefix: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a temporary memory-mapped file.
    
    Args:
        size (int): Number of elements in the array.
        dtype (str): Data type (default: "float64").
        prefix (Optional[str]): Prefix for the temporary filename.
    
    Returns:
        A dictionary containing:
        - array: The numpy memory-mapped array
        - filepath: Path to the temporary file
    
    Example:
        >>> from pyferris import create_temp_mmap
        >>> import os
        >>> 
        >>> # Create a temporary memory-mapped array
        >>> result = create_temp_mmap(size=100000, dtype="float32", prefix="data_")
        >>> arr = result['array']
        >>> filepath = result['filepath']
        >>> 
        >>> # Use the array
        >>> arr[:1000] = range(1000)
        >>> 
        >>> print(f"Temp file: {filepath}")
        >>> print(f"Array shape: {arr.shape}")
        >>> 
        >>> # Clean up when done
        >>> del arr
        >>> os.unlink(filepath)
    """
    return _create_temp_mmap(size, dtype, prefix)


__all__ = [
    'MemoryPool',
    'memory_mapped_array',
    'memory_mapped_array_2d', 
    'memory_mapped_info',
    'create_temp_mmap'
]