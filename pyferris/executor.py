"""
Task executor for managing parallel tasks with performance optimizations.
"""
import typing
import functools
import concurrent.futures
import gc
import weakref
from ._pyferris import Executor as _Executor

# Global executor pool to reuse executors and reduce overhead
_EXECUTOR_POOL = weakref.WeakValueDictionary()
_POOL_LOCK = None

def _get_pool_lock():
    global _POOL_LOCK
    if _POOL_LOCK is None:
        import threading
        _POOL_LOCK = threading.Lock()
    return _POOL_LOCK



class Executor(concurrent.futures.Executor):
    """High-performance parallel task executor with memory optimizations."""

    def __init__(self, max_workers: int = 4):
        """
        Initialize the executor with a specified number of worker threads.
        
        :param max_workers: Maximum number of worker threads to use.
        """
        super().__init__()
        
        # Try to reuse existing executor from pool
        pool_key = max_workers
        with _get_pool_lock():
            if pool_key in _EXECUTOR_POOL:
                cached_executor = _EXECUTOR_POOL[pool_key]
                if cached_executor.is_active():
                    self._executor = cached_executor._executor
                    self._shutdown = cached_executor._shutdown
                    return
        
        self._executor = _Executor(max_workers)
        self._shutdown = False
        
        # Cache this executor for reuse
        with _get_pool_lock():
            _EXECUTOR_POOL[pool_key] = self

    def submit(self, func, *args, **kwargs):
        """
        Submit a task to be executed by the executor with optimized argument handling.
        
        :param func: The function to execute.
        :param args: Positional arguments to pass to the function.
        :param kwargs: Keyword arguments to pass to the function.
        :return: A future representing the execution of the task.
        """
        if self._shutdown:
            raise RuntimeError("Cannot schedule new futures after shutdown")
        
        try:
            if args or kwargs:
                # Create a bound function with the arguments - optimized version
                bound_func = functools.partial(func, *args, **kwargs)
                result = self._executor.submit(bound_func)
            else:
                # Call with no arguments
                result = self._executor.submit(func)
            
            # Create a completed concurrent.futures.Future with the result
            future = concurrent.futures.Future()
            future.set_result(result)
            return future
        except Exception as e:
            # Enhanced error handling with memory management
            if "memory" in str(e).lower():
                gc.collect()  # Force garbage collection on memory errors
                # Retry once after garbage collection
                if args or kwargs:
                    bound_func = functools.partial(func, *args, **kwargs)
                    result = self._executor.submit(bound_func)
                else:
                    result = self._executor.submit(func)
                
                future = concurrent.futures.Future()
                future.set_result(result)
                return future
            raise
    
    def get_worker_count(self):
        """
        Get the number of worker threads in this executor.
        
        :return: Number of worker threads.
        """
        return self._executor.get_worker_count()
    
    def is_active(self):
        """
        Check if the executor is still active (not shut down).
        
        :return: True if the executor is active, False otherwise.
        """
        return self._executor.is_active()
    
    def map(self, func: typing.Callable, iterable: typing.Iterable) -> list:
        """
        Map a function over an iterable using the executor with memory optimization.
        
        :param func: The function to apply to each item in the iterable.
        :param iterable: An iterable of items to process.
        :return: A list of results from applying the function to each item.
        """
        try:
            return self._executor.map(func, iterable)
        except Exception as e:
            if "memory" in str(e).lower():
                gc.collect()  # Force garbage collection on memory errors
                return self._executor.map(func, iterable)
            raise

    def set_chunk_size(self, chunk_size: int):
        """
        Set the minimum chunk size for parallel processing.
        
        For small datasets, parallel processing overhead might outweigh benefits.
        This sets the threshold below which sequential processing is used.
        
        :param chunk_size: Minimum number of items to use parallel processing.
        """
        self._executor.set_chunk_size(chunk_size)
    
    def get_chunk_size(self) -> int:
        """
        Get the current chunk size threshold.
        
        :return: Current chunk size threshold.
        """
        return self._executor.get_chunk_size()

    def shutdown(self, wait=True):
        """
        Shutdown the executor, optionally waiting for all tasks to complete.
        
        :param wait: If True, wait for all tasks to complete before shutting down.
        """
        del wait  # Unused parameter - underlying Rust implementation handles synchronization
        self._shutdown = True
        self._executor.shutdown()

    def __enter__(self):
        """
        Enter the runtime context related to this executor.
        
        :return: The executor instance.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context related to this executor.
        """
        del exc_type, exc_value, traceback  # Unused parameters
        self.shutdown()
        return False

    def submit_computation(self, computation_type: str, data: list) -> float:
        """
        Submit a pure Rust computation task that can truly benefit from parallelism.
        
        This method performs computations entirely in Rust without Python callback overhead,
        allowing for true parallel speedup on CPU-bound tasks.
        
        :param computation_type: Type of computation ('sum', 'product', 'square_sum', 'heavy_computation')
        :param data: List of numbers to process
        :return: Computation result
        """
        try:
            # Use a simple approach - the Rust side will handle Python acquisition
            return self._executor.submit_computation(computation_type, data)
        except Exception as e:
            if "memory" in str(e).lower():
                gc.collect()  # Force garbage collection on memory errors
                return self._executor.submit_computation(computation_type, data)
            raise
    
    def submit_batch(self, tasks: list) -> list:
        """
        Submit multiple tasks for batch execution with optimized memory usage.
        
        :param tasks: List of tuples (function, args_tuple_or_None)
        :return: List of results
        """
        try:
            # Convert Python tasks to the format expected by Rust - optimized version
            rust_tasks = []
            for task in tasks:
                if isinstance(task, tuple) and len(task) == 2:
                    func, args = task
                    rust_tasks.append((func, args))
                else:
                    # Assume it's just a function with no args
                    rust_tasks.append((task, None))
            
            return self._executor.submit_batch(rust_tasks)
        except Exception as e:
            if "memory" in str(e).lower():
                gc.collect()  # Force garbage collection on memory errors
                # Retry with smaller batch size if possible
                if len(tasks) > 10:
                    # Split into smaller batches
                    mid = len(tasks) // 2
                    result1 = self.submit_batch(tasks[:mid])
                    result2 = self.submit_batch(tasks[mid:])
                    return result1 + result2
                else:
                    return self._executor.submit_batch(rust_tasks)
            raise

__all__ = ["Executor"]