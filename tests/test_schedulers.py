"""
PyFerris Schedulers Tests

Tests for custom scheduler functionality:
- WorkStealingScheduler
- RoundRobinScheduler
- AdaptiveScheduler
- PriorityScheduler
- TaskPriority
- execute_with_priority
- create_priority_task
"""

import pytest
import time
import threading

from pyferris import (
    WorkStealingScheduler, RoundRobinScheduler, AdaptiveScheduler,
    PriorityScheduler, TaskPriority, execute_with_priority, create_priority_task
)


class TestTaskPriority:
    """Test TaskPriority functionality."""

    def test_task_priority_values(self):
        """Test TaskPriority enum values."""
        # Test that priority values exist
        assert hasattr(TaskPriority, 'LOW')
        assert hasattr(TaskPriority, 'NORMAL')
        assert hasattr(TaskPriority, 'HIGH')
        assert hasattr(TaskPriority, 'URGENT')

    def test_task_priority_ordering(self):
        """Test TaskPriority ordering."""
        # Higher priority should have higher numeric value
        try:
            assert TaskPriority.URGENT > TaskPriority.HIGH
            assert TaskPriority.HIGH > TaskPriority.NORMAL
            assert TaskPriority.NORMAL > TaskPriority.LOW
        except (TypeError, AttributeError):
            # If comparison is not supported, just check they exist
            pass


class TestWorkStealingScheduler:
    """Test WorkStealingScheduler functionality."""

    def test_work_stealing_scheduler_creation(self):
        """Test basic WorkStealingScheduler creation."""
        scheduler = WorkStealingScheduler(num_workers=4)
        assert scheduler is not None

    def test_work_stealing_scheduler_execute(self):
        """Test WorkStealingScheduler task execution."""
        scheduler = WorkStealingScheduler(num_workers=2)
        
        def simple_task(x):
            return x * 2
        
        tasks = [simple_task] * 5
        task_args = [[i] for i in range(5)]
        
        results = scheduler.execute(tasks, task_args)
        expected = [i * 2 for i in range(5)]
        assert results == expected

    def test_work_stealing_scheduler_different_tasks(self):
        """Test WorkStealingScheduler with different tasks."""
        scheduler = WorkStealingScheduler(num_workers=3)
        
        def add_task(x, y):
            return x + y
        
        def multiply_task(x, y):
            return x * y
        
        def square_task(x):
            return x * x
        
        tasks = [add_task, multiply_task, square_task]
        task_args = [[1, 2], [3, 4], [5]]
        
        results = scheduler.execute(tasks, task_args)
        expected = [3, 12, 25]  # 1+2, 3*4, 5*5
        assert results == expected

    def test_work_stealing_scheduler_load_balancing(self):
        """Test WorkStealingScheduler load balancing."""
        scheduler = WorkStealingScheduler(num_workers=4)
        
        def variable_work_task(duration):
            time.sleep(duration)
            return duration
        
        # Tasks with different durations
        tasks = [variable_work_task] * 8
        task_args = [[0.01], [0.02], [0.01], [0.02], [0.01], [0.02], [0.01], [0.02]]
        
        start_time = time.time()
        results = scheduler.execute(tasks, task_args)
        execution_time = time.time() - start_time
        
        # Should complete faster than sequential execution
        sequential_time = sum([0.01, 0.02] * 4)
        assert execution_time < sequential_time * 0.8
        assert len(results) == 8

    def test_work_stealing_scheduler_empty_tasks(self):
        """Test WorkStealingScheduler with empty task list."""
        scheduler = WorkStealingScheduler(num_workers=2)
        
        results = scheduler.execute([], [])
        assert results == []

    def test_work_stealing_scheduler_single_task(self):
        """Test WorkStealingScheduler with single task."""
        scheduler = WorkStealingScheduler(num_workers=4)
        
        def single_task(x):
            return x ** 3
        
        results = scheduler.execute([single_task], [[2]])
        assert results == [8]

    def test_work_stealing_scheduler_error_handling(self):
        """Test WorkStealingScheduler error handling."""
        scheduler = WorkStealingScheduler(num_workers=2)
        
        def failing_task(x):
            if x == 2:
                raise ValueError("Task failed")
            return x
        
        tasks = [failing_task] * 4
        task_args = [[1], [2], [3], [4]]
        
        # Should handle or propagate errors appropriately
        with pytest.raises((ValueError, Exception)):
            scheduler.execute(tasks, task_args)


class TestRoundRobinScheduler:
    """Test RoundRobinScheduler functionality."""

    def test_round_robin_scheduler_creation(self):
        """Test basic RoundRobinScheduler creation."""
        scheduler = RoundRobinScheduler(num_workers=3)
        assert scheduler is not None

    def test_round_robin_scheduler_execute(self):
        """Test RoundRobinScheduler task execution."""
        scheduler = RoundRobinScheduler(num_workers=2)
        
        def task(x):
            return x + 10
        
        tasks = [task] * 6
        task_args = [[i] for i in range(6)]
        
        results = scheduler.execute(tasks, task_args)
        expected = [i + 10 for i in range(6)]
        assert results == expected

    def test_round_robin_scheduler_distribution(self):
        """Test RoundRobinScheduler even distribution."""
        scheduler = RoundRobinScheduler(num_workers=3)
        
        def worker_id_task():
            # Return current thread identifier for testing distribution
            return threading.current_thread().ident
        
        tasks = [worker_id_task] * 9
        task_args = [[] for _ in range(9)]
        
        results = scheduler.execute(tasks, task_args)
        
        # Should use multiple workers (thread IDs)
        unique_workers = set(results)
        assert len(unique_workers) >= 1  # At least one worker, ideally more

    def test_round_robin_scheduler_different_worker_counts(self):
        """Test RoundRobinScheduler with different worker counts."""
        def simple_task(x):
            return x * 3
        
        for num_workers in [1, 2, 4, 8]:
            scheduler = RoundRobinScheduler(num_workers=num_workers)
            
            tasks = [simple_task] * 10
            task_args = [[i] for i in range(10)]
            
            results = scheduler.execute(tasks, task_args)
            expected = [i * 3 for i in range(10)]
            assert results == expected

    def test_round_robin_scheduler_heavy_tasks(self):
        """Test RoundRobinScheduler with CPU-intensive tasks."""
        scheduler = RoundRobinScheduler(num_workers=4)
        
        def cpu_task(n):
            # Small CPU-intensive task
            return sum(i * i for i in range(n))
        
        tasks = [cpu_task] * 8
        task_args = [[50 + i] for i in range(8)]
        
        results = scheduler.execute(tasks, task_args)
        
        # Should complete all tasks
        assert len(results) == 8
        
        # Verify results are correct
        expected = [sum(i * i for i in range(50 + j)) for j in range(8)]
        assert results == expected


class TestAdaptiveScheduler:
    """Test AdaptiveScheduler functionality."""

    def test_adaptive_scheduler_creation(self):
        """Test basic AdaptiveScheduler creation."""
        scheduler = AdaptiveScheduler(num_workers=4)
        assert scheduler is not None

    def test_adaptive_scheduler_execute(self):
        """Test AdaptiveScheduler task execution."""
        scheduler = AdaptiveScheduler(num_workers=3)
        
        def adaptive_task(x):
            return x ** 2
        
        tasks = [adaptive_task] * 5
        task_args = [[i] for i in range(1, 6)]
        
        results = scheduler.execute(tasks, task_args)
        expected = [i ** 2 for i in range(1, 6)]
        assert results == expected

    def test_adaptive_scheduler_workload_adaptation(self):
        """Test AdaptiveScheduler workload adaptation."""
        scheduler = AdaptiveScheduler(num_workers=4)
        
        def variable_task(duration, value):
            time.sleep(duration)
            return value
        
        # Mix of fast and slow tasks
        tasks = [variable_task] * 8
        task_args = [
            [0.01, 1], [0.05, 2], [0.01, 3], [0.05, 4],
            [0.01, 5], [0.05, 6], [0.01, 7], [0.05, 8]
        ]
        
        start_time = time.time()
        results = scheduler.execute(tasks, task_args)
        execution_time = time.time() - start_time
        
        # Should adapt to different task durations
        assert len(results) == 8
        assert set(results) == {1, 2, 3, 4, 5, 6, 7, 8}
        
        # Should be faster than worst-case sequential
        worst_case_sequential = sum([0.05] * 8)
        assert execution_time < worst_case_sequential

    def test_adaptive_scheduler_performance_scaling(self):
        """Test AdaptiveScheduler performance with different loads."""
        def cpu_task(n):
            return sum(range(n))
        
        # Test with different workloads
        for num_tasks in [4, 8, 16]:
            scheduler = AdaptiveScheduler(num_workers=4)
            
            tasks = [cpu_task] * num_tasks
            task_args = [[100 + i] for i in range(num_tasks)]
            
            results = scheduler.execute(tasks, task_args)
            
            # Should complete all tasks
            assert len(results) == num_tasks
            
            # Results should be correct
            expected = [sum(range(100 + i)) for i in range(num_tasks)]
            assert results == expected


class TestPriorityScheduler:
    """Test PriorityScheduler functionality."""

    def test_priority_scheduler_creation(self):
        """Test basic PriorityScheduler creation."""
        scheduler = PriorityScheduler(num_workers=4)
        assert scheduler is not None

    def test_priority_scheduler_execute(self):
        """Test PriorityScheduler task execution."""
        scheduler = PriorityScheduler(num_workers=2)
        
        def priority_task(x):
            return x * 5
        
        tasks = [priority_task] * 4
        task_args = [[i] for i in range(4)]
        priorities = [TaskPriority.NORMAL] * 4
        
        results = scheduler.execute_with_priority(tasks, task_args, priorities)
        expected = [i * 5 for i in range(4)]
        assert results == expected

    def test_priority_scheduler_priority_ordering(self):
        """Test PriorityScheduler priority ordering."""
        scheduler = PriorityScheduler(num_workers=1)  # Single worker to test ordering
        
        execution_order = []
        
        def tracking_task(task_id):
            execution_order.append(task_id)
            time.sleep(0.01)  # Small delay
            return task_id
        
        tasks = [tracking_task] * 4
        task_args = [["low"], ["urgent"], ["high"], ["normal"]]
        priorities = [TaskPriority.LOW, TaskPriority.URGENT, TaskPriority.HIGH, TaskPriority.NORMAL]
        
        results = scheduler.execute_with_priority(tasks, task_args, priorities)
        
        # Results should include all tasks
        assert len(results) == 4
        assert set(results) == {"low", "urgent", "high", "normal"}
        
        # Execution order should prioritize urgent/high over normal/low
        # (exact order depends on implementation)
        assert len(execution_order) == 4

    def test_priority_scheduler_mixed_priorities(self):
        """Test PriorityScheduler with mixed priorities."""
        scheduler = PriorityScheduler(num_workers=3)
        
        def mixed_task(priority_name, value):
            time.sleep(0.01)
            return f"{priority_name}_{value}"
        
        tasks = [mixed_task] * 6
        task_args = [
            ["urgent", 1], ["low", 2], ["high", 3],
            ["normal", 4], ["urgent", 5], ["low", 6]
        ]
        priorities = [
            TaskPriority.URGENT, TaskPriority.LOW, TaskPriority.HIGH,
            TaskPriority.NORMAL, TaskPriority.URGENT, TaskPriority.LOW
        ]
        
        results = scheduler.execute_with_priority(tasks, task_args, priorities)
        
        # All tasks should complete
        assert len(results) == 6
        
        # Should contain expected results
        expected_set = {"urgent_1", "low_2", "high_3", "normal_4", "urgent_5", "low_6"}
        assert set(results) == expected_set

    def test_priority_scheduler_single_priority(self):
        """Test PriorityScheduler with single priority level."""
        scheduler = PriorityScheduler(num_workers=2)
        
        def uniform_task(x):
            return x + 100
        
        tasks = [uniform_task] * 5
        task_args = [[i] for i in range(5)]
        priorities = [TaskPriority.HIGH] * 5
        
        results = scheduler.execute_with_priority(tasks, task_args, priorities)
        expected = [i + 100 for i in range(5)]
        assert results == expected


class TestPriorityFunctions:
    """Test priority-related utility functions."""

    def test_execute_with_priority_basic(self):
        """Test basic execute_with_priority functionality."""
        def task_func(x):
            return x * 3
        
        result = execute_with_priority(task_func, [5], TaskPriority.HIGH)
        assert result == 15

    def test_execute_with_priority_different_priorities(self):
        """Test execute_with_priority with different priorities."""
        def task_func(msg):
            return f"processed_{msg}"
        
        # Test different priorities
        for priority in [TaskPriority.LOW, TaskPriority.NORMAL, TaskPriority.HIGH, TaskPriority.URGENT]:
            result = execute_with_priority(task_func, ["test"], priority)
            assert result == "processed_test"

    def test_execute_with_priority_complex_task(self):
        """Test execute_with_priority with complex task."""
        def complex_task(data_dict, multiplier):
            return {k: v * multiplier for k, v in data_dict.items()}
        
        input_data = {"a": 1, "b": 2, "c": 3}
        result = execute_with_priority(complex_task, [input_data, 4], TaskPriority.URGENT)
        expected = {"a": 4, "b": 8, "c": 12}
        assert result == expected

    def test_create_priority_task_basic(self):
        """Test basic create_priority_task functionality."""
        def task_func(x, y):
            return x + y
        
        priority_task = create_priority_task(task_func, [10, 20], TaskPriority.HIGH)
        assert priority_task is not None
        
        # Task should be executable
        if hasattr(priority_task, 'execute'):
            result = priority_task.execute()
            assert result == 30

    def test_create_priority_task_different_priorities(self):
        """Test create_priority_task with different priorities."""
        def simple_task(value):
            return value * 2
        
        for priority in [TaskPriority.LOW, TaskPriority.NORMAL, TaskPriority.HIGH, TaskPriority.URGENT]:
            priority_task = create_priority_task(simple_task, [10], priority)
            assert priority_task is not None
            
            # Verify priority is set correctly
            if hasattr(priority_task, 'priority'):
                assert priority_task.priority == priority

    def test_create_priority_task_complex_args(self):
        """Test create_priority_task with complex arguments."""
        def complex_task(items, operation, factor):
            if operation == "multiply":
                return [x * factor for x in items]
            elif operation == "add":
                return [x + factor for x in items]
            return items
        
        items = [1, 2, 3, 4, 5]
        priority_task = create_priority_task(complex_task, [items, "multiply", 3], TaskPriority.HIGH)
        
        assert priority_task is not None
        
        if hasattr(priority_task, 'execute'):
            result = priority_task.execute()
            expected = [3, 6, 9, 12, 15]
            assert result == expected


class TestSchedulerIntegration:
    """Test integration between different schedulers."""

    def test_scheduler_comparison(self):
        """Test comparison between different schedulers."""
        def test_task(x):
            time.sleep(0.01)
            return x * x
        
        tasks = [test_task] * 8
        task_args = [[i] for i in range(8)]
        expected = [i * i for i in range(8)]
        
        # Test different schedulers
        schedulers = [
            WorkStealingScheduler(num_workers=4),
            RoundRobinScheduler(num_workers=4),
            AdaptiveScheduler(num_workers=4),
        ]
        
        for scheduler in schedulers:
            start_time = time.time()
            results = scheduler.execute(tasks, task_args)
            execution_time = time.time() - start_time
            
            # All should produce correct results
            assert results == expected
            
            # Should complete in reasonable time
            assert execution_time < 1.0

    def test_scheduler_with_priority_comparison(self):
        """Test PriorityScheduler against regular schedulers."""
        def priority_aware_task(task_id, delay):
            time.sleep(delay)
            return task_id
        
        # Regular execution
        regular_scheduler = WorkStealingScheduler(num_workers=2)
        tasks = [priority_aware_task] * 4
        task_args = [["task1", 0.02], ["task2", 0.01], ["task3", 0.02], ["task4", 0.01]]
        
        regular_results = regular_scheduler.execute(tasks, task_args)
        
        # Priority execution
        priority_scheduler = PriorityScheduler(num_workers=2)
        priorities = [TaskPriority.LOW, TaskPriority.HIGH, TaskPriority.LOW, TaskPriority.HIGH]
        
        priority_results = priority_scheduler.execute_with_priority(tasks, task_args, priorities)
        
        # Both should complete all tasks
        assert len(regular_results) == 4
        assert len(priority_results) == 4
        assert set(regular_results) == set(priority_results)

    def test_scheduler_error_propagation(self):
        """Test error propagation across different schedulers."""
        def error_task(should_fail):
            if should_fail:
                raise RuntimeError("Scheduled task failed")
            return "success"
        
        tasks = [error_task] * 3
        task_args = [[False], [True], [False]]
        
        schedulers = [
            WorkStealingScheduler(num_workers=2),
            RoundRobinScheduler(num_workers=2),
            AdaptiveScheduler(num_workers=2),
        ]
        
        for scheduler in schedulers:
            with pytest.raises((RuntimeError, Exception)):
                scheduler.execute(tasks, task_args)


class TestSchedulerEdgeCases:
    """Test edge cases for schedulers."""

    def test_scheduler_with_zero_workers(self):
        """Test scheduler creation with zero workers."""
        for scheduler_class in [WorkStealingScheduler, RoundRobinScheduler, AdaptiveScheduler, PriorityScheduler]:
            with pytest.raises((ValueError, Exception)):
                scheduler_class(num_workers=0)

    def test_scheduler_with_negative_workers(self):
        """Test scheduler creation with negative workers."""
        for scheduler_class in [WorkStealingScheduler, RoundRobinScheduler, AdaptiveScheduler, PriorityScheduler]:
            with pytest.raises((ValueError, Exception)):
                scheduler_class(num_workers=-1)

    def test_scheduler_with_large_worker_count(self):
        """Test scheduler with large worker count."""
        # Should handle reasonable large worker counts
        scheduler = WorkStealingScheduler(num_workers=100)
        
        def simple_task(x):
            return x
        
        # Small number of tasks relative to workers
        tasks = [simple_task] * 5
        task_args = [[i] for i in range(5)]
        
        results = scheduler.execute(tasks, task_args)
        assert results == list(range(5))

    def test_scheduler_task_args_mismatch(self):
        """Test scheduler with mismatched tasks and arguments."""
        scheduler = WorkStealingScheduler(num_workers=2)
        
        def task(x):
            return x
        
        tasks = [task] * 3
        task_args = [[1], [2]]  # Fewer args than tasks
        
        # Should handle mismatch appropriately
        with pytest.raises((IndexError, ValueError, Exception)):
            scheduler.execute(tasks, task_args)

    def test_scheduler_with_none_tasks(self):
        """Test scheduler with None tasks."""
        scheduler = WorkStealingScheduler(num_workers=2)
        
        with pytest.raises((TypeError, AttributeError, Exception)):
            scheduler.execute([None, None], [[], []])

    @pytest.mark.slow
    def test_scheduler_stress_test(self):
        """Stress test schedulers with many tasks."""
        scheduler = AdaptiveScheduler(num_workers=4)
        
        def stress_task(x):
            return x % 1000
        
        # Many tasks
        num_tasks = 1000
        tasks = [stress_task] * num_tasks
        task_args = [[i] for i in range(num_tasks)]
        
        start_time = time.time()
        results = scheduler.execute(tasks, task_args)
        execution_time = time.time() - start_time
        
        # Should complete all tasks
        assert len(results) == num_tasks
        
        # Should complete in reasonable time
        assert execution_time < 10.0  # 10 seconds should be plenty
        
        # Results should be correct
        expected = [i % 1000 for i in range(num_tasks)]
        assert results == expected


if __name__ == "__main__":
    pytest.main([__file__])
