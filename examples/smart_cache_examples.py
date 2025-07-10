#!/usr/bin/env python3
"""
SmartCache Examples - Demonstrating high-performance caching with PyFerris

This example shows how to use SmartCache for various caching scenarios
with different eviction policies and performance optimizations.
"""

import time
import random
import threading
from pyferris import SmartCache, EvictionPolicy, cached

def example_basic_usage():
    """Basic SmartCache usage example."""
    print("=== Basic SmartCache Usage ===")
    
    # Create cache with LRU eviction
    cache = SmartCache(max_size=5, policy=EvictionPolicy.LRU)
    
    # Store some data
    cache.put("user:1", {"name": "Alice", "age": 25})
    cache.put("user:2", {"name": "Bob", "age": 30})
    cache.put("config", {"theme": "dark", "language": "en"})
    
    # Retrieve data
    user = cache.get("user:1")
    print(f"Retrieved user: {user}")
    
    # Check cache size and stats
    print(f"Cache size: {cache.size()}")
    stats = cache.stats()
    print(f"Hit rate: {stats['hit_rate']:.2%}")
    print()

def example_eviction_policies():
    """Demonstrate different eviction policies."""
    print("=== Eviction Policies Demonstration ===")
    
    # LRU Policy
    print("LRU Policy:")
    lru_cache = SmartCache(max_size=3, policy=EvictionPolicy.LRU)
    lru_cache.put("a", 1)
    lru_cache.put("b", 2)
    lru_cache.put("c", 3)
    lru_cache.get("a")  # Access 'a' to make it recently used
    lru_cache.put("d", 4)  # This should evict 'b'
    print(f"After adding 'd', 'b' exists: {lru_cache.contains('b')}")  # False
    print(f"After adding 'd', 'a' exists: {lru_cache.contains('a')}")  # True
    
    # LFU Policy
    print("\nLFU Policy:")
    lfu_cache = SmartCache(max_size=3, policy=EvictionPolicy.LFU)
    lfu_cache.put("x", 1)
    lfu_cache.put("y", 2)
    lfu_cache.put("z", 3)
    lfu_cache.get("x")  # Access 'x' multiple times
    lfu_cache.get("x")
    lfu_cache.put("w", 4)  # This should evict 'y' (least frequently used)
    print(f"After adding 'w', 'y' exists: {lfu_cache.contains('y')}")  # False
    print(f"After adding 'w', 'x' exists: {lfu_cache.contains('x')}")  # True
    
    # TTL Policy
    print("\nTTL Policy:")
    ttl_cache = SmartCache(max_size=10, policy=EvictionPolicy.TTL, ttl_seconds=0.5)
    ttl_cache.put("temp", "temporary value")
    print(f"Immediately after insert: {ttl_cache.get('temp')}")
    time.sleep(0.6)  # Wait for expiration
    print(f"After 0.6 seconds: {ttl_cache.get('temp')}")  # None (expired)
    print()

def example_cached_decorator():
    """Demonstrate the @cached decorator."""
    print("=== @cached Decorator Example ===")
    
    # Track function calls
    call_count = 0
    
    @cached(max_size=10, policy=EvictionPolicy.LRU)
    def fibonacci(n):
        nonlocal call_count
        call_count += 1
        if n < 2:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    # Calculate fibonacci numbers
    print("Calculating fibonacci(10)...")
    start_time = time.time()
    result = fibonacci(10)
    end_time = time.time()
    
    print(f"Result: {result}")
    print(f"Function calls: {call_count}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    
    # Check cache statistics
    stats = fibonacci.cache_stats()
    print(f"Cache hits: {stats['hits']}")
    print(f"Cache misses: {stats['misses']}")
    print(f"Hit rate: {stats['hit_rate']:.2%}")
    print()

def example_performance_comparison():
    """Compare performance with and without caching."""
    print("=== Performance Comparison ===")
    
    def expensive_computation(n):
        """Simulate expensive computation."""
        time.sleep(0.01)  # 10ms delay
        return n * n * n
    
    # Without caching
    start_time = time.time()
    results_no_cache = []
    for i in range(20):
        # Simulate repeated computations
        value = random.randint(1, 5)
        results_no_cache.append(expensive_computation(value))
    no_cache_time = time.time() - start_time
    
    # With caching
    cache = SmartCache(max_size=10, policy=EvictionPolicy.LRU)
    start_time = time.time()
    results_with_cache = []
    for i in range(20):
        value = random.randint(1, 5)
        cached_result = cache.get(f"compute_{value}")
        if cached_result is None:
            cached_result = expensive_computation(value)
            cache.put(f"compute_{value}", cached_result)
        results_with_cache.append(cached_result)
    with_cache_time = time.time() - start_time
    
    print(f"Without cache: {no_cache_time:.3f} seconds")
    print(f"With cache: {with_cache_time:.3f} seconds")
    print(f"Speedup: {no_cache_time / with_cache_time:.1f}x")
    
    # Show cache statistics
    stats = cache.stats()
    print(f"Cache hit rate: {stats['hit_rate']:.2%}")
    print()

def example_thread_safety():
    """Demonstrate thread-safe operations."""
    print("=== Thread Safety Example ===")
    
    cache = SmartCache(max_size=100, policy=EvictionPolicy.LRU)
    results = []
    
    def worker(thread_id):
        """Worker function for threading test."""
        for i in range(50):
            key = f"thread_{thread_id}_key_{i}"
            value = f"thread_{thread_id}_value_{i}"
            
            # Store value
            cache.put(key, value)
            
            # Retrieve and verify
            retrieved = cache.get(key)
            results.append(retrieved == value)
            
            # Random sleep to increase contention
            time.sleep(0.001)
    
    # Start multiple threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Check results
    success_rate = sum(results) / len(results)
    print(f"Thread safety test: {success_rate:.2%} success rate")
    print(f"Cache size after threading: {cache.size()}")
    
    stats = cache.stats()
    print("Final cache statistics:")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate']:.2%}")
    print()

def example_adaptive_policy():
    """Demonstrate adaptive eviction policy."""
    print("=== Adaptive Policy Example ===")
    
    cache = SmartCache(
        max_size=5,
        policy=EvictionPolicy.ADAPTIVE,
        adaptive_threshold=0.6
    )
    
    # Phase 1: Low hit rate (should behave like LRU)
    print("Phase 1: Low hit rate pattern")
    for i in range(10):
        cache.put(f"key_{i}", f"value_{i}")
        cache.get(f"key_{i}")  # Single access
    
    stats = cache.stats()
    print(f"Hit rate after phase 1: {stats['hit_rate']:.2%}")
    
    # Phase 2: High hit rate (should behave like LFU)
    print("\nPhase 2: High hit rate pattern")
    # Access some keys frequently
    for _ in range(10):
        cache.get("key_7")
        cache.get("key_8")
        cache.get("key_9")
    
    stats = cache.stats()
    print(f"Hit rate after phase 2: {stats['hit_rate']:.2%}")
    
    # Add new items to trigger adaptive behavior
    cache.put("new_key_1", "new_value_1")
    cache.put("new_key_2", "new_value_2")
    
    print("Adaptive policy automatically adjusted eviction strategy")
    print(f"Final cache size: {cache.size()}")
    print()

def example_cache_monitoring():
    """Show how to monitor cache performance."""
    print("=== Cache Monitoring Example ===")
    
    cache = SmartCache(max_size=20, policy=EvictionPolicy.LRU)
    
    # Simulate workload
    for i in range(100):
        key = f"key_{i % 15}"  # Create some overlap for hits
        value = f"value_{i}"
        
        # Try to get from cache first
        if cache.get(key) is None:
            cache.put(key, value)
    
    # Display comprehensive statistics
    stats = cache.stats()
    print("Cache Performance Report:")
    print(f"  Total operations: {stats['hits'] + stats['misses']}")
    print(f"  Cache hits: {stats['hits']}")
    print(f"  Cache misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate']:.2%}")
    print(f"  Evictions: {stats['evictions']}")
    print(f"  Current size: {stats['current_size']}/{stats['max_size']}")
    print(f"  Utilization: {stats['current_size'] / stats['max_size']:.2%}")
    
    # Performance recommendations
    if stats['hit_rate'] < 0.5:
        print("\n💡 Recommendation: Consider increasing cache size or adjusting eviction policy")
    elif stats['hit_rate'] > 0.8:
        print("\n✅ Good: High hit rate indicates effective caching")
    
    if stats['current_size'] / stats['max_size'] > 0.9:
        print("⚠️  Warning: Cache utilization is high, consider increasing size")
    
    print()

def main():
    """Run all examples."""
    print("SmartCache Examples - High-Performance Caching with PyFerris")
    print("=" * 60)
    
    example_basic_usage()
    example_eviction_policies()
    example_cached_decorator()
    example_performance_comparison()
    example_thread_safety()
    example_adaptive_policy()
    example_cache_monitoring()
    
    print("=" * 60)
    print("✅ All examples completed successfully!")
    print("SmartCache provides immediate performance gains for your applications.")

if __name__ == "__main__":
    main()
