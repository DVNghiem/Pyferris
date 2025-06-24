"""
Level 3 Features - Custom Schedulers

This module provides advanced scheduling strategies for optimal task distribution
and execution across multiple workers.
"""

from typing import Any, List, Callable, Tuple
from ._pyferris import (
    WorkStealingScheduler as _WorkStealingScheduler,
    RoundRobinScheduler as _RoundRobinScheduler, 
    AdaptiveScheduler as _AdaptiveScheduler,
    PriorityScheduler as _PriorityScheduler,
    TaskPriority as _TaskPriority,
    execute_with_priority as _execute_with_priority,
    create_priority_task as _create_priority_task
)


class TaskPriority:
    """
    Task priority levels for the PriorityScheduler.
    
    Attributes:
        High: Highest priority tasks (executed first)
        Normal: Standard priority tasks 
        Low: Lowest priority tasks (executed last)
    """
    High = _TaskPriority.High
    Normal = _TaskPriority.Normal
    Low = _TaskPriority.Low


class WorkStealingScheduler:
    """
    A work-stealing scheduler for dynamic load balancing.
    
    Work-stealing is optimal for workloads with variable execution times.
    When a worker finishes its tasks, it can "steal" work from other workers
    that are still busy, ensuring optimal CPU utilization.
    
    Args:
        workers (int): Number of worker threads to use.
    
    Example:
        >>> scheduler = WorkStealingScheduler(workers=4)
        >>> 
        >>> def variable_work(x):
        ...     # Some tasks take longer than others
        ...     iterations = x * 1000 if x % 3 == 0 else x * 100
        ...     return sum(i for i in range(iterations))
        >>> 
        >>> tasks = [lambda x=i: variable_work(x) for i in range(20)]
        >>> results = scheduler.execute(tasks)
        >>> print(f"Processed {len(results)} tasks")
    """
    
    def __init__(self, workers: int):
        """Initialize a WorkStealingScheduler with specified number of workers."""
        self._scheduler = _WorkStealingScheduler(workers)
    
    def execute(self, tasks: List[Callable[[], Any]]) -> List[Any]:
        """
        Execute a list of tasks using work-stealing strategy.
        
        Args:
            tasks: A list of callable tasks (functions with no arguments).
                  Use lambda functions to capture arguments if needed.
        
        Returns:
            A list of results in the same order as the input tasks.
        
        Note:
            Work-stealing is particularly effective when tasks have
            variable execution times, as it automatically balances load.
        """
        return self._scheduler.execute(tasks)


class RoundRobinScheduler:
    """
    A round-robin scheduler for fair task distribution.
    
    Distributes tasks evenly across workers in a circular fashion.
    Good for workloads where tasks have similar execution times.
    
    Args:
        workers (int): Number of worker threads to use.
    
    Example:
        >>> scheduler = RoundRobinScheduler(workers=3)
        >>> 
        >>> # Tasks with similar execution time work well
        >>> simple_tasks = [lambda x=i: x ** 2 + i for i in range(15)]
        >>> results = scheduler.execute(simple_tasks)
        >>> print(results)  # [0, 2, 6, 12, 20, 30, 42, 56, 72, 90, ...]
    """
    
    def __init__(self, workers: int):
        """Initialize a RoundRobinScheduler with specified number of workers."""
        self._scheduler = _RoundRobinScheduler(workers)
    
    def execute(self, tasks: List[Callable[[], Any]]) -> List[Any]:
        """
        Execute tasks using round-robin distribution.
        
        Args:
            tasks: A list of callable tasks (functions with no arguments).
        
        Returns:
            A list of results in the same order as the input tasks.
        
        Note:
            Round-robin works best when all tasks have similar execution times.
            For variable workloads, consider WorkStealingScheduler instead.
        """
        return self._scheduler.execute(tasks)


class AdaptiveScheduler:
    """
    An adaptive scheduler that adjusts worker count based on workload.
    
    Automatically scales the number of workers up or down based on the
    current workload and system performance, optimizing resource usage.
    
    Args:
        min_workers (int): Minimum number of workers.
        max_workers (int): Maximum number of workers.
    
    Example:
        >>> scheduler = AdaptiveScheduler(min_workers=2, max_workers=8)
        >>> 
        >>> # Small workload uses fewer workers
        >>> small_tasks = [lambda x=i: x + 1 for i in range(5)]
        >>> small_results = scheduler.execute(small_tasks)
        >>> print(f"Used {scheduler.current_workers} workers for small workload")
        >>> 
        >>> # Large workload automatically scales up
        >>> large_tasks = [lambda x=i: x ** 2 for i in range(200)]
        >>> large_results = scheduler.execute(large_tasks)
        >>> print(f"Used {scheduler.current_workers} workers for large workload")
    """
    
    def __init__(self, min_workers: int, max_workers: int):
        """Initialize an AdaptiveScheduler with worker count bounds."""
        self._scheduler = _AdaptiveScheduler(min_workers, max_workers)
    
    def execute(self, tasks: List[Callable[[], Any]]) -> List[Any]:
        """
        Execute tasks with adaptive worker scaling.
        
        Args:
            tasks: A list of callable tasks (functions with no arguments).
        
        Returns:
            A list of results in the same order as the input tasks.
        
        Note:
            The scheduler will automatically adjust the number of active
            workers based on workload size and system performance.
        """
        return self._scheduler.execute(tasks)
    
    @property
    def current_workers(self) -> int:
        """Get the current number of active workers."""
        return self._scheduler.current_workers


class PriorityScheduler:
    """
    A priority-based scheduler for task execution.
    
    Executes tasks based on their priority level: High priority tasks
    are executed before Normal priority, which are executed before Low priority.
    
    Args:
        workers (int): Number of worker threads to use.
    
    Example:
        >>> scheduler = PriorityScheduler(workers=4)
        >>> 
        >>> # Create tasks with different priorities
        >>> high_task = lambda: "HIGH PRIORITY COMPLETED"
        >>> normal_task = lambda: "Normal task completed"
        >>> low_task = lambda: "Low priority completed"
        >>> 
        >>> priority_tasks = [
        ...     (low_task, TaskPriority.Low),
        ...     (normal_task, TaskPriority.Normal),
        ...     (high_task, TaskPriority.High),
        ...     (normal_task, TaskPriority.Normal),
        ... ]
        >>> 
        >>> results = scheduler.execute(priority_tasks)
        >>> # High priority tasks will be executed first
        >>> print(results)
    """
    
    def __init__(self, workers: int):
        """Initialize a PriorityScheduler with specified number of workers."""
        self._scheduler = _PriorityScheduler(workers)
    
    def execute(self, tasks: List[Tuple[Callable[[], Any], Any]]) -> List[Any]:
        """
        Execute tasks based on their priority.
        
        Args:
            tasks: A list of (task, priority) tuples where:
                  - task: A callable function with no arguments
                  - priority: A TaskPriority value (High, Normal, or Low)
        
        Returns:
            A list of results. High priority tasks are executed first,
            followed by Normal, then Low priority tasks.
        
        Note:
            Within the same priority level, tasks are executed in the
            order they appear in the input list.
        """
        return self._scheduler.execute(tasks)


def execute_with_priority(tasks: List[Tuple[Callable[[], Any], Any]], 
                         workers: int = 4) -> List[Any]:
    """
    Execute tasks with priority using a default PriorityScheduler.
    
    Convenience function for executing prioritized tasks without creating
    a scheduler object explicitly.
    
    Args:
        tasks: A list of (task, priority) tuples.
        workers: Number of worker threads (default: 4).
    
    Returns:
        A list of results ordered by priority.
    
    Example:
        >>> tasks = [
        ...     (lambda: "Low priority", TaskPriority.Low),
        ...     (lambda: "High priority", TaskPriority.High),
        ...     (lambda: "Normal priority", TaskPriority.Normal),
        ... ]
        >>> results = execute_with_priority(tasks, workers=2)
        >>> print(results)  # High priority result will be first
    """
    return _execute_with_priority(tasks, workers)


def create_priority_task(task: Callable[[], Any], priority: Any) -> Tuple[Callable[[], Any], Any]:
    """
    Create a priority task tuple.
    
    Helper function to create properly formatted (task, priority) tuples
    for use with priority schedulers.
    
    Args:
        task: A callable function with no arguments.
        priority: A TaskPriority value.
    
    Returns:
        A tuple of (task, priority) ready for priority scheduling.
    
    Example:
        >>> task = lambda: "Hello World"
        >>> priority_task = create_priority_task(task, TaskPriority.High)
        >>> tasks = [priority_task]
        >>> results = execute_with_priority(tasks)
    """
    return _create_priority_task(task, priority)


__all__ = [
    'WorkStealingScheduler', 'RoundRobinScheduler', 'AdaptiveScheduler',
    'PriorityScheduler', 'TaskPriority', 'execute_with_priority', 'create_priority_task'
]
