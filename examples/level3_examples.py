"""
Level 3 Features Examples - Pipeline Processing, Async Support, Shared Memory, and Custom Schedulers
"""

import time
import asyncio
from pyferris import (
    # Pipeline Processing
    Pipeline, Chain, pipeline_map,
    
    # Async Support  
    AsyncExecutor, async_parallel_map, async_parallel_filter,
    
    # Shared Memory
    SharedArray, SharedDict, SharedQueue, SharedCounter,
    
    # Custom Schedulers
    WorkStealingScheduler, RoundRobinScheduler, AdaptiveScheduler,
    PriorityScheduler, TaskPriority, execute_with_priority
)


def pipeline_examples():
    """Demonstrate pipeline processing capabilities"""
    print("=== Pipeline Processing Examples ===")
    
    # Example 1: Basic Pipeline
    print("\n1. Basic Pipeline:")
    pipeline = Pipeline(chunk_size=100)
    
    # Add operations to pipeline
    pipeline.add(lambda x: x * 2)      # Double
    pipeline.add(lambda x: x + 1)      # Add 1
    pipeline.add(lambda x: x ** 2)     # Square
    
    data = range(10)
    results = pipeline.execute(data)
    print(f"Input: {list(data)}")
    print(f"Pipeline result: {results}")
    
    # Example 2: Chain operations
    print("\n2. Chain Operations:")
    chain = Chain()
    chain.then(lambda x: x * 3)
    chain.then(lambda x: x - 1)
    chain.then(lambda x: x / 2)
    
    single_result = chain.execute_one(10)
    print(f"Chain single input 10: {single_result}")
    
    many_results = chain.execute_many(range(5), 2)
    print(f"Chain multiple inputs: {many_results}")
    
    # Example 3: Functional pipeline
    print("\n3. Functional Pipeline:")
    operations = [
        lambda x: x + 10,
        lambda x: x * 0.5,
        lambda x: round(x, 2)
    ]
    
    func_results = pipeline_map(range(5), operations, 2)
    print(f"Functional pipeline: {func_results}")


def async_examples():
    """Demonstrate async processing capabilities"""
    print("\n\n=== Async Processing Examples ===")
    
    # Example 1: Async Executor
    print("\n1. Async Executor:")
    async_executor = AsyncExecutor(max_workers=4)
    
    def cpu_bound_task(x):
        # Simulate CPU-bound work
        result = sum(i * i for i in range(x * 1000))
        return result
    
    data = [10, 20, 30, 40, 50]
    start_time = time.time()
    results = async_executor.map_async(cpu_bound_task, data)
    end_time = time.time()
    
    print(f"Async execution time: {end_time - start_time:.3f}s")
    print(f"Results: {results[:3]}...")  # Show first 3 results
    
    # Example 2: Limited concurrency
    print("\n2. Limited Concurrency:")
    limited_results = async_executor.map_async_limited(
        lambda x: x ** 2, range(20)
    )
    print(f"Limited concurrency results: {limited_results[:10]}")
    
    # Example 3: Async filter
    print("\n3. Async Filter:")
    def is_even_slow(x):
        time.sleep(0.01)  # Simulate slow predicate
        return x % 2 == 0
    
    start_time = time.time()
    filtered = async_parallel_filter(is_even_slow, range(50))
    end_time = time.time()
    
    print(f"Async filter time: {end_time - start_time:.3f}s")
    print(f"Filtered results: {filtered[:10]}")


def shared_memory_examples():
    """Demonstrate shared memory capabilities"""
    print("\n\n=== Shared Memory Examples ===")
    
    # Example 1: SharedArray
    print("\n1. SharedArray:")
    shared_arr = SharedArray(capacity=1000)
    
    # Populate array
    for i in range(100):
        shared_arr.append(i * 1.5)
    
    print(f"Array length: {shared_arr.len}")
    print(f"First 10 elements: {shared_arr.slice(0, 10)}")
    print(f"Parallel sum: {shared_arr.sum()}")
    
    # Parallel map on shared array
    squared = shared_arr.parallel_map(lambda x: x ** 2)
    print(f"Parallel squared (first 5): {squared[:5]}")
    
    # Example 2: SharedDict
    print("\n2. SharedDict:")
    shared_dict = SharedDict()
    
    # Add some data
    for i in range(10):
        shared_dict.set(f"key_{i}", i * 10)
    
    print(f"Dict length: {shared_dict.len}")
    print(f"Keys: {shared_dict.keys()[:5]}")
    print(f"Get key_5: {shared_dict.get('key_5')}")
    
    # Parallel map over values
    doubled_dict = shared_dict.parallel_map_values(lambda x: x * 2)
    print(f"Doubled values dict: {dict(list(doubled_dict.items())[:3])}")
    
    # Example 3: SharedQueue
    print("\n3. SharedQueue:")
    shared_queue = SharedQueue(max_size=100)
    
    # Add items
    for i in range(10):
        shared_queue.put(f"item_{i}")
    
    print(f"Queue size: {shared_queue.size}")
    print(f"Get item: {shared_queue.get()}")
    print(f"Queue size after get: {shared_queue.size}")
    
    # Example 4: SharedCounter
    print("\n4. SharedCounter:")
    counter = SharedCounter(initial_value=100)
    
    print(f"Initial value: {counter.value}")
    print(f"After increment: {counter.increment()}")
    print(f"After add 10: {counter.add(10)}")
    print(f"After decrement: {counter.decrement()}")


def scheduler_examples():
    """Demonstrate custom scheduler capabilities"""
    print("\n\n=== Custom Scheduler Examples ===")
    
    # Example 1: Work-Stealing Scheduler
    print("\n1. Work-Stealing Scheduler:")
    ws_scheduler = WorkStealingScheduler(workers=4)
    
    def variable_work(x):
        # Simulate variable workload
        iterations = x * 1000 if x % 3 == 0 else x * 100
        return sum(i for i in range(iterations))
    
    tasks = [lambda x=i: variable_work(x) for i in range(20)]
    
    start_time = time.time()
    ws_results = ws_scheduler.execute(tasks)
    end_time = time.time()
    
    print(f"Work-stealing execution time: {end_time - start_time:.3f}s")
    print(f"Results (first 5): {ws_results[:5]}")
    
    # Example 2: Round-Robin Scheduler
    print("\n2. Round-Robin Scheduler:")
    rr_scheduler = RoundRobinScheduler(workers=3)
    
    simple_tasks = [lambda x=i: x ** 2 + i for i in range(15)]
    rr_results = rr_scheduler.execute(simple_tasks)
    print(f"Round-robin results: {rr_results}")
    
    # Example 3: Adaptive Scheduler
    print("\n3. Adaptive Scheduler:")
    adaptive = AdaptiveScheduler(min_workers=2, max_workers=8)
    
    # Small workload
    small_tasks = [lambda x=i: x + 1 for i in range(5)]
    small_results = adaptive.execute(small_tasks)
    print(f"Small workload workers: {adaptive.current_workers}")
    print(f"Small results: {small_results}")
    
    # Large workload
    large_tasks = [lambda x=i: x ** 2 for i in range(200)]
    large_results = adaptive.execute(large_tasks)
    print(f"Large workload workers: {adaptive.current_workers}")
    print(f"Large results (first 10): {large_results[:10]}")
    
    # Example 4: Priority Scheduler
    print("\n4. Priority Scheduler:")
    priority_scheduler = PriorityScheduler(workers=4)
    
    # Create tasks with different priorities
    high_priority_task = lambda: "HIGH PRIORITY COMPLETED"
    normal_task = lambda: "Normal task completed"
    low_priority_task = lambda: "Low priority completed"
    
    # Tasks with priorities (task, priority)
    priority_tasks = [
        (low_priority_task, TaskPriority.Low),
        (normal_task, TaskPriority.Normal),
        (high_priority_task, TaskPriority.High),
        (normal_task, TaskPriority.Normal),
        (low_priority_task, TaskPriority.Low),
    ]
    
    priority_results = priority_scheduler.execute(priority_tasks)
    print("Priority execution results (high priority should be first):")
    for i, result in enumerate(priority_results):
        print(f"  {i+1}: {result}")


def performance_comparison():
    """Compare performance of different approaches"""
    print("\n\n=== Performance Comparison ===")
    
    def cpu_intensive_task(n):
        return sum(i * i for i in range(n))
    
    data = [1000] * 100
    
    # Sequential processing
    start_time = time.time()
    sequential_results = [cpu_intensive_task(x) for x in data]
    sequential_time = time.time() - start_time
    
    # Pipeline processing
    pipeline = Pipeline(chunk_size=25)
    pipeline.add(cpu_intensive_task)
    
    start_time = time.time()
    pipeline_results = pipeline.execute(data)
    pipeline_time = time.time() - start_time
    
    # Work-stealing scheduler
    ws_scheduler = WorkStealingScheduler(workers=4)
    tasks = [lambda x=x: cpu_intensive_task(x) for x in data]
    
    start_time = time.time()
    ws_results = ws_scheduler.execute(tasks)
    ws_time = time.time() - start_time
    
    print(f"Sequential time: {sequential_time:.3f}s")
    print(f"Pipeline time: {pipeline_time:.3f}s (speedup: {sequential_time/pipeline_time:.2f}x)")
    print(f"Work-stealing time: {ws_time:.3f}s (speedup: {sequential_time/ws_time:.2f}x)")
    
    # Verify results are the same
    assert sequential_results == pipeline_results == ws_results
    print("✓ All results are identical")


if __name__ == "__main__":
    pipeline_examples()
    async_examples()
    shared_memory_examples()
    scheduler_examples()
    performance_comparison()
    
    print("\n\n🎉 Level 3 features demonstration completed!")
    print("These advanced features provide:")
    print("- Pipeline Processing: Chain operations for streamlined data processing")
    print("- Async Support: Asynchronous execution for I/O and CPU-bound tasks")
    print("- Shared Memory: Zero-copy data sharing between threads")
    print("- Custom Schedulers: Flexible scheduling strategies for optimal performance")
