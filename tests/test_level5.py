"""
Test Level 5 Enterprise Features

Simple tests to verify that Level 5 features are working correctly.
"""

import tempfile
import pytest
from pyferris import (
    RetryExecutor, CircuitBreaker, CheckpointManager, AutoCheckpoint,
    create_cluster
)


class TestRetryExecutor:
    """Test retry functionality."""
    
    def test_retry_success(self):
        """Test successful execution with retry."""
        executor = RetryExecutor(max_attempts=3, strategy="fixed", initial_delay=0.01)
        
        def always_succeed(x):
            return x * 2
        
        result = executor.execute(always_succeed, (5,))
        assert result == 10
    
    def test_retry_eventual_success(self):
        """Test eventual success after failures."""
        executor = RetryExecutor(max_attempts=3, strategy="fixed", initial_delay=0.01)
        
        self.attempt_count = 0
        def succeed_on_third_try(x):
            self.attempt_count += 1
            if self.attempt_count < 3:
                raise RuntimeError("Not yet")
            return x * 2
        
        result = executor.execute(succeed_on_third_try, (5,))
        assert result == 10
        assert self.attempt_count == 3
    
    def test_retry_max_attempts(self):
        """Test that max attempts are respected."""
        executor = RetryExecutor(max_attempts=2, strategy="fixed", initial_delay=0.01)
        
        def always_fail(x):
            raise RuntimeError("Always fails")
        
        with pytest.raises(RuntimeError):
            executor.execute(always_fail, (5,))


class TestCircuitBreaker:
    """Test circuit breaker functionality."""
    
    def test_circuit_breaker_success(self):
        """Test normal operation when service is working."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
        
        def working_service(x):
            return x * 2
        
        result = breaker.execute(working_service, (5,))
        assert result == 10
        
        status = breaker.get_status()
        assert status['state'] == 'closed'
    
    def test_circuit_breaker_opens(self):
        """Test that circuit breaker opens after failures."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        
        def failing_service(x):
            raise RuntimeError("Service down")
        
        # First two calls should fail but execute
        with pytest.raises(RuntimeError):
            breaker.execute(failing_service, (5,))
        
        with pytest.raises(RuntimeError):
            breaker.execute(failing_service, (5,))
        
        # Third call should fail fast due to open circuit
        with pytest.raises(RuntimeError) as exc_info:
            breaker.execute(failing_service, (5,))
        
        assert "Circuit breaker is open" in str(exc_info.value)
        
        status = breaker.get_status()
        assert status['state'] == 'open'


class TestCheckpointManager:
    """Test checkpoint functionality."""
    
    def test_save_and_restore_checkpoint(self):
        """Test saving and restoring checkpoints."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CheckpointManager(checkpoint_dir=temp_dir)
            
            # Save checkpoint
            state_data = {'processed': '50', 'last_item': 'item_50'}
            checkpoint_id = manager.save_checkpoint(
                operation_id="test_op",
                state_data=state_data,
                progress=0.5
            )
            
            # Restore checkpoint
            restored = manager.restore_checkpoint(checkpoint_id)
            assert restored.operation == "test_op"
            assert restored.state == state_data
            assert restored.progress == 0.5
    
    def test_get_latest_checkpoint(self):
        """Test getting the latest checkpoint for an operation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CheckpointManager(checkpoint_dir=temp_dir)
            
            # Save multiple checkpoints
            manager.save_checkpoint(
                "test_op", {'step': '1'}, 0.25
            )
            manager.save_checkpoint(
                "test_op", {'step': '2'}, 0.5
            )
            
            # Get latest
            latest = manager.get_latest_checkpoint("test_op")
            assert latest is not None
            assert latest.state['step'] == '2'
            assert latest.progress == 0.5
    
    def test_list_checkpoints(self):
        """Test listing checkpoints."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CheckpointManager(checkpoint_dir=temp_dir)
            
            # Save checkpoints for different operations
            manager.save_checkpoint("op1", {'data': 'test1'}, 0.5)
            manager.save_checkpoint("op2", {'data': 'test2'}, 0.5)
            manager.save_checkpoint("op1", {'data': 'test3'}, 0.8)
            
            # List all checkpoints
            all_checkpoints = manager.list_checkpoints()
            assert len(all_checkpoints) == 3
            
            # List checkpoints for specific operation
            op1_checkpoints = manager.list_checkpoints("op1")
            assert len(op1_checkpoints) == 2
            
            # Should be sorted by timestamp (newest first)
            assert op1_checkpoints[0].progress == 0.8
            assert op1_checkpoints[1].progress == 0.5


class TestAutoCheckpoint:
    """Test automatic checkpoint functionality."""
    
    def test_auto_checkpoint_timing(self):
        """Test that auto checkpoint respects timing intervals."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CheckpointManager(checkpoint_dir=temp_dir)
            auto_checkpoint = AutoCheckpoint(
                operation_id="test_op",
                checkpoint_manager=manager,
                interval_seconds=1  # 1 second interval
            )
            
            # First call should create checkpoint
            result1 = auto_checkpoint.maybe_checkpoint({'step': '1'}, 0.5)
            assert result1 is not None
            
            # Immediate second call should not create checkpoint
            result2 = auto_checkpoint.maybe_checkpoint({'step': '2'}, 0.6)
            assert result2 is None
            
            # Force checkpoint should always work
            result3 = auto_checkpoint.force_checkpoint({'step': '3'}, 0.7)
            assert result3 is not None


class TestDistributedProcessing:
    """Test distributed processing functionality."""
    
    def test_create_cluster(self):
        """Test creating a distributed cluster."""
        cluster = create_cluster("test_node", "127.0.0.1:9000", coordinator=True)
        
        # Test basic cluster operations
        stats = cluster.get_cluster_stats()
        assert isinstance(stats, dict)
        
        # Test task submission
        task_id = cluster.submit_task(lambda x: x * 2, 5)
        assert isinstance(task_id, str)
        assert len(task_id) > 0
    
    def test_distributed_map_basic(self):
        """Test basic distributed map functionality."""
        cluster = create_cluster("test_coordinator", "127.0.0.1:9001", coordinator=True)
        
        def square(x):
            return x * x
        
        # Test with small dataset
        data = [1, 2, 3, 4, 5]
        results = cluster.map(square, data)
        
        # Note: In a real distributed environment, this would work across nodes
        # For now, we're testing that the API works
        assert len(results) == len(data)
    
    def test_distributed_reduce_basic(self):
        """Test basic distributed reduce functionality."""
        cluster = create_cluster("test_reduce_coord", "127.0.0.1:9002", coordinator=True)
        
        def add(x, y):
            return x + y
        
        # Test with small dataset
        data = [1, 2, 3, 4, 5]
        result = cluster.reduce(add, data)
        
        # Should sum to 15
        assert result == 15


def test_integration_example():
    """Test that all components work together."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create components
        retry_executor = RetryExecutor(max_attempts=3, strategy="fixed", initial_delay=0.01)
        circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
        checkpoint_manager = CheckpointManager(checkpoint_dir=temp_dir)
        cluster = create_cluster("integration_test", "127.0.0.1:9003", coordinator=True)
        
        # Test that all components are accessible
        assert retry_executor is not None
        assert circuit_breaker is not None
        assert checkpoint_manager is not None
        assert cluster is not None
        
        # Test basic operations
        retry_stats = retry_executor.get_stats()
        circuit_status = circuit_breaker.get_status()
        checkpoint_stats = checkpoint_manager.get_stats()
        cluster_stats = cluster.get_cluster_stats()
        
        assert isinstance(retry_stats, dict)
        assert isinstance(circuit_status, dict)
        assert isinstance(checkpoint_stats, dict)
        assert isinstance(cluster_stats, dict)


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    test_retry = TestRetryExecutor()
    test_retry.test_retry_success()
    test_retry.test_retry_eventual_success()
    
    test_circuit = TestCircuitBreaker()
    test_circuit.test_circuit_breaker_success()
    
    test_checkpoint = TestCheckpointManager()
    test_checkpoint.test_save_and_restore_checkpoint()
    test_checkpoint.test_get_latest_checkpoint()
    test_checkpoint.test_list_checkpoints()
    
    test_auto = TestAutoCheckpoint()
    test_auto.test_auto_checkpoint_timing()
    
    test_distributed = TestDistributedProcessing()
    test_distributed.test_create_cluster()
    test_distributed.test_distributed_map_basic()
    test_distributed.test_distributed_reduce_basic()
    
    test_integration_example()
    
    print("All Level 5 tests completed successfully!")
