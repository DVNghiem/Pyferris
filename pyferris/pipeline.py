"""
This module provides high-level pipeline and chain operations for efficient
data processing with function composition and parallel execution.
"""

from typing import Any, List, Callable, Optional
from ._pyferris import Pipeline as _Pipeline, Chain as _Chain, pipeline_map as _pipeline_map


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
    provides both single-value and batch execution methods.
    
    Example:
        >>> chain = Chain()
        >>> chain.then(lambda x: x * 3)
        >>> chain.then(lambda x: x - 1)
        >>> chain.then(lambda x: x / 2)
        >>> result = chain.execute_one(10)
        >>> print(result)  # 14.5  ((10 * 3 - 1) / 2)
    """
    
    def __init__(self):
        """Initialize a new Chain."""
        self._chain = _Chain()
    
    def then(self, operation: Callable[[Any], Any]) -> 'Chain':
        """
        Add an operation to the chain.
        
        Args:
            operation: A callable that takes one argument and returns a result.
        
        Returns:
            Self, allowing for method chaining.
        
        Example:
            >>> chain = Chain()
            >>> result = (chain.then(lambda x: x * 2)
            ...                .then(lambda x: x + 1)
            ...                .execute_one(5))
            >>> print(result)  # 11
        """
        self._chain.then(operation)
        return self
    
    def execute_one(self, value: Any) -> Any:
        """
        Execute the chain on a single value.
        
        Args:
            value: The input value to process through the chain.
        
        Returns:
            The result after applying all chain operations.
        
        Example:
            >>> chain = Chain()
            >>> chain.then(lambda x: x ** 2).then(lambda x: x + 1)
            >>> result = chain.execute_one(5)
            >>> print(result)  # 26  (5^2 + 1)
        """
        return self._chain.execute_one(value)
    
    def execute_many(self, data: List[Any], chunk_size: int) -> List[Any]:
        """
        Execute the chain on multiple values with parallel processing.
        
        Args:
            data: A list of input values to process.
            chunk_size: Size of chunks for parallel processing.
        
        Returns:
            A list of results after applying the chain to each input value.
        
        Example:
            >>> chain = Chain()
            >>> chain.then(lambda x: x ** 2)
            >>> results = chain.execute_many([1, 2, 3, 4], chunk_size=2)
            >>> print(results)  # [1, 4, 9, 16]
        """
        return self._chain.execute_many(data, chunk_size)
    
    @property
    def length(self) -> int:
        """
        Get the number of operations currently in the chain.
        
        Returns:
            The number of operations that have been added to the chain.
        """
        return self._chain.length


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
