"""
Smart Cache

This module tests cache functionality for the PyFerris framework.
Features tested:
- SmartCache with different eviction policies
- Cached decorator functionality
- Thread-safe caching operations
"""

import pytest
import time
import threading

from pyferris import (
    SmartCache, EvictionPolicy, cached
)


class TestSmartCache:
    """Test SmartCache functionality."""

    def test_smart_cache_creation(self):
        """Test basic SmartCache creation."""
        cache = SmartCache()
        assert cache is not None

    def test_smart_cache_with_parameters(self):
        """Test SmartCache creation with parameters."""
        cache = SmartCache(max_size=100, policy=EvictionPolicy.LRU)
        assert cache is not None

    def test_smart_cache_put_get(self):
        """Test basic put/get operations."""
        cache = SmartCache(max_size=10)
        
        cache.put("key1", "value1")
        cache.put("key2", 42)
        cache.put("key3", [1, 2, 3])
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == 42
        assert cache.get("key3") == [1, 2, 3]

    def test_smart_cache_contains(self):
        """Test cache contains functionality."""
        cache = SmartCache(max_size=10)
        
        cache.put("test_key", "test_value")
        
        assert cache.contains("test_key")
        assert not cache.contains("nonexistent_key")

    def test_smart_cache_remove(self):
        """Test cache remove functionality."""
        cache = SmartCache(max_size=10)
        
        cache.put("key1", "value1")
        assert cache.contains("key1")
        
        cache.remove("key1")
        assert not cache.contains("key1")

    def test_smart_cache_clear(self):
        """Test cache clear functionality."""
        cache = SmartCache(max_size=10)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        cache.clear()
        
        assert not cache.contains("key1")
        assert not cache.contains("key2")

    def test_smart_cache_size(self):
        """Test cache size tracking."""
        cache = SmartCache(max_size=10)
        
        assert cache.size() == 0
        
        cache.put("key1", "value1")
        assert cache.size() == 1
        
        cache.put("key2", "value2")
        assert cache.size() == 2
        
        cache.remove("key1")
        assert cache.size() == 1

    def test_smart_cache_capacity_limit(self):
        """Test cache respects capacity limits."""
        cache = SmartCache(max_size=3)
        
        # Fill cache to capacity
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        assert cache.size() == 3
        
        # Adding one more should evict according to policy
        cache.put("key4", "value4")
        assert cache.size() == 3

    def test_smart_cache_thread_safety(self):
        """Test thread-safe operations."""
        cache = SmartCache(max_size=100)
        results = []
        
        def worker(thread_id):
            for i in range(10):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                cache.put(key, value)
                
                retrieved = cache.get(key)
                if retrieved == value:
                    results.append(True)
                else:
                    results.append(False)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All operations should have succeeded
        assert all(results)

    def test_smart_cache_performance(self):
        """Test cache performance with rapid operations."""
        cache = SmartCache(max_size=1000)
        
        start_time = time.time()
        
        # Rapid put operations
        for i in range(500):
            cache.put(f"key_{i}", f"value_{i}")
        
        # Rapid get operations
        for i in range(500):
            cache.get(f"key_{i}")
        
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 1.0
        assert cache.size() <= 1000


class TestEvictionPolicy:
    """Test EvictionPolicy functionality."""

    def test_eviction_policy_constants(self):
        """Test eviction policy constants are available."""
        assert EvictionPolicy.LRU is not None
        assert EvictionPolicy.LFU is not None
        assert EvictionPolicy.TTL is not None
        assert EvictionPolicy.ADAPTIVE is not None

    def test_smart_cache_with_lru_policy(self):
        """Test SmartCache with LRU eviction policy."""
        cache = SmartCache(max_size=3, policy=EvictionPolicy.LRU)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # Access key1 to make it most recently used
        cache.get("key1")
        
        # Add key4 - should evict key2 (least recently used)
        cache.put("key4", "value4")
        
        assert cache.contains("key1")  # Recently accessed
        assert not cache.contains("key2")  # Should be evicted
        assert cache.contains("key3")
        assert cache.contains("key4")

    def test_smart_cache_with_lfu_policy(self):
        """Test SmartCache with LFU eviction policy."""
        cache = SmartCache(max_size=3, policy=EvictionPolicy.LFU)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # Access key1 multiple times
        cache.get("key1")
        cache.get("key1")
        cache.get("key1")
        
        # Add key4 - should evict least frequently used
        cache.put("key4", "value4")
        
        assert cache.contains("key1")  # Most frequently accessed
        assert cache.size() == 3

    def test_smart_cache_with_ttl_policy(self):
        """Test SmartCache with TTL eviction policy."""
        cache = SmartCache(max_size=10, policy=EvictionPolicy.TTL, ttl_seconds=0.1)
        
        cache.put("key1", "value1")
        assert cache.contains("key1")
        
        # Wait for TTL to expire
        time.sleep(0.15)
        
        # Key should be expired
        assert not cache.contains("key1")

    def test_smart_cache_with_adaptive_policy(self):
        """Test SmartCache with adaptive eviction policy."""
        cache = SmartCache(max_size=5, policy=EvictionPolicy.ADAPTIVE)
        
        # Fill cache
        for i in range(5):
            cache.put(f"key_{i}", f"value_{i}")
        
        assert cache.size() == 5
        
        # Add one more - adaptive policy should handle eviction
        cache.put("key_6", "value_6")
        assert cache.size() == 5


class TestCachedDecorator:
    """Test @cached decorator functionality."""

    def test_cached_decorator_basic(self):
        """Test basic @cached decorator functionality."""
        call_count = 0
        
        @cached(max_size=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * x
        
        # First call
        result1 = expensive_function(5)
        assert result1 == 25
        assert call_count == 1
        
        # Second call with same argument - should use cache
        result2 = expensive_function(5)
        assert result2 == 25
        assert call_count == 1  # Should not increment

    def test_cached_decorator_with_policy(self):
        """Test @cached decorator with specific policy."""
        call_count = 0
        
        @cached(max_size=3, policy=EvictionPolicy.LRU)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Fill cache
        test_function(1)
        test_function(2)
        test_function(3)
        assert call_count == 3
        
        # Call cached values
        test_function(1)
        test_function(2)
        assert call_count == 3  # Should not increment

    def test_cached_decorator_with_different_args(self):
        """Test @cached decorator with different arguments."""
        call_count = 0
        
        @cached(max_size=10)
        def multi_arg_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # Different argument combinations
        result1 = multi_arg_function(1, 2)
        result2 = multi_arg_function(2, 3)
        result3 = multi_arg_function(1, 2)  # Should use cache
        
        assert result1 == 3
        assert result2 == 5
        assert result3 == 3
        assert call_count == 2  # Only 2 unique calls

    def test_cached_decorator_ttl(self):
        """Test @cached decorator with TTL."""
        call_count = 0
        
        @cached(max_size=10, policy=EvictionPolicy.TTL, ttl_seconds=0.1)
        def ttl_function(x):
            nonlocal call_count
            call_count += 1
            return x * 3
        
        # First call
        result1 = ttl_function(4)
        assert result1 == 12
        assert call_count == 1
        
        # Second call before TTL expires
        result2 = ttl_function(4)
        assert result2 == 12
        assert call_count == 1
        
        # Wait for TTL to expire
        time.sleep(0.15)
        
        # Third call after TTL expires
        result3 = ttl_function(4)
        assert result3 == 12
        assert call_count == 2  # Should increment


class TestCacheIntegration:
    """Test integration between cache components."""

    def test_multiple_caches_independent(self):
        """Test that multiple cache instances are independent."""
        cache1 = SmartCache(max_size=10)
        cache2 = SmartCache(max_size=10)
        
        cache1.put("key1", "value1")
        cache2.put("key1", "different_value")
        
        assert cache1.get("key1") == "value1"
        assert cache2.get("key1") == "different_value"

    def test_cache_with_complex_objects(self):
        """Test caching complex objects."""
        cache = SmartCache(max_size=10)
        
        # Test with various object types
        test_objects = [
            {"dict": "value"},
            ["list", "value"],
            ("tuple", "value"),
            42,
            3.14,
            "string"
        ]
        
        for i, obj in enumerate(test_objects):
            key = f"key_{i}"
            cache.put(key, obj)
            assert cache.get(key) == obj

    def test_cache_performance_under_load(self):
        """Test cache performance under heavy load."""
        cache = SmartCache(max_size=1000, policy=EvictionPolicy.LRU)
        
        # Heavy concurrent access
        def worker(worker_id):
            for i in range(100):
                key = f"worker_{worker_id}_key_{i}"
                value = f"worker_{worker_id}_value_{i}"
                cache.put(key, value)
                retrieved = cache.get(key)
                assert retrieved == value
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 5.0
        assert cache.size() <= 1000

    def test_cache_memory_efficiency(self):
        """Test cache memory usage patterns."""
        cache = SmartCache(max_size=100)
        
        # Fill cache completely
        for i in range(100):
            cache.put(f"key_{i}", f"value_{i}" * 100)  # Larger values
        
        assert cache.size() == 100
        
        # Add more items - should maintain size limit
        for i in range(100, 200):
            cache.put(f"key_{i}", f"value_{i}" * 100)
        
        assert cache.size() == 100  # Should not exceed limit


if __name__ == "__main__":
    pytest.main([__file__])
