"""
Task executor for managing parallel tasks.
"""
import typing
import functools
import concurrent.futures
from ._pyferris import Executor as _Executor

class Future:
    """A simple future-like object for compatibility."""
    
    def __init__(self, result):
        self._result = result
        self._done = True
    
    def result(self, timeout=None):
        """Get the result of the computation."""
        return self._result
    
    def done(self):
        """Return True if the computation is done."""
        return self._done

class Executor(concurrent.futures.Executor):

    def __init__(self, max_workers: int = 4):
        """
        Initialize the executor with a specified number of worker threads.
        
        :param max_workers: Maximum number of worker threads to use.
        """
        super().__init__()
        self._executor = _Executor(max_workers)
        self._shutdown = False

    def submit(self, func, *args, **kwargs):
        """
        Submit a task to be executed by the executor.
        
        :param func: The function to execute.
        :param args: Positional arguments to pass to the function.
        :param kwargs: Keyword arguments to pass to the function.
        :return: A future representing the execution of the task.
        """
        if self._shutdown:
            raise RuntimeError("Cannot schedule new futures after shutdown")
            
        if args or kwargs:
            # Create a bound function with the arguments
            bound_func = functools.partial(func, *args, **kwargs)
            result = self._executor.submit(bound_func)
        else:
            # Call with no arguments
            result = self._executor.submit(func)
        
        # Create a completed concurrent.futures.Future with the result
        future = concurrent.futures.Future()
        future.set_result(result)
        return future
    
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
        Map a function over an iterable using the executor.
        
        :param func: The function to apply to each item in the iterable.
        :param iterable: An iterable of items to process.
        :return: A list of results from applying the function to each item.
        """
        return self._executor.map(func, iterable)

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
        # Use a simple approach - the Rust side will handle Python acquisition
        return self._executor.submit_computation(computation_type, data)
    
    def submit_batch(self, tasks: list) -> list:
        """
        Submit multiple tasks for batch execution.
        
        :param tasks: List of tuples (function, args_tuple_or_None)
        :return: List of results
        """
        # Convert Python tasks to the format expected by Rust
        rust_tasks = []
        for task in tasks:
            if isinstance(task, tuple) and len(task) == 2:
                func, args = task
                rust_tasks.append((func, args))
            else:
                # Assume it's just a function with no args
                rust_tasks.append((task, None))
        
        return self._executor.submit_batch(rust_tasks)

__all__ = ["Executor"]