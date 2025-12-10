"""
This module provides high-level pipeline and chain operations for efficient
data processing with function composition and parallel execution.
"""

from typing import Any, List, Callable, Optional, Union
from ._pyferris import Pipeline as _Pipeline, Chain as _Chain, pipeline_map as _pipeline_map
from . import lodash

class Pipeline:
    """
    A pipeline for chaining operations on data with parallel execution.
    
    Pipeline allows you to compose multiple operations that will be applied
    sequentially to input data, with automatic parallelization for performance.
    
    Args:
        chunk_size (int, optional): Size of chunks for parallel processing. 
                                   Defaults to optimal size based on data.
    
    Example:
        >>> pipeline = Pipeline(chunk_size=100)
        >>> pipeline.add(lambda x: x * 2)      # Double each value
        >>> pipeline.add(lambda x: x + 1)      # Add 1 to each value
        >>> pipeline.add(lambda x: x ** 2)     # Square each value
        >>> result = pipeline.execute([1, 2, 3, 4, 5])
        >>> print(result)  # [9, 25, 49, 81, 121]
    """
    
    def __init__(self, chunk_size: Optional[int] = None):
        """Initialize a new Pipeline with optional chunk size."""
        if chunk_size is None:
            self._pipeline = _Pipeline()
        else:
            self._pipeline = _Pipeline(chunk_size)
    
    def add(self, operation: Callable[[Any], Any]) -> None:
        """
        Add a single operation to the pipeline.
        
        Args:
            operation: A callable that takes one argument and returns a result.
                      This function will be applied to each element in the pipeline.
        
        Example:
            >>> pipeline = Pipeline()
            >>> pipeline.add(lambda x: x * 2)
            >>> pipeline.add(str)  # Convert to string
        """
        self._pipeline.add(operation)
    
    def chain(self, operations: List[Callable[[Any], Any]]) -> None:
        """
        Add multiple operations to the pipeline at once.
        
        Args:
            operations: A list of callable functions to be applied in sequence.
        
        Example:
            >>> pipeline = Pipeline()
            >>> operations = [
            ...     lambda x: x + 10,
            ...     lambda x: x * 2,
            ...     lambda x: x - 5
            ... ]
            >>> pipeline.chain(operations)
        """
        self._pipeline.chain(operations)
    
    def execute(self, data: List[Any]) -> List[Any]:
        """
        Execute the pipeline on the provided data.
        
        Args:
            data: A list of input data to process through the pipeline.
        
        Returns:
            A list of results after applying all pipeline operations.
        
        Example:
            >>> pipeline = Pipeline()
            >>> pipeline.add(lambda x: x ** 2)
            >>> result = pipeline.execute([1, 2, 3, 4])
            >>> print(result)  # [1, 4, 9, 16]
        """
        return self._pipeline.execute(data)
    
    def clear(self) -> None:
        """
        Remove all operations from the pipeline.
        
        After calling clear(), the pipeline will have no operations
        and execute() will return the input data unchanged.
        """
        self._pipeline.clear()
    
    @property
    def length(self) -> int:
        """
        Get the number of operations currently in the pipeline.
        
        Returns:
            The number of operations that have been added to the pipeline.
        """
        return self._pipeline.length


class Chain:
    """
    A chain for composing operations that can be executed on single values or collections.
    
    Chain is similar to Pipeline but optimized for functional composition and
    provides both single-value and batch execution methods. It also integrates
    Lodash-like utility functions for advanced data manipulation.
    
    Example:
        >>> chain = Chain()
        >>> chain.map(lambda x: x * 2).uniq().sort()
        >>> result = chain.execute([1, 2, 1, 3])
        >>> print(result)  # [2, 4, 6]
    """
    
    def __init__(self, data: Optional[Any] = None):
        """
        Initialize a new Chain.
        
        Args:
            data: Optional initial data. If provided, the chain acts as a wrapper
                  and can be executed with .value().
        """
        self._stages = []
        self._current_parallel_chain = None
        self._initial_data = data
    
    def _ensure_parallel_chain(self):
        if self._current_parallel_chain is None:
            self._current_parallel_chain = _Chain()
            self._stages.append(('parallel', self._current_parallel_chain))
    
    def _close_parallel_chain(self):
        self._current_parallel_chain = None

    def then(self, operation: Callable[[Any], Any]) -> 'Chain':
        """
        Add a mapping operation to the chain (alias for map).
        
        Args:
            operation: A callable that takes one argument and returns a result.
        
        Returns:
            Self, allowing for method chaining.
        """
        return self.map(operation)

    def map(self, operation: Callable[[Any], Any]) -> 'Chain':
        """
        Add a mapping operation to the chain.
        
        Args:
            operation: Function to apply to each element.
        """
        self._ensure_parallel_chain()
        self._current_parallel_chain.then(operation)
        return self
    
    def filter(self, predicate: Callable[[Any], bool]) -> 'Chain':
        """
        Add a filter operation to the chain.
        
        Note: This breaks the parallel map chain and executes a global filter.
        Future versions may optimize this into the parallel chain.
        """
        self._close_parallel_chain()
        
        def filter_stage(data):
            # Use lodash.compact if predicate is None, else standard filter
            # But here we use list comprehension for simplicity or lodash.filter if we had it
            # We implemented 'compact' but not generic 'filter' in array.rs yet (oops, missed it in array.rs but have it in collection.rs?)
            # We have 'partition' in collection.rs.
            # Let's use Python's filter for now or custom logic
            if predicate is None:
                return lodash.compact(data)
            return [x for x in data if predicate(x)]
            
        self._stages.append(('global', filter_stage))
        return self

    def uniq(self) -> 'Chain':
        """Creates a duplicate-free version of the array."""
        self._close_parallel_chain()
        self._stages.append(('global', lodash.uniq))
        return self
    
    def chunk(self, size: int) -> 'Chain':
        """Creates an array of elements split into groups the length of size."""
        self._close_parallel_chain()
        self._stages.append(('global', lambda d: lodash.chunk(d, size)))
        return self
    
    def compact(self) -> 'Chain':
        """Creates an array with all falsey values removed."""
        self._close_parallel_chain()
        self._stages.append(('global', lodash.compact))
        return self
    
    def flatten(self) -> 'Chain':
        """Flattens array a single level deep."""
        self._close_parallel_chain()
        self._stages.append(('global', lodash.flatten))
        return self
    
    def group_by(self, iteratee: Any) -> 'Chain':
        """Creates an object composed of keys generated from the results of running each element of collection thru iteratee."""
        self._close_parallel_chain()
        self._stages.append(('global', lambda d: lodash.group_by(d, iteratee)))
        return self
    
    def count_by(self, iteratee: Any) -> 'Chain':
        """Creates an object composed of keys generated from the results of running each element of collection thru iteratee."""
        self._close_parallel_chain()
        self._stages.append(('global', lambda d: lodash.count_by(d, iteratee)))
        return self
    
    def shuffle(self) -> 'Chain':
        """Creates an array of shuffled values."""
        self._close_parallel_chain()
        self._stages.append(('global', lodash.shuffle))
        return self
    
    def sample(self) -> 'Chain':
        """Gets a random element from collection."""
        self._close_parallel_chain()
        self._stages.append(('global', lodash.sample))
        return self
    
    def key_by(self, iteratee: Any) -> 'Chain':
        """Creates an object composed of keys generated from the results of running each element of collection thru iteratee."""
        self._close_parallel_chain()
        self._stages.append(('global', lambda d: lodash.key_by(d, iteratee)))
        return self
    
    def sort(self, key: Optional[Callable] = None, reverse: bool = False) -> 'Chain':
        """Sorts the array."""
        self._close_parallel_chain()
        def sort_stage(data):
            # Use Python's sort or pyferris.parallel_sort
            # Since we are in pipeline, data is likely a list
            if isinstance(data, list):
                # Return a new sorted list to avoid mutating input in place if that matters
                # But for pipeline, mutation is often fine if it's intermediate
                return sorted(data, key=key, reverse=reverse)
            return data
        self._stages.append(('global', sort_stage))
        return self

    def execute(self, data: Optional[List[Any]] = None) -> Any:
        """
        Execute the chain on the provided data.
        
        Args:
            data: Input data. If None, uses the data provided in __init__.
        """
        current_data = data if data is not None else self._initial_data
        if current_data is None:
            raise ValueError("No data provided for execution")
            
        for stage_type, stage_op in self._stages:
            if stage_type == 'parallel':
                # stage_op is _Chain
                # We need to decide chunk_size. Default to None (auto)
                # _Chain.execute_many expects a list
                if not isinstance(current_data, list):
                    current_data = list(current_data)
                current_data = stage_op.execute_many(current_data, 1000) # Default chunk size
            else:
                # stage_op is a callable
                current_data = stage_op(current_data)
                
        return current_data
    
    def execute_one(self, value: Any) -> Any:
        """
        Execute the chain on a single value.
        
        Note: Global operations (uniq, group_by) might fail or behave unexpectedly
        if called on a single value that isn't a list. This method is primarily
        for chains that only contain 'map' operations.
        """
        current_value = value
        for stage_type, stage_op in self._stages:
            if stage_type == 'parallel':
                current_value = stage_op.execute_one(current_value)
            else:
                # Global ops usually expect a list. If we have a single value,
                # we might need to wrap it? Or just let it fail?
                # For backward compatibility, we assume execute_one is used with map-only chains.
                # If a global op is present, we treat the value as the dataset?
                # No, execute_one implies the input IS the item.
                # If we have 'uniq', it doesn't make sense on a single scalar.
                raise NotImplementedError("Global operations are not supported in execute_one")
        return current_value

    def execute_many(self, data: List[Any], chunk_size: int) -> List[Any]:
        """
        Execute the chain on multiple values. Alias for execute, but with chunk_size ignored for global ops.
        """
        # We can't easily pass chunk_size to the mixed pipeline stages yet
        # except for the parallel ones.
        # For now, just delegate to execute, but we could optimize to pass chunk_size to parallel stages.
        
        current_data = data
        for stage_type, stage_op in self._stages:
            if stage_type == 'parallel':
                if not isinstance(current_data, list):
                    current_data = list(current_data)
                current_data = stage_op.execute_many(current_data, chunk_size)
            else:
                current_data = stage_op(current_data)
        return current_data

    def value(self) -> Any:
        """Execute the chain and return the result (requires data in __init__)."""
        return self.execute()
    
    @property
    def length(self) -> int:
        """Get the number of stages (approximate)."""
        return len(self._stages)


def pipeline_map(data: List[Any], operations: List[Callable[[Any], Any]], 
                chunk_size: int) -> List[Any]:
    """
    Apply a series of operations to data using functional pipeline approach.
    
    This is a functional interface for pipeline processing, useful when you
    want to apply operations without creating a Pipeline object.
    
    Args:
        data: Input data to process.
        operations: List of functions to apply in sequence.
        chunk_size: Size of chunks for parallel processing.
    
    Returns:
        Results after applying all operations to the data.
    
    Example:
        >>> operations = [
        ...     lambda x: x + 10,
        ...     lambda x: x * 0.5,
        ...     lambda x: round(x, 2)
        ... ]
        >>> result = pipeline_map(range(5), operations, 2)
        >>> print(result)  # [5.0, 5.5, 6.0, 6.5, 7.0]
    """
    return _pipeline_map(data, operations, chunk_size)


__all__ = ['Pipeline', 'Chain', 'pipeline_map']
