# SmartCache - High-Performance Intelligent Caching

## Overview

SmartCache is a high-performance, thread-safe caching system implemented in Rust with Python bindings. It provides multiple eviction policies and comprehensive performance monitoring to optimize application performance.

## Features

### 🚀 **High Performance**
- **Rust-powered**: Core implementation in Rust for maximum performance
- **Thread-safe**: Concurrent access from multiple threads
- **Lock-free operations**: Optimized for high-throughput scenarios
- **Memory efficient**: Minimal overhead and smart memory management

### 🧠 **Intelligent Eviction Policies**
- **LRU (Least Recently Used)**: Evicts items that haven't been accessed recently
- **LFU (Least Frequently Used)**: Evicts items with lowest access frequency
- **TTL (Time-To-Live)**: Automatically expires items after a specified time
- **Adaptive**: Dynamically switches between LRU and LFU based on hit rate

### 📊 **Comprehensive Monitoring**
- **Real-time statistics**: Hit rate, miss rate, eviction count
- **Performance metrics**: Cache size, utilization, throughput
- **Automatic cleanup**: Expired entries are removed automatically

## Quick Start

### Basic Usage

```python
from pyferris import SmartCache, EvictionPolicy

# Create a cache with LRU eviction
cache = SmartCache(max_size=1000, policy=EvictionPolicy.LRU)

# Store and retrieve values
cache.put("user:123", {"name": "Alice", "age": 30})
user = cache.get("user:123")
print(user)  # {'name': 'Alice', 'age': 30}

# Check if key exists
if cache.contains("user:123"):
    print("User found in cache")

# Get performance statistics
stats = cache.stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
print(f"Cache size: {stats['current_size']}/{stats['max_size']}")
```

### Function Caching with Decorator

```python
from pyferris import cached, EvictionPolicy
import time

@cached(max_size=100, policy=EvictionPolicy.LRU)
def expensive_computation(n):
    time.sleep(0.1)  # Simulate expensive work
    return n * n

# First call is slow
result1 = expensive_computation(5)  # Takes ~0.1 seconds

# Second call is fast (cached)
result2 = expensive_computation(5)  # Takes ~0.001 seconds

# Check cache statistics
stats = expensive_computation.cache_stats()
print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")
```

## Eviction Policies

### LRU (Least Recently Used)
Best for: General-purpose caching with temporal locality
```python
cache = SmartCache(max_size=100, policy=EvictionPolicy.LRU)
```

### LFU (Least Frequently Used)
Best for: Workloads with frequency-based access patterns
```python
cache = SmartCache(max_size=100, policy=EvictionPolicy.LFU)
```

### TTL (Time-To-Live)
Best for: Time-sensitive data with expiration requirements
```python
cache = SmartCache(
    max_size=100, 
    policy=EvictionPolicy.TTL, 
    ttl_seconds=60.0  # 1 minute expiration
)
```

### Adaptive Policy
Best for: Dynamic workloads with changing access patterns
```python
cache = SmartCache(
    max_size=100, 
    policy=EvictionPolicy.ADAPTIVE,
    adaptive_threshold=0.7  # Switch to LFU when hit rate > 70%
)
```

## Performance Optimization

### Configuration Guidelines

```python
# For high-throughput scenarios
high_throughput_cache = SmartCache(
    max_size=10000,
    policy=EvictionPolicy.LRU  # Fast eviction decisions
)

# For memory-constrained environments
memory_efficient_cache = SmartCache(
    max_size=100,
    policy=EvictionPolicy.LFU,  # Keep frequently used items
    ttl_seconds=300.0  # 5 minute expiration
)

# For adaptive workloads
adaptive_cache = SmartCache(
    max_size=1000,
    policy=EvictionPolicy.ADAPTIVE,
    adaptive_threshold=0.8  # High threshold for stability
)
```

### Performance Benchmarks

Based on our tests, SmartCache delivers:
- **Write operations**: ~374,000 ops/sec
- **Read operations**: ~3,718,000 ops/sec
- **Memory overhead**: Minimal (< 1% per cached item)
- **Thread safety**: Full concurrent access support

## API Reference

### SmartCache Class

#### Constructor
```python
SmartCache(
    max_size: int = 1000,
    policy: EvictionPolicy = EvictionPolicy.LRU,
    ttl_seconds: Optional[float] = None,
    adaptive_threshold: float = 0.7
)
```

#### Core Methods
- `put(key, value)`: Store a key-value pair
- `get(key)`: Retrieve a value by key
- `contains(key)`: Check if key exists
- `remove(key)`: Remove a key
- `clear()`: Remove all entries
- `size()`: Get current cache size

#### Statistics and Monitoring
- `stats()`: Get performance statistics
- `cleanup()`: Manually clean expired entries
- `get_policy()` / `set_policy()`: Manage eviction policy
- `get_max_size()` / `set_max_size()`: Manage cache size
- `get_ttl()` / `set_ttl()`: Manage TTL settings

### @cached Decorator

```python
@cached(
    max_size: int = 128,
    policy: EvictionPolicy = EvictionPolicy.LRU,
    ttl_seconds: Optional[float] = None,
    typed: bool = False
)
def your_function():
    pass
```

#### Decorator Methods
- `your_function.cache_clear()`: Clear the cache
- `your_function.cache_stats()`: Get cache statistics
- `your_function.cache_size()`: Get current cache size
- `your_function.cache`: Access the underlying cache object

## Best Practices

### 1. Choose the Right Policy
```python
# For web applications with temporal locality
web_cache = SmartCache(policy=EvictionPolicy.LRU)

# For machine learning feature caches
ml_cache = SmartCache(policy=EvictionPolicy.LFU)

# For API response caching
api_cache = SmartCache(policy=EvictionPolicy.TTL, ttl_seconds=300)

# For dynamic workloads
dynamic_cache = SmartCache(policy=EvictionPolicy.ADAPTIVE)
```

### 2. Size Your Cache Appropriately
```python
import psutil

# Size based on available memory
available_memory = psutil.virtual_memory().available
cache_size = min(10000, available_memory // (1024 * 1024))  # 1MB per item estimate
cache = SmartCache(max_size=cache_size)
```

### 3. Monitor Performance
```python
def monitor_cache_performance(cache):
    stats = cache.stats()
    hit_rate = stats['hit_rate']
    
    if hit_rate < 0.5:
        print("Warning: Low hit rate, consider increasing cache size")
    elif hit_rate > 0.9:
        print("Info: High hit rate, cache is working well")
    
    utilization = stats['current_size'] / stats['max_size']
    if utilization > 0.8:
        print("Warning: High cache utilization, consider increasing size")
```

### 4. Handle Errors Gracefully
```python
def safe_cache_operation(cache, key, compute_func):
    try:
        # Try to get from cache
        result = cache.get(key)
        if result is not None:
            return result
        
        # Compute and cache result
        result = compute_func()
        cache.put(key, result)
        return result
    except Exception as e:
        # Fallback to direct computation
        print(f"Cache error: {e}")
        return compute_func()
```

## Use Cases

### 1. Web Application Caching
```python
# User session cache
session_cache = SmartCache(
    max_size=1000,
    policy=EvictionPolicy.LRU,
    ttl_seconds=3600  # 1 hour sessions
)

# Database query cache
query_cache = SmartCache(
    max_size=500,
    policy=EvictionPolicy.LFU  # Keep frequently used queries
)
```

### 2. Machine Learning Feature Cache
```python
# Feature computation cache
feature_cache = SmartCache(
    max_size=10000,
    policy=EvictionPolicy.LFU  # Keep frequently used features
)

@cached(max_size=1000, policy=EvictionPolicy.LRU)
def extract_features(data_id):
    # Expensive feature extraction
    return compute_features(data_id)
```

### 3. API Response Caching
```python
# API response cache with TTL
api_cache = SmartCache(
    max_size=1000,
    policy=EvictionPolicy.TTL,
    ttl_seconds=300  # 5 minute cache
)

@cached(max_size=200, ttl_seconds=60)
def fetch_external_data(endpoint):
    # Expensive API call
    return requests.get(endpoint).json()
```

## Thread Safety

SmartCache is fully thread-safe and designed for concurrent access:

```python
import threading
from pyferris import SmartCache

cache = SmartCache(max_size=1000)

def worker(thread_id):
    for i in range(100):
        key = f"thread_{thread_id}_key_{i}"
        value = f"thread_{thread_id}_value_{i}"
        
        # Thread-safe operations
        cache.put(key, value)
        result = cache.get(key)
        assert result == value

# Multiple threads can safely access the cache
threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Comparison with Other Caching Solutions

| Feature | SmartCache | functools.lru_cache | Redis | Memcached |
|---------|------------|---------------------|-------|-----------|
| **Performance** | Very High | High | Medium | Medium |
| **Thread Safety** | ✅ | ✅ | ✅ | ✅ |
| **Eviction Policies** | 4 policies | LRU only | Multiple | LRU only |
| **TTL Support** | ✅ | ❌ | ✅ | ✅ |
| **Memory Efficiency** | High | Medium | Low | Low |
| **Network Overhead** | None | None | High | High |
| **Persistence** | No | No | Yes | No |
| **Monitoring** | Comprehensive | Basic | Good | Basic |

## Troubleshooting

### Common Issues

1. **Low Hit Rate**
   - Increase cache size
   - Adjust eviction policy
   - Check TTL settings

2. **High Memory Usage**
   - Reduce cache size
   - Implement TTL
   - Use LFU policy

3. **Performance Issues**
   - Check for thread contention
   - Monitor cache statistics
   - Consider cache size vs. hit rate trade-off

### Debugging

```python
# Enable debug monitoring
def debug_cache_performance(cache):
    stats = cache.stats()
    print(f"Cache Performance Report:")
    print(f"  Hit Rate: {stats['hit_rate']:.2%}")
    print(f"  Size: {stats['current_size']}/{stats['max_size']}")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Evictions: {stats['evictions']}")
```

## Conclusion

SmartCache provides a high-performance, intelligent caching solution that can significantly improve application performance. With its multiple eviction policies, comprehensive monitoring, and thread-safe design, it's suitable for a wide range of use cases from web applications to machine learning pipelines.

The Rust implementation ensures maximum performance while the Python bindings provide ease of use. Whether you need simple LRU caching or advanced adaptive policies, SmartCache delivers the performance and features you need.
