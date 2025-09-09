"""
Smart Cache

This module provides a high-performance intelligent caching system with multiple 
eviction policies for optimizing Python application performance.
"""

from typing import Any, Dict, Optional, Union, Callable
import functools
from ._pyferris import SmartCache as _SmartCache, EvictionPolicy as _EvictionPolicy

# Re-export the eviction policy constants
class EvictionPolicy:
    """Cache eviction policies for SmartCache."""
    LRU = _EvictionPolicy.lru()
    LFU = _EvictionPolicy.lfu()
    TTL = _EvictionPolicy.ttl()
    ADAPTIVE = _EvictionPolicy.adaptive()


class SmartCache:
    """
    A high-performance thread-safe cache with intelligent eviction policies.
    
    SmartCache provides multiple eviction strategies to optimize performance based on
    different access patterns. It supports LRU, LFU, TTL, and adaptive eviction
    policies with comprehensive performance monitoring.
    
    Args:
        max_size (int): Maximum number of items to store in the cache (default: 1000).
        policy (EvictionPolicy): Eviction policy to use (default: EvictionPolicy.LRU).
        ttl_seconds (Optional[float]): Time-to-live for cache entries in seconds.
        adaptive_threshold (float): Hit rate threshold for adaptive policy (default: 0.7).
    
    Features:
        - Thread-safe operations
        - Multiple eviction policies (LRU, LFU, TTL, Adaptive)
        - Comprehensive performance statistics
        - Automatic cleanup of expired entries
        - High-performance Rust implementation
    
    Example:
        >>> from pyferris import SmartCache, EvictionPolicy
        >>> import time
        >>> 
        >>> # Create cache with LRU eviction
        >>> cache = SmartCache(max_size=100, policy=EvictionPolicy.LRU)
        >>> 
        >>> # Store values
        >>> cache.put("key1", "value1")
        >>> cache.put("key2", {"data": [1, 2, 3]})
        >>> 
        >>> # Retrieve values
        >>> value = cache.get("key1")
        >>> print(value)  # "value1"
        >>> 
        >>> # Check existence
        >>> if cache.contains("key2"):
        ...     print("Key exists")
        >>> 
        >>> # Get performance statistics
        >>> stats = cache.stats()
        >>> print(f"Hit rate: {stats['hit_rate']:.2%}")
        >>> print(f"Cache size: {stats['current_size']}")
        
        >>> # Create cache with TTL
        >>> ttl_cache = SmartCache(
        ...     max_size=50,
        ...     policy=EvictionPolicy.TTL,
        ...     ttl_seconds=60.0  # 1 minute TTL
        ... )
        >>> 
        >>> ttl_cache.put("temp_key", "temp_value")
        >>> # After 60 seconds, the entry will be automatically evicted
        
        >>> # Create adaptive cache
        >>> adaptive_cache = SmartCache(
        ...     max_size=200,
        ...     policy=EvictionPolicy.ADAPTIVE,
        ...     adaptive_threshold=0.8  # Switch to LFU when hit rate > 80%
        ... )
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        policy: _EvictionPolicy = EvictionPolicy.LRU,
        ttl_seconds: Optional[float] = None,
        adaptive_threshold: float = 0.7,
    ):
        """Initialize SmartCache with specified configuration."""
        self._cache = _SmartCache(max_size, policy, ttl_seconds, adaptive_threshold)
    
    def get(self, key: Any) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The key to look up.
            
        Returns:
            The cached value if found and not expired, None otherwise.
            
        Example:
            >>> cache = SmartCache()
            >>> cache.put("name", "Alice")
            >>> value = cache.get("name")
            >>> print(value)  # "Alice"
            >>> 
            >>> # Non-existent key
            >>> missing = cache.get("missing")
            >>> print(missing)  # None
        """
        return self._cache.get(key)
    
    def put(self, key: Any, value: Any) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: The key to store the value under.
            value: The value to store.
            
        Note:
            If the cache is full, items will be evicted according to the
            configured eviction policy.
            
        Example:
            >>> cache = SmartCache(max_size=2)
            >>> cache.put("a", 1)
            >>> cache.put("b", 2)
            >>> cache.put("c", 3)  # This will evict "a" (LRU)
            >>> 
            >>> print(cache.get("a"))  # None (evicted)
            >>> print(cache.get("b"))  # 2
            >>> print(cache.get("c"))  # 3
        """
        self._cache.put(key, value)
    
    def contains(self, key: Any) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: The key to check.
            
        Returns:
            True if the key exists and is not expired, False otherwise.
            
        Example:
            >>> cache = SmartCache()
            >>> cache.put("exists", "value")
            >>> 
            >>> print(cache.contains("exists"))     # True
            >>> print(cache.contains("missing"))    # False
        """
        return self._cache.contains(key)
    
    def remove(self, key: Any) -> Optional[Any]:
        """
        Remove a key from the cache.
        
        Args:
            key: The key to remove.
            
        Returns:
            The removed value if the key existed, None otherwise.
            
        Example:
            >>> cache = SmartCache()
            >>> cache.put("remove_me", "value")
            >>> 
            >>> removed = cache.remove("remove_me")
            >>> print(removed)  # "value"
            >>> 
            >>> # Key no longer exists
            >>> print(cache.contains("remove_me"))  # False
        """
        return self._cache.remove(key)
    
    def clear(self) -> None:
        """
        Remove all entries from the cache.
        
        This operation resets all statistics except for historical counts.
        
        Example:
            >>> cache = SmartCache()
            >>> cache.put("a", 1)
            >>> cache.put("b", 2)
            >>> 
            >>> print(cache.size())  # 2
            >>> cache.clear()
            >>> print(cache.size())  # 0
        """
        self._cache.clear()
    
    def size(self) -> int:
        """
        Get the current number of items in the cache.
        
        Returns:
            The number of items currently stored in the cache.
            
        Example:
            >>> cache = SmartCache()
            >>> print(cache.size())  # 0
            >>> 
            >>> cache.put("a", 1)
            >>> cache.put("b", 2)
            >>> print(cache.size())  # 2
        """
        return self._cache.size()
    
    def stats(self) -> Dict[str, Union[int, float]]:
        """
        Get comprehensive cache performance statistics.
        
        Returns:
            Dictionary containing:
            - hits: Number of cache hits
            - misses: Number of cache misses
            - evictions: Number of items evicted
            - current_size: Current number of items in cache
            - max_size: Maximum cache capacity
            - hit_rate: Cache hit rate (0.0 to 1.0)
            
        Example:
            >>> cache = SmartCache(max_size=2)
            >>> cache.put("a", 1)
            >>> cache.put("b", 2)
            >>> 
            >>> # Generate some hits and misses
            >>> cache.get("a")      # hit
            >>> cache.get("a")      # hit
            >>> cache.get("missing") # miss
            >>> 
            >>> stats = cache.stats()
            >>> print(f"Hit rate: {stats['hit_rate']:.2%}")
            >>> print(f"Total hits: {stats['hits']}")
            >>> print(f"Total misses: {stats['misses']}")
            >>> print(f"Cache utilization: {stats['current_size']}/{stats['max_size']}")
        """
        return self._cache.stats()
    
    def cleanup(self) -> int:
        """
        Manually trigger cleanup of expired entries.
        
        Returns:
            Number of entries that were removed.
            
        Note:
            This is automatically called during normal cache operations,
            but can be useful for proactive cleanup.
            
        Example:
            >>> cache = SmartCache(ttl_seconds=1.0)
            >>> cache.put("temp", "value")
            >>> 
            >>> import time
            >>> time.sleep(1.1)  # Wait for expiration
            >>> 
            >>> expired_count = cache.cleanup()
            >>> print(f"Cleaned up {expired_count} expired entries")
        """
        return self._cache.cleanup()
    
    def get_policy(self) -> _EvictionPolicy:
        """
        Get the current eviction policy.
        
        Returns:
            The current eviction policy.
            
        Example:
            >>> cache = SmartCache(policy=EvictionPolicy.LRU)
            >>> policy = cache.get_policy()
            >>> print(policy)  # EvictionPolicy.LRU
        """
        return self._cache.get_policy()
    
    def set_policy(self, policy: _EvictionPolicy) -> None:
        """
        Set the eviction policy.
        
        Args:
            policy: The new eviction policy to use.
            
        Example:
            >>> cache = SmartCache(policy=EvictionPolicy.LRU)
            >>> cache.set_policy(EvictionPolicy.LFU)
            >>> print(cache.get_policy())  # EvictionPolicy.LFU
        """
        self._cache.set_policy(policy)
    
    def get_max_size(self) -> int:
        """
        Get the maximum cache size.
        
        Returns:
            The maximum number of items the cache can hold.
            
        Example:
            >>> cache = SmartCache(max_size=100)
            >>> print(cache.get_max_size())  # 100
        """
        return self._cache.get_max_size()
    
    def set_max_size(self, max_size: int) -> None:
        """
        Set the maximum cache size.
        
        Args:
            max_size: The new maximum cache size.
            
        Note:
            If the new size is smaller than the current cache size,
            items will be evicted according to the eviction policy.
            
        Example:
            >>> cache = SmartCache(max_size=100)
            >>> cache.set_max_size(50)
            >>> print(cache.get_max_size())  # 50
        """
        self._cache.set_max_size(max_size)
    
    def get_ttl(self) -> Optional[float]:
        """
        Get the current TTL setting.
        
        Returns:
            The TTL in seconds, or None if no TTL is set.
            
        Example:
            >>> cache = SmartCache(ttl_seconds=60.0)
            >>> print(cache.get_ttl())  # 60.0
        """
        return self._cache.get_ttl()
    
    def set_ttl(self, ttl_seconds: Optional[float]) -> None:
        """
        Set the TTL for cache entries.
        
        Args:
            ttl_seconds: TTL in seconds, or None to disable TTL.
            
        Example:
            >>> cache = SmartCache()
            >>> cache.set_ttl(30.0)  # 30 second TTL
            >>> print(cache.get_ttl())  # 30.0
        """
        self._cache.set_ttl(ttl_seconds)
    
    def __len__(self) -> int:
        """Get the current cache size."""
        return self.size()
    
    def __contains__(self, key: Any) -> bool:
        """Check if a key exists in the cache."""
        return self.contains(key)
    
    def __getitem__(self, key: Any) -> Any:
        """Get a value from the cache, raising KeyError if not found."""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
    
    def __setitem__(self, key: Any, value: Any) -> None:
        """Set a value in the cache."""
        self.put(key, value)
    
    def __delitem__(self, key: Any) -> None:
        """Remove a key from the cache, raising KeyError if not found."""
        if self.remove(key) is None:
            raise KeyError(key)
    
    def __repr__(self) -> str:
        """String representation of the cache."""
        return f"SmartCache(size={self.size()}, max_size={self.get_max_size()})"


def cached(
    max_size: int = 128,
    policy: _EvictionPolicy = EvictionPolicy.LRU,
    ttl_seconds: Optional[float] = None,
    typed: bool = False,
) -> Callable:
    """
    Decorator that adds intelligent caching to a function.
    
    This decorator uses SmartCache internally to provide high-performance
    caching with configurable eviction policies.
    
    Args:
        max_size (int): Maximum number of cached results (default: 128).
        policy (EvictionPolicy): Eviction policy to use (default: LRU).
        ttl_seconds (Optional[float]): Time-to-live for cached results.
        typed (bool): If True, cache arguments of different types separately.
        
    Returns:
        Decorated function with caching capabilities.
        
    Example:
        >>> from pyferris import cached, EvictionPolicy
        >>> import time
        >>> 
        >>> # Simple LRU cache
        >>> @cached(max_size=100)
        ... def expensive_function(x):
        ...     time.sleep(0.1)  # Simulate expensive computation
        ...     return x * x
        >>> 
        >>> # First call is slow
        >>> start = time.time()
        >>> result1 = expensive_function(5)
        >>> print(f"First call: {time.time() - start:.3f}s")
        >>> 
        >>> # Second call is fast (cached)
        >>> start = time.time()
        >>> result2 = expensive_function(5)
        >>> print(f"Second call: {time.time() - start:.3f}s")
        >>> 
        >>> # Check cache statistics
        >>> stats = expensive_function.cache_stats()
        >>> print(f"Cache hits: {stats['hits']}")
        >>> print(f"Cache misses: {stats['misses']}")
        
        >>> # TTL-based cache
        >>> @cached(max_size=50, ttl_seconds=10.0)
        ... def api_call(endpoint):
        ...     # Simulate API call
        ...     return f"Data from {endpoint}"
        >>> 
        >>> # LFU cache for frequently accessed data
        >>> @cached(max_size=200, policy=EvictionPolicy.LFU)
        ... def database_query(query_id):
        ...     # Simulate database query
        ...     return f"Result for query {query_id}"
    """
    def decorator(func: Callable) -> Callable:
        cache = SmartCache(max_size=max_size, policy=policy, ttl_seconds=ttl_seconds)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            if typed:
                key = (args, tuple(sorted(kwargs.items())), 
                      tuple(type(arg) for arg in args))
            else:
                key = (args, tuple(sorted(kwargs.items())))
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Compute result and cache it
            result = func(*args, **kwargs)
            cache.put(key, result)
            return result
        
        # Add cache methods to the wrapper
        wrapper.cache_clear = cache.clear
        wrapper.cache_stats = cache.stats
        wrapper.cache_size = cache.size
        wrapper.cache = cache
        
        return wrapper
    
    return decorator


__all__ = [
    'SmartCache',
    'EvictionPolicy',
    'cached',
]
