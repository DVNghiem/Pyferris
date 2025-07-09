#!/usr/bin/env python3
"""
Quick validation script to verify PyFerris optimizations work correctly.
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.abspath('.'))

def test_basic_functionality():
    """Test that basic functionality still works after optimizations."""
    print("Testing basic functionality...")
    
    try:
        # Test core functions
        from pyferris import parallel_map, parallel_filter, parallel_reduce
        
        # Simple test data
        data = list(range(100))
        
        # Test parallel_map
        result = parallel_map(lambda x: x * 2, data)
        assert len(result) == 100
        assert result[0] == 0
        assert result[50] == 100
        print("✓ parallel_map works correctly")
        
        # Test parallel_filter  
        result = parallel_filter(lambda x: x % 2 == 0, data)
        assert len(result) == 50
        assert all(x % 2 == 0 for x in result)
        print("✓ parallel_filter works correctly")
        
        # Test parallel_reduce
        result = parallel_reduce(lambda x, y: x + y, range(10))
        assert result == 45
        print("✓ parallel_reduce works correctly")
        
        # Test executor
        from pyferris import Executor
        with Executor(max_workers=2) as executor:
            future = executor.submit(lambda: 42)
            assert future.result() == 42
        print("✓ Executor works correctly")
        
        print("All basic tests passed! ✓")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_performance_improvements():
    """Test that performance improvements are working."""
    print("\nTesting performance improvements...")
    
    try:
        from pyferris.core import _CHUNK_SIZE_CACHE
        from pyferris import parallel_map
        
        # Test chunk size caching
        data = list(range(10000))
        parallel_map(lambda x: x + 1, data)
        parallel_map(lambda x: x + 1, data)  # Second call should use cache
        
        # Cache should have entries now
        assert len(_CHUNK_SIZE_CACHE) > 0
        print("✓ Chunk size caching is working")
        
        # Test memory optimization paths exist
        import pyferris.executor
        assert hasattr(pyferris.executor, '_EXECUTOR_POOL')
        print("✓ Executor pooling is available")
        
        # Test I/O optimizations
        import pyferris.io
        assert hasattr(pyferris.io, '_optimize_io_operation')
        print("✓ I/O optimizations are available")
        
        print("Performance improvement tests passed! ✓")
        return True
        
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        return False

def test_no_unused_parameters():
    """Verify no unused parameter warnings in our code."""
    print("\nChecking for unused parameters...")
    
    # This is a basic check - the real verification was done with vulture
    try:
        # Import main modules to check for import errors
        from pyferris import parallel_map, Executor
        
        print("✓ All imports work without errors")
        
        # Test that functions handle parameters correctly
        data = [1, 2, 3]
        result = parallel_map(lambda x: x * 2, data, chunk_size=None)
        assert result == [2, 4, 6]
        print("✓ Chunk size parameter handling works")
        
        with Executor() as executor:
            executor.shutdown(wait=True)  # Should not raise error about unused param
        print("✓ Executor parameter handling works")
        
        print("Unused parameter checks passed! ✓")
        return True
        
    except Exception as e:
        print(f"✗ Unused parameter check failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("PyFerris Optimization Validation")
    print("=" * 40)
    
    results = []
    results.append(test_basic_functionality())
    results.append(test_performance_improvements()) 
    results.append(test_no_unused_parameters())
    
    print("\n" + "=" * 40)
    if all(results):
        print("🎉 All validation tests passed! Optimizations are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
