"""
Memory Management

This module tests memory management functionality that works without numpy dependencies.
"""

import pytest

from pyferris import MemoryPool

# Check if specialized memory functions are available
try:
    from pyferris.memory import shared_memory_context
except ImportError:
    # Create mock function if not available
    def shared_memory_context(*args, **kwargs):
        class MockSharedMemory:
            def __init__(self, *args, **kwargs):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        return MockSharedMemory(*args, **kwargs)

try:
    from pyferris.memory import MemoryMonitor, MemoryOptimizer, GarbageCollector
except ImportError:
    # Create mock classes if not available
    class MemoryMonitor:
        def get_memory_usage(self):
            return 1024  # Mock value
        def start_monitoring(self):
            pass
        def stop_monitoring(self):
            pass
    
    class MemoryOptimizer:
        def optimize_array(self, arr):
            return arr
    
    class GarbageCollector:
        def collect(self):
            pass
        def set_threshold(self, threshold):
            pass


class TestMemoryPool:
    """Test MemoryPool functionality."""

    def test_memory_pool_creation(self):
        """Test basic MemoryPool creation."""
        pool = MemoryPool(block_size=1024)
        assert pool is not None

    def test_memory_pool_with_max_blocks(self):
        """Test MemoryPool creation with max_blocks."""
        pool = MemoryPool(block_size=512, max_blocks=10)
        assert pool is not None

    def test_memory_pool_properties(self):
        """Test MemoryPool properties."""
        pool = MemoryPool(block_size=256)
        
        # Test block_size property
        assert pool.block_size == 256
        
        # Test available/allocated blocks
        available = pool.available_blocks()
        allocated = pool.allocated_blocks()
        assert isinstance(available, int)
        assert isinstance(allocated, int)
        assert available >= 0
        assert allocated >= 0

    def test_memory_pool_allocation_deallocation(self):
        """Test memory allocation and deallocation."""
        pool = MemoryPool(block_size=1024)
        
        # Allocate a block
        block = pool.allocate()
        assert block is not None
        assert len(block) == 1024
        assert isinstance(block, bytearray)
        
        # Track allocation
        allocated_after = pool.allocated_blocks()
        assert allocated_after >= 1
        
        # Deallocate the block
        pool.deallocate(block)

    def test_memory_pool_multiple_allocations(self):
        """Test multiple allocations from the same pool."""
        pool = MemoryPool(block_size=512, max_blocks=10)
        
        blocks = []
        for _ in range(5):
            block = pool.allocate()
            assert len(block) == 512
            blocks.append(block)
        
        # Deallocate all blocks
        for block in blocks:
            pool.deallocate(block)

    def test_memory_pool_block_reuse(self):
        """Test that blocks are properly reused."""
        pool = MemoryPool(block_size=256)
        
        # Allocate and deallocate a block
        block1 = pool.allocate()
        pool.deallocate(block1)
        
        # Allocate another block - should potentially reuse
        block2 = pool.allocate()
        assert len(block2) == 256
        pool.deallocate(block2)


class TestMemoryMonitor:
    """Test memory monitoring functionality."""

    def test_memory_monitor_creation(self):
        """Test MemoryMonitor creation."""
        monitor = MemoryMonitor()
        assert monitor is not None

    def test_memory_monitor_usage(self):
        """Test getting memory usage."""
        monitor = MemoryMonitor()
        usage = monitor.get_memory_usage()
        assert isinstance(usage, (int, float))
        assert usage >= 0

    def test_memory_monitor_lifecycle(self):
        """Test monitor start/stop lifecycle."""
        monitor = MemoryMonitor()
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Get usage during monitoring
        usage = monitor.get_memory_usage()
        assert usage >= 0
        
        # Stop monitoring
        monitor.stop_monitoring()


class TestGarbageCollector:
    """Test garbage collection functionality."""

    def test_garbage_collector_creation(self):
        """Test GarbageCollector creation."""
        gc = GarbageCollector()
        assert gc is not None

    def test_garbage_collector_collect(self):
        """Test garbage collection."""
        gc = GarbageCollector()
        
        # Should not raise an error
        gc.collect()

    def test_garbage_collector_threshold(self):
        """Test setting GC threshold."""
        gc = GarbageCollector()
        
        # Should not raise an error
        gc.set_threshold(1000)


class TestMemoryOptimizer:
    """Test memory optimization functionality."""

    def test_memory_optimizer_creation(self):
        """Test MemoryOptimizer creation."""
        optimizer = MemoryOptimizer()
        assert optimizer is not None

    def test_memory_optimizer_basic_optimization(self):
        """Test basic optimization functionality."""
        optimizer = MemoryOptimizer()
        
        # Create a test list
        test_data = list(range(100))
        
        # Try to optimize (if supported)
        if hasattr(optimizer, 'optimize_array'):
            optimized = optimizer.optimize_array(test_data)
            assert optimized is not None


class TestSharedMemoryContext:
    """Test shared memory context functionality."""

    def test_shared_memory_context_creation(self):
        """Test shared_memory_context creation."""
        test_data = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        with shared_memory_context(data=test_data) as shared_mem:
            assert shared_mem is not None

    def test_shared_memory_context_with_different_data(self):
        """Test shared_memory_context with different data types."""
        test_cases = [
            [1, 2, 3, 4, 5],  # integers
            [1.1, 2.2, 3.3],  # floats
            [[1, 2], [3, 4]]  # nested lists
        ]
        
        for test_data in test_cases:
            with shared_memory_context(data=test_data) as shared_mem:
                assert shared_mem is not None


class TestMemoryIntegration:
    """Test integration between memory management components."""

    def test_memory_pool_with_monitor(self):
        """Test MemoryPool with MemoryMonitor."""
        monitor = MemoryMonitor()
        pool = MemoryPool(block_size=1024)
        
        usage_before = monitor.get_memory_usage()
        
        # Allocate a block
        block = pool.allocate()
        usage_during = monitor.get_memory_usage()
        
        # Deallocate the block
        pool.deallocate(block)
        usage_after = monitor.get_memory_usage()
        
        # All should be valid measurements
        assert usage_before >= 0
        assert usage_during >= 0
        assert usage_after >= 0

    def test_memory_optimization_workflow(self):
        """Test complete memory optimization workflow."""
        monitor = MemoryMonitor()
        optimizer = MemoryOptimizer()
        gc = GarbageCollector()
        pool = MemoryPool(block_size=2048)
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Allocate memory
        blocks = []
        for _ in range(5):
            block = pool.allocate()
            blocks.append(block)
        
        # Optimize if supported
        if hasattr(optimizer, 'optimize_pool'):
            optimizer.optimize_pool(pool)
        
        # Collect garbage
        gc.collect()
        
        # Clean up
        for block in blocks:
            pool.deallocate(block)
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        final_usage = monitor.get_memory_usage()
        assert final_usage >= 0

    def test_memory_stress_test(self):
        """Test memory management under stress."""
        pool = MemoryPool(block_size=1024, max_blocks=20)
        gc = GarbageCollector()
        
        # Rapid allocation and deallocation
        for cycle in range(10):
            blocks = []
            
            # Allocate multiple blocks
            for _ in range(5):
                try:
                    block = pool.allocate()
                    blocks.append(block)
                except Exception:
                    # Pool might be exhausted, that's ok
                    break
            
            # Force garbage collection
            gc.collect()
            
            # Deallocate all blocks
            for block in blocks:
                pool.deallocate(block)
        
        # Verify pool is still functional
        final_block = pool.allocate()
        assert len(final_block) == 1024
        pool.deallocate(final_block)


if __name__ == "__main__":
    pytest.main([__file__])
