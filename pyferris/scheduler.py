"""
This module provides advanced scheduling strategies for optimal task distribution
and execution across multiple workers.
"""

from typing import Any, List, Callable, Tuple
from ._pyferris import (
    WorkStealingScheduler as _WorkStealingScheduler,
    RoundRobinScheduler as _RoundRobinScheduler, 
    AdaptiveScheduler as _AdaptiveScheduler,
    PriorityScheduler as _PriorityScheduler,
    TaskPriority as _TaskPriority
)


class TaskPriority:
    """
    Task priority levels for the PriorityScheduler.
    
    Attributes:
        High: Highest priority tasks (executed first)
        Normal: Standard priority tasks 
        Low: Lowest priority tasks (executed last)
        
        # Uppercase aliases for backwards compatibility
        HIGH: Alias for High
        NORMAL: Alias for Normal
        LOW: Alias for Low
        URGENT: Alias for High (highest priority)
    """
    High = _TaskPriority.High
    Normal = _TaskPriority.Normal
    Low = _TaskPriority.Low
    
    # Uppercase aliases for test compatibility
    HIGH = _TaskPriority.High
    NORMAL = _TaskPriority.Normal
    LOW = _TaskPriority.Low
    URGENT = _TaskPriority.High  # URGENT is treated as highest priority


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
    
    def __init__(self, workers: int = None, num_workers: int = None):
        """Initialize a WorkStealingScheduler with specified number of workers.
        
        Args:
            workers: Number of worker threads to use
            num_workers: Alternative parameter name for workers (for compatibility)
        """
        if workers is not None and num_workers is not None:
            raise ValueError("Cannot specify both 'workers' and 'num_workers'")
        
        worker_count = workers if workers is not None else num_workers
        if worker_count is None:
            raise ValueError("Must specify either 'workers' or 'num_workers'")
        if worker_count <= 0:
            raise ValueError("Number of workers must be positive")
            
        self._scheduler = _WorkStealingScheduler(worker_count)
    
    def execute(self, tasks: List[Callable], task_args: List[List] = None) -> List[Any]:
        """
        Execute tasks using work-stealing distribution.
        
        Args:
            tasks: A list of callable tasks.
            task_args: Optional list of argument lists for each task.
                      If None, tasks are assumed to be zero-argument callables.
        
        Returns:
            A list of results in the same order as the input tasks.
        
        Note:
            Work-stealing dynamically balances load between workers.
        """
        if task_args is None:
            # Direct execution of zero-argument tasks
            return self._scheduler.execute(tasks)
        else:
            # Check for mismatch between tasks and arguments
            if len(tasks) != len(task_args):
                raise ValueError(f"Number of tasks ({len(tasks)}) must match number of argument lists ({len(task_args)})")
            
            # Wrap tasks with their arguments
            wrapped_tasks = []
            for task, args in zip(tasks, task_args):
                if args:
                    def wrapped_task(t=task, a=args):
                        return t(*a)
                    wrapped_tasks.append(wrapped_task)
                else:
                    wrapped_tasks.append(task)
            return self._scheduler.execute(wrapped_tasks)


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
    
    def __init__(self, workers: int = None, num_workers: int = None):
        """Initialize a RoundRobinScheduler with specified number of workers.
        
        Args:
            workers: Number of worker threads to use
            num_workers: Alternative parameter name for workers (for compatibility)
        """
        if workers is not None and num_workers is not None:
            raise ValueError("Cannot specify both 'workers' and 'num_workers'")
        
        worker_count = workers if workers is not None else num_workers
        if worker_count is None:
            raise ValueError("Must specify either 'workers' or 'num_workers'")
        if worker_count <= 0:
            raise ValueError("Number of workers must be positive")
            
        self._scheduler = _RoundRobinScheduler(worker_count)
    
    def execute(self, tasks: List[Callable], task_args: List[List] = None) -> List[Any]:
        """
        Execute tasks using round-robin distribution.
        
        Args:
            tasks: A list of callable tasks.
            task_args: Optional list of argument lists for each task.
                      If None, tasks are assumed to be zero-argument callables.
        
        Returns:
            A list of results in the same order as the input tasks.
        
        Note:
            Round-robin works best when all tasks have similar execution times.
            For variable workloads, consider WorkStealingScheduler instead.
        """
        if task_args is None:
            # Direct execution of zero-argument tasks
            return self._scheduler.execute(tasks)
        else:
            # Check for mismatch between tasks and arguments
            if len(tasks) != len(task_args):
                raise ValueError(f"Number of tasks ({len(tasks)}) must match number of argument lists ({len(task_args)})")
            
            # Wrap tasks with their arguments
            wrapped_tasks = []
            for task, args in zip(tasks, task_args):
                if args:
                    def wrapped_task(t=task, a=args):
                        return t(*a)
                    wrapped_tasks.append(wrapped_task)
                else:
                    wrapped_tasks.append(task)
            return self._scheduler.execute(wrapped_tasks)


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
    
    def __init__(self, min_workers: int = None, max_workers: int = None, num_workers: int = None):
        """Initialize an AdaptiveScheduler with worker count bounds.
        
        Args:
            min_workers: Minimum number of workers
            max_workers: Maximum number of workers  
            num_workers: If specified, uses this as both min and max workers (for compatibility)
        """
        if num_workers is not None:
            if min_workers is not None or max_workers is not None:
                raise ValueError("Cannot specify 'num_workers' with 'min_workers' or 'max_workers'")
            min_workers = max_workers = num_workers
        elif min_workers is None or max_workers is None:
            raise ValueError("Must specify either 'num_workers' or both 'min_workers' and 'max_workers'")
        
        if min_workers <= 0 or max_workers <= 0:
            raise ValueError("Number of workers must be positive")
        if min_workers > max_workers:
            raise ValueError("min_workers cannot be greater than max_workers")
            
        self._scheduler = _AdaptiveScheduler(min_workers, max_workers)
    
    def execute(self, tasks: List[Callable], task_args: List[List] = None) -> List[Any]:
        """
        Execute tasks with adaptive worker scaling.
        
        Args:
            tasks: A list of callable tasks.
            task_args: Optional list of argument lists for each task.
                      If None, tasks are assumed to be zero-argument callables.
        
        Returns:
            A list of results in the same order as the input tasks.
        
        Note:
            The scheduler will automatically adjust the number of active
            workers based on workload size and system performance.
        """
        if task_args is None:
            # Direct execution of zero-argument tasks
            return self._scheduler.execute(tasks)
        else:
            # Check for mismatch between tasks and arguments
            if len(tasks) != len(task_args):
                raise ValueError(f"Number of tasks ({len(tasks)}) must match number of argument lists ({len(task_args)})")
            
            # Wrap tasks with their arguments
            wrapped_tasks = []
            for task, args in zip(tasks, task_args):
                if args:
                    def wrapped_task(t=task, a=args):
                        return t(*a)
                    wrapped_tasks.append(wrapped_task)
                else:
                    wrapped_tasks.append(task)
            return self._scheduler.execute(wrapped_tasks)
    
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
    
    def __init__(self, workers: int = None, num_workers: int = None):
        """Initialize a PriorityScheduler with specified number of workers.
        
        Args:
            workers: Number of worker threads to use
            num_workers: Alternative parameter name for workers (for compatibility)
        """
        if workers is not None and num_workers is not None:
            raise ValueError("Cannot specify both 'workers' and 'num_workers'")
        
        worker_count = workers if workers is not None else num_workers
        if worker_count is None:
            raise ValueError("Must specify either 'workers' or 'num_workers'")
        if worker_count <= 0:
            raise ValueError("Number of workers must be positive")
            
        self._scheduler = _PriorityScheduler(worker_count)
    
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
    
    def execute_with_priority(self, tasks: List[Callable], task_args: List[List], priorities: List[Any]) -> List[Any]:
        """
        Execute tasks with specified priorities.
        
        Args:
            tasks: A list of callable tasks.
            task_args: A list of argument lists for each task.
            priorities: A list of TaskPriority values for each task.
        
        Returns:
            A list of results. High priority tasks are executed first,
            followed by Normal, then Low priority tasks.
        """
        # Wrap tasks with their arguments and pair with priorities
        priority_tasks = []
        for task, args, priority in zip(tasks, task_args, priorities):
            if args:
                def wrapped_task(t=task, a=args):
                    return t(*a)
            else:
                wrapped_task = task
            priority_tasks.append((wrapped_task, priority))
        
        return self._scheduler.execute(priority_tasks)


def execute_with_priority(task: Callable, args: List, priority: Any) -> Any:
    """
    Execute a single task with specified priority.
    
    Convenience function for executing a single prioritized task.
    
    Args:
        task: A callable function.
        args: List of arguments to pass to the task.
        priority: A TaskPriority value.
    
    Returns:
        The result of executing the task.
    
    Example:
        >>> def multiply(x, y):
        ...     return x * y
        >>> result = execute_with_priority(multiply, [5, 3], TaskPriority.HIGH)
        >>> print(result)  # 15
    """
    # Execute the task directly with arguments
    return task(*args)


class PriorityTask:
    """A task wrapper that includes priority information and arguments."""
    
    def __init__(self, func: Callable, args: List, priority: Any):
        self.func = func
        self.args = args
        self.priority = priority
    
    def execute(self):
        """Execute the task with its arguments."""
        return self.func(*self.args)


def create_priority_task(task: Callable, args: List, priority: Any) -> PriorityTask:
    """
    Create a priority task object.
    
    Helper function to create a task object with priority information
    for use with priority schedulers.
    
    Args:
        task: A callable function.
        args: List of arguments to pass to the task.
        priority: A TaskPriority value.
    
    Returns:
        A PriorityTask object ready for priority scheduling.
    
    Example:
        >>> def multiply(x, y):
        ...     return x * y
        >>> priority_task = create_priority_task(multiply, [5, 3], TaskPriority.HIGH)
        >>> result = priority_task.execute()
        >>> print(result)  # 15
        >>> print(priority_task.priority)  # TaskPriority.HIGH
    """
    return PriorityTask(task, args, priority)


__all__ = [
    'WorkStealingScheduler', 'RoundRobinScheduler', 'AdaptiveScheduler',
    'PriorityScheduler', 'TaskPriority', 'execute_with_priority', 'create_priority_task', 'PriorityTask'
]
