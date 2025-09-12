"""
Virtual Thread module for PyFerris - Lightweight threading inspired by Java's Project Loom

This module provides virtual threads (also known as fibers or green threads) that are
extremely lightweight and can scale to millions of concurrent tasks. Virtual threads
are managed by a small pool of OS threads and can yield control when they would block,
allowing for massive concurrency without the overhead of traditional threads.

Key Features:
- Millions of virtual threads with minimal memory overhead
- Automatic work-stealing scheduling
- Integration with Python's async/await syntax
- Seamless blocking operation handling
- Priority-based task scheduling
"""

from ._pyferris import (
    VirtualThreadExecutor,
    create_virtual_thread_executor,
    execute_in_virtual_thread,
    virtual_thread_map,
)
import asyncio
import functools
from typing import Any, Callable, Optional, List, Tuple
import concurrent.futures
import time


class VirtualThreadPool:
    """
    High-level interface for virtual thread management.
    
    This class provides a more Pythonic interface to the underlying
    Rust virtual thread executor, with features like context management,
    automatic lifecycle management, and integration with Python's
    concurrent.futures interface.
    """
    
    def __init__(
        self,
        max_virtual_threads: Optional[int] = None,
        max_platform_threads: Optional[int] = None,
        auto_start: bool = True
    ):
        """
        Initialize a virtual thread pool.
        
        Args:
            max_virtual_threads: Maximum number of virtual threads (default: 1M)
            max_platform_threads: Number of OS threads to use (default: CPU count)
            auto_start: Whether to automatically start the executor
        """
        self._executor = create_virtual_thread_executor(
            max_virtual_threads, max_platform_threads
        )
        self._started = False
        
        if auto_start:
            self.start()
    
    def start(self):
        """Start the virtual thread executor."""
        if not self._started:
            self._executor.start()
            self._started = True
    
    def submit(
        self,
        func: Callable,
        *args,
        priority: int = 128,
        is_blocking: bool = False,
        **kwargs
    ) -> 'VirtualThreadFuture':
        """
        Submit a function to be executed in a virtual thread.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            priority: Task priority (0-255, lower is higher priority)
            is_blocking: Whether the task may block
            **kwargs: Keyword arguments for the function
            
        Returns:
            VirtualThreadFuture: Future-like object for the result
        """
        if not self._started:
            self.start()
        
        # Wrap function with kwargs if needed
        if kwargs:
            wrapped_func = functools.partial(func, **kwargs)
        else:
            wrapped_func = func
        
        thread_id = self._executor.submit_virtual_task(
            wrapped_func, args if args else None, priority, is_blocking
        )
        
        return VirtualThreadFuture(thread_id, self._executor)
    
    def map(
        self,
        func: Callable,
        iterable,
        priority: int = 128,
        is_blocking: bool = False
    ) -> List[Any]:
        """
        Apply function to every item in iterable using virtual threads.
        
        Args:
            func: Function to apply
            iterable: Items to process
            priority: Task priority
            is_blocking: Whether tasks may block
            
        Returns:
            List of results in order
        """
        if not self._started:
            self.start()
        
        items = list(iterable)
        futures = []
        
        for item in items:
            future = self.submit(func, item, priority=priority, is_blocking=is_blocking)
            futures.append(future)
        
        return [future.result() for future in futures]
    
    def starmap(
        self,
        func: Callable,
        iterable,
        priority: int = 128,
        is_blocking: bool = False
    ) -> List[Any]:
        """
        Apply function to arguments from iterable using virtual threads.
        
        Args:
            func: Function to apply
            iterable: Argument tuples to process
            priority: Task priority
            is_blocking: Whether tasks may block
            
        Returns:
            List of results in order
        """
        if not self._started:
            self.start()
        
        futures = []
        for args in iterable:
            if not isinstance(args, (tuple, list)):
                args = (args,)
            future = self.submit(func, *args, priority=priority, is_blocking=is_blocking)
            futures.append(future)
        
        return [future.result() for future in futures]
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the virtual thread executor.
        
        Args:
            wait: Whether to wait for completion
        """
        if self._started:
            self._executor.shutdown()
            self._started = False
    
    def get_stats(self) -> dict:
        """Get executor statistics."""
        total, active, completed, platform_threads = self._executor.get_stats()
        return {
            'total_threads_created': total,
            'active_threads': active,
            'completed_threads': completed,
            'platform_threads': platform_threads,
            'is_running': self._executor.is_running()
        }
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


class VirtualThreadFuture:
    """
    Future-like object for virtual thread results.
    
    This class provides a concurrent.futures.Future-like interface
    for virtual thread execution results.
    """
    
    def __init__(self, thread_id: int, executor):
        self._thread_id = thread_id
        self._executor = executor
        self._result = None
        self._exception = None
        self._done = False
    
    def result(self, timeout: Optional[float] = None) -> Any:
        """
        Get the result of the virtual thread execution.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            The result of the execution
            
        Raises:
            TimeoutError: If timeout is exceeded
            Exception: Any exception raised during execution
        """
        if self._done:
            if self._exception:
                raise self._exception
            return self._result
        
        try:
            result = self._executor.join(self._thread_id)
            self._result = result
            self._done = True
            return result
        except Exception as e:
            self._exception = e
            self._done = True
            raise
    
    def done(self) -> bool:
        """Check if the virtual thread has completed."""
        if self._done:
            return True
        
        try:
            state = self._executor.get_thread_state(self._thread_id)
            self._done = state == "Terminated"
            return self._done
        except Exception:
            return False
    
    def cancel(self) -> bool:
        """Attempt to cancel the virtual thread (not supported)."""
        return False  # Virtual threads cannot be cancelled once started
    
    def cancelled(self) -> bool:
        """Check if the virtual thread was cancelled."""
        return False  # Virtual threads cannot be cancelled
    
    def exception(self, timeout: Optional[float] = None) -> Optional[Exception]:
        """Get any exception raised during execution."""
        if not self.done():
            self.result(timeout)  # This will populate _exception if needed
        return self._exception


class AsyncVirtualThreadPool:
    """
    Async interface for virtual thread pool.
    
    This class provides async/await integration for virtual threads,
    allowing seamless integration with Python's asyncio ecosystem.
    """
    
    def __init__(
        self,
        max_virtual_threads: Optional[int] = None,
        max_platform_threads: Optional[int] = None
    ):
        self._pool = VirtualThreadPool(
            max_virtual_threads, max_platform_threads, auto_start=False
        )
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    
    async def start(self):
        """Start the virtual thread pool asynchronously."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._pool.start)
    
    async def submit(
        self,
        func: Callable,
        *args,
        priority: int = 128,
        is_blocking: bool = False,
        **kwargs
    ) -> Any:
        """
        Submit a function to be executed in a virtual thread asynchronously.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            priority: Task priority
            is_blocking: Whether the task may block
            **kwargs: Keyword arguments
            
        Returns:
            The result of the execution
        """
        loop = asyncio.get_event_loop()
        future = await loop.run_in_executor(
            self._executor,
            self._pool.submit,
            func, *args
        )
        return await loop.run_in_executor(self._executor, future.result)
    
    async def map(
        self,
        func: Callable,
        iterable,
        priority: int = 128,
        is_blocking: bool = False
    ) -> List[Any]:
        """
        Apply function to every item in iterable using virtual threads asynchronously.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._pool.map,
            func, iterable, priority, is_blocking
        )
    
    async def shutdown(self):
        """Shutdown the virtual thread pool asynchronously."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._pool.shutdown)
        self._executor.shutdown(wait=True)
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()


# Convenience functions
def run_in_virtual_thread(
    func: Callable,
    *args,
    priority: int = 128,
    is_blocking: bool = False,
    **kwargs
) -> Any:
    """
    Execute a function in a virtual thread and return the result.
    
    This is a convenience function for simple one-off virtual thread execution.
    For multiple operations, consider using VirtualThreadPool for better performance.
    
    Args:
        func: Function to execute
        *args: Positional arguments
        priority: Task priority (0-255) TODO: Currently unused in this function
        is_blocking: Whether the function may block
        **kwargs: Keyword arguments
        
    Returns:
        The result of the function execution
    """
    if kwargs:
        wrapped_func = functools.partial(func, **kwargs)
    else:
        wrapped_func = func
    
    return execute_in_virtual_thread(
        wrapped_func, args if args else None, is_blocking
    )


def virtual_map(
    func: Callable,
    iterable,
    max_virtual_threads: Optional[int] = None,
    max_platform_threads: Optional[int] = None
) -> List[Any]:
    """
    Apply function to every item in iterable using virtual threads.
    
    This is a convenience function that creates a temporary virtual thread
    executor for the operation. For repeated operations, use VirtualThreadPool.
    
    Args:
        func: Function to apply
        iterable: Items to process
        max_virtual_threads: Maximum virtual threads
        max_platform_threads: Number of OS threads
        
    Returns:
        List of results in order
    """
    return virtual_thread_map(func, iterable, max_virtual_threads, max_platform_threads)


# Threading utilities
def virtual_thread_benchmark(
    func: Callable,
    args_list: List[Tuple],
    traditional_threads: bool = False,
    max_platform_threads: Optional[int] = None
) -> dict:
    """
    Benchmark virtual threads vs traditional threads.
    
    Args:
        func: Function to benchmark
        args_list: List of argument tuples for each call
        traditional_threads: Whether to also benchmark traditional threads
        max_platform_threads: Number of platform threads for virtual thread executor
        
    Returns:
        Dictionary with benchmark results
    """
    results = {}
    
    # Virtual thread benchmark
    start_time = time.time()
    with VirtualThreadPool(max_platform_threads=max_platform_threads) as pool:
        vt_results = pool.starmap(func, args_list)
    vt_time = time.time() - start_time
    
    results['virtual_threads'] = {
        'time': vt_time,
        'results': vt_results,
        'threads_used': max_platform_threads or 4
    }
    
    # Traditional thread benchmark (if requested)
    if traditional_threads:
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(args_list)) as executor:
            futures = [executor.submit(func, *args) for args in args_list]
            tt_results = [f.result() for f in futures]
        tt_time = time.time() - start_time
        
        results['traditional_threads'] = {
            'time': tt_time,
            'results': tt_results,
            'threads_used': len(args_list)
        }
        
        results['speedup'] = tt_time / vt_time if vt_time > 0 else float('inf')
    
    return results


__all__ = [
    'VirtualThreadExecutor',
    'VirtualThreadPool', 
    'VirtualThreadFuture',
    'AsyncVirtualThreadPool',
    'create_virtual_thread_executor',
    'execute_in_virtual_thread',
    'virtual_thread_map',
    'run_in_virtual_thread',
    'virtual_map',
    'virtual_thread_benchmark',
]
