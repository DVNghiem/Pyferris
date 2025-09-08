"""
Level 5 Enterprise Features Examples

This module demonstrates the advanced Level 5 features of PyFerris including:
- Distributed processing across multiple machines
- Fault tolerance with retry mechanisms and circuit breakers
- Checkpoint systems for long-running operations
- Resource management and monitoring
"""

import time
import random
from typing import List, Dict, Any

# Import Level 5 features
from pyferris import (
    # Distributed processing
    create_cluster,
    
    # Fault tolerance
    retry, with_checkpoints, resilient_operation,
    RetryExecutor, CircuitBreaker
)


def example_distributed_cluster():
    """Example: Setting up and using a distributed cluster."""
    print("\n=== Distributed Cluster Example ===")
    
    # Create cluster coordinator
    coordinator = create_cluster("coordinator", "127.0.0.1:8000", coordinator=True)
    print("Created cluster coordinator")
    
    # Create worker nodes (in practice, these would be on different machines)
    worker1 = create_cluster("worker1", "127.0.0.1:8001")
    worker2 = create_cluster("worker2", "127.0.0.1:8002")
    
    # Workers join the cluster
    worker1.join("127.0.0.1:8000")
    worker2.join("127.0.0.1:8000")
    print("Workers joined cluster")
    
    # Example computation: square numbers
    def square(x):
        # Simulate some processing time
        time.sleep(0.01)
        return x * x
    
    # Distribute computation across cluster
    data = list(range(100))
    print(f"Processing {len(data)} items across cluster...")
    
    start_time = time.time()
    results = coordinator.map(square, data, chunk_size=10)
    end_time = time.time()
    
    print(f"Processed {len(results)} items in {end_time - start_time:.2f} seconds")
    print(f"Sample results: {results[:10]}")
    
    # Get cluster statistics
    stats = coordinator.get_cluster_stats()
    print(f"Cluster stats: {stats}")
    
    return coordinator, [worker1, worker2]


def example_retry_mechanisms():
    """Example: Using retry mechanisms for fault tolerance."""
    print("\n=== Retry Mechanisms Example ===")
    
    # Example 1: Simple retry decorator
    @retry(max_attempts=5, strategy="exponential", initial_delay=0.1)
    def unreliable_api_call():
        """Simulates an unreliable API call."""
        if random.random() < 0.7:  # 70% chance of failure
            raise ConnectionError("API temporarily unavailable")
        return "API call successful"
    
    print("Testing unreliable API call with retry...")
    try:
        result = unreliable_api_call()
        print(f"Success: {result}")
    except Exception as e:
        print(f"Failed after all retries: {e}")
    
    # Example 2: Manual retry executor
    retry_executor = RetryExecutor(
        strategy="exponential",
        max_attempts=3,
        initial_delay=0.1,
        max_delay=2.0,
        backoff_multiplier=2.0
    )
    
    def flaky_operation(x):
        if random.random() < 0.5:
            raise RuntimeError("Operation failed")
        return x * 2
    
    print("\nTesting with manual retry executor...")
    try:
        result, attempts = retry_executor.execute_with_info(flaky_operation, (42,))
        print(f"Success after {attempts} attempts: {result}")
    except Exception as e:
        print(f"Failed: {e}")


def example_circuit_breaker():
    """Example: Using circuit breaker for preventing cascading failures."""
    print("\n=== Circuit Breaker Example ===")
    
    # Create circuit breaker
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2.0)
    
    def unreliable_service():
        """Simulates an unreliable service."""
        if random.random() < 0.8:  # 80% failure rate to trigger circuit breaker
            raise Exception("Service unavailable")
        return "Service response"
    
    print("Testing circuit breaker with unreliable service...")
    
    for i in range(10):
        try:
            result = breaker.execute(unreliable_service, ())
            print(f"Call {i+1}: Success - {result}")
        except Exception as e:
            status = breaker.get_status()
            print(f"Call {i+1}: Failed - {e} (Circuit: {status['state']})")
        
        time.sleep(0.1)
    
    # Reset circuit breaker
    print("\nResetting circuit breaker...")
    breaker.reset()
    status = breaker.get_status()
    print(f"Circuit breaker status: {status}")


def example_checkpointing():
    """Example: Using checkpointing for long-running operations."""
    print("\n=== Checkpointing Example ===")
    
    @with_checkpoints(
        operation_id="large_dataset_processing",
        checkpoint_dir="./checkpoints",
    )
    def process_large_dataset(
        data: List[int], 
        _checkpoint_manager=None, 
        _operation_id=None, 
        _initial_state=None
    ):
        """Process a large dataset with checkpointing."""
        processed = 0
        total = len(data)
        results = []
        
        # Restore from checkpoint if available
        if _initial_state and 'processed_count' in _initial_state:
            processed = int(_initial_state['processed_count'])
            print(f"Resuming from item {processed}")
            # In a real scenario, you'd also restore partial results
        
        start_time = time.time()
        
        for i in range(processed, total):
            # Simulate processing
            time.sleep(0.01)  # Simulate work
            result = data[i] ** 2
            results.append(result)
            processed += 1
            
            # Create checkpoint every 50 items
            if processed % 50 == 0:
                state = {
                    'processed_count': str(processed),
                    'last_processed_value': str(data[i])
                }
                progress = processed / total
                checkpoint_id = _checkpoint_manager.save_checkpoint(
                    _operation_id, state, progress
                )
                elapsed = time.time() - start_time
                print(f"Checkpoint {checkpoint_id}: {processed}/{total} items "
                      f"({progress*100:.1f}%) in {elapsed:.1f}s")
        
        return results
    
    # Process dataset
    large_dataset = list(range(200))
    print(f"Processing dataset of {len(large_dataset)} items...")
    
    try:
        results = process_large_dataset(large_dataset)
        print(f"Completed processing {len(results)} items")
    except KeyboardInterrupt:
        print("Processing interrupted - state saved in checkpoint")


def example_resilient_operation():
    """Example: Combining all fault tolerance features."""
    print("\n=== Resilient Operation Example ===")
    
    @resilient_operation(
        operation_id="critical_data_pipeline",
        retry_config={
            'max_attempts': 3,
            'strategy': 'exponential',
            'initial_delay': 0.1
        },
        circuit_config={
            'failure_threshold': 5,
            'recovery_timeout': 3.0
        },
        checkpoint_config={
            'checkpoint_dir': './checkpoints',
        }
    )
    def critical_data_pipeline(data: List[int]) -> Dict[str, Any]:
        """A critical data processing pipeline with full resilience."""
        
        # Simulate various processing stages
        stage1_results = []
        stage2_results = []
        
        for i, item in enumerate(data):
            # Stage 1: Data validation
            if random.random() < 0.1:  # 10% chance of validation error
                raise ValueError(f"Invalid data at position {i}")
            
            stage1_results.append(item * 2)
            
            # Stage 2: Data transformation
            if random.random() < 0.05:  # 5% chance of transformation error
                raise RuntimeError(f"Transformation failed at position {i}")
            
            stage2_results.append(stage1_results[-1] + 1)
            
            # Simulate processing time
            time.sleep(0.001)
        
        return {
            'processed_items': len(data),
            'stage1_results': stage1_results[:5],  # Sample
            'stage2_results': stage2_results[:5],  # Sample
            'total_sum': sum(stage2_results)
        }
    
    # Run the resilient pipeline
    test_data = list(range(100))
    print(f"Running critical pipeline on {len(test_data)} items...")
    
    try:
        result = critical_data_pipeline(test_data)
        print(f"Pipeline completed successfully: {result}")
        
        # Get resilience statistics
        resilient_op = critical_data_pipeline._resilient_op
        status = resilient_op.get_status()
        print(f"Resilience status: {status}")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")


def example_distributed_fault_tolerance():
    """Example: Combining distributed processing with fault tolerance."""
    print("\n=== Distributed + Fault Tolerance Example ===")
    
    # Create a resilient distributed operation
    def resilient_distributed_computation():
        # Set up cluster
        cluster = create_cluster("resilient_coordinator", "127.0.0.1:9000", coordinator=True)
        
        # Define a computation that might fail
        @retry(max_attempts=3, strategy="exponential")
        def risky_computation(x):
            if random.random() < 0.2:  # 20% chance of failure
                raise RuntimeError("Computation failed")
            return x ** 3
        
        # Distribute resilient computation
        data = list(range(50))
        print("Distributing resilient computation across cluster...")
        
        try:
            results = cluster.map(risky_computation, data, chunk_size=5)
            print(f"Successfully computed {len(results)} results")
            return results
        except Exception as e:
            print(f"Distributed computation failed: {e}")
            return None
    
    results = resilient_distributed_computation()
    if results:
        print(f"Sample results: {results[:5]}")


def run_all_examples():
    """Run all Level 5 feature examples."""
    print("PyFerris Level 5: Enterprise Features Demo")
    print("=" * 50)
    
    try:
        # Distributed processing
        example_distributed_cluster()
        
        # Fault tolerance examples
        example_retry_mechanisms()
        example_circuit_breaker()
        example_checkpointing()
        example_resilient_operation()
        
        # Combined features
        example_distributed_fault_tolerance()
        
        print("\n" + "=" * 50)
        print("All Level 5 examples completed successfully!")
        
    except Exception as e:
        print(f"Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
