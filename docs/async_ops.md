# Async Operations

PyFerris provides comprehensive asynchronous parallel processing capabilities that allow you to combine the benefits of async/await with parallel execution, making it ideal for I/O-bound workloads and mixed async/sync operations.

## Table of Contents

1. [Overview](#overview)
2. [AsyncExecutor](#asyncexecutor)
3. [Async Parallel Operations](#async-parallel-operations)
4. [AsyncTask Management](#asynctask-management)
5. [Integration with Standard Async Code](#integration-with-standard-async-code)
6. [Performance Optimization](#performance-optimization)
7. [Error Handling](#error-handling)
8. [Real-world Examples](#real-world-examples)

## Overview

The async operations module enables you to:
- Run asynchronous functions in parallel across multiple workers
- Combine async I/O operations with CPU-intensive parallel processing
- Manage async task execution with progress tracking
- Handle mixed workloads efficiently

### Key Components

- **AsyncExecutor**: Main executor for async task management
- **async_parallel_map**: Asynchronous version of parallel_map
- **async_parallel_filter**: Asynchronous parallel filtering
- **AsyncTask**: Wrapper for individual async tasks

## AsyncExecutor

The AsyncExecutor provides advanced asynchronous task execution capabilities.

### Basic Usage

```python
import asyncio
from pyferris.async_ops import AsyncExecutor

async def async_computation(x):
    """Example async function."""
    await asyncio.sleep(0.1)  # Simulate async I/O
    return x * x

async def main():
    # Create executor
    executor = AsyncExecutor(max_workers=4)
    
    try:
        # Submit single task
        task = await executor.submit(async_computation(10))
        result = await task.result()
        print(f"Single task result: {result}")
        
        # Submit multiple tasks
        data = range(20)
        results = await executor.map(async_computation, data)
        print(f"Multiple task results: {list(results)}")
        
    finally:
        await executor.shutdown()

asyncio.run(main())
```

### Context Manager Usage

```python
import asyncio
from pyferris.async_ops import AsyncExecutor

async def async_worker(item):
    await asyncio.sleep(0.05)
    return item * 2

async def main():
    # Recommended: Use as context manager
    async with AsyncExecutor(max_workers=8) as executor:
        data = range(50)
        results = await executor.map(async_worker, data)
        print(f"Processed {len(list(results))} items")

asyncio.run(main())
```

### Advanced Configuration

```python
import asyncio
from pyferris.async_ops import AsyncExecutor

class ConfigurableAsyncProcessor:
    def __init__(self, max_workers=None, semaphore_limit=100):
        self.max_workers = max_workers
        self.semaphore_limit = semaphore_limit
    
    async def create_executor(self):
        """Create optimally configured async executor."""
        import os
        
        if self.max_workers is None:
            # For I/O-bound async work, use more workers than CPU cores
            self.max_workers = min(50, os.cpu_count() * 4)
        
        executor = AsyncExecutor(
            max_workers=self.max_workers,
            queue_size=1000,
            semaphore_limit=self.semaphore_limit
        )
        
        return executor
    
    async def process_with_backpressure(self, data, async_func):
        """Process data with backpressure control."""
        semaphore = asyncio.Semaphore(self.semaphore_limit)
        
        async def controlled_execution(item):
            async with semaphore:
                return await async_func(item)
        
        async with await self.create_executor() as executor:
            tasks = [controlled_execution(item) for item in data]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Separate successful results from exceptions
            successful = [r for r in results if not isinstance(r, Exception)]
            failed = [r for r in results if isinstance(r, Exception)]
            
            return successful, failed

# Example usage
async def flaky_async_operation(x):
    """Async operation that might fail."""
    await asyncio.sleep(0.01)
    
    if x % 10 == 0:
        raise ValueError(f"Simulated error for {x}")
    
    return x ** 2

async def main():
    processor = ConfigurableAsyncProcessor(max_workers=10, semaphore_limit=20)
    
    data = range(100)
    successful, failed = await processor.process_with_backpressure(
        data, 
        flaky_async_operation
    )
    
    print(f"Successful: {len(successful)}, Failed: {len(failed)}")

asyncio.run(main())
```

## Async Parallel Operations

### async_parallel_map

Apply an async function to every item in an iterable.

```python
import asyncio
import aiohttp
from pyferris import async_parallel_map, ProgressTracker

async def fetch_url(session, url):
    """Fetch a URL asynchronously."""
    try:
        async with session.get(url, timeout=10) as response:
            content = await response.text()
            return {
                'url': url,
                'status': response.status,
                'content_length': len(content),
                'success': True
            }
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'success': False
        }

async def fetch_multiple_urls():
    """Fetch multiple URLs in parallel."""
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/json',
        'https://httpbin.org/html',
        'https://httpbin.org/xml',
        'https://httpbin.org/get'
    ] * 4  # 20 URLs total
    
    # Create progress tracker
    tracker = ProgressTracker(total=len(urls), desc="Fetching URLs")
    
    async with aiohttp.ClientSession() as session:
        # Create partial function with session
        from functools import partial
        fetch_with_session = partial(fetch_url, session)
        
        # Execute in parallel
        results = await async_parallel_map(
            fetch_with_session, 
            urls, 
            max_workers=10,
            progress=tracker
        )
        
        return list(results)

async def main():
    results = await fetch_multiple_urls()
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"Successfully fetched: {len(successful)} URLs")
    print(f"Failed to fetch: {len(failed)} URLs")
    
    if failed:
        print("Failed URLs:")
        for result in failed:
            print(f"  {result['url']}: {result['error']}")

asyncio.run(main())
```

### async_parallel_filter

Filter items asynchronously based on an async predicate.

```python
import asyncio
import aiofiles
from pyferris import async_parallel_filter

async def file_exists_and_readable(filepath):
    """Check if file exists and is readable asynchronously."""
    try:
        async with aiofiles.open(filepath, 'r') as f:
            # Try to read first few bytes
            await f.read(100)
        return True
    except (FileNotFoundError, PermissionError, IOError):
        return False

async def validate_files():
    """Filter a list of files to find valid, readable ones."""
    
    # Create some test files
    test_files = [
        'existing_file.txt',
        'nonexistent_file.txt',
        'another_file.txt',
        '/etc/passwd',  # May exist but might not be readable
        'temp_file.txt'
    ]
    
    # Create a few actual files for testing
    for filename in ['existing_file.txt', 'another_file.txt', 'temp_file.txt']:
        try:
            async with aiofiles.open(filename, 'w') as f:
                await f.write(f"Content of {filename}\n")
        except:
            pass
    
    # Filter files asynchronously
    valid_files = await async_parallel_filter(
        file_exists_and_readable,
        test_files,
        max_workers=5
    )
    
    print(f"Valid files: {list(valid_files)}")
    
    # Cleanup
    import os
    for filename in ['existing_file.txt', 'another_file.txt', 'temp_file.txt']:
        try:
            os.remove(filename)
        except:
            pass

asyncio.run(validate_files())
```

### Complex Async Processing Pipeline

```python
import asyncio
import json
from pyferris import async_parallel_map, async_parallel_filter

class AsyncDataPipeline:
    def __init__(self, max_workers=10):
        self.max_workers = max_workers
        self.session = None
    
    async def __aenter__(self):
        import aiohttp
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_data(self, api_endpoint):
        """Fetch data from API endpoint."""
        try:
            async with self.session.get(api_endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'endpoint': api_endpoint,
                        'data': data,
                        'status': 'success'
                    }
                else:
                    return {
                        'endpoint': api_endpoint,
                        'status': 'error',
                        'error': f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                'endpoint': api_endpoint,
                'status': 'error',
                'error': str(e)
            }
    
    async def process_data(self, raw_result):
        """Process raw API result."""
        await asyncio.sleep(0.01)  # Simulate processing time
        
        if raw_result['status'] != 'success':
            return raw_result
        
        data = raw_result['data']
        
        # Extract and transform data
        processed = {
            'endpoint': raw_result['endpoint'],
            'processed_at': asyncio.get_event_loop().time(),
            'record_count': len(data) if isinstance(data, list) else 1,
            'summary': self._summarize_data(data),
            'status': 'processed'
        }
        
        return processed
    
    def _summarize_data(self, data):
        """Create summary of data."""
        if isinstance(data, dict):
            return {
                'type': 'object',
                'keys': list(data.keys())[:5],  # First 5 keys
                'total_keys': len(data)
            }
        elif isinstance(data, list):
            return {
                'type': 'array',
                'length': len(data),
                'sample': data[:2] if data else []
            }
        else:
            return {
                'type': type(data).__name__,
                'value': str(data)[:100]
            }
    
    async def is_valid_result(self, result):
        """Filter predicate for valid results."""
        await asyncio.sleep(0.001)  # Simulate async validation
        return result['status'] in ['success', 'processed']
    
    async def run_pipeline(self, endpoints):
        """Run the complete async processing pipeline."""
        
        print(f"Starting pipeline for {len(endpoints)} endpoints...")
        
        # Stage 1: Fetch data from all endpoints
        print("Stage 1: Fetching data...")
        raw_results = await async_parallel_map(
            self.fetch_data,
            endpoints,
            max_workers=self.max_workers
        )
        raw_results = list(raw_results)
        
        # Stage 2: Filter successful fetches
        print("Stage 2: Filtering successful fetches...")
        successful_fetches = await async_parallel_filter(
            self.is_valid_result,
            raw_results,
            max_workers=self.max_workers
        )
        successful_fetches = list(successful_fetches)
        
        # Stage 3: Process the data
        print("Stage 3: Processing data...")
        processed_results = await async_parallel_map(
            self.process_data,
            successful_fetches,
            max_workers=self.max_workers
        )
        processed_results = list(processed_results)
        
        print(f"Pipeline complete: {len(processed_results)} results processed")
        return processed_results

async def run_data_pipeline():
    """Example of running the async data pipeline."""
    
    # Sample API endpoints (using httpbin for testing)
    endpoints = [
        'https://httpbin.org/json',
        'https://httpbin.org/get',
        'https://httpbin.org/headers',
        'https://httpbin.org/ip',
        'https://httpbin.org/user-agent',
    ] * 3  # 15 total requests
    
    async with AsyncDataPipeline(max_workers=8) as pipeline:
        results = await pipeline.run_pipeline(endpoints)
        
        print(f"\nPipeline Results Summary:")
        for result in results[:3]:  # Show first 3 results
            print(f"  {result['endpoint']}: {result['summary']}")

asyncio.run(run_data_pipeline())
```

## AsyncTask Management

### Individual Task Control

```python
import asyncio
from pyferris.async_ops import AsyncTask

async def long_running_task(duration, task_id):
    """Simulate a long-running async task."""
    print(f"Task {task_id} starting (duration: {duration}s)")
    
    for i in range(duration):
        await asyncio.sleep(1)
        print(f"Task {task_id} progress: {i+1}/{duration}")
    
    print(f"Task {task_id} completed")
    return f"Result from task {task_id}"

async def manage_async_tasks():
    """Example of managing individual async tasks."""
    
    # Create tasks with different durations
    tasks = []
    for i in range(5):
        duration = 3 + i  # 3, 4, 5, 6, 7 seconds
        coro = long_running_task(duration, i)
        task = AsyncTask(coro)
        tasks.append(task)
    
    print("Starting 5 async tasks...")
    
    # Start all tasks
    started_tasks = await asyncio.gather(*[task.start() for task in tasks])
    
    # Monitor task completion
    completed = []
    while len(completed) < len(tasks):
        await asyncio.sleep(0.5)
        
        for i, task in enumerate(tasks):
            if i not in completed and task.done():
                try:
                    result = await task.result()
                    print(f"✓ Task {i} completed: {result}")
                    completed.append(i)
                except Exception as e:
                    print(f"✗ Task {i} failed: {e}")
                    completed.append(i)
    
    print("All tasks completed")

asyncio.run(manage_async_tasks())
```

### Task Cancellation and Timeout

```python
import asyncio
from pyferris.async_ops import AsyncExecutor, AsyncTask

async def cancellable_task(task_id, work_duration):
    """Task that can be cancelled."""
    try:
        print(f"Task {task_id} starting...")
        
        for i in range(work_duration):
            # Check for cancellation
            if asyncio.current_task().cancelled():
                print(f"Task {task_id} detected cancellation")
                break
            
            await asyncio.sleep(1)
            print(f"Task {task_id} working... ({i+1}/{work_duration})")
        
        print(f"Task {task_id} completed normally")
        return f"Success: Task {task_id}"
        
    except asyncio.CancelledError:
        print(f"Task {task_id} was cancelled")
        raise

async def timeout_and_cancellation_example():
    """Example of task timeout and cancellation."""
    
    async with AsyncExecutor(max_workers=3) as executor:
        # Submit tasks with different durations
        task1 = await executor.submit(cancellable_task(1, 3))  # 3 seconds
        task2 = await executor.submit(cancellable_task(2, 8))  # 8 seconds
        task3 = await executor.submit(cancellable_task(3, 5))  # 5 seconds
        
        try:
            # Wait for completion with timeout
            results = await asyncio.wait_for(
                asyncio.gather(
                    task1.result(),
                    task2.result(), 
                    task3.result(),
                    return_exceptions=True
                ),
                timeout=6.0  # 6 second timeout
            )
            
            print("All tasks completed within timeout")
            for i, result in enumerate(results, 1):
                if isinstance(result, Exception):
                    print(f"Task {i} failed: {result}")
                else:
                    print(f"Task {i} result: {result}")
        
        except asyncio.TimeoutError:
            print("Tasks timed out, cancelling remaining tasks...")
            
            # Cancel all tasks
            task1.cancel()
            task2.cancel()
            task3.cancel()
            
            # Wait for cancellation to complete
            await asyncio.sleep(1)
            print("Cancellation complete")

asyncio.run(timeout_and_cancellation_example())
```

## Integration with Standard Async Code

### Mixing Sync and Async Operations

```python
import asyncio
from pyferris import parallel_map
from pyferris.async_ops import async_parallel_map

def cpu_intensive_sync(n):
    """CPU-intensive synchronous function."""
    total = 0
    for i in range(n * 1000):
        total += i * i
    return total

async def io_intensive_async(url):
    """I/O-intensive asynchronous function."""
    await asyncio.sleep(0.1)  # Simulate network I/O
    return f"Data from {url}"

async def mixed_workload_processing():
    """Process mixed sync/async workloads efficiently."""
    
    # Data for different types of processing
    cpu_data = list(range(100, 200))  # Numbers for CPU work
    io_data = [f"https://api.example.com/data/{i}" for i in range(50)]
    
    print("Processing mixed workload...")
    
    # Process CPU-intensive work in parallel (sync)
    print("Stage 1: CPU-intensive processing...")
    cpu_results = list(parallel_map(cpu_intensive_sync, cpu_data))
    
    # Process I/O-intensive work asynchronously  
    print("Stage 2: I/O-intensive processing...")
    io_results = await async_parallel_map(io_intensive_async, io_data)
    io_results = list(io_results)
    
    print(f"CPU results: {len(cpu_results)} items")
    print(f"I/O results: {len(io_results)} items")
    
    return cpu_results, io_results

# Advanced: Concurrent sync and async processing
async def concurrent_mixed_processing():
    """Run sync and async processing concurrently."""
    
    cpu_data = list(range(50, 100))
    io_data = [f"url_{i}" for i in range(30)]
    
    async def run_sync_in_executor():
        """Run sync parallel processing in thread executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: list(parallel_map(cpu_intensive_sync, cpu_data))
        )
    
    # Run both sync and async processing concurrently
    cpu_task = asyncio.create_task(run_sync_in_executor())
    io_task = asyncio.create_task(async_parallel_map(io_intensive_async, io_data))
    
    # Wait for both to complete
    cpu_results, io_results = await asyncio.gather(
        cpu_task,
        io_task
    )
    
    print(f"Concurrent processing complete:")
    print(f"  CPU results: {len(cpu_results)}")
    print(f"  I/O results: {len(list(io_results))}")

# Run examples
asyncio.run(mixed_workload_processing())
print("\n" + "="*50 + "\n")
asyncio.run(concurrent_mixed_processing())
```

### Integration with asyncio.gather

```python
import asyncio
from pyferris.async_ops import async_parallel_map

async def fetch_user_data(user_id):
    """Mock async function to fetch user data."""
    await asyncio.sleep(0.1)
    return {
        'user_id': user_id,
        'name': f'User {user_id}',
        'email': f'user{user_id}@example.com'
    }

async def fetch_user_posts(user_id):
    """Mock async function to fetch user posts."""
    await asyncio.sleep(0.05)
    return [f'Post {i} by User {user_id}' for i in range(3)]

async def comprehensive_user_processing():
    """Process users with multiple async operations."""
    
    user_ids = list(range(1, 21))  # 20 users
    
    # Method 1: Sequential async operations
    print("Method 1: Sequential processing")
    start_time = asyncio.get_event_loop().time()
    
    users = await async_parallel_map(fetch_user_data, user_ids)
    posts = await async_parallel_map(fetch_user_posts, user_ids)
    
    method1_time = asyncio.get_event_loop().time() - start_time
    print(f"Sequential time: {method1_time:.2f}s")
    
    # Method 2: Concurrent async operations with gather
    print("\nMethod 2: Concurrent processing with gather")
    start_time = asyncio.get_event_loop().time()
    
    users_task = async_parallel_map(fetch_user_data, user_ids)
    posts_task = async_parallel_map(fetch_user_posts, user_ids)
    
    users, posts = await asyncio.gather(users_task, posts_task)
    
    method2_time = asyncio.get_event_loop().time() - start_time
    print(f"Concurrent time: {method2_time:.2f}s")
    print(f"Speedup: {method1_time / method2_time:.2f}x")
    
    # Combine results
    combined_data = []
    for user, user_posts in zip(users, posts):
        combined_data.append({
            **user,
            'posts': user_posts
        })
    
    print(f"\nProcessed {len(combined_data)} users with their posts")

asyncio.run(comprehensive_user_processing())
```

## Performance Optimization

### Async Pool Management

```python
import asyncio
from pyferris.async_ops import AsyncExecutor

class OptimizedAsyncPool:
    def __init__(self, max_workers=None, max_concurrent=100):
        self.max_workers = max_workers or min(50, asyncio.Semaphore()._value)
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_with_semaphore(self, coro):
        """Execute coroutine with concurrency limiting."""
        async with self.semaphore:
            return await coro
    
    async def optimized_map(self, coro_func, data):
        """Optimized async map with backpressure."""
        
        # Create semaphore-controlled coroutines
        controlled_coros = [
            self.execute_with_semaphore(coro_func(item)) 
            for item in data
        ]
        
        # Process in batches to manage memory
        batch_size = min(self.max_concurrent, 1000)
        results = []
        
        for i in range(0, len(controlled_coros), batch_size):
            batch = controlled_coros[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
            
            # Optional: progress reporting
            print(f"Completed batch {i//batch_size + 1}/{(len(controlled_coros)-1)//batch_size + 1}")
        
        return results

async def performance_comparison():
    """Compare different async processing approaches."""
    
    async def mock_async_work(x):
        await asyncio.sleep(0.01)
        return x * x
    
    data = list(range(500))
    
    # Standard approach
    print("Standard async_parallel_map:")
    start = asyncio.get_event_loop().time()
    results1 = await async_parallel_map(mock_async_work, data, max_workers=20)
    time1 = asyncio.get_event_loop().time() - start
    print(f"Time: {time1:.2f}s")
    
    # Optimized approach
    print("\nOptimized pool:")
    start = asyncio.get_event_loop().time()
    pool = OptimizedAsyncPool(max_workers=20, max_concurrent=50)
    results2 = await pool.optimized_map(mock_async_work, data)
    time2 = asyncio.get_event_loop().time() - start
    print(f"Time: {time2:.2f}s")
    
    print(f"\nSpeedup: {time1/time2:.2f}x")

asyncio.run(performance_comparison())
```

### Memory-Efficient Async Processing

```python
import asyncio
import gc
from pyferris.async_ops import async_parallel_map

class MemoryEfficientAsyncProcessor:
    def __init__(self, batch_size=100, max_memory_items=1000):
        self.batch_size = batch_size
        self.max_memory_items = max_memory_items
    
    async def process_in_batches(self, async_func, data):
        """Process large datasets in memory-efficient batches."""
        
        total_items = len(data)
        results = []
        
        print(f"Processing {total_items} items in batches of {self.batch_size}")
        
        for i in range(0, total_items, self.batch_size):
            batch = data[i:i + self.batch_size]
            
            print(f"Processing batch {i//self.batch_size + 1}/{(total_items-1)//self.batch_size + 1}")
            
            # Process batch
            batch_results = await async_parallel_map(
                async_func, 
                batch, 
                max_workers=10
            )
            
            # Collect results
            results.extend(list(batch_results))
            
            # Memory management
            del batch_results
            gc.collect()
            
            # Optional: yield control to other tasks
            await asyncio.sleep(0)
        
        return results
    
    async def streaming_process(self, async_func, data_generator):
        """Process streaming data without loading everything into memory."""
        
        async def process_item_safe(item):
            try:
                return await async_func(item)
            except Exception as e:
                return {'error': str(e), 'item': item}
        
        batch = []
        async for item in data_generator:
            batch.append(item)
            
            if len(batch) >= self.batch_size:
                # Process current batch
                batch_results = await asyncio.gather(
                    *[process_item_safe(item) for item in batch],
                    return_exceptions=True
                )
                
                for result in batch_results:
                    yield result
                
                batch.clear()
                gc.collect()
        
        # Process remaining items
        if batch:
            batch_results = await asyncio.gather(
                *[process_item_safe(item) for item in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                yield result

async def memory_efficient_example():
    """Example of memory-efficient async processing."""
    
    async def memory_intensive_async_work(x):
        # Simulate memory-intensive async work
        await asyncio.sleep(0.01)
        temp_data = list(range(x % 1000))  # Create temporary data
        result = sum(temp_data)
        del temp_data  # Cleanup
        return result
    
    # Large dataset
    large_data = list(range(5000))
    
    processor = MemoryEfficientAsyncProcessor(batch_size=200)
    
    # Batch processing
    print("Batch processing:")
    results = await processor.process_in_batches(
        memory_intensive_async_work, 
        large_data
    )
    print(f"Processed {len(results)} items")
    
    # Streaming processing
    print("\nStreaming processing:")
    
    async def data_generator():
        for x in range(1000):
            yield x
            await asyncio.sleep(0.001)  # Simulate streaming delay
    
    streaming_results = []
    async for result in processor.streaming_process(
        memory_intensive_async_work,
        data_generator()
    ):
        streaming_results.append(result)
    
    print(f"Streamed {len(streaming_results)} items")

asyncio.run(memory_efficient_example())
```

## Error Handling

### Robust Async Error Handling

```python
import asyncio
import random
from pyferris.async_ops import async_parallel_map

class AsyncErrorHandler:
    def __init__(self, max_retries=3, retry_delay=1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def retry_async_function(self, async_func, *args, **kwargs):
        """Retry async function with exponential backoff."""
        
        for attempt in range(self.max_retries + 1):
            try:
                return await async_func(*args, **kwargs)
            
            except Exception as e:
                if attempt == self.max_retries:
                    # Last attempt failed, re-raise
                    raise
                
                # Wait before retry with exponential backoff
                wait_time = self.retry_delay * (2 ** attempt)
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
    
    async def safe_async_map(self, async_func, data):
        """Async map with error handling and retries."""
        
        async def safe_wrapper(item):
            try:
                result = await self.retry_async_function(async_func, item)
                return {'success': True, 'result': result, 'item': item}
            except Exception as e:
                return {'success': False, 'error': str(e), 'item': item}
        
        results = await async_parallel_map(safe_wrapper, data, max_workers=5)
        return list(results)

async def flaky_async_operation(x):
    """Async operation that randomly fails."""
    await asyncio.sleep(0.1)
    
    # 30% chance of failure
    if random.random() < 0.3:
        if random.random() < 0.5:
            raise ConnectionError(f"Network error for item {x}")
        else:
            raise ValueError(f"Invalid data for item {x}")
    
    return x * x

async def error_handling_example():
    """Example of robust async error handling."""
    
    error_handler = AsyncErrorHandler(max_retries=2, retry_delay=0.5)
    
    data = list(range(20))
    
    print("Processing with error handling and retries...")
    results = await error_handler.safe_async_map(flaky_async_operation, data)
    
    # Analyze results
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\nResults:")
    print(f"Successful: {len(successful)}/{len(data)} ({len(successful)/len(data)*100:.1f}%)")
    print(f"Failed: {len(failed)}/{len(data)} ({len(failed)/len(data)*100:.1f}%)")
    
    if failed:
        print("\nFailure analysis:")
        error_types = {}
        for failure in failed:
            error_type = failure['error'].split(':')[0]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            print(f"  {error_type}: {count} occurrences")

asyncio.run(error_handling_example())
```

## Real-world Examples

### Async Web Scraping Pipeline

```python
import asyncio
import aiohttp
from pyferris.async_ops import async_parallel_map, AsyncExecutor

class AsyncWebScraper:
    def __init__(self, max_workers=10, timeout=30):
        self.max_workers = max_workers
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_url(self, url):
        """Scrape a single URL."""
        try:
            async with self.session.get(url) as response:
                content = await response.text()
                
                return {
                    'url': url,
                    'status_code': response.status,
                    'content_length': len(content),
                    'title': self._extract_title(content),
                    'success': True
                }
        
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'success': False
            }
    
    def _extract_title(self, html):
        """Extract title from HTML content."""
        import re
        match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    async def scrape_urls(self, urls):
        """Scrape multiple URLs concurrently."""
        results = await async_parallel_map(
            self.scrape_url,
            urls,
            max_workers=self.max_workers
        )
        return list(results)

async def web_scraping_example():
    """Example of async web scraping."""
    
    # Test URLs
    urls = [
        'https://httpbin.org/html',
        'https://httpbin.org/json',
        'https://httpbin.org/xml',
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/2',
    ] * 2  # 10 URLs total
    
    async with AsyncWebScraper(max_workers=5) as scraper:
        print(f"Scraping {len(urls)} URLs...")
        
        start_time = asyncio.get_event_loop().time()
        results = await scraper.scrape_urls(urls)
        end_time = asyncio.get_event_loop().time()
        
        # Analyze results
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\nScraping completed in {end_time - start_time:.2f} seconds")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if successful:
            avg_content_length = sum(r['content_length'] for r in successful) / len(successful)
            print(f"Average content length: {avg_content_length:.0f} characters")

asyncio.run(web_scraping_example())
```

### Async Database Operations

```python
import asyncio
import sqlite3
import aiosqlite
from pyferris.async_ops import async_parallel_map

class AsyncDatabaseProcessor:
    def __init__(self, db_path):
        self.db_path = db_path
    
    async def setup_database(self):
        """Setup test database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    age INTEGER
                )
            ''')
            await db.commit()
    
    async def insert_user(self, user_data):
        """Insert a single user asynchronously."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT INTO users (name, email, age) VALUES (?, ?, ?)',
                (user_data['name'], user_data['email'], user_data['age'])
            )
            await db.commit()
            return user_data['name']
    
    async def process_user_data(self, user_data):
        """Process and validate user data."""
        await asyncio.sleep(0.01)  # Simulate processing time
        
        # Validation
        if not user_data.get('name') or not user_data.get('email'):
            raise ValueError("Missing required fields")
        
        # Add computed fields
        processed = {
            **user_data,
            'email_domain': user_data['email'].split('@')[1],
            'age_group': 'adult' if user_data['age'] >= 18 else 'minor'
        }
        
        return processed
    
    async def bulk_process_users(self, user_list):
        """Process and insert users in parallel."""
        
        # Stage 1: Process/validate user data
        print("Stage 1: Processing user data...")
        processed_users = await async_parallel_map(
            self.process_user_data,
            user_list,
            max_workers=10
        )
        
        valid_users = [u for u in processed_users if u is not None]
        print(f"Processed {len(valid_users)} valid users")
        
        # Stage 2: Insert into database
        print("Stage 2: Inserting into database...")
        inserted_names = await async_parallel_map(
            self.insert_user,
            valid_users,
            max_workers=5  # Fewer workers for database operations
        )
        
        return list(inserted_names)

async def database_example():
    """Example of async database operations."""
    
    # Sample user data
    users = [
        {'name': f'User {i}', 'email': f'user{i}@example.com', 'age': 20 + i}
        for i in range(100)
    ]
    
    # Add some invalid data
    users.extend([
        {'name': '', 'email': 'invalid@example.com', 'age': 25},  # Invalid name
        {'name': 'Valid User', 'email': '', 'age': 30},  # Invalid email
    ])
    
    processor = AsyncDatabaseProcessor('test_async.db')
    
    # Setup database
    await processor.setup_database()
    
    # Process users
    print(f"Processing {len(users)} users...")
    
    try:
        inserted_names = await processor.bulk_process_users(users)
        print(f"Successfully inserted {len(inserted_names)} users")
        
        # Verify by counting records
        async with aiosqlite.connect('test_async.db') as db:
            cursor = await db.execute('SELECT COUNT(*) FROM users')
            count = await cursor.fetchone()
            print(f"Total users in database: {count[0]}")
    
    except Exception as e:
        print(f"Error during processing: {e}")
    
    # Cleanup
    import os
    try:
        os.remove('test_async.db')
    except:
        pass

asyncio.run(database_example())
```

This comprehensive async operations guide demonstrates how to effectively use PyFerris's async capabilities for I/O-bound workloads, providing patterns for everything from simple async mapping to complex data processing pipelines with error handling and performance optimization.

## Next Steps

- Explore [Shared Memory](shared_memory.md) for data sharing between async workers
- Learn about [Distributed Computing](distributed.md) for scaling async operations across multiple machines
- Check out [Performance Guide](performance.md) for async-specific optimization techniques
