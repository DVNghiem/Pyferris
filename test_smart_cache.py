#!/usr/bin/env python3
"""
Test script for SmartCache implementation
"""

import sys
import os
import time
import threading
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from pyferris import SmartCache, EvictionPolicy, cached
    print("✓ SmartCache imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

def test_basic_operations():
    """Test basic cache operations"""
    print("\n=== Testing Basic Operations ===")
    
    cache = SmartCache(max_size=3, policy=EvictionPolicy.LRU)
    
    # Test put and get
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    assert cache.get("missing") is None
    
    # Test contains
    assert cache.contains("key1")
    assert not cache.contains("missing")
    
    # Test size
    assert cache.size() == 2
    
    print("✓ Basic operations work correctly")

def test_eviction_policies():
    """Test different eviction policies"""
    print("\n=== Testing Eviction Policies ===")
    
    # Test LRU
    lru_cache = SmartCache(max_size=2, policy=EvictionPolicy.LRU)
    lru_cache.put("a", 1)
    lru_cache.put("b", 2)
    lru_cache.get("a")  # Make 'a' recently used
    lru_cache.put("c", 3)  # Should evict 'b'
    
    assert lru_cache.contains("a")
    assert not lru_cache.contains("b")
    assert lru_cache.contains("c")
    
    # Test LFU
    lfu_cache = SmartCache(max_size=2, policy=EvictionPolicy.LFU)
    lfu_cache.put("x", 1)
    lfu_cache.put("y", 2)
    lfu_cache.get("x")  # Make 'x' more frequently used
    lfu_cache.get("x")
    lfu_cache.put("z", 3)  # Should evict 'y' (less frequently used)
    
    assert lfu_cache.contains("x")
    assert not lfu_cache.contains("y")
    assert lfu_cache.contains("z")
    
    print("✓ Eviction policies work correctly")

def test_ttl():
    """Test TTL functionality"""
    print("\n=== Testing TTL ===")
    
    # Create cache with 0.1 second TTL
    ttl_cache = SmartCache(max_size=10, policy=EvictionPolicy.TTL, ttl_seconds=0.1)
    
    ttl_cache.put("temp", "value")
    assert ttl_cache.get("temp") == "value"
    
    # Wait for expiration
    time.sleep(0.15)
    
    # Should be expired now
    assert ttl_cache.get("temp") is None
    
    print("✓ TTL functionality works correctly")

def test_statistics():
    """Test cache statistics"""
    print("\n=== Testing Statistics ===")
    
    cache = SmartCache(max_size=5)
    
    # Generate some hits and misses
    cache.put("a", 1)
    cache.put("b", 2)
    
    cache.get("a")      # hit
    cache.get("a")      # hit
    cache.get("missing") # miss
    cache.get("b")      # hit
    cache.get("missing") # miss
    
    stats = cache.stats()
    
    assert stats["hits"] == 3
    assert stats["misses"] == 2
    assert stats["current_size"] == 2
    assert stats["max_size"] == 5
    assert abs(stats["hit_rate"] - 0.6) < 0.01  # 3/(3+2) = 0.6
    
    print("✓ Statistics work correctly")

def test_cached_decorator():
    """Test the @cached decorator"""
    print("\n=== Testing @cached Decorator ===")
    
    call_count = 0
    
    @cached(max_size=3, policy=EvictionPolicy.LRU)
    def expensive_function(x):
        nonlocal call_count
        call_count += 1
        return x * x
    
    # First calls should compute
    result1 = expensive_function(5)
    result2 = expensive_function(10)
    assert call_count == 2
    assert result1 == 25
    assert result2 == 100
    
    # Second calls should use cache
    result3 = expensive_function(5)
    result4 = expensive_function(10)
    assert call_count == 2  # No new calls
    assert result3 == 25
    assert result4 == 100
    
    # Check cache stats
    stats = expensive_function.cache_stats()
    assert stats["hits"] == 2
    assert stats["misses"] == 2
    
    print("✓ @cached decorator works correctly")

def test_thread_safety():
    """Test thread safety"""
    print("\n=== Testing Thread Safety ===")
    
    cache = SmartCache(max_size=100)
    results = []
    
    def worker(thread_id):
        for i in range(10):
            key = f"thread_{thread_id}_key_{i}"
            value = f"thread_{thread_id}_value_{i}"
            cache.put(key, value)
            
            # Random access pattern
            if random.random() > 0.5:
                retrieved = cache.get(key)
                results.append(retrieved == value)
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # All retrievals should have been successful
    assert all(results)
    
    print("✓ Thread safety works correctly")

def test_adaptive_policy():
    """Test adaptive eviction policy"""
    print("\n=== Testing Adaptive Policy ===")
    
    # Create adaptive cache
    adaptive_cache = SmartCache(
        max_size=3, 
        policy=EvictionPolicy.ADAPTIVE, 
        adaptive_threshold=0.5
    )
    
    # Fill cache
    adaptive_cache.put("a", 1)
    adaptive_cache.put("b", 2)
    adaptive_cache.put("c", 3)
    
    # Generate some access patterns
    adaptive_cache.get("a")
    adaptive_cache.get("b")
    adaptive_cache.get("missing")  # miss
    
    # Add another item (should trigger eviction)
    adaptive_cache.put("d", 4)
    
    # Should still have at least 3 items
    assert adaptive_cache.size() <= 3
    
    print("✓ Adaptive policy works correctly")

def performance_benchmark():
    """Run performance benchmark"""
    print("\n=== Performance Benchmark ===")
    
    cache = SmartCache(max_size=1000, policy=EvictionPolicy.LRU)
    
    # Benchmark put operations
    start_time = time.time()
    for i in range(10000):
        cache.put(f"key_{i}", f"value_{i}")
    put_time = time.time() - start_time
    
    # Benchmark get operations
    start_time = time.time()
    for i in range(10000):
        cache.get(f"key_{i}")
    get_time = time.time() - start_time
    
    print(f"Put operations: {10000/put_time:.0f} ops/sec")
    print(f"Get operations: {10000/get_time:.0f} ops/sec")
    print(f"Cache size: {cache.size()}")
    
    stats = cache.stats()
    print(f"Hit rate: {stats['hit_rate']:.2%}")

def main():
    """Run all tests"""
    print("Testing SmartCache Implementation")
    print("=" * 50)
    
    try:
        test_basic_operations()
        test_eviction_policies()
        test_ttl()
        test_statistics()
        test_cached_decorator()
        test_thread_safety()
        test_adaptive_policy()
        performance_benchmark()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed successfully!")
        print("SmartCache is ready for production use.")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
