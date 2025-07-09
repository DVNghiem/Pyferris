"""
PyFerris Level 5: Enterprise Fault Tolerance

This module provides enterprise-grade fault tolerance capabilities including:
- Retry mechanisms with various strategies
- Circuit breakers for preventing cascading failures  
- Checkpoint systems for long-running operations
- Automatic recovery and state management
"""

from typing import Any, Callable, Dict, List, Optional
import functools
import time
from ._pyferris import (
    RetryExecutor,
    CircuitBreaker,
    CheckpointManager,
    AutoCheckpoint,
)

__all__ = [
    'RetryExecutor',
    'CircuitBreaker', 
    'CheckpointManager',
    'AutoCheckpoint',
    'retry',
    'circuit_breaker',
    'with_checkpoints',
    'resilient_operation',
]


def retry(
    max_attempts: int = 3,
    strategy: str = "exponential",
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0,
    exceptions: Optional[List[str]] = None,
    on_retry: Optional[Callable] = None
):
    """Decorator for adding retry logic to functions.
    
    Args:
        max_attempts: Maximum number of retry attempts
        strategy: Retry strategy - "exponential", "linear", or "fixed"
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_multiplier: Multiplier for exponential backoff
        exceptions: List of exception names that should trigger retries
        on_retry: Callback function called on each retry attempt
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            executor = RetryExecutor(
                strategy=strategy,
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                max_delay=max_delay,
                backoff_multiplier=backoff_multiplier
            )
            
            if exceptions:
                for exc in exceptions:
                    executor.add_retryable_exception(exc)
            
            if on_retry:
                executor.set_retry_callback(on_retry)
                
            return executor.execute(func, args)
        
        return wrapper
    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    on_open: Optional[Callable] = None,
    on_close: Optional[Callable] = None
):
    """Decorator for adding circuit breaker protection to functions.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Time to wait before testing recovery
        on_open: Callback when circuit opens
        on_close: Callback when circuit closes
        
    Returns:
        Decorated function with circuit breaker protection
    """
    def decorator(func: Callable) -> Callable:
        breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = breaker.execute(func, args)
                if on_close:
                    on_close()
                return result
            except Exception:
                status = breaker.get_status()
                if status['state'] == 'open' and on_open:
                    on_open()
                raise
        
        return wrapper
    return decorator


def with_checkpoints(
    operation_id: str,
    checkpoint_dir: Optional[str] = None,
    auto_save_interval: Optional[int] = 300,  # 5 minutes
    max_checkpoints: Optional[int] = 10,
    restore_on_start: bool = True
):
    """Decorator for adding checkpoint functionality to functions.
    
    Args:
        operation_id: Unique identifier for the operation
        checkpoint_dir: Directory to store checkpoints
        auto_save_interval: Automatic checkpoint interval in seconds
        max_checkpoints: Maximum number of checkpoints to keep
        restore_on_start: Whether to restore from latest checkpoint on start
        
    Returns:
        Decorated function with checkpoint support
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            manager = CheckpointManager(
                checkpoint_dir=checkpoint_dir,
                auto_save_interval=auto_save_interval,
                max_checkpoints=max_checkpoints
            )
            
            # Try to restore from latest checkpoint if requested
            initial_state = None
            if restore_on_start:
                latest = manager.get_latest_checkpoint(operation_id)
                if latest:
                    initial_state = latest.state
                    print(f"Restored from checkpoint {latest.id} at {latest.progress*100:.1f}% progress")
            
            # Add checkpoint manager to kwargs
            kwargs['_checkpoint_manager'] = manager
            kwargs['_operation_id'] = operation_id
            kwargs['_initial_state'] = initial_state
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class ResilientOperation:
    """High-level class combining retry, circuit breaker, and checkpoint functionality."""
    
    def __init__(
        self,
        operation_id: str,
        retry_config: Optional[Dict[str, Any]] = None,
        circuit_config: Optional[Dict[str, Any]] = None,
        checkpoint_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize resilient operation.
        
        Args:
            operation_id: Unique identifier for the operation
            retry_config: Configuration for retry behavior
            circuit_config: Configuration for circuit breaker
            checkpoint_config: Configuration for checkpointing
        """
        self.operation_id = operation_id
        
        # Set up retry executor
        retry_config = retry_config or {}
        self.retry_executor = RetryExecutor(
            strategy=retry_config.get('strategy', 'exponential'),
            max_attempts=retry_config.get('max_attempts', 3),
            initial_delay=retry_config.get('initial_delay', 1.0),
            max_delay=retry_config.get('max_delay', 60.0),
            backoff_multiplier=retry_config.get('backoff_multiplier', 2.0)
        )
        
        # Set up circuit breaker
        circuit_config = circuit_config or {}
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_config.get('failure_threshold', 5),
            recovery_timeout=circuit_config.get('recovery_timeout', 60.0)
        )
        
        # Set up checkpoint manager
        checkpoint_config = checkpoint_config or {}
        self.checkpoint_manager = CheckpointManager(
            checkpoint_dir=checkpoint_config.get('checkpoint_dir'),
            auto_save_interval=checkpoint_config.get('auto_save_interval', 300),
            max_checkpoints=checkpoint_config.get('max_checkpoints', 10)
        )
        
        # Set up auto-checkpoint
        self.auto_checkpoint = AutoCheckpoint(
            operation_id=operation_id,
            checkpoint_manager=self.checkpoint_manager,
            interval_seconds=checkpoint_config.get('auto_save_interval', 300)
        )
    
    def execute(
        self,
        operation: Callable,
        *args,
        state_provider: Optional[Callable[[], Dict[str, str]]] = None,
        progress_provider: Optional[Callable[[], float]] = None,
        **kwargs
    ) -> Any:
        """Execute operation with full resilience protection.
        
        Args:
            operation: Function to execute
            *args: Arguments for the operation
            state_provider: Function that returns current operation state for checkpointing
            progress_provider: Function that returns current progress (0.0 to 1.0)
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation
        """
        def protected_operation():
            # Try to restore from checkpoint
            latest_checkpoint = self.checkpoint_manager.get_latest_checkpoint(self.operation_id)
            if latest_checkpoint:
                kwargs['_restored_state'] = latest_checkpoint.state
                kwargs['_restored_progress'] = latest_checkpoint.progress
            
            # Execute with circuit breaker protection
            return self.circuit_breaker.execute(operation, args)
        
        # Execute with retry logic
        result = self.retry_executor.execute(protected_operation, ())
        
        # Create final checkpoint on success
        if state_provider:
            state = state_provider()
            progress = progress_provider() if progress_provider else 1.0
            self.checkpoint_manager.save_checkpoint(
                operation_id=self.operation_id,
                state_data=state,
                progress=progress,
                metadata={'status': 'completed', 'timestamp': str(time.time())}
            )
        
        return result
    
    def checkpoint_progress(
        self,
        state_data: Dict[str, str],
        progress: float,
        force: bool = False
    ) -> Optional[str]:
        """Create a checkpoint of current progress.
        
        Args:
            state_data: Current operation state
            progress: Current progress (0.0 to 1.0)
            force: Whether to force checkpoint regardless of timing
            
        Returns:
            Checkpoint ID if created, None otherwise
        """
        if force:
            return self.auto_checkpoint.force_checkpoint(state_data, progress)
        else:
            return self.auto_checkpoint.maybe_checkpoint(state_data, progress)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the resilient operation.
        
        Returns:
            Dictionary with status information
        """
        return {
            'retry_stats': self.retry_executor.get_stats(),
            'circuit_status': self.circuit_breaker.get_status(),
            'checkpoint_stats': self.checkpoint_manager.get_stats(),
            'latest_checkpoint': self.checkpoint_manager.get_latest_checkpoint(self.operation_id)
        }


def resilient_operation(
    operation_id: str,
    retry_config: Optional[Dict[str, Any]] = None,
    circuit_config: Optional[Dict[str, Any]] = None,
    checkpoint_config: Optional[Dict[str, Any]] = None
) -> Callable:
    """Decorator that combines retry, circuit breaker, and checkpoint functionality.
    
    Args:
        operation_id: Unique identifier for the operation
        retry_config: Configuration for retry behavior
        circuit_config: Configuration for circuit breaker
        checkpoint_config: Configuration for checkpointing
        
    Returns:
        Decorated function with full resilience protection
    """
    def decorator(func: Callable) -> Callable:
        resilient_op = ResilientOperation(
            operation_id=operation_id,
            retry_config=retry_config,
            circuit_config=circuit_config,
            checkpoint_config=checkpoint_config
        )
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return resilient_op.execute(func, *args, **kwargs)
        
        # Attach the resilient operation for access to methods
        wrapper._resilient_op = resilient_op
        return wrapper
    
    return decorator


# Example usage
if __name__ == "__main__":
    # Example 1: Simple retry decorator
    @retry(max_attempts=5, strategy="exponential")
    def unreliable_api_call():
        import random
        if random.random() < 0.7:  # 70% chance of failure
            raise ConnectionError("API temporarily unavailable")
        return "API call successful"
    
    # Example 2: Circuit breaker for database operations
    @circuit_breaker(failure_threshold=3, recovery_timeout=30.0)
    def database_query():
        # Simulate database operation
        import random
        if random.random() < 0.5:
            raise Exception("Database connection failed")
        return "Query result"
    
    # Example 3: Long-running operation with checkpoints
    @with_checkpoints("data_processing", auto_save_interval=60)
    def process_large_dataset(data, _checkpoint_manager=None, _operation_id=None, _initial_state=None):
        # Process data with periodic checkpointing
        processed = 0
        total = len(data)
        
        # Restore from checkpoint if available
        if _initial_state and 'processed_count' in _initial_state:
            processed = int(_initial_state['processed_count'])
            print(f"Resuming from item {processed}")
        
        for i in range(processed, total):
            # Process item (example processing)
            _ = data[i] * 2
            processed += 1
            
            # Checkpoint every 100 items
            if processed % 100 == 0:
                state = {'processed_count': str(processed)}
                progress = processed / total
                _checkpoint_manager.save_checkpoint(_operation_id, state, progress)
                print(f"Checkpointed at {processed}/{total} items ({progress*100:.1f}%)")
        
        return f"Processed {processed} items"
    
    # Example 4: Full resilient operation
    @resilient_operation(
        operation_id="critical_batch_job",
        retry_config={'max_attempts': 3, 'strategy': 'exponential'},
        circuit_config={'failure_threshold': 5},
        checkpoint_config={'auto_save_interval': 120}
    )
    def critical_batch_job():
        # Critical operation that needs full protection
        return "Batch job completed successfully"
