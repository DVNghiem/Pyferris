# Async Operations

PyFerris provides comprehensive asynchronous processing capabilities that enable efficient concurrent execution of I/O-bound tasks, async function calls, and parallel async operations. The async system integrates seamlessly with Python's native asyncio ecosystem.

## Overview

The async operations system includes:
- **AsyncExecutor** - High-performance async task executor
- **AsyncTask** - Wrapper for async task management
- **async_parallel_map** - Parallel async transformations
- **async_parallel_filter** - Parallel async filtering

## Quick Start

```python
import pyferris
import asyncio

async def main():
    # Create async executor
    executor = pyferris.AsyncExecutor()
    
    # Define async function
    async def fetch_data(url):
        await asyncio.sleep(0.1)  # Simulate network request
        return f"Data from {url}"
    
    # Execute multiple async tasks
    urls = ["api.example.com/1", "api.example.com/2", "api.example.com/3"]
    results = await pyferris.async_parallel_map(fetch_data, urls)
    print(results)
    # ['Data from api.example.com/1', 'Data from api.example.com/2', 'Data from api.example.com/3']

# Run the async function
asyncio.run(main())
```

## Core Components

### AsyncExecutor

The main executor for managing and running async tasks efficiently.

```python
import pyferris
import asyncio

async def example_async_executor():
    # Create executor with custom configuration
    executor = pyferris.AsyncExecutor(max_workers=10)
    
    # Define async tasks
    async def process_item(item):
        await asyncio.sleep(0.1)
        return item * 2
    
    async def validate_item(item):
        await asyncio.sleep(0.05)
        return item > 0
    
    # Submit individual async tasks
    task1 = executor.submit_async(process_item(5))
    task2 = executor.submit_async(validate_item(10))
    
    # Wait for results
    result1 = await task1
    result2 = await task2
    
    print(f"Processed: {result1}, Valid: {result2}")

asyncio.run(example_async_executor())
```

### AsyncTask

Wrapper for async task management with additional metadata and control.

```python
import pyferris
import asyncio

async def example_async_task():
    async def long_running_task(duration):
        await asyncio.sleep(duration)
        return f"Completed after {duration} seconds"
    
    # Create async task with metadata
    task = pyferris.AsyncTask(
        coro=long_running_task(2),
        name="data_processing",
        timeout=5.0
    )
    
    # Execute and get result
    result = await task.execute()
    print(f"Task result: {result}")

asyncio.run(example_async_task())
```

### Parallel Async Operations

#### async_parallel_map

Apply async function to multiple items concurrently.

```python
import pyferris
import asyncio
import aiohttp

async def example_parallel_map():
    async def fetch_url(session, url):
        async with session.get(url) as response:
            return await response.text()
    
    # Parallel async mapping
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2", 
        "https://httpbin.org/delay/1"
    ]
    
    async with aiohttp.ClientSession() as session:
        # Create partial function with session
        fetch_func = lambda url: fetch_url(session, url)
        
        # Execute all requests concurrently
        results = await pyferris.async_parallel_map(fetch_func, urls)
        print(f"Fetched {len(results)} responses")

# asyncio.run(example_parallel_map())  # Uncomment to run
```

#### async_parallel_filter

Filter items using async predicate functions.

```python
import pyferris
import asyncio

async def example_parallel_filter():
    async def is_valid_email(email):
        # Simulate async email validation
        await asyncio.sleep(0.1)
        return "@" in email and "." in email
    
    emails = [
        "user@example.com",
        "invalid-email",
        "admin@company.org",
        "test@test",
        "contact@site.net"
    ]
    
    # Filter emails asynchronously
    valid_emails = await pyferris.async_parallel_filter(is_valid_email, emails)
    print(f"Valid emails: {valid_emails}")

asyncio.run(example_parallel_filter())
```

## Advanced Usage

### Concurrent Data Processing

```python
import pyferris
import asyncio
import json

async def advanced_data_processing():
    # Simulate database records
    records = [
        {"id": 1, "url": "api.example.com/user/1", "type": "user"},
        {"id": 2, "url": "api.example.com/order/2", "type": "order"},
        {"id": 3, "url": "api.example.com/user/3", "type": "user"},
        {"id": 4, "url": "api.example.com/product/4", "type": "product"},
    ]
    
    async def fetch_and_process(record):
        # Simulate API call
        await asyncio.sleep(0.2)
        
        # Simulate processing based on type
        if record["type"] == "user":
            return {"id": record["id"], "name": f"User {record['id']}", "type": "user"}
        elif record["type"] == "order":
            return {"id": record["id"], "total": 99.99, "type": "order"}
        else:
            return {"id": record["id"], "title": f"Product {record['id']}", "type": "product"}
    
    # Process all records concurrently
    results = await pyferris.async_parallel_map(fetch_and_process, records)
    
    # Group results by type
    grouped = {}
    for result in results:
        result_type = result["type"]
        if result_type not in grouped:
            grouped[result_type] = []
        grouped[result_type].append(result)
    
    print("Processed records by type:")
    for record_type, items in grouped.items():
        print(f"  {record_type}: {len(items)} items")

asyncio.run(advanced_data_processing())
```

### Error Handling in Async Operations

```python
import pyferris
import asyncio

async def error_handling_example():
    async def unreliable_operation(item):
        await asyncio.sleep(0.1)
        if item % 3 == 0:
            raise ValueError(f"Item {item} caused an error")
        return item * 2
    
    async def safe_operation(item):
        try:
            result = await unreliable_operation(item)
            return {"success": True, "value": result, "item": item}
        except Exception as e:
            return {"success": False, "error": str(e), "item": item}
    
    items = list(range(10))
    
    # Process all items, handling errors gracefully
    results = await pyferris.async_parallel_map(safe_operation, items)
    
    # Separate successful and failed operations
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]
    
    print(f"Successful operations: {len(successes)}")
    print(f"Failed operations: {len(failures)}")
    
    for failure in failures:
        print(f"  Item {failure['item']}: {failure['error']}")

asyncio.run(error_handling_example())
```

### Rate Limiting and Throttling

```python
import pyferris
import asyncio

async def rate_limited_processing():
    # Semaphore for rate limiting
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent operations
    
    async def rate_limited_operation(item):
        async with semaphore:
            # Simulate API call with rate limiting
            await asyncio.sleep(0.5)
            return f"Processed {item}"
    
    items = list(range(10))
    
    # Execute with rate limiting
    start_time = asyncio.get_event_loop().time()
    results = await pyferris.async_parallel_map(rate_limited_operation, items)
    end_time = asyncio.get_event_loop().time()
    
    print(f"Processed {len(results)} items in {end_time - start_time:.2f} seconds")
    print("Results:", results[:3], "...")  # Show first 3 results

asyncio.run(rate_limited_processing())
```

## Integration Examples

### With Pipeline Processing

```python
import pyferris
import asyncio

async def async_pipeline_example():
    # Async pipeline stages
    async def fetch_stage(urls):
        async def fetch_single(url):
            await asyncio.sleep(0.1)
            return f"data_from_{url}"
        
        return await pyferris.async_parallel_map(fetch_single, urls)
    
    async def process_stage(data_items):
        async def process_single(item):
            await asyncio.sleep(0.05)
            return item.upper() + "_PROCESSED"
        
        return await pyferris.async_parallel_map(process_single, data_items)
    
    async def filter_stage(processed_items):
        async def is_valid(item):
            await asyncio.sleep(0.02)
            return len(item) > 10
        
        return await pyferris.async_parallel_filter(is_valid, processed_items)
    
    # Execute async pipeline
    urls = ["api1", "api2", "api3", "api4"]
    
    # Stage 1: Fetch data
    fetched_data = await fetch_stage(urls)
    print(f"Fetched {len(fetched_data)} items")
    
    # Stage 2: Process data
    processed_data = await process_stage(fetched_data)
    print(f"Processed {len(processed_data)} items")
    
    # Stage 3: Filter data
    filtered_data = await filter_stage(processed_data)
    print(f"Filtered to {len(filtered_data)} items")
    
    return filtered_data

result = asyncio.run(async_pipeline_example())
print("Final result:", result)
```

### With Shared Memory

```python
import pyferris
import asyncio

async def async_shared_memory_example():
    # Create shared array for results
    shared_results = pyferris.create_shared_array([])
    
    async def worker_task(worker_id, work_items):
        results = []
        for item in work_items:
            # Simulate async work
            await asyncio.sleep(0.1)
            result = item * worker_id
            results.append(result)
        
        # Store results in shared memory (in real scenario, need thread safety)
        return results
    
    # Distribute work across async workers
    all_items = list(range(20))
    chunk_size = 5
    worker_tasks = []
    
    for i in range(0, len(all_items), chunk_size):
        chunk = all_items[i:i + chunk_size]
        worker_id = (i // chunk_size) + 1
        task = worker_task(worker_id, chunk)
        worker_tasks.append(task)
    
    # Execute all workers concurrently
    all_results = await asyncio.gather(*worker_tasks)
    
    # Combine results
    final_results = []
    for worker_results in all_results:
        final_results.extend(worker_results)
    
    print(f"Processed {len(final_results)} items across {len(worker_tasks)} workers")
    print("Sample results:", final_results[:10])

asyncio.run(async_shared_memory_example())
```

## Performance Optimization

### Batching Operations

```python
import pyferris
import asyncio

async def batched_processing_example():
    async def process_batch(batch):
        # Simulate batch processing (more efficient than individual items)
        await asyncio.sleep(0.1 * len(batch))  # Batch overhead is less
        return [item * 2 for item in batch]
    
    def create_batches(items, batch_size):
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
    
    items = list(range(100))
    batch_size = 10
    batches = list(create_batches(items, batch_size))
    
    # Process batches concurrently
    start_time = asyncio.get_event_loop().time()
    batch_results = await pyferris.async_parallel_map(process_batch, batches)
    end_time = asyncio.get_event_loop().time()
    
    # Flatten results
    final_results = []
    for batch_result in batch_results:
        final_results.extend(batch_result)
    
    print(f"Processed {len(final_results)} items in {len(batches)} batches")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

asyncio.run(batched_processing_example())
```

### Connection Pooling

```python
import pyferris
import asyncio

class AsyncConnectionPool:
    def __init__(self, max_connections=10):
        self.semaphore = asyncio.Semaphore(max_connections)
        self.connections = []
    
    async def get_connection(self):
        await self.semaphore.acquire()
        # Simulate getting connection
        return f"connection_{len(self.connections)}"
    
    async def release_connection(self, conn):
        # Simulate releasing connection
        self.semaphore.release()

async def connection_pool_example():
    pool = AsyncConnectionPool(max_connections=5)
    
    async def database_operation(query_id):
        # Get connection from pool
        conn = await pool.get_connection()
        try:
            # Simulate database operation
            await asyncio.sleep(0.2)
            result = f"Query {query_id} result"
            return result
        finally:
            # Always release connection
            await pool.release_connection(conn)
    
    # Execute many database operations concurrently
    queries = list(range(20))
    results = await pyferris.async_parallel_map(database_operation, queries)
    
    print(f"Executed {len(results)} database queries")
    print("Sample results:", results[:5])

asyncio.run(connection_pool_example())
```

## Real-World Examples

### Web Scraping

```python
import pyferris
import asyncio

async def web_scraping_example():
    async def scrape_url(url_info):
        url, expected_size = url_info
        
        # Simulate HTTP request
        await asyncio.sleep(0.3)
        
        # Simulate parsing
        content = f"Content from {url}"
        
        return {
            "url": url,
            "content": content,
            "size": len(content),
            "success": True
        }
    
    async def validate_content(scraped_data):
        # Simulate content validation
        await asyncio.sleep(0.1)
        return scraped_data["size"] > 10
    
    # URLs to scrape
    urls = [
        ("https://example.com/page1", 100),
        ("https://example.com/page2", 150),
        ("https://example.com/page3", 200),
        ("https://example.com/page4", 80),
        ("https://example.com/page5", 300),
    ]
    
    # Scrape all URLs concurrently
    scraped_results = await pyferris.async_parallel_map(scrape_url, urls)
    
    # Filter valid content
    valid_content = await pyferris.async_parallel_filter(validate_content, scraped_results)
    
    print(f"Scraped {len(scraped_results)} URLs")
    print(f"Valid content from {len(valid_content)} URLs")
    
    for content in valid_content:
        print(f"  {content['url']}: {content['size']} characters")

asyncio.run(web_scraping_example())
```

### API Data Aggregation

```python
import pyferris
import asyncio
import json

async def api_aggregation_example():
    async def fetch_user_data(user_id):
        # Simulate user API call
        await asyncio.sleep(0.1)
        return {
            "user_id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com"
        }
    
    async def fetch_user_orders(user_id):
        # Simulate orders API call
        await asyncio.sleep(0.15)
        return [
            {"order_id": f"order_{user_id}_1", "amount": 99.99},
            {"order_id": f"order_{user_id}_2", "amount": 149.99}
        ]
    
    async def fetch_user_preferences(user_id):
        # Simulate preferences API call
        await asyncio.sleep(0.08)
        return {
            "theme": "dark",
            "notifications": True,
            "language": "en"
        }
    
    async def aggregate_user_profile(user_id):
        # Fetch all user data concurrently
        user_data, orders, preferences = await asyncio.gather(
            fetch_user_data(user_id),
            fetch_user_orders(user_id),
            fetch_user_preferences(user_id)
        )
        
        # Aggregate into complete profile
        return {
            "profile": user_data,
            "orders": orders,
            "preferences": preferences,
            "total_spent": sum(order["amount"] for order in orders)
        }
    
    # Process multiple users
    user_ids = [1, 2, 3, 4, 5]
    user_profiles = await pyferris.async_parallel_map(aggregate_user_profile, user_ids)
    
    # Generate summary statistics
    total_users = len(user_profiles)
    total_revenue = sum(profile["total_spent"] for profile in user_profiles)
    avg_revenue = total_revenue / total_users
    
    print(f"Aggregated data for {total_users} users")
    print(f"Total revenue: ${total_revenue:.2f}")
    print(f"Average revenue per user: ${avg_revenue:.2f}")

asyncio.run(api_aggregation_example())
```

## Error Handling and Debugging

### Comprehensive Error Handling

```python
import pyferris
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def robust_async_processing():
    async def risky_operation(item):
        await asyncio.sleep(0.1)
        
        if item % 5 == 0:
            raise ConnectionError(f"Network error for item {item}")
        elif item % 7 == 0:
            raise ValueError(f"Invalid value: {item}")
        else:
            return item * 2
    
    async def safe_wrapper(item):
        try:
            result = await risky_operation(item)
            return {"item": item, "result": result, "status": "success"}
        except ConnectionError as e:
            logger.warning(f"Connection error for item {item}: {e}")
            return {"item": item, "error": str(e), "status": "network_error"}
        except ValueError as e:
            logger.error(f"Value error for item {item}: {e}")
            return {"item": item, "error": str(e), "status": "value_error"}
        except Exception as e:
            logger.error(f"Unexpected error for item {item}: {e}")
            return {"item": item, "error": str(e), "status": "unknown_error"}
    
    items = list(range(20))
    results = await pyferris.async_parallel_map(safe_wrapper, items)
    
    # Analyze results
    successes = [r for r in results if r["status"] == "success"]
    network_errors = [r for r in results if r["status"] == "network_error"]
    value_errors = [r for r in results if r["status"] == "value_error"]
    unknown_errors = [r for r in results if r["status"] == "unknown_error"]
    
    print(f"Results: {len(successes)} success, {len(network_errors)} network errors, "
          f"{len(value_errors)} value errors, {len(unknown_errors)} unknown errors")

asyncio.run(robust_async_processing())
```

## Best Practices

### Async Function Design

1. **Use appropriate concurrency limits** to avoid overwhelming systems
2. **Implement proper error handling** for network and I/O operations
3. **Use connection pooling** for resource-intensive operations
4. **Batch operations** when possible for better efficiency

```python
# Good async function design
async def well_designed_async_function(items, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_limit(item):
        async with semaphore:
            try:
                return await actual_processing(item)
            except Exception as e:
                logger.error(f"Error processing {item}: {e}")
                return None
    
    results = await pyferris.async_parallel_map(process_with_limit, items)
    return [r for r in results if r is not None]
```

### Performance Guidelines

1. **Use async for I/O-bound tasks**, not CPU-bound tasks
2. **Avoid blocking operations** in async functions
3. **Monitor memory usage** with large concurrent operations
4. **Profile async performance** to identify bottlenecks

### Resource Management

```python
# Proper resource management
async def resource_managed_operations():
    async with aiohttp.ClientSession() as session:
        async def fetch_with_session(url):
            async with session.get(url) as response:
                return await response.text()
        
        urls = ["http://example.com"] * 10
        results = await pyferris.async_parallel_map(fetch_with_session, urls)
        return results
    # Session automatically closed here
```

## API Reference

### AsyncExecutor

```python
class AsyncExecutor:
    def __init__(self, max_workers: int = None)
    async def submit_async(self, coro: Coroutine) -> Any
    async def map_async(self, func: Callable, items: List[Any]) -> List[Any]
    async def shutdown(self) -> None
```

### AsyncTask

```python
class AsyncTask:
    def __init__(self, coro: Coroutine, name: str = None, timeout: float = None)
    async def execute(self) -> Any
    def cancel(self) -> None
    @property
    def is_done(self) -> bool
```

### Functions

```python
async def async_parallel_map(func: Callable, items: List[Any]) -> List[Any]
async def async_parallel_filter(predicate: Callable, items: List[Any]) -> List[Any]
```

This comprehensive async operations documentation provides everything needed to leverage PyFerris's powerful async capabilities for efficient concurrent processing.
