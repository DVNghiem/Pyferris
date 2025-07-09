"""
Auto Garbage Collection Examples

This module demonstrates how to use the advanced auto garbage collection system
in Pyferris for optimal memory management in high-performance applications.
"""

import time
import threading
import tempfile
import os
import sys

# Import Pyferris auto GC components
from pyferris.gc import (
    AutoGCConfig, enable_auto_gc, disable_auto_gc, force_gc,
    gc_stats, track_allocation, register_cleanup_callback, managed_memory,
    auto_gc_decorator, ManagedMemoryPool, create_managed_mmap
)
from pyferris import parallel_map
from pyferris.profiling import Profiler


def example_1_basic_auto_gc():
    """Example 1: Basic Auto GC Usage"""
    print("=== Example 1: Basic Auto GC Usage ===")
    
    # Enable auto garbage collection with default settings
    enable_auto_gc()
    
    # Create some data that will be tracked
    large_data = []
    for i in range(10000):
        data = [x * x for x in range(100)]
        large_data.append(data)
        
        # Track the allocation
        track_allocation("large_data_item", sys.getsizeof(data))
    
    print(f"Created {len(large_data)} data items")
    
    # Force garbage collection
    force_gc()
    
    # Get statistics
    stats = gc_stats()
    print(f"Memory stats: {stats['memory_stats']['current_memory_mb']:.2f} MB")
    print(f"Total allocations: {stats['memory_stats']['total_allocations']}")
    print(f"GC counts: {stats['gc_counts']}")
    
    # Clean up
    del large_data
    force_gc()
    
    # Disable auto GC
    disable_auto_gc()
    print("Auto GC disabled\n")


def example_2_custom_configuration():
    """Example 2: Custom Auto GC Configuration"""
    print("=== Example 2: Custom Auto GC Configuration ===")
    
    # Create custom configuration
    config = AutoGCConfig()
    config.aggressive_mode = True
    config.memory_threshold_mb = 256  # Lower threshold
    config.cleanup_interval = 2.0     # More frequent cleanup
    config.track_allocations = True
    config.auto_optimize = True
    
    # Enable with custom config
    enable_auto_gc(config)
    
    print("Enabled auto GC with custom config:")
    print(f"  - Aggressive mode: {config.aggressive_mode}")
    print(f"  - Memory threshold: {config.memory_threshold_mb} MB")
    print(f"  - Cleanup interval: {config.cleanup_interval} seconds")
    
    # Simulate high memory usage
    memory_intensive_data = []
    for i in range(1000):
        data = bytearray(1024 * 1024)  # 1MB per item
        memory_intensive_data.append(data)
        
        if i % 100 == 0:
            stats = gc_stats()
            print(f"  Iteration {i}: {stats['memory_stats']['current_memory_mb']:.2f} MB")
    
    # Let auto GC do its work
    time.sleep(3)
    
    # Final stats
    stats = gc_stats()
    print(f"Final memory usage: {stats['memory_stats']['current_memory_mb']:.2f} MB")
    print(f"Emergency cleanups: {stats['emergency_cleanups']}")
    
    # Clean up
    del memory_intensive_data
    disable_auto_gc()
    print("Custom auto GC disabled\n")


def example_3_managed_memory_pools():
    """Example 3: Managed Memory Pools"""
    print("=== Example 3: Managed Memory Pools ===")
    
    enable_auto_gc()
    
    # Create managed memory pool (auto-registered with GC)
    pool = ManagedMemoryPool(block_size=4096, max_blocks=1000)
    
    print("Created managed memory pool:")
    print(f"  - Block size: {pool.block_size} bytes")
    print(f"  - Max blocks: {pool.max_blocks}")
    
    # Use the pool in a multi-threaded scenario
    def worker_thread(thread_id):
        allocated_blocks = []
        
        for i in range(100):
            # Allocate block
            block = pool.allocate()
            allocated_blocks.append(block)
            
            # Use the block
            block[0:10] = f"Thread{thread_id}_{i}".encode()[:10]
            
            # Occasionally return blocks to pool
            if i % 10 == 0 and allocated_blocks:
                pool.deallocate(allocated_blocks.pop(0))
        
        # Return remaining blocks
        for block in allocated_blocks:
            pool.deallocate(block)
    
    # Run multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker_thread, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Check pool stats
    stats = pool.stats()
    print("Pool stats after threading:")
    print(f"  - Allocated blocks: {stats['allocated_blocks']}")
    print(f"  - Available blocks: {stats['available_blocks']}")
    print(f"  - Total memory: {stats['total_memory_bytes'] / 1024:.2f} KB")
    
    # Force cleanup
    force_gc()
    
    # Check stats after cleanup
    stats = pool.stats()
    print("Pool stats after cleanup:")
    print(f"  - Available blocks: {stats['available_blocks']}")
    
    disable_auto_gc()
    print("Managed memory pool example completed\n")


def example_4_memory_mapped_arrays():
    """Example 4: Auto-managed Memory-Mapped Arrays"""
    print("=== Example 4: Auto-managed Memory-Mapped Arrays ===")
    
    enable_auto_gc()
    
    # Create temporary files for memory mapping
    temp_files = []
    arrays = []
    
    try:
        for i in range(3):
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as f:
                filepath = f.name
                temp_files.append(filepath)
            
            # Create managed memory-mapped array
            arr = create_managed_mmap(
                filepath, 
                size=100000, 
                dtype="float64", 
                mode="w+"
            )
            arrays.append(arr)
            
            # Fill with data
            arr[:] = [x * (i + 1) for x in range(100000)]
            
            print(f"Created mmap array {i+1}: {filepath}")
            print(f"  - Size: {arr.shape}")
            print(f"  - First 5 values: {arr[:5]}")
        
        # Check GC stats
        stats = gc_stats()
        print(f"Registered mmap files: {stats['resource_counts']['mmap_files']}")
        
        # Process arrays with parallel operations
        def process_array(arr):
            return arr.sum()
        
        # Use parallel processing
        results = parallel_map(process_array, arrays)
        print(f"Array sums: {results}")
        
        # Force cleanup
        force_gc()
        
    finally:
        # Clean up arrays and files
        for arr in arrays:
            del arr
        
        for filepath in temp_files:
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    disable_auto_gc()
    print("Memory-mapped array example completed\n")


def example_5_context_manager():
    """Example 5: Using Managed Memory Context"""
    print("=== Example 5: Using Managed Memory Context ===")
    
    # Use context manager for automatic GC management
    with managed_memory() as auto_gc:
        print("Inside managed memory context")
        
        # Create lots of temporary data
        temp_data = []
        for i in range(1000):
            data = [x ** 2 for x in range(100)]
            temp_data.append(data)
            
            # Track allocation
            track_allocation("temp_data", sys.getsizeof(data))
        
        # Get stats within context
        stats = auto_gc.get_stats()
        print(f"Memory usage: {stats['memory_stats']['current_memory_mb']:.2f} MB")
        print(f"Total allocations: {stats['memory_stats']['total_allocations']}")
        
        # Process data
        processed = parallel_map(lambda x: sum(x), temp_data)
        print(f"Processed {len(processed)} items")
        
        # Memory will be automatically managed on exit
    
    print("Exited managed memory context (automatic cleanup performed)\n")


def example_6_decorator_usage():
    """Example 6: Using Auto GC Decorator"""
    print("=== Example 6: Using Auto GC Decorator ===")
    
    @auto_gc_decorator
    def memory_intensive_function(size):
        """Function that uses lots of memory."""
        print(f"  Processing {size} items...")
        
        # Create large data structures
        data = []
        for i in range(size):
            item = {
                'id': i,
                'values': [x * i for x in range(100)],
                'metadata': f"Item {i} with lots of data"
            }
            data.append(item)
            
            # Track allocation
            track_allocation("function_data", sys.getsizeof(item))
        
        # Process data
        result = sum(len(item['values']) for item in data)
        
        print(f"  Processed data, result: {result}")
        return result
    
    # Call decorated function multiple times
    results = []
    for i in range(5):
        result = memory_intensive_function(1000 + i * 500)
        results.append(result)
    
    print(f"Function results: {results}")
    print("Auto GC decorator handled memory management automatically\n")


def example_7_custom_cleanup_callbacks():
    """Example 7: Custom Cleanup Callbacks"""
    print("=== Example 7: Custom Cleanup Callbacks ===")
    
    enable_auto_gc()
    
    # Global resources to track
    global_resources = {
        'file_handles': [],
        'network_connections': [],
        'cached_data': {}
    }
    
    def cleanup_file_handles():
        """Custom cleanup for file handles."""
        closed_count = 0
        for handle in global_resources['file_handles']:
            if not handle.closed:
                handle.close()
                closed_count += 1
        global_resources['file_handles'].clear()
        print(f"  Cleanup: Closed {closed_count} file handles")
    
    def cleanup_cached_data():
        """Custom cleanup for cached data."""
        cache_size = len(global_resources['cached_data'])
        global_resources['cached_data'].clear()
        print(f"  Cleanup: Cleared {cache_size} cached items")
    
    # Register custom cleanup callbacks
    register_cleanup_callback(cleanup_file_handles)
    register_cleanup_callback(cleanup_cached_data)
    
    # Create resources that need cleanup
    for i in range(10):
        # Create file handles
        f = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        f.write(f"Test data {i}")
        global_resources['file_handles'].append(f)
        
        # Create cached data
        global_resources['cached_data'][f"key_{i}"] = f"Large cached value {i}" * 100
    
    print(f"Created {len(global_resources['file_handles'])} file handles")
    print(f"Created {len(global_resources['cached_data'])} cached items")
    
    # Force cleanup (will trigger our custom callbacks)
    print("Forcing cleanup...")
    force_gc()
    
    # Check resources after cleanup
    print(f"Remaining file handles: {len(global_resources['file_handles'])}")
    print(f"Remaining cached items: {len(global_resources['cached_data'])}")
    
    disable_auto_gc()
    print("Custom cleanup callbacks example completed\n")


def example_8_performance_monitoring():
    """Example 8: Performance Monitoring with Auto GC"""
    print("=== Example 8: Performance Monitoring with Auto GC ===")
    
    # Enable auto GC with profiling
    config = AutoGCConfig()
    config.profile_gc = True
    config.track_allocations = True
    enable_auto_gc(config)
    
    # Create profiler for additional monitoring
    profiler = Profiler()
    
    def performance_test():
        """Test function with performance monitoring."""
        profiler.start_timer("performance_test")
        
        # Phase 1: Memory allocation
        profiler.start_timer("allocation_phase")
        large_structures = []
        for i in range(1000):
            structure = {
                'data': [x ** 2 for x in range(100)],
                'metadata': f"Structure {i}",
                'timestamp': time.time()
            }
            large_structures.append(structure)
            track_allocation("performance_structure", sys.getsizeof(structure))
        
        profiler.stop_timer("allocation_phase")
        
        # Phase 2: Processing
        profiler.start_timer("processing_phase")
        results = parallel_map(
            lambda s: sum(s['data']), 
            large_structures
        )
        profiler.stop_timer("processing_phase")
        
        # Phase 3: Cleanup
        profiler.start_timer("cleanup_phase")
        del large_structures
        force_gc()
        profiler.stop_timer("cleanup_phase")
        
        profiler.stop_timer("performance_test")
        return results
    
    # Run performance test
    print("Running performance test...")
    results = performance_test()
    
    # Get comprehensive stats
    gc_stats_data = gc_stats()
    profiler_stats = profiler.get_report()
    
    print("Performance Results:")
    print(f"  - Processed {len(results)} items")
    print(f"  - Current memory: {gc_stats_data['memory_stats']['current_memory_mb']:.2f} MB")
    print(f"  - Total allocations: {gc_stats_data['memory_stats']['total_allocations']}")
    print(f"  - GC collections: {gc_stats_data['gc_counts']}")
    
    print("Timing Results:")
    for operation, duration in profiler_stats['timings'].items():
        print(f"  - {operation}: {duration:.3f}s")
    
    disable_auto_gc()
    print("Performance monitoring example completed\n")


def example_9_integration_with_parallel_processing():
    """Example 9: Integration with Parallel Processing"""
    print("=== Example 9: Integration with Parallel Processing ===")
    
    # Configure auto GC for parallel processing
    config = AutoGCConfig()
    config.aggressive_mode = True  # More aggressive cleanup for parallel workloads
    config.memory_threshold_mb = 512
    config.thread_safe = True
    enable_auto_gc(config)
    
    # Create managed memory pool for parallel workers
    worker_pool = ManagedMemoryPool(block_size=8192, max_blocks=500)
    
    def parallel_worker(data_chunk):
        """Worker function that processes data chunks."""
        # Allocate working memory from pool
        work_buffer = worker_pool.allocate()
        
        try:
            # Process the chunk
            result = []
            for item in data_chunk:
                # Use work buffer for intermediate calculations
                work_buffer[0:len(str(item))] = str(item * item).encode()[:len(str(item))]
                result.append(item * item)
            
            # Track allocation for monitoring
            track_allocation("parallel_result", sys.getsizeof(result))
            
            return sum(result)
        finally:
            # Return buffer to pool
            worker_pool.deallocate(work_buffer)
    
    # Create large dataset
    print("Creating large dataset for parallel processing...")
    large_dataset = list(range(100000))
    
    # Split into chunks for parallel processing
    chunk_size = 1000
    chunks = [large_dataset[i:i+chunk_size] for i in range(0, len(large_dataset), chunk_size)]
    
    print(f"Processing {len(chunks)} chunks in parallel...")
    
    # Process chunks in parallel
    start_time = time.time()
    results = parallel_map(parallel_worker, chunks)
    end_time = time.time()
    
    print(f"Parallel processing completed in {end_time - start_time:.2f} seconds")
    print(f"Processed {len(results)} chunks, total result: {sum(results)}")
    
    # Check final stats
    stats = gc_stats()
    pool_stats = worker_pool.stats()
    
    print("Final Statistics:")
    print(f"  - Memory usage: {stats['memory_stats']['current_memory_mb']:.2f} MB")
    print(f"  - Total allocations: {stats['memory_stats']['total_allocations']}")
    print(f"  - Pool allocated blocks: {pool_stats['allocated_blocks']}")
    print(f"  - Pool available blocks: {pool_stats['available_blocks']}")
    print(f"  - Emergency cleanups: {stats['emergency_cleanups']}")
    
    disable_auto_gc()
    print("Parallel processing integration example completed\n")


def example_10_advanced_configuration():
    """Example 10: Advanced Configuration and Optimization"""
    print("=== Example 10: Advanced Configuration and Optimization ===")
    
    # Create highly customized configuration
    config = AutoGCConfig()
    config.enabled = True
    config.aggressive_mode = False
    config.memory_threshold_mb = 1024
    config.memory_threshold_percent = 85
    config.cleanup_interval = 3.0
    config.generation_thresholds = (1000, 15, 15)  # Custom GC thresholds
    config.track_allocations = True
    config.profile_gc = True
    config.auto_optimize = True
    config.weak_ref_cleanup = True
    config.memory_pool_management = True
    config.mmap_file_cleanup = True
    config.thread_safe = True
    config.emergency_threshold_mb = 2048
    config.max_cleanup_time = 15.0
    
    enable_auto_gc(config)
    
    print("Advanced Auto GC Configuration:")
    print(f"  - Memory threshold: {config.memory_threshold_mb} MB ({config.memory_threshold_percent}%)")
    print(f"  - Cleanup interval: {config.cleanup_interval} seconds")
    print(f"  - GC thresholds: {config.generation_thresholds}")
    print(f"  - Emergency threshold: {config.emergency_threshold_mb} MB")
    print(f"  - Max cleanup time: {config.max_cleanup_time} seconds")
    
    # Simulate complex workload
    print("\nSimulating complex workload...")
    
    # Create multiple types of resources
    memory_pools = []
    mmap_arrays = []
    temp_files = []
    
    try:
        # Create memory pools
        for i in range(3):
            pool = ManagedMemoryPool(block_size=2048 * (i + 1), max_blocks=200)
            memory_pools.append(pool)
        
        # Create memory-mapped arrays
        for i in range(2):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                filepath = f.name
                temp_files.append(filepath)
            
            arr = create_managed_mmap(filepath, size=50000, dtype="float32", mode="w+")
            arr[:] = [x * 0.5 for x in range(50000)]
            mmap_arrays.append(arr)
        
        # Simulate workload with mixed resource usage
        for iteration in range(10):
            print(f"  Iteration {iteration + 1}/10")
            
            # Use memory pools
            allocated_blocks = []
            for pool in memory_pools:
                for _ in range(50):
                    block = pool.allocate()
                    allocated_blocks.append((pool, block))
            
            # Process memory-mapped arrays
            for arr in mmap_arrays:
                result = arr.sum()
                track_allocation("mmap_processing", sys.getsizeof(result))
            
            # Create temporary data
            temp_data = [list(range(1000)) for _ in range(100)]
            for data in temp_data:
                track_allocation("temp_processing", sys.getsizeof(data))
            
            # Return blocks to pools
            for pool, block in allocated_blocks:
                pool.deallocate(block)
            
            # Check stats periodically
            if iteration % 3 == 0:
                stats = gc_stats()
                print(f"    Memory: {stats['memory_stats']['current_memory_mb']:.2f} MB")
                print(f"    Allocations: {stats['memory_stats']['total_allocations']}")
        
        # Final optimization and cleanup
        print("\nPerforming final optimization...")
        force_gc()
        
        # Get comprehensive final stats
        final_stats = gc_stats()
        
        print("Final Advanced Configuration Results:")
        print(f"  - Peak memory: {final_stats['memory_stats']['peak_memory_mb']:.2f} MB")
        print(f"  - Current memory: {final_stats['memory_stats']['current_memory_mb']:.2f} MB")
        print(f"  - Total allocations: {final_stats['memory_stats']['total_allocations']}")
        print(f"  - Total deallocations: {final_stats['memory_stats']['total_deallocations']}")
        print(f"  - Emergency cleanups: {final_stats['emergency_cleanups']}")
        print(f"  - Cleanup stats: {final_stats['cleanup_stats']}")
        
        # Resource counts
        resource_counts = final_stats['resource_counts']
        print(f"  - Managed memory pools: {resource_counts['memory_pools']}")
        print(f"  - Managed mmap files: {resource_counts['mmap_files']}")
        print(f"  - Cleanup callbacks: {resource_counts['cleanup_callbacks']}")
        
    finally:
        # Clean up resources
        for arr in mmap_arrays:
            del arr
        for filepath in temp_files:
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    disable_auto_gc()
    print("Advanced configuration example completed\n")


def run_all_examples():
    """Run all auto GC examples."""
    print("=" * 60)
    print("PYFERRIS AUTO GARBAGE COLLECTION EXAMPLES")
    print("=" * 60)
    print()
    
    examples = [
        example_1_basic_auto_gc,
        example_2_custom_configuration,
        example_3_managed_memory_pools,
        example_4_memory_mapped_arrays,
        example_5_context_manager,
        example_6_decorator_usage,
        example_7_custom_cleanup_callbacks,
        example_8_performance_monitoring,
        example_9_integration_with_parallel_processing,
        example_10_advanced_configuration
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"Example {i} failed: {e}")
            print()
    
    print("=" * 60)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
