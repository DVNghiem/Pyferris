# Custom Schedulers

PyFerris provides a flexible scheduler system that allows you to control how tasks are distributed and executed across workers. The custom scheduler system enables fine-grained control over task execution order, resource allocation, and load balancing strategies.

## Overview

The scheduler system includes:
- **WorkStealingScheduler** - Dynamic load balancing with work stealing
- **RoundRobinScheduler** - Even distribution across workers
- **AdaptiveScheduler** - Intelligent scheduling based on system load
- **PriorityScheduler** - Priority-based task execution
- **TaskPriority** - Priority levels for task classification

## Quick Start

```python
import pyferris

# Create a work-stealing scheduler for dynamic load balancing
scheduler = pyferris.WorkStealingScheduler(num_workers=4)

# Define tasks
def compute_task(n):
    return sum(i * i for i in range(n))

# Execute tasks with custom scheduling
tasks = [1000, 2000, 500, 1500, 800, 1200]
results = scheduler.execute_tasks(compute_task, tasks)
print(f"Processed {len(results)} tasks: {results}")

# Priority-based scheduling
priority_scheduler = pyferris.PriorityScheduler()

# Create tasks with different priorities
high_priority_task = pyferris.create_priority_task(
    lambda: "Critical operation", 
    pyferris.TaskPriority.HIGH
)

low_priority_task = pyferris.create_priority_task(
    lambda: "Background operation",
    pyferris.TaskPriority.LOW
)

# Execute with priority ordering
result = pyferris.execute_with_priority([high_priority_task, low_priority_task])
print(f"Priority results: {result}")
```

## Scheduler Types

### WorkStealingScheduler

Dynamic load balancing where idle workers can "steal" tasks from busy workers' queues.

```python
import pyferris
import time

# Create work-stealing scheduler
ws_scheduler = pyferris.WorkStealingScheduler(
    num_workers=6,
    queue_size=100,
    steal_threshold=5  # Steal when queue has 5+ items
)

def variable_workload_task(workload):
    """Task with variable processing time"""
    duration = workload / 1000.0  # Convert to seconds
    time.sleep(duration)
    return f"Completed workload {workload}"

# Tasks with varying workloads (some workers will finish faster)
workloads = [100, 500, 50, 800, 25, 600, 75, 400, 900, 150]

# Work stealing automatically balances load
start_time = time.time()
results = ws_scheduler.execute_tasks(variable_workload_task, workloads)
end_time = time.time()

print(f"Work stealing completed {len(results)} tasks in {end_time - start_time:.2f}s")
print("Sample results:", results[:3])
```

### RoundRobinScheduler

Distributes tasks evenly across workers in a rotating fashion.

```python
import pyferris

# Create round-robin scheduler
rr_scheduler = pyferris.RoundRobinScheduler(num_workers=4)

def data_processing_task(data_chunk):
    """Process a chunk of data"""
    processed = [item.upper() for item in data_chunk]
    return f"Processed {len(processed)} items"

# Divide data into chunks for even distribution
data = ["item1", "item2", "item3", "item4", "item5", "item6", "item7", "item8"]
chunk_size = 2
data_chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

# Round-robin ensures even distribution
results = rr_scheduler.execute_tasks(data_processing_task, data_chunks)
print(f"Round-robin processed {len(results)} chunks")
print("Results:", results)
```

### AdaptiveScheduler

Intelligently adjusts scheduling based on system load and task characteristics.

```python
import pyferris

# Create adaptive scheduler
adaptive_scheduler = pyferris.AdaptiveScheduler(
    initial_workers=2,
    max_workers=8,
    load_threshold=0.8,  # Scale up when 80% loaded
    scale_factor=1.5     # Increase workers by 50%
)

def cpu_intensive_task(complexity):
    """CPU-intensive task with varying complexity"""
    result = 0
    for i in range(complexity * 1000):
        result += i ** 2
    return result % 1000000

# Mix of simple and complex tasks
complexities = [10, 100, 50, 200, 25, 150, 75, 300]

# Adaptive scheduler adjusts worker count based on load
results = adaptive_scheduler.execute_tasks(cpu_intensive_task, complexities)
print(f"Adaptive scheduling processed {len(results)} tasks")
print(f"Final worker count: {adaptive_scheduler.current_workers}")
```

### PriorityScheduler

Executes tasks based on assigned priority levels.

```python
import pyferris

# Create priority scheduler
priority_scheduler = pyferris.PriorityScheduler(num_workers=3)

def important_calculation(value):
    return value ** 2 + value

def background_cleanup(item):
    return f"Cleaned {item}"

def critical_alert(message):
    return f"ALERT: {message}"

# Create tasks with different priorities
tasks = [
    pyferris.create_priority_task(
        lambda: critical_alert("System overload"), 
        pyferris.TaskPriority.CRITICAL
    ),
    pyferris.create_priority_task(
        lambda: important_calculation(42),
        pyferris.TaskPriority.HIGH
    ),
    pyferris.create_priority_task(
        lambda: background_cleanup("temp_files"),
        pyferris.TaskPriority.LOW
    ),
    pyferris.create_priority_task(
        lambda: important_calculation(24),
        pyferris.TaskPriority.NORMAL
    ),
]

# Execute in priority order (Critical -> High -> Normal -> Low)
results = priority_scheduler.execute_priority_tasks(tasks)
print("Priority execution results:")
for i, result in enumerate(results):
    print(f"  {i+1}: {result}")
```

## Task Priority System

### Priority Levels

```python
import pyferris

# Available priority levels
priorities = [
    pyferris.TaskPriority.CRITICAL,  # Highest priority
    pyferris.TaskPriority.HIGH,      # High priority
    pyferris.TaskPriority.NORMAL,    # Default priority
    pyferris.TaskPriority.LOW,       # Low priority
    pyferris.TaskPriority.BACKGROUND # Lowest priority
]

def demonstrate_priorities():
    """Demonstrate task priority system"""
    
    def make_task(name, priority):
        return pyferris.create_priority_task(
            lambda: f"Executed {name}",
            priority
        )
    
    # Create tasks with different priorities
    tasks = [
        make_task("Background Sync", pyferris.TaskPriority.BACKGROUND),
        make_task("Critical Alert", pyferris.TaskPriority.CRITICAL),
        make_task("Normal Processing", pyferris.TaskPriority.NORMAL),
        make_task("High Priority Report", pyferris.TaskPriority.HIGH),
        make_task("Low Priority Cleanup", pyferris.TaskPriority.LOW),
    ]
    
    # Execute with priority scheduling
    results = pyferris.execute_with_priority(tasks)
    
    print("Execution order (by priority):")
    for result in results:
        print(f"  {result}")

demonstrate_priorities()
```

### Dynamic Priority Adjustment

```python
import pyferris

class DynamicPriorityScheduler:
    def __init__(self):
        self.scheduler = pyferris.PriorityScheduler()
        self.task_history = {}
    
    def adjust_priority(self, task_id, base_priority, execution_time):
        """Adjust priority based on execution time"""
        if execution_time > 5.0:  # Long-running tasks get lower priority
            if base_priority == pyferris.TaskPriority.HIGH:
                return pyferris.TaskPriority.NORMAL
            elif base_priority == pyferris.TaskPriority.NORMAL:
                return pyferris.TaskPriority.LOW
        return base_priority
    
    def execute_with_dynamic_priority(self, task_specs):
        """Execute tasks with dynamic priority adjustment"""
        adjusted_tasks = []
        
        for task_id, task_func, base_priority in task_specs:
            # Get historical execution time
            avg_time = self.task_history.get(task_id, 0.0)
            
            # Adjust priority based on history
            actual_priority = self.adjust_priority(task_id, base_priority, avg_time)
            
            # Create task with adjusted priority
            priority_task = pyferris.create_priority_task(task_func, actual_priority)
            adjusted_tasks.append(priority_task)
        
        return self.scheduler.execute_priority_tasks(adjusted_tasks)

# Example usage
dynamic_scheduler = DynamicPriorityScheduler()

task_specs = [
    ("fast_task", lambda: "Quick operation", pyferris.TaskPriority.NORMAL),
    ("slow_task", lambda: "Slow operation", pyferris.TaskPriority.HIGH),
    ("medium_task", lambda: "Medium operation", pyferris.TaskPriority.NORMAL),
]

results = dynamic_scheduler.execute_with_dynamic_priority(task_specs)
print("Dynamic priority results:", results)
```

## Advanced Scheduling Patterns

### Load-Aware Scheduling

```python
import pyferris
import psutil
import time

class LoadAwareScheduler:
    def __init__(self):
        self.schedulers = {
            'light': pyferris.RoundRobinScheduler(num_workers=2),
            'medium': pyferris.AdaptiveScheduler(initial_workers=4, max_workers=6),
            'heavy': pyferris.WorkStealingScheduler(num_workers=8)
        }
    
    def get_system_load(self):
        """Get current system load level"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        
        avg_load = (cpu_percent + memory_percent) / 2
        
        if avg_load < 30:
            return 'light'
        elif avg_load < 70:
            return 'medium'
        else:
            return 'heavy'
    
    def execute_load_aware(self, task_func, task_data):
        """Execute tasks using load-appropriate scheduler"""
        load_level = self.get_system_load()
        scheduler = self.schedulers[load_level]
        
        print(f"System load level: {load_level}")
        return scheduler.execute_tasks(task_func, task_data)

# Example usage
load_scheduler = LoadAwareScheduler()

def computational_task(n):
    return sum(i ** 2 for i in range(n))

tasks = [100, 200, 150, 300, 250]
results = load_scheduler.execute_load_aware(computational_task, tasks)
print(f"Load-aware execution completed: {len(results)} results")
```

### Deadline-Based Scheduling

```python
import pyferris
import time
from datetime import datetime, timedelta

class DeadlineScheduler:
    def __init__(self):
        self.priority_scheduler = pyferris.PriorityScheduler()
    
    def create_deadline_task(self, task_func, deadline_seconds):
        """Create task with deadline-based priority"""
        current_time = time.time()
        deadline_time = current_time + deadline_seconds
        
        # Closer deadlines get higher priority
        if deadline_seconds < 10:
            priority = pyferris.TaskPriority.CRITICAL
        elif deadline_seconds < 30:
            priority = pyferris.TaskPriority.HIGH
        elif deadline_seconds < 60:
            priority = pyferris.TaskPriority.NORMAL
        else:
            priority = pyferris.TaskPriority.LOW
        
        def deadline_wrapper():
            result = task_func()
            completion_time = time.time()
            missed_deadline = completion_time > deadline_time
            return {
                'result': result,
                'deadline_met': not missed_deadline,
                'completion_time': completion_time
            }
        
        return pyferris.create_priority_task(deadline_wrapper, priority)
    
    def execute_with_deadlines(self, task_specs):
        """Execute tasks prioritized by deadlines"""
        deadline_tasks = []
        
        for task_func, deadline_seconds in task_specs:
            task = self.create_deadline_task(task_func, deadline_seconds)
            deadline_tasks.append(task)
        
        return self.priority_scheduler.execute_priority_tasks(deadline_tasks)

# Example usage
deadline_scheduler = DeadlineScheduler()

task_specs = [
    (lambda: "Urgent report", 5),      # 5 second deadline
    (lambda: "Daily backup", 120),     # 2 minute deadline
    (lambda: "Critical fix", 8),       # 8 second deadline
    (lambda: "Routine check", 60),     # 1 minute deadline
]

results = deadline_scheduler.execute_with_deadlines(task_specs)
print("Deadline-based execution:")
for i, result in enumerate(results):
    status = "✓" if result['deadline_met'] else "✗"
    print(f"  Task {i+1}: {result['result']} {status}")
```

### Multi-Queue Scheduling

```python
import pyferris
from collections import defaultdict

class MultiQueueScheduler:
    def __init__(self):
        self.queues = {
            'cpu_intensive': pyferris.WorkStealingScheduler(num_workers=4),
            'io_bound': pyferris.RoundRobinScheduler(num_workers=8),
            'memory_intensive': pyferris.AdaptiveScheduler(initial_workers=2, max_workers=4)
        }
        self.task_classification = defaultdict(list)
    
    def classify_task(self, task_func, task_type):
        """Classify task for appropriate queue"""
        return task_type  # Simplified classification
    
    def add_task(self, task_func, task_data, task_type):
        """Add task to appropriate queue"""
        queue_type = self.classify_task(task_func, task_type)
        self.task_classification[queue_type].append((task_func, task_data))
    
    def execute_all_queues(self):
        """Execute all queues concurrently"""
        import threading
        
        results = {}
        threads = []
        
        def execute_queue(queue_type, tasks):
            scheduler = self.queues[queue_type]
            queue_results = []
            
            for task_func, task_data in tasks:
                if isinstance(task_data, list):
                    result = scheduler.execute_tasks(task_func, task_data)
                else:
                    result = scheduler.execute_tasks(task_func, [task_data])
                queue_results.extend(result)
            
            results[queue_type] = queue_results
        
        # Start threads for each queue
        for queue_type, tasks in self.task_classification.items():
            thread = threading.Thread(
                target=execute_queue,
                args=(queue_type, tasks)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all queues to complete
        for thread in threads:
            thread.join()
        
        return results

# Example usage
multi_scheduler = MultiQueueScheduler()

# Add different types of tasks
def cpu_task(n):
    return sum(i ** 2 for i in range(n))

def io_task(filename):
    return f"Processed file: {filename}"

def memory_task(size):
    return f"Allocated {size}MB memory"

# Classify and add tasks
multi_scheduler.add_task(cpu_task, [1000, 2000, 1500], 'cpu_intensive')
multi_scheduler.add_task(io_task, ['file1.txt', 'file2.txt'], 'io_bound')
multi_scheduler.add_task(memory_task, [100, 200], 'memory_intensive')

# Execute all queues
all_results = multi_scheduler.execute_all_queues()
print("Multi-queue execution results:")
for queue_type, results in all_results.items():
    print(f"  {queue_type}: {len(results)} tasks completed")
```

## Integration Examples

### With Pipeline Processing

```python
import pyferris

def scheduler_pipeline_integration():
    """Integrate custom schedulers with pipeline processing"""
    
    # Create pipeline with different schedulers for different stages
    pipeline = pyferris.Pipeline()
    
    # Stage 1: Data preparation (round-robin for even distribution)
    def prepare_data_stage(raw_data):
        scheduler = pyferris.RoundRobinScheduler(num_workers=4)
        
        def prepare_item(item):
            return item.strip().lower()
        
        return scheduler.execute_tasks(prepare_item, raw_data)
    
    # Stage 2: Heavy processing (work-stealing for load balancing)
    def process_data_stage(prepared_data):
        scheduler = pyferris.WorkStealingScheduler(num_workers=6)
        
        def heavy_process(item):
            # Simulate heavy processing
            result = hash(item) % 1000000
            return f"processed_{result}"
        
        return scheduler.execute_tasks(heavy_process, prepared_data)
    
    # Stage 3: Priority-based finalization
    def finalize_stage(processed_data):
        scheduler = pyferris.PriorityScheduler()
        
        tasks = []
        for i, item in enumerate(processed_data):
            # Alternate priorities for demonstration
            priority = pyferris.TaskPriority.HIGH if i % 2 == 0 else pyferris.TaskPriority.NORMAL
            
            task = pyferris.create_priority_task(
                lambda item=item: f"final_{item}",
                priority
            )
            tasks.append(task)
        
        return scheduler.execute_priority_tasks(tasks)
    
    # Build pipeline
    pipeline.add_stage(prepare_data_stage)
    pipeline.add_stage(process_data_stage)
    pipeline.add_stage(finalize_stage)
    
    # Execute pipeline
    input_data = [f"  Raw Data {i}  " for i in range(10)]
    final_results = pipeline.execute(input_data)
    
    print(f"Pipeline with custom schedulers processed {len(final_results)} items")
    print("Sample results:", final_results[:3])

scheduler_pipeline_integration()
```

### With Async Operations

```python
import pyferris
import asyncio

async def async_scheduler_integration():
    """Integrate schedulers with async operations"""
    
    class AsyncAwareScheduler:
        def __init__(self):
            self.priority_scheduler = pyferris.PriorityScheduler()
        
        async def execute_async_tasks(self, async_task_specs):
            """Execute async tasks with priority scheduling"""
            
            # Convert async tasks to sync wrappers
            priority_tasks = []
            
            for async_func, args, priority in async_task_specs:
                def sync_wrapper(af=async_func, a=args):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(af(*a))
                    finally:
                        loop.close()
                
                task = pyferris.create_priority_task(sync_wrapper, priority)
                priority_tasks.append(task)
            
            # Execute with priority scheduling
            results = self.priority_scheduler.execute_priority_tasks(priority_tasks)
            return results
    
    # Define async functions
    async def async_fetch(url):
        await asyncio.sleep(0.1)  # Simulate network delay
        return f"Data from {url}"
    
    async def async_process(data):
        await asyncio.sleep(0.05)  # Simulate processing
        return data.upper()
    
    # Create scheduler
    async_scheduler = AsyncAwareScheduler()
    
    # Define task specifications
    task_specs = [
        (async_fetch, ("api.example.com",), pyferris.TaskPriority.HIGH),
        (async_process, ("background data",), pyferris.TaskPriority.LOW),
        (async_fetch, ("urgent.api.com",), pyferris.TaskPriority.CRITICAL),
        (async_process, ("normal data",), pyferris.TaskPriority.NORMAL),
    ]
    
    # Execute async tasks with priority scheduling
    results = await async_scheduler.execute_async_tasks(task_specs)
    print("Async scheduler results:", results)

# Run async integration example
# asyncio.run(async_scheduler_integration())
```

## Performance Monitoring

### Scheduler Performance Metrics

```python
import pyferris
import time
from collections import defaultdict

class PerformanceMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def benchmark_scheduler(self, scheduler, task_func, task_data, name):
        """Benchmark scheduler performance"""
        start_time = time.time()
        start_cpu = time.process_time()
        
        results = scheduler.execute_tasks(task_func, task_data)
        
        end_time = time.time()
        end_cpu = time.process_time()
        
        wall_time = end_time - start_time
        cpu_time = end_cpu - start_cpu
        
        self.metrics[name].append({
            'wall_time': wall_time,
            'cpu_time': cpu_time,
            'tasks_completed': len(results),
            'throughput': len(results) / wall_time if wall_time > 0 else 0
        })
        
        return results
    
    def compare_schedulers(self, task_func, task_data):
        """Compare different scheduler types"""
        schedulers = {
            'WorkStealing': pyferris.WorkStealingScheduler(num_workers=4),
            'RoundRobin': pyferris.RoundRobinScheduler(num_workers=4),
            'Adaptive': pyferris.AdaptiveScheduler(initial_workers=2, max_workers=6),
        }
        
        print(f"Benchmarking schedulers with {len(task_data)} tasks...")
        
        for name, scheduler in schedulers.items():
            print(f"\nTesting {name} scheduler...")
            results = self.benchmark_scheduler(scheduler, task_func, task_data, name)
            
            metrics = self.metrics[name][-1]
            print(f"  Wall time: {metrics['wall_time']:.3f}s")
            print(f"  CPU time: {metrics['cpu_time']:.3f}s")
            print(f"  Throughput: {metrics['throughput']:.1f} tasks/sec")
        
        return self.metrics

# Benchmark example
monitor = PerformanceMonitor()

def benchmark_task(complexity):
    """Task with variable complexity for benchmarking"""
    result = 0
    for i in range(complexity * 100):
        result += i % 1000
    return result

# Create mixed workload
mixed_workload = [10, 50, 25, 75, 40, 60, 30, 80, 20, 90] * 5

# Compare scheduler performance
performance_data = monitor.compare_schedulers(benchmark_task, mixed_workload)

# Find best performer
best_scheduler = None
best_throughput = 0

for scheduler_name, metrics_list in performance_data.items():
    avg_throughput = sum(m['throughput'] for m in metrics_list) / len(metrics_list)
    if avg_throughput > best_throughput:
        best_throughput = avg_throughput
        best_scheduler = scheduler_name

print(f"\nBest performing scheduler: {best_scheduler} ({best_throughput:.1f} tasks/sec)")
```

## Best Practices

### Scheduler Selection Guidelines

1. **WorkStealingScheduler** - Best for variable workloads and CPU-intensive tasks
2. **RoundRobinScheduler** - Best for uniform workloads and predictable tasks
3. **AdaptiveScheduler** - Best for dynamic workloads with changing requirements
4. **PriorityScheduler** - Best when task importance varies significantly

### Configuration Optimization

```python
import pyferris
import psutil

def optimize_scheduler_config():
    """Optimize scheduler configuration based on system capabilities"""
    
    # Get system information
    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    # Configure based on system capabilities
    if cpu_count >= 8 and memory_gb >= 16:
        # High-end system configuration
        return {
            'work_stealing': pyferris.WorkStealingScheduler(
                num_workers=cpu_count,
                queue_size=cpu_count * 20
            ),
            'adaptive': pyferris.AdaptiveScheduler(
                initial_workers=cpu_count // 2,
                max_workers=cpu_count * 2
            )
        }
    elif cpu_count >= 4 and memory_gb >= 8:
        # Mid-range system configuration
        return {
            'work_stealing': pyferris.WorkStealingScheduler(
                num_workers=cpu_count,
                queue_size=cpu_count * 10
            ),
            'adaptive': pyferris.AdaptiveScheduler(
                initial_workers=cpu_count // 2,
                max_workers=cpu_count
            )
        }
    else:
        # Low-end system configuration
        return {
            'round_robin': pyferris.RoundRobinScheduler(
                num_workers=max(2, cpu_count)
            ),
            'priority': pyferris.PriorityScheduler(
                num_workers=max(2, cpu_count)
            )
        }

# Get optimized configuration
optimal_schedulers = optimize_scheduler_config()
print("Optimal scheduler configuration:")
for name, scheduler in optimal_schedulers.items():
    print(f"  {name}: {type(scheduler).__name__}")
```

### Error Handling and Recovery

```python
import pyferris

class RobustScheduler:
    def __init__(self):
        self.primary_scheduler = pyferris.WorkStealingScheduler(num_workers=4)
        self.fallback_scheduler = pyferris.RoundRobinScheduler(num_workers=2)
    
    def execute_with_fallback(self, task_func, task_data):
        """Execute with automatic fallback on failure"""
        try:
            return self.primary_scheduler.execute_tasks(task_func, task_data)
        except Exception as e:
            print(f"Primary scheduler failed: {e}")
            print("Falling back to secondary scheduler...")
            
            try:
                return self.fallback_scheduler.execute_tasks(task_func, task_data)
            except Exception as e2:
                print(f"Fallback scheduler also failed: {e2}")
                # Final fallback: sequential execution
                print("Using sequential execution as last resort...")
                return [task_func(item) for item in task_data]

# Example usage
robust_scheduler = RobustScheduler()

def potentially_failing_task(item):
    if item > 100:
        raise ValueError(f"Item {item} is too large")
    return item * 2

# This will demonstrate fallback behavior
test_data = [1, 2, 150, 4, 5]  # 150 will cause failure
results = robust_scheduler.execute_with_fallback(potentially_failing_task, test_data)
print("Robust execution results:", results)
```

## API Reference

### Scheduler Classes

```python
class WorkStealingScheduler:
    def __init__(self, num_workers: int, queue_size: int = 100, steal_threshold: int = 5)
    def execute_tasks(self, task_func: Callable, task_data: List[Any]) -> List[Any]

class RoundRobinScheduler:
    def __init__(self, num_workers: int)
    def execute_tasks(self, task_func: Callable, task_data: List[Any]) -> List[Any]

class AdaptiveScheduler:
    def __init__(self, initial_workers: int, max_workers: int, load_threshold: float = 0.8)
    def execute_tasks(self, task_func: Callable, task_data: List[Any]) -> List[Any]
    @property
    def current_workers(self) -> int

class PriorityScheduler:
    def __init__(self, num_workers: int = None)
    def execute_priority_tasks(self, priority_tasks: List[PriorityTask]) -> List[Any]
```

### Priority System

```python
class TaskPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

def create_priority_task(task_func: Callable, priority: TaskPriority) -> PriorityTask
def execute_with_priority(priority_tasks: List[PriorityTask]) -> List[Any]
```

This comprehensive custom scheduler documentation provides all the tools needed to optimize task execution and resource utilization in PyFerris applications.
