# Shared Memory Operations

PyFerris provides powerful shared memory capabilities that enable efficient data sharing between parallel workers without the overhead of serialization and inter-process communication. This is particularly useful for large datasets and memory-intensive computations.

## Table of Contents

1. [Overview](#overview)
2. [Shared Arrays](#shared-arrays)
3. [Shared Dictionaries](#shared-dictionaries)
4. [Memory Pools](#memory-pools)
5. [Advanced Patterns](#advanced-patterns)
6. [Performance Optimization](#performance-optimization)
7. [Memory Safety](#memory-safety)
8. [Real-world Examples](#real-world-examples)

## Overview

Shared memory in PyFerris allows multiple workers to access the same memory region directly, enabling:
- Zero-copy data sharing between processes
- Efficient processing of large datasets
- Reduced memory footprint for parallel operations
- High-performance numerical computations

### Key Components

- **SharedArray**: Numpy-compatible shared arrays
- **SharedDict**: Thread-safe shared dictionaries
- **MemoryPool**: Managed memory allocation
- **SharedBuffer**: Low-level shared memory buffers

## Shared Arrays

Shared arrays provide numpy-compatible arrays that can be accessed by multiple processes simultaneously.

### Basic Shared Array Usage

```python
import numpy as np
from pyferris import SharedArray, parallel_map

# Create a shared array
shared_data = SharedArray((1000, 1000), dtype=np.float64)

# Initialize with data
shared_data[:] = np.random.rand(1000, 1000)

def process_chunk(chunk_info):
    """Process a chunk of the shared array."""
    start_row, end_row = chunk_info
    
    # Access the shared array directly
    chunk = shared_data[start_row:end_row]
    
    # Perform computation (e.g., apply mathematical operation)
    result = np.mean(chunk, axis=1)
    
    # Can also modify in-place
    shared_data[start_row:end_row] *= 1.1
    
    return result

# Define chunks for parallel processing
chunk_size = 100
chunks = [(i, min(i + chunk_size, 1000)) for i in range(0, 1000, chunk_size)]

# Process chunks in parallel
results = parallel_map(process_chunk, chunks, max_workers=4)

print(f"Processed {len(list(results))} chunks")
print(f"Final array mean: {np.mean(shared_data):.4f}")
```

### Shared Array with Different Data Types

```python
import numpy as np
from pyferris import SharedArray, parallel_map

class SharedArrayProcessor:
    def __init__(self):
        self.arrays = {}
    
    def create_arrays(self, size):
        """Create shared arrays of different types."""
        
        self.arrays['float32'] = SharedArray((size,), dtype=np.float32)
        self.arrays['float64'] = SharedArray((size,), dtype=np.float64)
        self.arrays['int32'] = SharedArray((size,), dtype=np.int32)
        self.arrays['int64'] = SharedArray((size,), dtype=np.int64)
        self.arrays['bool'] = SharedArray((size,), dtype=np.bool_)
        
        # Initialize with test data
        self.arrays['float32'][:] = np.random.rand(size).astype(np.float32)
        self.arrays['float64'][:] = np.random.rand(size)
        self.arrays['int32'][:] = np.random.randint(0, 100, size, dtype=np.int32)
        self.arrays['int64'][:] = np.random.randint(0, 1000, size, dtype=np.int64)
        self.arrays['bool'][:] = np.random.choice([True, False], size)
    
    def process_array_segment(self, segment_info):
        """Process a segment of all arrays."""
        array_type, start, end = segment_info
        
        array = self.arrays[array_type]
        segment = array[start:end]
        
        if array_type in ['float32', 'float64']:
            # Statistical operations for float arrays
            result = {
                'type': array_type,
                'mean': np.mean(segment),
                'std': np.std(segment),
                'min': np.min(segment),
                'max': np.max(segment)
            }
        elif array_type in ['int32', 'int64']:
            # Operations for integer arrays
            result = {
                'type': array_type,
                'sum': np.sum(segment),
                'median': np.median(segment),
                'unique_count': len(np.unique(segment))
            }
        else:  # bool
            # Operations for boolean arrays
            result = {
                'type': array_type,
                'true_count': np.sum(segment),
                'false_count': len(segment) - np.sum(segment),
                'true_ratio': np.mean(segment)
            }
        
        return result

def shared_array_types_example():
    """Example working with different shared array types."""
    
    processor = SharedArrayProcessor()
    size = 10000
    processor.create_arrays(size)
    
    # Create segments for each array type
    segment_size = 1000
    segments = []
    
    for array_type in processor.arrays.keys():
        for i in range(0, size, segment_size):
            end = min(i + segment_size, size)
            segments.append((array_type, i, end))
    
    print(f"Processing {len(segments)} segments across different data types...")
    
    # Process all segments in parallel
    results = parallel_map(processor.process_array_segment, segments)
    results = list(results)
    
    # Organize results by type
    type_results = {}
    for result in results:
        array_type = result['type']
        if array_type not in type_results:
            type_results[array_type] = []
        type_results[array_type].append(result)
    
    # Display summary
    for array_type, type_data in type_results.items():
        print(f"\n{array_type.upper()} Array Results:")
        if array_type in ['float32', 'float64']:
            overall_mean = np.mean([r['mean'] for r in type_data])
            overall_std = np.mean([r['std'] for r in type_data])
            print(f"  Overall mean: {overall_mean:.4f}")
            print(f"  Average std: {overall_std:.4f}")
        elif array_type in ['int32', 'int64']:
            total_sum = sum([r['sum'] for r in type_data])
            avg_unique = np.mean([r['unique_count'] for r in type_data])
            print(f"  Total sum: {total_sum}")
            print(f"  Average unique count: {avg_unique:.1f}")
        else:  # bool
            total_true = sum([r['true_count'] for r in type_data])
            overall_ratio = np.mean([r['true_ratio'] for r in type_data])
            print(f"  Total true values: {total_true}")
            print(f"  Overall true ratio: {overall_ratio:.3f}")

shared_array_types_example()
```

### Multi-dimensional Shared Arrays

```python
import numpy as np
from pyferris import SharedArray, parallel_map

class ImageProcessor:
    def __init__(self, width, height, channels=3):
        self.width = width
        self.height = height
        self.channels = channels
        
        # Create shared array for image data
        self.image = SharedArray((height, width, channels), dtype=np.uint8)
        
        # Create shared arrays for intermediate processing
        self.grayscale = SharedArray((height, width), dtype=np.float32)
        self.filtered = SharedArray((height, width), dtype=np.float32)
    
    def generate_test_image(self):
        """Generate a test image."""
        # Create a gradient pattern
        y, x = np.ogrid[:self.height, :self.width]
        
        # RGB channels with different patterns
        self.image[:, :, 0] = (x * 255 // self.width).astype(np.uint8)  # Red gradient
        self.image[:, :, 1] = (y * 255 // self.height).astype(np.uint8)  # Green gradient
        self.image[:, :, 2] = ((x + y) * 255 // (self.width + self.height)).astype(np.uint8)  # Blue gradient
    
    def convert_to_grayscale_chunk(self, row_range):
        """Convert a chunk of the image to grayscale."""
        start_row, end_row = row_range
        
        # Convert RGB to grayscale using standard formula
        rgb_chunk = self.image[start_row:end_row].astype(np.float32)
        gray_chunk = (0.299 * rgb_chunk[:, :, 0] + 
                     0.587 * rgb_chunk[:, :, 1] + 
                     0.114 * rgb_chunk[:, :, 2])
        
        # Store in shared grayscale array
        self.grayscale[start_row:end_row] = gray_chunk
        
        return end_row - start_row  # Return number of rows processed
    
    def apply_filter_chunk(self, row_range):
        """Apply a simple filter to a chunk of the grayscale image."""
        start_row, end_row = row_range
        
        # Simple edge detection filter (Sobel-like)
        chunk = self.grayscale[max(0, start_row-1):min(self.height, end_row+1)]
        
        if chunk.shape[0] < 3:
            return 0
        
        # Apply horizontal gradient
        filtered_chunk = np.zeros((end_row - start_row, self.width))
        
        for i in range(1, chunk.shape[0] - 1):
            output_row = i - 1 + start_row
            if output_row < start_row or output_row >= end_row:
                continue
            
            # Simple edge detection
            for j in range(1, self.width - 1):
                gx = (chunk[i-1, j+1] - chunk[i-1, j-1] + 
                     2 * (chunk[i, j+1] - chunk[i, j-1]) + 
                     chunk[i+1, j+1] - chunk[i+1, j-1])
                
                gy = (chunk[i-1, j-1] - chunk[i+1, j-1] + 
                     2 * (chunk[i-1, j] - chunk[i+1, j]) + 
                     chunk[i-1, j+1] - chunk[i+1, j+1])
                
                filtered_chunk[output_row - start_row, j] = np.sqrt(gx*gx + gy*gy)
        
        # Store in shared filtered array
        self.filtered[start_row:end_row] = filtered_chunk
        
        return end_row - start_row

def image_processing_example():
    """Example of parallel image processing with shared arrays."""
    
    # Create image processor
    processor = ImageProcessor(800, 600)
    processor.generate_test_image()
    
    print(f"Processing {processor.width}x{processor.height} image...")
    
    # Define row chunks for parallel processing
    chunk_size = 50
    row_ranges = []
    for i in range(0, processor.height, chunk_size):
        end = min(i + chunk_size, processor.height)
        row_ranges.append((i, end))
    
    # Stage 1: Convert to grayscale in parallel
    print("Stage 1: Converting to grayscale...")
    gray_results = parallel_map(
        processor.convert_to_grayscale_chunk, 
        row_ranges, 
        max_workers=4
    )
    total_gray_rows = sum(gray_results)
    print(f"Converted {total_gray_rows} rows to grayscale")
    
    # Stage 2: Apply edge detection filter in parallel
    print("Stage 2: Applying edge detection filter...")
    filter_results = parallel_map(
        processor.apply_filter_chunk, 
        row_ranges, 
        max_workers=4
    )
    total_filtered_rows = sum(filter_results)
    print(f"Filtered {total_filtered_rows} rows")
    
    # Calculate statistics
    original_stats = {
        'mean_r': np.mean(processor.image[:, :, 0]),
        'mean_g': np.mean(processor.image[:, :, 1]),
        'mean_b': np.mean(processor.image[:, :, 2])
    }
    
    grayscale_stats = {
        'mean': np.mean(processor.grayscale),
        'std': np.std(processor.grayscale),
        'min': np.min(processor.grayscale),
        'max': np.max(processor.grayscale)
    }
    
    filtered_stats = {
        'mean': np.mean(processor.filtered),
        'std': np.std(processor.filtered),
        'min': np.min(processor.filtered),
        'max': np.max(processor.filtered)
    }
    
    print(f"\nImage Statistics:")
    print(f"Original RGB means: R={original_stats['mean_r']:.1f}, G={original_stats['mean_g']:.1f}, B={original_stats['mean_b']:.1f}")
    print(f"Grayscale: mean={grayscale_stats['mean']:.1f}, std={grayscale_stats['std']:.1f}")
    print(f"Filtered: mean={filtered_stats['mean']:.1f}, std={filtered_stats['std']:.1f}")

image_processing_example()
```

## Shared Dictionaries

Shared dictionaries enable thread-safe key-value storage that can be accessed by multiple workers.

### Basic Shared Dictionary

```python
from pyferris import SharedDict, parallel_map
import time

# Create shared dictionary
shared_cache = SharedDict()

def worker_with_cache(worker_id):
    """Worker function that uses shared cache."""
    
    # Check if result is already cached
    cache_key = f"result_{worker_id}"
    
    if cache_key in shared_cache:
        print(f"Worker {worker_id}: Cache hit!")
        return shared_cache[cache_key]
    
    # Simulate expensive computation
    time.sleep(0.1)
    result = worker_id ** 2
    
    # Store in cache
    shared_cache[cache_key] = result
    print(f"Worker {worker_id}: Computed and cached result")
    
    return result

def shared_dict_example():
    """Example of using shared dictionary as cache."""
    
    worker_ids = list(range(10)) * 2  # Duplicate work to demonstrate caching
    
    print("First run (no cache):")
    start_time = time.time()
    results1 = parallel_map(worker_with_cache, worker_ids, max_workers=4)
    time1 = time.time() - start_time
    
    print(f"\nFirst run completed in {time1:.2f}s")
    print(f"Cache contents: {dict(shared_cache)}")
    
    print(f"\nSecond run (with cache):")
    start_time = time.time()
    results2 = parallel_map(worker_with_cache, worker_ids, max_workers=4)
    time2 = time.time() - start_time
    
    print(f"Second run completed in {time2:.2f}s")
    print(f"Speedup: {time1/time2:.2f}x")

shared_dict_example()
```

### Advanced Shared Dictionary Operations

```python
from pyferris import SharedDict, parallel_map
import threading
import time
import json

class SharedCounter:
    def __init__(self, shared_dict, key):
        self.shared_dict = shared_dict
        self.key = key
        self.lock = threading.Lock()
        
        # Initialize counter if it doesn't exist
        if key not in shared_dict:
            shared_dict[key] = 0
    
    def increment(self, amount=1):
        """Thread-safe increment."""
        with self.lock:
            current = self.shared_dict[key]
            self.shared_dict[key] = current + amount
            return self.shared_dict[key]
    
    def get(self):
        """Get current value."""
        return self.shared_dict[key]

class SharedMetrics:
    def __init__(self):
        self.shared_data = SharedDict()
        self.counters = {}
        self.lock = threading.Lock()
    
    def get_counter(self, name):
        """Get or create a named counter."""
        if name not in self.counters:
            with self.lock:
                if name not in self.counters:
                    self.counters[name] = SharedCounter(self.shared_data, f"counter_{name}")
        return self.counters[name]
    
    def set_metric(self, name, value):
        """Set a metric value."""
        self.shared_data[f"metric_{name}"] = value
    
    def get_metric(self, name):
        """Get a metric value."""
        return self.shared_data.get(f"metric_{name}")
    
    def add_to_list(self, list_name, item):
        """Add item to a shared list."""
        list_key = f"list_{list_name}"
        
        if list_key not in self.shared_data:
            self.shared_data[list_key] = []
        
        current_list = self.shared_data[list_key]
        current_list.append(item)
        self.shared_data[list_key] = current_list
    
    def get_summary(self):
        """Get summary of all metrics."""
        summary = {}
        for key, value in self.shared_data.items():
            if key.startswith('counter_'):
                name = key.replace('counter_', '')
                summary[f"counter_{name}"] = value
            elif key.startswith('metric_'):
                name = key.replace('metric_', '')
                summary[f"metric_{name}"] = value
            elif key.startswith('list_'):
                name = key.replace('list_', '')
                summary[f"list_{name}"] = len(value) if isinstance(value, list) else value
        
        return summary

# Global metrics instance
metrics = SharedMetrics()

def data_processing_worker(data_chunk):
    """Worker that processes data and updates shared metrics."""
    
    start_time = time.time()
    
    # Get counters
    processed_counter = metrics.get_counter('items_processed')
    error_counter = metrics.get_counter('errors')
    
    processed_items = 0
    errors = 0
    
    for item in data_chunk:
        try:
            # Simulate processing
            time.sleep(0.01)
            
            # Simulate occasional errors
            if item % 50 == 0:
                raise ValueError(f"Simulated error for item {item}")
            
            processed_items += 1
            processed_counter.increment()
            
            # Add successful items to results list
            metrics.add_to_list('successful_items', item)
            
        except Exception as e:
            errors += 1
            error_counter.increment()
            metrics.add_to_list('error_items', item)
    
    # Record processing time
    processing_time = time.time() - start_time
    worker_id = threading.current_thread().ident
    metrics.set_metric(f'worker_{worker_id}_time', processing_time)
    
    return {
        'worker_id': worker_id,
        'processed': processed_items,
        'errors': errors,
        'time': processing_time
    }

def shared_metrics_example():
    """Example of using shared dictionary for metrics collection."""
    
    # Create data chunks
    all_data = list(range(500))
    chunk_size = 50
    data_chunks = [all_data[i:i+chunk_size] for i in range(0, len(all_data), chunk_size)]
    
    print(f"Processing {len(all_data)} items in {len(data_chunks)} chunks...")
    
    start_time = time.time()
    
    # Process chunks in parallel
    worker_results = parallel_map(
        data_processing_worker, 
        data_chunks, 
        max_workers=6
    )
    
    total_time = time.time() - start_time
    
    # Get final metrics
    final_metrics = metrics.get_summary()
    
    print(f"\nProcessing completed in {total_time:.2f}s")
    print(f"Total items processed: {final_metrics.get('counter_items_processed', 0)}")
    print(f"Total errors: {final_metrics.get('counter_errors', 0)}")
    print(f"Successful items list length: {final_metrics.get('list_successful_items', 0)}")
    print(f"Error items list length: {final_metrics.get('list_error_items', 0)}")
    
    # Show worker timing
    worker_times = []
    for key, value in final_metrics.items():
        if key.startswith('metric_worker_') and key.endswith('_time'):
            worker_times.append(value)
    
    if worker_times:
        print(f"Worker times: avg={np.mean(worker_times):.3f}s, min={min(worker_times):.3f}s, max={max(worker_times):.3f}s")

shared_metrics_example()
```

## Memory Pools

Memory pools provide efficient allocation and reuse of shared memory buffers.

### Basic Memory Pool Usage

```python
import numpy as np
from pyferris import MemoryPool, parallel_map

class ManagedArrayProcessor:
    def __init__(self, pool_size=10, array_size=(1000, 1000)):
        self.array_size = array_size
        self.element_count = np.prod(array_size)
        
        # Create memory pool
        self.pool = MemoryPool(
            buffer_size=self.element_count * 8,  # 8 bytes per float64
            pool_size=pool_size
        )
    
    def get_array_buffer(self):
        """Get an array buffer from the pool."""
        buffer = self.pool.get_buffer()
        # Create numpy array view of the buffer
        array = np.frombuffer(buffer, dtype=np.float64).reshape(self.array_size)
        return array, buffer
    
    def return_array_buffer(self, buffer):
        """Return array buffer to the pool."""
        self.pool.return_buffer(buffer)
    
    def process_with_pool(self, task_id):
        """Process data using pooled memory."""
        
        # Get buffer from pool
        array, buffer = self.get_array_buffer()
        
        try:
            # Fill with random data
            array[:] = np.random.rand(*self.array_size)
            
            # Perform computation
            result = {
                'task_id': task_id,
                'mean': np.mean(array),
                'std': np.std(array),
                'min': np.min(array),
                'max': np.max(array),
                'sum': np.sum(array)
            }
            
            return result
        
        finally:
            # Always return buffer to pool
            self.return_array_buffer(buffer)

def memory_pool_example():
    """Example of using memory pools for efficient array processing."""
    
    processor = ManagedArrayProcessor(pool_size=5, array_size=(500, 500))
    
    # Process many tasks with limited memory
    task_ids = list(range(20))  # More tasks than pool size
    
    print(f"Processing {len(task_ids)} tasks with pool size 5...")
    
    start_time = time.time()
    results = parallel_map(processor.process_with_pool, task_ids, max_workers=5)
    end_time = time.time()
    
    results = list(results)
    
    print(f"Completed {len(results)} tasks in {end_time - start_time:.2f}s")
    
    # Calculate overall statistics
    overall_stats = {
        'avg_mean': np.mean([r['mean'] for r in results]),
        'avg_std': np.mean([r['std'] for r in results]),
        'total_sum': sum([r['sum'] for r in results])
    }
    
    print(f"Overall statistics:")
    print(f"  Average mean: {overall_stats['avg_mean']:.4f}")
    print(f"  Average std: {overall_stats['avg_std']:.4f}")
    print(f"  Total sum: {overall_stats['total_sum']:.2e}")

memory_pool_example()
```

### Advanced Memory Pool with Different Buffer Sizes

```python
import numpy as np
from pyferris import MemoryPool, parallel_map
import time

class MultiSizeMemoryManager:
    def __init__(self):
        # Create pools for different buffer sizes
        self.pools = {
            'small': MemoryPool(buffer_size=1024 * 1024, pool_size=10),      # 1MB buffers
            'medium': MemoryPool(buffer_size=4 * 1024 * 1024, pool_size=5),  # 4MB buffers  
            'large': MemoryPool(buffer_size=16 * 1024 * 1024, pool_size=3),  # 16MB buffers
        }
    
    def get_optimal_buffer(self, required_size):
        """Get the smallest buffer that can accommodate the required size."""
        
        if required_size <= 1024 * 1024:
            pool_name = 'small'
        elif required_size <= 4 * 1024 * 1024:
            pool_name = 'medium'
        else:
            pool_name = 'large'
        
        buffer = self.pools[pool_name].get_buffer()
        return buffer, pool_name
    
    def return_buffer(self, buffer, pool_name):
        """Return buffer to the appropriate pool."""
        self.pools[pool_name].return_buffer(buffer)

# Global memory manager
memory_manager = MultiSizeMemoryManager()

def variable_size_processing(task_config):
    """Process data with variable memory requirements."""
    
    task_id, data_size, computation_type = task_config
    
    # Calculate required memory
    if computation_type == 'matrix':
        # Square matrix of float64 values
        side_size = int(np.sqrt(data_size))
        array_shape = (side_size, side_size)
        required_bytes = side_size * side_size * 8
    elif computation_type == 'vector':
        # Vector of float64 values
        array_shape = (data_size,)
        required_bytes = data_size * 8
    else:  # 'image'
        # 3-channel image
        side_size = int(np.sqrt(data_size / 3))
        array_shape = (side_size, side_size, 3)
        required_bytes = side_size * side_size * 3 * 8
    
    # Get appropriate buffer
    buffer, pool_name = memory_manager.get_optimal_buffer(required_bytes)
    
    try:
        # Create array view
        array = np.frombuffer(buffer, dtype=np.float64, count=np.prod(array_shape)).reshape(array_shape)
        
        # Fill with data
        array[:] = np.random.rand(*array_shape)
        
        # Perform computation based on type
        if computation_type == 'matrix':
            # Matrix operations
            eigenvalues = np.linalg.eigvals(array + array.T)  # Make symmetric
            result = {
                'task_id': task_id,
                'type': computation_type,
                'pool': pool_name,
                'shape': array_shape,
                'max_eigenvalue': np.max(np.real(eigenvalues)),
                'trace': np.trace(array)
            }
        elif computation_type == 'vector':
            # Vector operations
            result = {
                'task_id': task_id,
                'type': computation_type,
                'pool': pool_name,
                'shape': array_shape,
                'norm': np.linalg.norm(array),
                'mean': np.mean(array)
            }
        else:  # 'image'
            # Image operations
            result = {
                'task_id': task_id,
                'type': computation_type,
                'pool': pool_name,
                'shape': array_shape,
                'brightness': np.mean(array),
                'contrast': np.std(array)
            }
        
        return result
    
    finally:
        # Return buffer to pool
        memory_manager.return_buffer(buffer, pool_name)

def variable_memory_example():
    """Example of processing tasks with variable memory requirements."""
    
    # Create tasks with different memory requirements
    tasks = []
    
    # Small tasks (vectors)
    for i in range(10):
        tasks.append((i, 1000, 'vector'))
    
    # Medium tasks (small matrices)
    for i in range(10, 15):
        tasks.append((i, 10000, 'matrix'))  # 100x100 matrix
    
    # Large tasks (images)
    for i in range(15, 20):
        tasks.append((i, 30000, 'image'))  # ~100x100x3 image
    
    # Extra large tasks (large matrices)
    for i in range(20, 23):
        tasks.append((i, 250000, 'matrix'))  # 500x500 matrix
    
    print(f"Processing {len(tasks)} tasks with variable memory requirements...")
    
    start_time = time.time()
    results = parallel_map(variable_size_processing, tasks, max_workers=4)
    end_time = time.time()
    
    results = list(results)
    
    print(f"Completed in {end_time - start_time:.2f}s")
    
    # Analyze pool usage
    pool_usage = {}
    for result in results:
        pool_name = result['pool']
        if pool_name not in pool_usage:
            pool_usage[pool_name] = []
        pool_usage[pool_name].append(result)
    
    print(f"\nPool usage analysis:")
    for pool_name, pool_results in pool_usage.items():
        print(f"  {pool_name}: {len(pool_results)} tasks")
        types = [r['type'] for r in pool_results]
        type_counts = {t: types.count(t) for t in set(types)}
        print(f"    Types: {type_counts}")

variable_memory_example()
```

## Advanced Patterns

### Producer-Consumer with Shared Memory

```python
import numpy as np
from pyferris import SharedArray, SharedDict, parallel_map
import time
import threading

class SharedDataProducerConsumer:
    def __init__(self, buffer_size=1000, num_buffers=5):
        self.buffer_size = buffer_size
        self.num_buffers = num_buffers
        
        # Create shared buffers
        self.buffers = []
        for i in range(num_buffers):
            buffer = SharedArray((buffer_size,), dtype=np.float64)
            self.buffers.append(buffer)
        
        # Create shared state
        self.state = SharedDict()
        self.state['next_buffer'] = 0
        self.state['produced_count'] = 0
        self.state['consumed_count'] = 0
        self.state['finished'] = False
        
        # Create locks for synchronization
        self.buffer_lock = threading.Lock()
        self.state_lock = threading.Lock()
    
    def produce_data(self, producer_id):
        """Producer function that fills buffers with data."""
        
        items_produced = 0
        
        while items_produced < 100:  # Produce 100 items per producer
            with self.buffer_lock:
                buffer_idx = self.state['next_buffer']
                buffer = self.buffers[buffer_idx]
                
                # Generate data
                start_val = producer_id * 1000 + items_produced
                data = np.arange(start_val, start_val + self.buffer_size, dtype=np.float64)
                buffer[:] = data
                
                # Update state
                with self.state_lock:
                    self.state['next_buffer'] = (buffer_idx + 1) % self.num_buffers
                    self.state['produced_count'] += 1
                
                items_produced += 1
                
                # Small delay to simulate production time
                time.sleep(0.01)
        
        return f"Producer {producer_id} finished: {items_produced} items"
    
    def consume_data(self, consumer_id):
        """Consumer function that processes data from buffers."""
        
        items_consumed = 0
        results = []
        
        while items_consumed < 50:  # Consume 50 items per consumer
            # Find a buffer with data
            buffer_found = False
            
            for buffer_idx in range(self.num_buffers):
                buffer = self.buffers[buffer_idx]
                
                # Process the buffer
                result = {
                    'consumer_id': consumer_id,
                    'buffer_idx': buffer_idx,
                    'mean': np.mean(buffer),
                    'sum': np.sum(buffer),
                    'std': np.std(buffer)
                }
                
                results.append(result)
                items_consumed += 1
                buffer_found = True
                
                with self.state_lock:
                    self.state['consumed_count'] += 1
                
                # Small delay to simulate processing time
                time.sleep(0.02)
                break
            
            if not buffer_found:
                time.sleep(0.001)  # Wait for data
        
        return {
            'consumer_id': consumer_id,
            'items_consumed': items_consumed,
            'avg_mean': np.mean([r['mean'] for r in results]),
            'total_sum': sum([r['sum'] for r in results])
        }

def producer_consumer_example():
    """Example of producer-consumer pattern with shared memory."""
    
    system = SharedDataProducerConsumer(buffer_size=1000, num_buffers=3)
    
    # Create producer and consumer tasks
    producer_tasks = [('producer', i) for i in range(2)]  # 2 producers
    consumer_tasks = [('consumer', i) for i in range(3)]  # 3 consumers
    
    def worker_dispatcher(task_info):
        task_type, task_id = task_info
        if task_type == 'producer':
            return system.produce_data(task_id)
        else:
            return system.consume_data(task_id)
    
    print("Starting producer-consumer system...")
    
    start_time = time.time()
    
    # Run producers and consumers concurrently
    all_tasks = producer_tasks + consumer_tasks
    results = parallel_map(worker_dispatcher, all_tasks, max_workers=5)
    
    end_time = time.time()
    
    results = list(results)
    
    print(f"System completed in {end_time - start_time:.2f}s")
    
    # Analyze results
    producer_results = [r for r in results if isinstance(r, str)]
    consumer_results = [r for r in results if isinstance(r, dict)]
    
    print(f"\nProducer results:")
    for result in producer_results:
        print(f"  {result}")
    
    print(f"\nConsumer results:")
    total_consumed = sum([r['items_consumed'] for r in consumer_results])
    avg_consumer_mean = np.mean([r['avg_mean'] for r in consumer_results])
    
    print(f"  Total items consumed: {total_consumed}")
    print(f"  Average consumer mean: {avg_consumer_mean:.2f}")
    
    # Final state
    print(f"\nFinal state:")
    print(f"  Items produced: {system.state['produced_count']}")
    print(f"  Items consumed: {system.state['consumed_count']}")

producer_consumer_example()
```

### Shared Memory Data Pipeline

```python
import numpy as np
from pyferris import SharedArray, SharedDict, parallel_map
import time

class SharedMemoryPipeline:
    def __init__(self, data_size=10000, num_stages=3):
        self.data_size = data_size
        self.num_stages = num_stages
        
        # Create shared arrays for each pipeline stage
        self.stage_data = []
        for i in range(num_stages + 1):  # +1 for input data
            array = SharedArray((data_size,), dtype=np.float64)
            self.stage_data.append(array)
        
        # Shared progress tracking
        self.progress = SharedDict()
        for i in range(num_stages):
            self.progress[f'stage_{i}_completed'] = 0
    
    def initialize_data(self):
        """Initialize the input data."""
        self.stage_data[0][:] = np.random.rand(self.data_size)
        print(f"Initialized input data: mean={np.mean(self.stage_data[0]):.4f}")
    
    def stage_processor(self, stage_info):
        """Process a chunk of data for a specific pipeline stage."""
        stage_id, chunk_start, chunk_end = stage_info
        
        # Get input and output arrays for this stage
        input_array = self.stage_data[stage_id]
        output_array = self.stage_data[stage_id + 1]
        
        # Get the chunk to process
        input_chunk = input_array[chunk_start:chunk_end]
        
        # Stage-specific processing
        if stage_id == 0:
            # Stage 0: Normalization
            chunk_mean = np.mean(input_chunk)
            chunk_std = np.std(input_chunk)
            if chunk_std > 0:
                processed_chunk = (input_chunk - chunk_mean) / chunk_std
            else:
                processed_chunk = input_chunk
        
        elif stage_id == 1:
            # Stage 1: Smoothing (simple moving average)
            window_size = 5
            processed_chunk = np.copy(input_chunk)
            
            for i in range(window_size, len(input_chunk) - window_size):
                start_idx = i - window_size
                end_idx = i + window_size + 1
                processed_chunk[i] = np.mean(input_chunk[start_idx:end_idx])
        
        elif stage_id == 2:
            # Stage 2: Feature extraction (local maxima)
            processed_chunk = np.zeros_like(input_chunk)
            
            for i in range(1, len(input_chunk) - 1):
                if (input_chunk[i] > input_chunk[i-1] and 
                    input_chunk[i] > input_chunk[i+1]):
                    processed_chunk[i] = input_chunk[i]
        
        else:
            # Default: pass through
            processed_chunk = input_chunk
        
        # Store processed chunk
        output_array[chunk_start:chunk_end] = processed_chunk
        
        # Update progress
        completed_key = f'stage_{stage_id}_completed'
        current = self.progress.get(completed_key, 0)
        self.progress[completed_key] = current + (chunk_end - chunk_start)
        
        return {
            'stage_id': stage_id,
            'chunk_start': chunk_start,
            'chunk_end': chunk_end,
            'input_mean': np.mean(input_chunk),
            'output_mean': np.mean(processed_chunk),
            'processing_ratio': np.mean(processed_chunk) / (np.mean(input_chunk) + 1e-10)
        }
    
    def run_pipeline(self, chunk_size=1000, max_workers=4):
        """Run the complete pipeline."""
        
        # Initialize data
        self.initialize_data()
        
        # Create chunks
        chunks = []
        for i in range(0, self.data_size, chunk_size):
            end = min(i + chunk_size, self.data_size)
            chunks.append((i, end))
        
        print(f"Running {self.num_stages} stage pipeline with {len(chunks)} chunks...")
        
        # Process each stage sequentially (stages depend on previous stage)
        for stage_id in range(self.num_stages):
            print(f"\nProcessing stage {stage_id}...")
            
            # Create tasks for this stage
            stage_tasks = [(stage_id, start, end) for start, end in chunks]
            
            start_time = time.time()
            stage_results = parallel_map(
                self.stage_processor, 
                stage_tasks, 
                max_workers=max_workers
            )
            stage_time = time.time() - start_time
            
            stage_results = list(stage_results)
            
            # Analyze stage results
            stage_stats = {
                'avg_input_mean': np.mean([r['input_mean'] for r in stage_results]),
                'avg_output_mean': np.mean([r['output_mean'] for r in stage_results]),
                'avg_ratio': np.mean([r['processing_ratio'] for r in stage_results]),
                'chunks_processed': len(stage_results),
                'processing_time': stage_time
            }
            
            print(f"  Stage {stage_id} completed in {stage_time:.2f}s")
            print(f"  Input mean: {stage_stats['avg_input_mean']:.4f}")
            print(f"  Output mean: {stage_stats['avg_output_mean']:.4f}")
            print(f"  Processing ratio: {stage_stats['avg_ratio']:.4f}")
        
        # Final analysis
        print(f"\nPipeline completed!")
        print(f"Final data statistics:")
        for i, array in enumerate(self.stage_data):
            mean_val = np.mean(array)
            std_val = np.std(array)
            print(f"  Stage {i}: mean={mean_val:.4f}, std={std_val:.4f}")

def pipeline_example():
    """Example of shared memory data pipeline."""
    
    pipeline = SharedMemoryPipeline(data_size=50000, num_stages=3)
    pipeline.run_pipeline(chunk_size=2000, max_workers=6)

pipeline_example()
```

This comprehensive shared memory guide demonstrates how to effectively use PyFerris's shared memory capabilities for zero-copy data sharing, efficient parallel processing, and complex data pipeline scenarios.

## Next Steps

- Learn about [Distributed Computing](distributed.md) for scaling shared memory operations across multiple machines  
- Explore [Performance Guide](performance.md) for shared memory optimization techniques
- Check out [Memory Management](memory.md) for advanced memory optimization strategies
