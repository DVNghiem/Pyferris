"""
Task executor for managing parallel tasks.
"""
import typing
from ._pyferris import Executor as _Executor

class Executor:

    def __init__(self, max_workers: int = 4):
        """
        Initialize the executor with a specified number of worker threads.
        
        :param max_workers: Maximum number of worker threads to use.
        """
        self._executor = _Executor(max_workers)

    def submit(self, func, args=None):
        """
        Submit a task to be executed by the executor.
        
        :param func: The function to execute.
        :param args: Optional arguments to pass to the function.
        :return: A future representing the execution of the task.
        """
        return self._executor.submit(func, args)
    
    def map(self, func: typing.Callable, iterable: typing.Iterable) -> list:
        """
        Map a function over an iterable using the executor.
        
        :param func: The function to apply to each item in the iterable.
        :param iterable: An iterable of items to process.
        :return: A list of results from applying the function to each item.
        """
        return self._executor.map(func, iterable)

    def shutdown(self):
        """
        Shutdown the executor, optionally waiting for all tasks to complete.
        """
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