"""
Level 4 Features - Concurrent Data Structures

This module provides high-performance, thread-safe data structures for concurrent
access across multiple threads without blocking operations.
"""

from typing import Any, Dict, List, Optional, Tuple
from ._pyferris import (
    ConcurrentHashMap as _ConcurrentHashMap,
    LockFreeQueue as _LockFreeQueue,
    AtomicCounter as _AtomicCounter,
    RwLockDict as _RwLockDict,
)


class ConcurrentHashMap:
    """
    A thread-safe, lock-free hash map for high-performance concurrent access.
    
    Uses DashMap internally for optimal performance with minimal locking.
    Perfect for scenarios with high read/write concurrency.
    
    Example:
        >>> from pyferris import ConcurrentHashMap
        >>> 
        >>> # Create a concurrent hash map
        >>> cmap = ConcurrentHashMap()
        >>> 
        >>> # Thread-safe operations
        >>> cmap['key1'] = 'value1'
        >>> cmap['key2'] = 42
        >>> 
        >>> # Concurrent access from multiple threads
        >>> import threading
        >>> 
        >>> def worker(i):
        ...     cmap[f'thread_{i}'] = i * 2
        >>> 
        >>> threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        >>> for t in threads:
        ...     t.start()
        >>> for t in threads:
        ...     t.join()
        >>> 
        >>> print(f"Map size: {len(cmap)}")
        >>> print(f"Keys: {cmap.keys()}")
    """
    
    def __init__(self):
        """Initialize an empty concurrent hash map."""
        self._map = _ConcurrentHashMap()
    
    def __getitem__(self, key: str) -> Any:
        """Get a value by key."""
        return self._map.__getitem__(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set a value by key."""
        self._map.__setitem__(key, value)
    
    def __delitem__(self, key: str) -> None:
        """Delete a key-value pair."""
        self._map.__delitem__(key)
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists."""
        return self._map.__contains__(key)
    
    def __len__(self) -> int:
        """Get the number of entries."""
        return self._map.__len__()
    
    def __repr__(self) -> str:
        """String representation."""
        return self._map.__repr__()
    
    def __str__(self) -> str:
        """String representation."""
        return self._map.__str__()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value with optional default."""
        return self._map.get_or_default(key, default)
    
    def insert(self, key: str, value: Any) -> Optional[Any]:
        """Insert a key-value pair, returning the previous value if any."""
        return self._map.insert(key, value)
    
    def remove(self, key: str) -> Optional[Any]:
        """Remove a key-value pair, returning the value if found."""
        return self._map.remove(key)
    
    def contains_key(self, key: str) -> bool:
        """Check if a key exists."""
        return self._map.contains_key(key)
    
    def is_empty(self) -> bool:
        """Check if the map is empty."""
        return self._map.is_empty()
    
    def clear(self) -> None:
        """Clear all entries."""
        self._map.clear()
    
    def keys(self) -> List[str]:
        """Get all keys."""
        return self._map.keys()
    
    def values(self) -> List[Any]:
        """Get all values."""
        return self._map.values()
    
    def items(self) -> List[Tuple[str, Any]]:
        """Get all key-value pairs as tuples."""
        return self._map.items()
    
    def update(self, other: Dict[str, Any]) -> None:
        """Update with another dictionary."""
        self._map.update(other)
    
    def get_or_insert(self, key: str, value: Any) -> Any:
        """Get existing value or insert and return new value atomically."""
        return self._map.get_or_insert(key, value)
    
    def shard_count(self) -> int:
        """Get the number of internal shards (for debugging/optimization)."""
        return self._map.shard_count()


class LockFreeQueue:
    """
    A lock-free queue for high-performance concurrent operations.
    
    Uses Crossbeam's SegQueue for true lock-free operations.
    Ideal for producer-consumer scenarios with multiple threads.
    
    Example:
        >>> from pyferris import LockFreeQueue
        >>> import threading
        >>> import time
        >>> 
        >>> queue = LockFreeQueue()
        >>> 
        >>> # Producer function
        >>> def producer(start, end):
        ...     for i in range(start, end):
        ...         queue.push(f"item_{i}")
        ...         time.sleep(0.001)  # Simulate work
        >>> 
        >>> # Consumer function
        >>> def consumer(name):
        ...     items = []
        ...     for _ in range(5):
        ...         item = queue.pop()
        ...         if item is not None:
        ...             items.append(item)
        ...         time.sleep(0.001)
        ...     return items
        >>> 
        >>> # Start producers and consumers
        >>> producers = [
        ...     threading.Thread(target=producer, args=(i*10, (i+1)*10))
        ...     for i in range(3)
        ... ]
        >>> 
        >>> for p in producers:
        ...     p.start()
        >>> for p in producers:
        ...     p.join()
        >>> 
        >>> print(f"Queue length: {len(queue)}")
    """
    
    def __init__(self):
        """Initialize an empty lock-free queue."""
        self._queue = _LockFreeQueue()
    
    def push(self, item: Any) -> None:
        """Push an item to the queue."""
        self._queue.push(item)
    
    def pop(self) -> Optional[Any]:
        """Pop an item from the queue (returns None if empty)."""
        return self._queue.pop()
    
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return self._queue.is_empty()
    
    def __len__(self) -> int:
        """Get approximate length (may not be exact due to concurrent operations)."""
        return self._queue.__len__()
    
    def clear(self) -> None:
        """Clear all items from the queue."""
        self._queue.clear()
    
    def __repr__(self) -> str:
        """String representation."""
        return self._queue.__repr__()
    
    def __str__(self) -> str:
        """String representation."""
        return self._queue.__str__()


class AtomicCounter:
    """
    An atomic counter for thread-safe counting operations.
    
    Provides atomic increment, decrement, and other operations without locks.
    Perfect for counters, statistics, and coordination between threads.
    
    Example:
        >>> from pyferris import AtomicCounter
        >>> import threading
        >>> 
        >>> counter = AtomicCounter(0)
        >>> 
        >>> def increment_worker():
        ...     for _ in range(1000):
        ...         counter.increment()
        >>> 
        >>> # Run multiple threads incrementing the counter
        >>> threads = [threading.Thread(target=increment_worker) for _ in range(10)]
        >>> for t in threads:
        ...     t.start()
        >>> for t in threads:
        ...     t.join()
        >>> 
        >>> print(f"Final count: {counter.get()}")  # Should be 10000
        >>> 
        >>> # Other atomic operations
        >>> counter.add(500)
        >>> counter.sub(200)
        >>> print(f"After add/sub: {counter.get()}")
    """
    
    def __init__(self, initial_value: int = 0):
        """Initialize the atomic counter with an initial value."""
        self._counter = _AtomicCounter(initial_value)
    
    def get(self) -> int:
        """Get the current value."""
        return self._counter.get()
    
    def set(self, value: int) -> None:
        """Set the value."""
        self._counter.set(value)
    
    def increment(self) -> int:
        """Increment by 1 and return the new value."""
        return self._counter.increment()
    
    def decrement(self) -> int:
        """Decrement by 1 and return the new value."""
        return self._counter.decrement()
    
    def add(self, value: int) -> int:
        """Add a value and return the new value."""
        return self._counter.add(value)
    
    def sub(self, value: int) -> int:
        """Subtract a value and return the new value."""
        return self._counter.sub(value)
    
    def compare_and_swap(self, expected: int, new: int) -> int:
        """
        Compare and swap - atomically sets new value if current equals expected.
        Returns the actual value before the operation.
        """
        return self._counter.compare_and_swap(expected, new)
    
    def reset(self) -> None:
        """Reset to zero."""
        self._counter.reset()
    
    def __int__(self) -> int:
        """Convert to int."""
        return self._counter.__int__()
    
    def __add__(self, other: int) -> int:
        """Add operation."""
        return self._counter.__add__(other)
    
    def __sub__(self, other: int) -> int:
        """Subtract operation."""
        return self._counter.__sub__(other)
    
    def __repr__(self) -> str:
        """String representation."""
        return self._counter.__repr__()
    
    def __str__(self) -> str:
        """String representation."""
        return self._counter.__str__()


class RwLockDict:
    """
    A readers-writer lock dictionary for concurrent read access with exclusive write access.
    
    Allows multiple concurrent readers OR one exclusive writer at a time.
    Optimal for read-heavy workloads where writes are less frequent.
    
    Example:
        >>> from pyferris import RwLockDict
        >>> import threading
        >>> import time
        >>> 
        >>> rw_dict = RwLockDict()
        >>> 
        >>> # Initialize with some data
        >>> rw_dict['config'] = {'workers': 4, 'timeout': 30}
        >>> rw_dict['stats'] = {'requests': 0, 'errors': 0}
        >>> 
        >>> def reader_worker(worker_id):
        ...     # Multiple readers can access concurrently
        ...     for _ in range(100):
        ...         config = rw_dict.get('config', {})
        ...         stats = rw_dict.get('stats', {})
        ...         time.sleep(0.001)
        >>> 
        >>> def writer_worker():
        ...     # Writers get exclusive access
        ...     for i in range(10):
        ...         current_stats = rw_dict.get('stats', {})
        ...         current_stats['requests'] = current_stats.get('requests', 0) + 1
        ...         rw_dict['stats'] = current_stats
        ...         time.sleep(0.01)
        >>> 
        >>> # Start multiple readers and one writer
        >>> readers = [threading.Thread(target=reader_worker, args=(i,)) for i in range(5)]
        >>> writer = threading.Thread(target=writer_worker)
        >>> 
        >>> for r in readers:
        ...     r.start()
        >>> writer.start()
        >>> 
        >>> for r in readers:
        ...     r.join()
        >>> writer.join()
        >>> 
        >>> print(f"Final stats: {rw_dict['stats']}")
    """
    
    def __init__(self):
        """Initialize an empty RwLockDict."""
        self._dict = _RwLockDict()
    
    def __getitem__(self, key: str) -> Any:
        """Get a value by key."""
        return self._dict.__getitem__(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set a value by key."""
        self._dict.__setitem__(key, value)
    
    def __delitem__(self, key: str) -> None:
        """Delete a key-value pair."""
        self._dict.__delitem__(key)
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists."""
        return self._dict.__contains__(key)
    
    def __len__(self) -> int:
        """Get the number of entries."""
        return self._dict.__len__()
    
    def __repr__(self) -> str:
        """String representation."""
        return self._dict.__repr__()
    
    def __str__(self) -> str:
        """String representation."""
        return self._dict.__str__()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value with optional default (allows concurrent reads)."""
        return self._dict.get_or_default(key, default)
    
    def insert(self, key: str, value: Any) -> Optional[Any]:
        """Insert a key-value pair, returning the previous value if any (exclusive write)."""
        return self._dict.insert(key, value)
    
    def remove(self, key: str) -> Optional[Any]:
        """Remove a key-value pair, returning the value if found (exclusive write)."""
        return self._dict.remove(key)
    
    def contains_key(self, key: str) -> bool:
        """Check if a key exists (allows concurrent reads)."""
        return self._dict.contains_key(key)
    
    def is_empty(self) -> bool:
        """Check if the dictionary is empty (allows concurrent reads)."""
        return self._dict.is_empty()
    
    def clear(self) -> None:
        """Clear all entries (exclusive write)."""
        self._dict.clear()
    
    def keys(self) -> List[str]:
        """Get all keys (allows concurrent reads)."""
        return self._dict.keys()
    
    def values(self) -> List[Any]:
        """Get all values (allows concurrent reads)."""
        return self._dict.values()
    
    def items(self) -> List[Tuple[str, Any]]:
        """Get all key-value pairs as tuples (allows concurrent reads)."""
        return self._dict.items()
    
    def update(self, other: Dict[str, Any]) -> None:
        """Update with another dictionary (exclusive write)."""
        self._dict.update(other)


__all__ = [
    'ConcurrentHashMap',
    'LockFreeQueue', 
    'AtomicCounter',
    'RwLockDict'
]