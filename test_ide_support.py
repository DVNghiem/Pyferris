#!/usr/bin/env python3
"""
Test script to verify IDE support and docstring functionality.
Run this to test that the wrapper classes provide good IDE hints.
"""

from pyferris import (
    # Pipeline Processing
    Pipeline, Chain, pipeline_map,
    
    # Async Support
    AsyncExecutor, AsyncTask, async_parallel_map, async_parallel_filter,
    
    # Shared Memory
    SharedArray, SharedDict, SharedQueue, SharedCounter, create_shared_array,
    
    # Custom Schedulers
    WorkStealingScheduler, RoundRobinScheduler, AdaptiveScheduler,
    PriorityScheduler, TaskPriority, execute_with_priority
)


def test_pipeline_ide_support():
    """Test Pipeline class for IDE autocompletion and hints."""
    print("=== Testing Pipeline IDE Support ===")
    
    # Create pipeline - IDE should show constructor signature
    pipeline = Pipeline(chunk_size=10)
    
    # IDE should suggest these methods with their docstrings
    pipeline.add(lambda x: x * 2)  # Should show: Add a single operation to the pipeline
    pipeline.chain([lambda x: x + 1])  # Should show: Add multiple operations at once
    
    data = [1, 2, 3, 4, 5]
    results = pipeline.execute(data)  # Should show: Execute the pipeline on data
    
    print(f"Pipeline length: {pipeline.length}")  # Should show property docstring
    print(f"Results: {results}")
    
    # Test method chaining
    chain = Chain()
    chain.then(lambda x: x * 2).then(lambda x: x + 1)  # Should show fluent interface
    single_result = chain.execute_one(10)
    print(f"Chain result: {single_result}")


def test_shared_memory_ide_support():
    """Test SharedMemory classes for IDE autocompletion."""
    print("\n=== Testing SharedMemory IDE Support ===")
    
    # SharedArray - IDE should show constructor with capacity parameter
    arr = SharedArray(capacity=100)
    
    # IDE should suggest these methods with type hints
    arr.append(1.5)  # Should show: (value: float) -> None
    arr.extend([2.0, 3.0, 4.0])  # Should show: (values: List[float]) -> None
    
    value = arr.get(0)  # Should show: (index: int) -> float
    arr.set(1, 99.5)  # Should show: (index: int, value: float) -> None
    
    # Property access - should show return types
    length = arr.len  # Should show: int
    is_empty = arr.is_empty()  # Should show: () -> bool
    
    # Parallel operations
    total = arr.sum()  # Should show: () -> float
    squared = arr.parallel_map(lambda x: x ** 2)  # Should show parallel_map signature
    
    print(f"Array length: {length}, Sum: {total}")
    
    # SharedDict - should show key-value operations
    shared_dict = SharedDict()
    shared_dict.set("key1", "value1")  # Should show: (key: str, value: Any) -> None
    value = shared_dict.get("key1")  # Should show: (key: str) -> Any
    
    # SharedQueue - should show FIFO operations
    queue = SharedQueue(max_size=50)
    queue.put("item")  # Should show: (item: Any) -> None
    item = queue.get()  # Should show: () -> Any
    
    print(f"Queue size: {queue.size}")  # Should show: int property


def test_scheduler_ide_support():
    """Test Scheduler classes for IDE autocompletion."""
    print("\n=== Testing Scheduler IDE Support ===")
    
    # WorkStealingScheduler - should show workers parameter
    ws_scheduler = WorkStealingScheduler(workers=4)
    
    # Task creation with lambda - IDE should understand the pattern
    tasks = [lambda x=i: x ** 2 for i in range(5)]
    results = ws_scheduler.execute(tasks)  # Should show: (tasks: List[Callable]) -> List[Any]
    
    print(f"Work stealing results: {results}")
    
    # PriorityScheduler with TaskPriority enum
    priority_scheduler = PriorityScheduler(workers=2)
    
    # IDE should suggest TaskPriority values
    high_task = lambda: "High priority"
    normal_task = lambda: "Normal priority"
    
    priority_tasks = [
        (high_task, TaskPriority.High),    # Should show enum values
        (normal_task, TaskPriority.Normal),
    ]
    
    priority_results = priority_scheduler.execute(priority_tasks)
    print(f"Priority results: {priority_results}")
    
    # AdaptiveScheduler - should show min/max workers
    adaptive = AdaptiveScheduler(min_workers=2, max_workers=8)
    current_workers = adaptive.current_workers  # Should show: int property


def test_async_ide_support():
    """Test Async classes for IDE autocompletion."""
    print("\n=== Testing Async IDE Support ===")
    
    # AsyncExecutor - should show max_workers parameter
    async_executor = AsyncExecutor(max_workers=4)
    
    def cpu_task(x):
        return x * x
    
    # Should show proper type hints for async methods
    data = [1, 2, 3, 4, 5]
    results = async_executor.map_async(cpu_task, data)  # Should show signatures
    limited_results = async_executor.map_async_limited(
        cpu_task, data, max_concurrent=2
    )
    
    print(f"Async results: {results}")
    
    # Functional async operations
    filtered = async_parallel_filter(
        lambda x: x % 2 == 0, 
        range(10), 
        max_concurrent=3
    )
    print(f"Async filtered: {filtered}")


def test_function_signatures():
    """Test standalone function signatures."""
    print("\n=== Testing Function Signatures ===")
    
    # pipeline_map - should show all parameters with types
    operations = [lambda x: x + 1, lambda x: x * 2]
    results = pipeline_map([1, 2, 3], operations, chunk_size=2)
    print(f"Pipeline map results: {results}")
    
    # create_shared_array - should show data parameter
    initial_data = [1.0, 2.0, 3.0]
    shared_arr = create_shared_array(initial_data)
    print(f"Created shared array with length: {shared_arr.len}")


if __name__ == "__main__":
    print("🔍 Testing IDE Support for PyFerris Level 3 Features")
    print("=" * 60)
    
    test_pipeline_ide_support()
    test_shared_memory_ide_support()
    test_scheduler_ide_support()
    test_async_ide_support()
    test_function_signatures()
    
    print("\n" + "=" * 60)
    print("✅ IDE Support Test Complete!")
    print("\nKey improvements:")
    print("• Comprehensive docstrings for all classes and methods")
    print("• Type hints for parameters and return values")
    print("• Detailed examples in docstrings")
    print("• Property documentation")
    print("• Method chaining support")
    print("• Enum/constant documentation")
    print("\nYour IDE should now provide:")
    print("• Autocompletion for all methods and properties")
    print("• Parameter hints when calling functions")
    print("• Inline documentation in tooltips")
    print("• Type checking and validation")
