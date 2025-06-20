"""
Tests for Level 3 Features - Pipeline Processing
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from pyferris import Pipeline, Chain, pipeline_map
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure PyFerris is built with: maturin develop")
    sys.exit(1)


class TestPipelineProcessing(unittest.TestCase):
    
    def test_pipeline_basic(self):
        """Test basic pipeline functionality"""
        pipeline = Pipeline(chunk_size=10)
        
        # Add operations
        pipeline.add(lambda x: x * 2)
        pipeline.add(lambda x: x + 1)
        
        data = [1, 2, 3, 4, 5]
        results = pipeline.execute(data)
        expected = [3, 5, 7, 9, 11]  # (x*2)+1
        
        self.assertEqual(results, expected)
    
    def test_pipeline_empty(self):
        """Test pipeline with empty data"""
        pipeline = Pipeline()
        pipeline.add(lambda x: x * 2)
        
        results = pipeline.execute([])
        self.assertEqual(results, [])
    
    def test_pipeline_no_operations(self):
        """Test pipeline with no operations"""
        pipeline = Pipeline()
        data = [1, 2, 3]
        results = pipeline.execute(data)
        self.assertEqual(results, data)
    
    def test_pipeline_chain_operations(self):
        """Test chaining multiple operations"""
        pipeline = Pipeline()
        operations = [
            lambda x: x + 10,
            lambda x: x * 2,
            lambda x: x - 5
        ]
        pipeline.chain(operations)
        
        data = [1, 2, 3]
        results = pipeline.execute(data)
        expected = [17, 19, 21]  # ((x+10)*2)-5
        
        self.assertEqual(results, expected)
    
    def test_pipeline_length(self):
        """Test pipeline length property"""
        pipeline = Pipeline()
        self.assertEqual(pipeline.length, 0)
        
        pipeline.add(lambda x: x)
        self.assertEqual(pipeline.length, 1)
        
        pipeline.add(lambda x: x * 2)
        self.assertEqual(pipeline.length, 2)
        
        pipeline.clear()
        self.assertEqual(pipeline.length, 0)
    
    def test_chain_basic(self):
        """Test basic chain functionality"""
        chain = Chain()
        chain.then(lambda x: x * 3)
        chain.then(lambda x: x + 1)
        
        result = chain.execute_one(5)
        expected = 16  # (5*3)+1
        
        self.assertEqual(result, expected)
    
    def test_chain_multiple(self):
        """Test chain with multiple inputs"""
        chain = Chain()
        chain.then(lambda x: x ** 2)
        chain.then(lambda x: x + 10)
        
        data = [1, 2, 3, 4]
        results = chain.execute_many(data, 2)  # chunk_size=2
        expected = [11, 14, 19, 26]  # (x^2)+10
        
        self.assertEqual(results, expected)
    
    def test_chain_length(self):
        """Test chain length property"""
        chain = Chain()
        self.assertEqual(chain.length, 0)
        
        chain.then(lambda x: x)
        self.assertEqual(chain.length, 1)
        
        chain.then(lambda x: x * 2)
        self.assertEqual(chain.length, 2)
    
    def test_functional_pipeline(self):
        """Test functional pipeline_map"""
        operations = [
            lambda x: x * 2,
            lambda x: x + 5,
            lambda x: x / 2
        ]
        
        data = [2, 4, 6, 8]
        results = pipeline_map(data, operations, 2)  # chunk_size=2
        expected = [4.5, 6.5, 8.5, 10.5]  # ((x*2)+5)/2
        
        self.assertEqual(results, expected)
    
    def test_functional_pipeline_empty_operations(self):
        """Test functional pipeline with empty operations"""
        data = [1, 2, 3]
        results = pipeline_map(data, [], 1)  # chunk_size=1
        self.assertEqual(results, data)
    
    def test_functional_pipeline_empty_data(self):
        """Test functional pipeline with empty data"""
        operations = [lambda x: x * 2]
        results = pipeline_map([], operations, 1)  # chunk_size=1
        self.assertEqual(results, [])
    
    def test_pipeline_large_data(self):
        """Test pipeline with large dataset"""
        pipeline = Pipeline(chunk_size=100)
        pipeline.add(lambda x: x ** 2)
        pipeline.add(lambda x: x % 1000)
        
        data = list(range(1000))
        results = pipeline.execute(data)
        
        # Verify first few results
        self.assertEqual(results[0], 0)   # (0^2) % 1000 = 0
        self.assertEqual(results[1], 1)   # (1^2) % 1000 = 1
        self.assertEqual(results[2], 4)   # (2^2) % 1000 = 4
        
        # Verify length
        self.assertEqual(len(results), 1000)
    
    def test_chain_custom_chunk_size(self):
        """Test chain with custom chunk size"""
        chain = Chain()
        chain.then(lambda x: x + 1)
        chain.then(lambda x: x * 2)
        
        data = list(range(50))
        results = chain.execute_many(data, chunk_size=10)
        expected = [(x + 1) * 2 for x in data]
        
        self.assertEqual(results, expected)


if __name__ == '__main__':
    unittest.main()
