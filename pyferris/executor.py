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

__all__ = ["Executor"]