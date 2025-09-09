"""
This module provides thread-safe shared memory data structures for efficient
zero-copy data sharing between threads and processes.
"""

from typing import Any, List, Optional
from ._pyferris import (
    SharedArray as _SharedArray, 
    SharedArrayInt as _SharedArrayInt,
    SharedArrayStr as _SharedArrayStr, 
    SharedArrayObj as _SharedArrayObj,
    SharedDict as _SharedDict, 
    SharedQueue as _SharedQueue, 
    SharedCounter as _SharedCounter, 
    create_shared_array as _create_shared_array
)


class SharedArray:
    """
    A thread-safe shared array for efficient parallel data processing.
    
    SharedArray provides a high-performance, thread-safe array that can be
    shared between multiple threads without copying data. It supports
    parallel operations for maximum performance.
    
    Args:
        capacity (int): Maximum number of elements the array can hold.
    
    Example:
        >>> arr = SharedArray(capacity=1000)
        >>> arr.append(1.5)
        >>> arr.append(2.5)
        >>> arr.extend([3.0, 4.0, 5.0])
        >>> print(arr.len)  # 5
        >>> print(arr.sum())  # 16.0
        >>> squared = arr.parallel_map(lambda x: x ** 2)
        >>> print(squared)  # [2.25, 6.25, 9.0, 16.0, 25.0]
    """
    
    def __init__(self, capacity: int):
        """Initialize a new SharedArray with specified capacity."""
        self._array = _SharedArray(capacity)
        self._capacity = capacity
    
    def append(self, value: float) -> None:
        """
        Add a single value to the end of the array.
        
        Args:
            value: The float value to append.
        
        Raises:
            RuntimeError: If the array is at capacity.
        """
        self._array.append(value)
    
    def extend(self, values: List[float]) -> None:
        """
        Add multiple values to the end of the array.
        
        Args:
            values: A list of float values to append.
        
        Raises:
            RuntimeError: If adding all values would exceed capacity.
        """
        self._array.extend(values)
    
    def get(self, index: int) -> float:
        """
        Get the value at the specified index.
        
        Args:
            index: The index to retrieve (0-based).
        
        Returns:
            The value at the specified index.
        
        Raises:
            IndexError: If index is out of bounds.
        """
        return self._array.get(index)
    
    def set(self, index: int, value: float) -> None:
        """
        Set the value at the specified index.
        
        Args:
            index: The index to modify (0-based).
            value: The new value to set.
        
        Raises:
            IndexError: If index is out of bounds.
        """
        self._array.set(index, value)
    
    def slice(self, start: int, end: Optional[int] = None) -> List[float]:
        """
        Get a slice of the array.
        
        Args:
            start: Starting index (inclusive).
            end: Ending index (exclusive). If None, slice to the end.
        
        Returns:
            A list containing the sliced elements.
        """
        return self._array.slice(start, end)
    
    def to_list(self) -> List[float]:
        """
        Convert the entire array to a Python list.
        
        Returns:
            A list containing all elements in the array.
        """
        return self._array.to_list()
    
    def sum(self) -> float:
        """
        Calculate the sum of all elements using parallel processing.
        
        Returns:
            The sum of all elements in the array.
        """
        return self._array.sum()
    
    def parallel_map(self, func) -> List[float]:
        """
        Apply a function to all elements using parallel processing.
        
        Args:
            func: A callable that takes a float and returns a float.
        
        Returns:
            A list of results after applying the function to each element.
        """
        return self._array.parallel_map(func)
    
    def len(self) -> int:
        """Get the current number of elements in the array."""
        return self._array.len
    
    def capacity(self) -> int:
        """Get the maximum capacity of the array."""
        return self._capacity

    def is_empty(self) -> bool:
        """Check if the array is empty."""
        return self._array.is_empty()
    
    def clear(self) -> None:
        """
        Remove all elements from the array.
        
        After calling clear(), the array will be empty and len will be 0.
        """
        self._array.clear()
    
    @classmethod
    def from_data(cls, data: List[float]) -> 'SharedArray':
        """
        Create a SharedArray from existing data.
        
        Args:
            data: Initial data to populate the array.
        
        Returns:
            A new SharedArray containing the provided data.
        """
        rust_array = _SharedArray.from_data(data)
        wrapper = cls.__new__(cls)
        wrapper._array = rust_array
        return wrapper


class SharedArrayInt:
    """
    A thread-safe shared array for integer values.
    
    Similar to SharedArray but optimized for integer data types.
    
    Args:
        capacity (int): Maximum number of elements the array can hold.
    """
    
    def __init__(self, capacity: int):
        """Initialize a new SharedArrayInt with specified capacity."""
        self._array = _SharedArrayInt(capacity)
    
    def append(self, value: int) -> None:
        """Add a single integer value to the end of the array."""
        self._array.append(value)
    
    def extend(self, values: List[int]) -> None:
        """Add multiple integer values to the end of the array."""
        self._array.extend(values)
    
    def get(self, index: int) -> int:
        """Get the integer value at the specified index."""
        return self._array.get(index)
    
    def set(self, index: int, value: int) -> None:
        """Set the integer value at the specified index."""
        self._array.set(index, value)
    
    def to_list(self) -> List[int]:
        """Convert the entire array to a Python list of integers."""
        return self._array.to_list()
    
    def len(self) -> int:
        """Get the current number of elements in the array."""
        return self._array.len


class SharedArrayStr:
    """
    A thread-safe shared array for string values.
    
    Optimized for storing and processing string data with thread safety.
    
    Args:
        capacity (int): Maximum number of elements the array can hold.
    """
    
    def __init__(self, capacity: int):
        """Initialize a new SharedArrayStr with specified capacity."""
        self._array = _SharedArrayStr(capacity)
    
    def append(self, value: str) -> None:
        """Add a single string value to the end of the array."""
        self._array.append(value)
    
    def extend(self, values: List[str]) -> None:
        """Add multiple string values to the end of the array."""
        self._array.extend(values)
    
    def get(self, index: int) -> str:
        """Get the string value at the specified index."""
        return self._array.get(index)
    
    def set(self, index: int, value: str) -> None:
        """Set the string value at the specified index."""
        self._array.set(index, value)
    
    def to_list(self) -> List[str]:
        """Convert the entire array to a Python list of strings."""
        return self._array.to_list()
    
    def len(self) -> int:
        """Get the current number of elements in the array."""
        return self._array.len


class SharedArrayObj:
    """
    A thread-safe shared array for arbitrary Python objects.
    
    Can store any Python object, but with some performance overhead
    compared to specialized arrays.
    
    Args:
        capacity (int): Maximum number of elements the array can hold.
    """
    
    def __init__(self, capacity: int):
        """Initialize a new SharedArrayObj with specified capacity."""
        self._array = _SharedArrayObj(capacity)
    
    def append(self, value: Any) -> None:
        """Add a single object to the end of the array."""
        self._array.append(value)
    
    def extend(self, values: List[Any]) -> None:
        """Add multiple objects to the end of the array."""
        self._array.extend(values)
    
    def get(self, index: int) -> Any:
        """Get the object at the specified index."""
        return self._array.get(index)
    
    def set(self, index: int, value: Any) -> None:
        """Set the object at the specified index."""
        self._array.set(index, value)
    
    def to_list(self) -> List[Any]:
        """Convert the entire array to a Python list."""
        return self._array.to_list()
    
    def len(self) -> int:
        """Get the current number of elements in the array."""
        return self._array.len


class SharedDict:
    """
    A thread-safe shared dictionary for key-value storage.
    
    Provides concurrent access to a dictionary with thread-safe operations
    and parallel processing capabilities.
    
    Example:
        >>> shared_dict = SharedDict()
        >>> shared_dict.set("key1", 10)
        >>> shared_dict.set("key2", 20)
        >>> print(shared_dict.get("key1"))  # 10
        >>> print(shared_dict.len)  # 2
        >>> doubled = shared_dict.parallel_map_values(lambda x: x * 2)
    """
    
    def __init__(self):
        """Initialize a new empty SharedDict."""
        self._dict = _SharedDict()
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a key-value pair in the dictionary.
        
        Args:
            key: The string key.
            value: The value to associate with the key.
        """
        self._dict.set(key, value)
    
    def get(self, key: str) -> Any:
        """
        Get the value associated with a key.
        
        Args:
            key: The string key to look up.
        
        Returns:
            The value associated with the key.
        
        Raises:
            KeyError: If the key is not found.
        """
        return self._dict.get(key)
    
    def contains(self, key: str) -> bool:
        """
        Check if a key exists in the dictionary.
        
        Args:
            key: The string key to check.
        
        Returns:
            True if the key exists, False otherwise.
        """
        return self._dict.contains(key)
    
    def remove(self, key: str) -> None:
        """
        Remove a key-value pair from the dictionary.
        
        Args:
            key: The string key to remove.
        
        Raises:
            KeyError: If the key is not found.
        """
        self._dict.pop(key)
    
    def keys(self) -> List[str]:
        """
        Get all keys in the dictionary.
        
        Returns:
            A list of all keys.
        """
        return self._dict.keys()
    
    def values(self) -> List[Any]:
        """
        Get all values in the dictionary.
        
        Returns:
            A list of all values.
        """
        return self._dict.values()
    
    def items(self) -> List[tuple]:
        """
        Get all key-value pairs as tuples.
        
        Returns:
            A list of (key, value) tuples.
        """
        return self._dict.items()
    
    def parallel_map_values(self, func) -> 'SharedDict':
        """
        Apply a function to all values using parallel processing.
        
        Args:
            func: A callable that takes a value and returns a new value.
        
        Returns:
            A new SharedDict with the transformed values.
        """
        return SharedDict._from_rust(self._dict.parallel_map_values(func))
    
    @classmethod
    def _from_rust(cls, rust_dict):
        """Create a SharedDict from a Rust SharedDict object."""
        instance = cls.__new__(cls)
        instance._dict = rust_dict
        return instance
    
    def is_empty(self) -> bool:
        """Check if the dictionary is empty."""
        return self._dict.is_empty()
    
    def clear(self) -> None:
        """
        Remove all key-value pairs from the dictionary.
        
        After calling clear(), the dictionary will be empty and len will be 0.
        """
        self._dict.clear()
    
    def pop(self, key: str, default=None):
        """
        Remove and return the value for a key.
        
        Args:
            key: The string key to remove.
            default: Value to return if key is not found.
        
        Returns:
            The value that was associated with the key, or default if not found.
        """
        try:
            return self._dict.pop(key)
        except KeyError:
            if default is not None:
                return default
            raise
    
    def setdefault(self, key: str, default=None):
        """
        Get the value for a key, setting it to default if not present.
        
        Args:
            key: The string key to look up or set.
            default: The default value to set if key is not found.
        
        Returns:
            The value associated with the key.
        """
        return self._dict.setdefault(key, default)
    
    def update(self, other) -> None:
        """
        Update the dictionary with key-value pairs from another dict-like object.
        
        Args:
            other: A dictionary or dict-like object to merge into this one.
        """
        self._dict.update(other)
    
    def to_dict(self) -> dict:
        """
        Convert the SharedDict to a regular Python dictionary.
        
        Returns:
            A new dict containing all key-value pairs.
        """
        return self._dict.to_dict()
    
    @property
    def len(self) -> int:
        """Get the number of key-value pairs in the dictionary."""
        return self._dict.len
    
    # Compatibility methods for tests
    def put(self, key: str, value: Any) -> None:
        """Alias for set() method for backwards compatibility."""
        self.set(key, value)
    
    def size(self) -> int:
        """Get the number of key-value pairs in the dictionary (method version)."""
        return self._dict.len
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SharedDict':
        """
        Create a SharedDict from a regular Python dictionary.
        
        Args:
            data: A dictionary to populate the SharedDict with.
        
        Returns:
            A new SharedDict containing the provided data.
        """
        rust_dict = _SharedDict.from_dict(data)
        wrapper = cls.__new__(cls)
        wrapper._dict = rust_dict
        return wrapper


class SharedQueue:
    """
    A thread-safe queue for producer-consumer scenarios.
    
    Provides FIFO (first-in-first-out) access with thread safety,
    perfect for coordinating work between multiple threads.
    
    Args:
        max_size (int, optional): Maximum number of items the queue can hold.
                                 If not provided, creates an unbounded queue.
    
    Example:
        >>> queue = SharedQueue(max_size=100)
        >>> queue.put("item1")
        >>> queue.put("item2")
        >>> print(queue.size)  # 2
        >>> item = queue.get()
        >>> print(item)  # "item1"
        >>> print(queue.size)  # 1
    """
    
    def __init__(self, max_size: Optional[int] = None):
        """Initialize a new SharedQueue with optional maximum size."""
        if max_size is None:
            self._queue = _SharedQueue()
        else:
            self._queue = _SharedQueue(max_size)
    
    def put(self, item: Any) -> None:
        """
        Add an item to the queue.
        
        Args:
            item: The item to add to the queue.
        
        Raises:
            RuntimeError: If the queue is full.
        """
        self._queue.put(item)
    
    def get(self) -> Any:
        """
        Remove and return an item from the queue.
        
        Returns:
            The next item in the queue (FIFO order).
        
        Raises:
            RuntimeError: If the queue is empty.
        """
        return self._queue.get()
    
    def try_put(self, item: Any) -> bool:
        """
        Try to add an item to the queue without blocking.
        
        Args:
            item: The item to add to the queue.
        
        Returns:
            True if the item was added, False if the queue is full.
        """
        return self._queue.try_put(item)
    
    def try_get(self) -> Optional[Any]:
        """
        Try to get an item from the queue without blocking.
        
        Returns:
            The next item if available, None if the queue is empty.
        """
        return self._queue.try_get()
    
    def size(self) -> int:
        """Get the current number of items in the queue."""
        return self._queue.size
    
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return self._queue.empty()
    
    def is_full(self) -> bool:
        """Check if the queue is full."""
        return self._queue.is_full()
    
    def get_nowait(self) -> Optional[Any]:
        """
        Try to get an item from the queue without blocking.
        
        Returns:
            The next item if available, None if the queue is empty.
        
        Note:
            This is equivalent to try_get() but matches Python's queue.Queue API.
        """
        return self._queue.get_nowait()
    
    def clear(self) -> None:
        """
        Remove all items from the queue.
        
        After calling clear(), the queue will be empty and size will be 0.
        """
        self._queue.clear()
    
    def empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if the queue is empty, False otherwise.
        
        Note:
            This is equivalent to is_empty() but matches Python's queue.Queue API.
        """
        return self._queue.empty()
    
    # Compatibility methods for tests
    def push(self, item: Any) -> None:
        """Alias for put() method for backwards compatibility."""
        self.put(item)
    
    def pop(self) -> Any:
        """Alias for get() method for backwards compatibility."""
        return self.get()


class SharedCounter:
    """
    A thread-safe counter for atomic operations.
    
    Provides atomic increment, decrement, and arithmetic operations
    that are safe to use from multiple threads.
    
    Args:
        initial_value (int, optional): Starting value for the counter. Defaults to 0.
    
    Example:
        >>> counter = SharedCounter(initial_value=100)
        >>> print(counter.value)  # 100
        >>> print(counter.increment())  # 101
        >>> print(counter.add(10))  # 111
        >>> print(counter.decrement())  # 110
    """
    
    def __init__(self, initial_value: int = 0):
        """Initialize a new SharedCounter with optional initial value."""
        self._counter = _SharedCounter(initial_value)
    
    def increment(self, amount: int = 1) -> int:
        """
        Atomically increment the counter by the specified amount.
        
        Args:
            amount: The amount to increment by (defaults to 1).
        
        Returns:
            The new value after incrementing.
        """
        if amount == 1:
            return self._counter.increment()
        else:
            return self.add(amount)
    
    def decrement(self, amount: int = 1) -> int:
        """
        Atomically decrement the counter by the specified amount.
        
        Args:
            amount: The amount to decrement by (defaults to 1).
        
        Returns:
            The new value after decrementing.
        """
        if amount == 1:
            return self._counter.decrement()
        else:
            return self.subtract(amount)
    
    def add(self, value: int) -> int:
        """
        Atomically add a value to the counter.
        
        Args:
            value: The value to add (can be negative).
        
        Returns:
            The new value after adding.
        """
        return self._counter.add(value)
    
    def subtract(self, value: int) -> int:
        """
        Atomically subtract a value from the counter.
        
        Args:
            value: The value to subtract.
        
        Returns:
            The new value after subtracting.
        """
        return self._counter.subtract(value)
    
    @property
    def value(self) -> int:
        """Get the current value of the counter."""
        return self._counter.value
    
    def set(self, value: int) -> int:
        """
        Atomically set the counter to a new value.

        Args:
            value: The new value to set.

        Returns:
            The previous value of the counter.
        """
        return self._counter.set(value)

    def reset(self) -> int:
        """
        Reset the counter to zero.
        
        Returns:
            The previous value of the counter.
        """
        return self._counter.reset()
    
    def compare_and_swap(self, expected: int, new_value: int) -> bool:
        """
        Atomically compare and swap the counter value.
        
        Args:
            expected: The expected current value.
            new_value: The new value to set if current equals expected.
        
        Returns:
            True if the swap was successful, False otherwise.
        """
        return self._counter.compare_and_swap(expected, new_value)
    
    # Compatibility methods for tests
    def get(self) -> int:
        """Get the current value of the counter (method version for compatibility)."""
        return self._counter.value


def create_shared_array(array_type: str, capacity: int = 100):
    """
    Create a shared array of the specified type.
    
    Factory function for creating different types of shared arrays.
    
    Args:
        array_type: Type of array to create ("int", "str", "obj", or "float")
        capacity: Maximum capacity of the array (default: 100)
    
    Returns:
        A SharedArray variant of the specified type.
    
    Example:
        >>> int_array = create_shared_array("int", capacity=10)
        >>> str_array = create_shared_array("str", capacity=20)
        >>> obj_array = create_shared_array("obj", capacity=5)
    """
    if array_type == "int":
        return SharedArrayInt(capacity)
    elif array_type == "str":
        return SharedArrayStr(capacity)
    elif array_type == "obj":
        return SharedArrayObj(capacity)
    elif array_type in ("float", "default"):
        return SharedArray(capacity)
    else:
        raise ValueError(f"Unknown array type: {array_type}. Supported types: 'int', 'str', 'obj', 'float'")


__all__ = [
    'SharedArray', 'SharedArrayInt', 'SharedArrayStr', 'SharedArrayObj',
    'SharedDict', 'SharedQueue', 'SharedCounter', 'create_shared_array'
]
