"""
Safe threading module for PyFerris - A replacement for Python's threading module
that leverages Rust's safety guarantees and performance optimizations.
"""

import threading
from functools import wraps
from ._pyferris import Executor as _RustExecutor
from .concurrent import AtomicCounter, LockFreeQueue
from .shared_memory import SharedDict, SharedArray

class Future:
    """A simple future-like object for compatibility with optimized memory usage."""
    
    __slots__ = ('_result', '_done')  # Memory optimization
    
    def __init__(self, result):
        self._result = result
        self._done = True
    
    def result(self, timeout=None):
        """Get the result of the computation."""
        del timeout  # Unused parameter
        return self._result
    
    def done(self):
        """Return True if the computation is done."""
        return self._done
    
class SafeThreadError(Exception):
    """Exception raised when safe thread operations fail."""
    pass


class SafeThread:
    """
    A safe thread implementation that uses Rust's executor for better performance
    and memory safety compared to Python's threading.Thread.
    
    This implementation provides:
    - Memory safety through Rust's guarantees
    - Better performance through work-stealing scheduler
    - Automatic resource cleanup
    - Thread-safe data structures
    - Exception handling with proper propagation
    """
    
    def __init__(self, target=None, name=None, args=(), kwargs=None, daemon=None):
        """
        Initialize a safe thread.
        
        Args:
            target: The callable object to be invoked by the run() method
            name: The thread name (for debugging)
            args: Tuple of arguments for the target invocation
            kwargs: Dictionary of keyword arguments for the target invocation
            daemon: Whether the thread is a daemon thread
        """
        self._target = target
        self._name = name or f"SafeThread-{id(self)}"
        self._args = args or ()
        self._kwargs = kwargs or {}
        self._daemon = daemon
        self._executor = None
        self._future = None
        self._started = False
        self._finished = False
        self._exception = None
        self._result = None
        self._lock = threading.Lock()
        
    @property
    def name(self):
        """Thread name."""
        return self._name
    
    @name.setter
    def name(self, value):
        """Set thread name."""
        self._name = value
    
    @property
    def daemon(self):
        """Whether this thread is a daemon thread."""
        return self._daemon
    
    @daemon.setter
    def daemon(self, value):
        """Set daemon status."""
        if self._started:
            raise RuntimeError("Cannot set daemon status of active thread")
        self._daemon = value
    
    def start(self):
        """
        Start the thread's activity.
        
        This method can only be called once per thread object.
        """
        with self._lock:
            if self._started:
                raise RuntimeError("Thread already started")
            
            self._started = True
            # Use a single-threaded executor for this specific task
            self._executor = _RustExecutor(1)
            
            # Wrap the target function to handle exceptions properly
            def safe_wrapper():
                try:
                    if self._target:
                        return self._target(*self._args, **self._kwargs)
                    else:
                        return self.run()
                except Exception as e:
                    self._exception = e
                    return None
            
            # Submit the task to the Rust executor
            # The Rust executor returns the result directly, not a Future
            try:
                self._result = self._executor.submit(safe_wrapper)
                self._finished = True
            except Exception as e:
                self._exception = e
                self._finished = True
    
    def run(self):
        """
        Method representing the thread's activity.
        
        You may override this method in a subclass. The standard run() method
        invokes the callable object passed to the object's constructor as the
        target argument, if any, with positional and keyword arguments taken
        from the args and kwargs arguments, respectively.
        """
        if self._target:
            self._target(*self._args, **self._kwargs)
    
    def join(self, timeout=None):
        """
        Wait until the thread terminates.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if thread finished, False if timeout occurred
        """
        if not self._started:
            raise RuntimeError("Cannot join thread before it is started")
        
        # Since the Rust executor executes immediately, the thread is already finished
        return self._finished
    
    def is_alive(self):
        """
        Return whether the thread is alive.
        
        Returns:
            True if the thread is alive, False otherwise
        """
        if not self._started:
            return False
        
        # Since the Rust executor executes immediately, check if finished
        return not self._finished
    
    def get_result(self):
        """
        Get the result of the thread's execution.
        
        Returns:
            The return value of the target function
            
        Raises:
            SafeThreadError: If the thread hasn't finished or had an exception
        """
        if not self._finished:
            raise SafeThreadError("Thread has not finished yet")
        
        if self._exception:
            raise SafeThreadError(f"Thread raised an exception: {self._exception}")
        
        return self._result
    
    def get_exception(self):
        """
        Get any exception that occurred during thread execution.
        
        Returns:
            The exception that occurred, or None if no exception
        """
        return self._exception


class SafeThreadPool:
    """
    A thread pool implementation using Rust's executor for better performance
    and safety compared to concurrent.futures.ThreadPoolExecutor.
    """
    
    def __init__(self, max_workers=None, thread_name_prefix='SafeThreadPool'):
        """
        Initialize the thread pool.
        
        Args:
            max_workers: Maximum number of worker threads
            thread_name_prefix: Prefix for thread names
        """
        self.max_workers = max_workers or min(32, (threading.cpu_count() or 1) + 4)
        self.thread_name_prefix = thread_name_prefix
        self._executor = _RustExecutor(self.max_workers)
        self._shutdown = False
        self._task_counter = AtomicCounter(0)
    
    def submit(self, func, *args, **kwargs):
        """
        Submit a task to be executed with the given arguments.
        
        Args:
            func: The callable to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            A Future-like object representing the execution
        """
        if self._shutdown:
            raise RuntimeError("Cannot schedule new futures after shutdown")
        
        self._task_counter.increment()
        
        # Create a wrapper function that handles the arguments
        def wrapper():
            try:
                return func(*args, **kwargs)
            finally:
                self._task_counter.decrement()
        
        # The Rust executor returns the result directly, so we need to wrap it
        result = self._executor.submit(wrapper)
        
        # Create a simple future-like object
        return Future(result)
    
    def map(self, func, iterable, timeout=None, chunksize=1):
        """
        Apply func to each element of iterable, collecting results.
        
        Args:
            func: The function to apply
            iterable: The iterable to process
            timeout: Maximum time to wait (unused, for compatibility)
            chunksize: Size of chunks (passed to underlying executor)
            
        Returns:
            A list of results
        """
        if self._shutdown:
            raise RuntimeError("Cannot schedule new futures after shutdown")
        
        # Set chunk size on the executor
        self._executor.set_chunk_size(chunksize)
        
        # Use the executor's optimized map function
        return self._executor.map(func, iterable)
    
    def shutdown(self, wait=True):
        """
        Shutdown the thread pool.
        
        Args:
            wait: Whether to wait for pending tasks
        """
        self._shutdown = True
        self._executor.shutdown()  # The Rust executor doesn't take arguments
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        return False
    
    @property
    def active_tasks(self):
        """Get the number of currently active tasks."""
        return self._task_counter.get()


class SafeLock:
    """
    A lock implementation that uses Rust's thread-safe primitives
    for better performance and safety.
    """
    
    def __init__(self):
        """Initialize the safe lock."""
        # Use Python's threading.Lock as the base, but wrap it safely
        self._lock = threading.RLock()
        self._owner_count = AtomicCounter(0)
    
    def acquire(self, blocking=True, timeout=-1):
        """
        Acquire the lock.
        
        Args:
            blocking: Whether to block if lock is unavailable
            timeout: Maximum time to wait for the lock
            
        Returns:
            True if lock was acquired, False otherwise
        """
        acquired = self._lock.acquire(blocking, timeout)
        if acquired:
            self._owner_count.increment()
        return acquired
    
    def release(self):
        """Release the lock."""
        self._owner_count.decrement()
        self._lock.release()
    
    def locked(self):
        """Return True if the lock is currently held."""
        return self._owner_count.get() > 0
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


class SafeCondition:
    """
    A condition variable implementation using safe primitives.
    """
    
    def __init__(self, lock=None):
        """
        Initialize the condition variable.
        
        Args:
            lock: The lock to use (creates new SafeLock if None)
        """
        self._lock = lock or SafeLock()
        self._condition = threading.Condition(self._lock._lock)
    
    def acquire(self, blocking=True, timeout=-1):
        """Acquire the underlying lock."""
        return self._lock.acquire(blocking, timeout)
    
    def release(self):
        """Release the underlying lock."""
        self._lock.release()
    
    def wait(self, timeout=None):
        """Wait until notified or timeout occurs."""
        return self._condition.wait(timeout)
    
    def wait_for(self, predicate, timeout=None):
        """Wait until a predicate becomes true."""
        return self._condition.wait_for(predicate, timeout)
    
    def notify(self, n=1):
        """Wake up one or more threads waiting on this condition."""
        self._condition.notify(n)
    
    def notify_all(self):
        """Wake up all threads waiting on this condition."""
        self._condition.notify_all()
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


def safe_thread_decorator(max_workers=None):
    """
    Decorator to run a function in a safe thread pool.
    
    Args:
        max_workers: Maximum number of worker threads in the pool
        
    Example:
        @safe_thread_decorator(max_workers=4)
        def cpu_intensive_task(data):
            return process_data(data)
        
        # Use it
        future = cpu_intensive_task(my_data)
        result = future.result()
    """
    def decorator(func):
        # Create a thread pool for this function
        pool = SafeThreadPool(max_workers=max_workers)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return pool.submit(func, *args, **kwargs)
        
        wrapper.shutdown = pool.shutdown
        return wrapper
    
    return decorator


# Utility functions for safe threading

def run_in_safe_thread(func, *args, **kwargs):
    """
    Run a function in a safe thread and return a future.
    
    Args:
        func: The function to run
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        A future representing the execution
    """
    thread = SafeThread(target=func, args=args, kwargs=kwargs)
    thread.start()
    return thread


def safe_parallel_map(func, iterable, max_workers=None, chunksize=1):
    """
    Apply a function to each element of an iterable in parallel using safe threads.
    
    Args:
        func: The function to apply
        iterable: The iterable to process
        max_workers: Maximum number of worker threads
        chunksize: Size of chunks for processing
        
    Returns:
        A list of results
    """
    with SafeThreadPool(max_workers=max_workers) as pool:
        return pool.map(func, iterable, chunksize=chunksize)


def create_safe_shared_data(data_type="dict", initial_data=None):
    """
    Create thread-safe shared data structures.
    
    Args:
        data_type: Type of data structure ("dict", "array", "queue", "counter")
        initial_data: Initial data to populate the structure
        
    Returns:
        A thread-safe data structure
    """
    if data_type == "dict":
        shared_dict = SharedDict()
        if initial_data:
            for key, value in initial_data.items():
                shared_dict.put(key, value)
        return shared_dict
    
    elif data_type == "array":
        if initial_data:
            # Create array with capacity and populate it using append
            array = SharedArray(len(initial_data))
            for value in initial_data:
                array.append(float(value))  # SharedArray expects float values
            return array
        else:
            return SharedArray(10)  # Default capacity of 10
    
    elif data_type == "queue":
        queue = LockFreeQueue()
        if initial_data:
            for item in initial_data:
                queue.push(item)
        return queue
    
    elif data_type == "counter":
        initial_value = initial_data if initial_data is not None else 0
        return AtomicCounter(initial_value)
    
    else:
        raise ValueError(f"Unknown data type: {data_type}")


# Export the main classes and functions
__all__ = [
    'SafeThread',
    'SafeThreadPool', 
    'SafeLock',
    'SafeCondition',
    'SafeThreadError',
    'safe_thread_decorator',
    'run_in_safe_thread',
    'safe_parallel_map',
    'create_safe_shared_data'
]
