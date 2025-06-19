"""
Unit tests for PyFerris Level 2 Advanced Features.

This module contains comprehensive tests for advanced parallel operations,
batch processing, progress tracking, and result collection functionality.
"""

import unittest
from pyferris.advanced import (
    parallel_sort, parallel_group_by, parallel_unique, parallel_partition,
    parallel_chunks, BatchProcessor, ProgressTracker, ResultCollector
)


class TestAdvancedParallelOperations(unittest.TestCase):
    """Test advanced parallel operations."""
    
    def test_parallel_sort_basic(self):
        """Test basic parallel sorting."""
        data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
        result = parallel_sort(data)
        expected = sorted(data)
        self.assertEqual(result, expected)
    
    def test_parallel_sort_with_key(self):
        """Test parallel sorting with key function."""
        words = ['apple', 'pie', 'banana', 'cherry']
        result = parallel_sort(words, key=len)
        expected = sorted(words, key=len)
        self.assertEqual(result, expected)
    
    def test_parallel_sort_reverse(self):
        """Test parallel sorting in reverse order."""
        data = [1, 2, 3, 4, 5]
        result = parallel_sort(data, reverse=True)
        expected = [5, 4, 3, 2, 1]
        self.assertEqual(result, expected)
    
    def test_parallel_sort_empty(self):
        """Test parallel sorting with empty list."""
        result = parallel_sort([])
        self.assertEqual(result, [])
    
    def test_parallel_group_by_basic(self):
        """Test basic parallel group_by."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = parallel_group_by(data, lambda x: x % 3)
        
        # Check that all expected keys are present
        self.assertIn(0, result)
        self.assertIn(1, result)
        self.assertIn(2, result)
        
        # Check group contents
        self.assertEqual(sorted(result[0]), [3, 6, 9])
        self.assertEqual(sorted(result[1]), [1, 4, 7, 10])
        self.assertEqual(sorted(result[2]), [2, 5, 8])
    
    def test_parallel_group_by_strings(self):
        """Test parallel group_by with strings."""
        words = ['apple', 'apricot', 'banana', 'blueberry', 'cherry']
        result = parallel_group_by(words, lambda w: w[0])
        
        self.assertIn('a', result)
        self.assertIn('b', result)
        self.assertIn('c', result)
        
        self.assertEqual(sorted(result['a']), ['apple', 'apricot'])
        self.assertEqual(sorted(result['b']), ['banana', 'blueberry'])
        self.assertEqual(sorted(result['c']), ['cherry'])
        
    def test_parallel_group_by_empty(self):
        """Test parallel group_by with empty list."""
        result = parallel_group_by([], lambda x: x)
        self.assertEqual(result, {})
    
    def test_parallel_unique_basic(self):
        """Test basic parallel unique."""
        data = [1, 2, 2, 3, 3, 3, 4, 4, 5]
        result = parallel_unique(data)
        expected = [1, 2, 3, 4, 5]
        # Order might not be preserved in parallel processing
        self.assertEqual(sorted(result), expected)
    
    def test_parallel_unique_with_key(self):
        """Test parallel unique with key function."""
        words = ['apple', 'APPLE', 'banana', 'BANANA', 'cherry']
        result = parallel_unique(words, key=str.lower)
        
        # Should have 3 unique items based on lowercase
        self.assertEqual(len(result), 3)
        unique_lower = [w.lower() for w in result]
        self.assertEqual(sorted(unique_lower), ['apple', 'banana', 'cherry'])
    
    def test_parallel_unique_empty(self):
        """Test parallel unique with empty list."""
        result = parallel_unique([])
        self.assertEqual(result, [])
    
    def test_parallel_partition_basic(self):
        """Test basic parallel partition."""
        numbers = list(range(10))
        evens, odds = parallel_partition(lambda x: x % 2 == 0, numbers)
        
        self.assertEqual(sorted(evens), [0, 2, 4, 6, 8])
        self.assertEqual(sorted(odds), [1, 3, 5, 7, 9])
    
    def test_parallel_partition_strings(self):
        """Test parallel partition with strings."""
        words = ['apple', 'banana', 'cherry', 'date', 'elderberry']
        short, long = parallel_partition(lambda w: len(w) <= 5, words)
        
        self.assertEqual(sorted(short), ['apple', 'date'])
        self.assertEqual(sorted(long), ['banana', 'cherry', 'elderberry'])
    
    def test_parallel_partition_empty(self):
        """Test parallel partition with empty list."""
        true_items, false_items = parallel_partition(lambda x: True, [])
        self.assertEqual(true_items, [])
        self.assertEqual(false_items, [])


class TestParallelChunks(unittest.TestCase):
    """Test parallel chunks processing."""
    
    def test_parallel_chunks_basic(self):
        """Test basic parallel chunks processing."""
        data = list(range(100))
        
        def sum_chunk(chunk_idx, chunk_data):
            return sum(chunk_data)
        
        results = parallel_chunks(data, 10, sum_chunk)
        
        # Should have 10 chunks
        self.assertEqual(len(results), 10)
        
        # Each result should be a sum
        for result in results:
            self.assertIsInstance(result, int)
            self.assertGreater(result, 0)
        
        # Total sum should match
        total_sum = sum(results)
        expected_sum = sum(data)
        self.assertEqual(total_sum, expected_sum)
    
    def test_parallel_chunks_with_info(self):
        """Test parallel chunks with chunk information."""
        data = list(range(50))
        
        def analyze_chunk(chunk_idx, chunk_data):
            return {
                'chunk_id': chunk_idx,
                'size': len(chunk_data),
                'min': min(chunk_data),
                'max': max(chunk_data),
                'sum': sum(chunk_data)
            }
        
        results = parallel_chunks(data, 5, analyze_chunk)
        
        # Should have 10 chunks
        self.assertEqual(len(results), 10)
        
        # Check structure
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn('chunk_id', result)
            self.assertIn('size', result)
            self.assertIn('sum', result)
            self.assertEqual(result['size'], 5)
    
    def test_parallel_chunks_empty(self):
        """Test parallel chunks with empty data."""
        results = parallel_chunks([], 10, lambda i, chunk: len(chunk))
        self.assertEqual(results, [])


class TestBatchProcessor(unittest.TestCase):
    """Test BatchProcessor functionality."""
    
    def test_batch_processor_initialization(self):
        """Test BatchProcessor initialization."""
        bp = BatchProcessor()
        self.assertIsInstance(bp, BatchProcessor)
        self.assertEqual(bp.batch_size, 1000)
        self.assertGreater(bp.max_workers, 0)
    
    def test_batch_processor_custom_params(self):
        """Test BatchProcessor with custom parameters."""
        bp = BatchProcessor(batch_size=100, max_workers=4)
        self.assertEqual(bp.batch_size, 100)
        self.assertEqual(bp.max_workers, 4)
    
    def test_batch_processor_process_batches(self):
        """Test BatchProcessor batch processing."""
        bp = BatchProcessor(batch_size=10)
        data = list(range(50))
        
        def process_batch(batch_idx, batch_data):
            return {
                'batch': batch_idx,
                'count': len(batch_data),
                'sum': sum(batch_data)
            }
        
        results = bp.process_batches(data, process_batch)
        
        # Should have 5 batches
        self.assertEqual(len(results), 5)
        
        # Check results structure
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn('batch', result)
            self.assertIn('count', result)
            self.assertIn('sum', result)
            self.assertEqual(result['count'], 10)
        
        # Check total sum
        total_sum = sum(r['sum'] for r in results)
        expected_sum = sum(data)
        self.assertEqual(total_sum, expected_sum)
    
    def test_batch_processor_empty_data(self):
        """Test BatchProcessor with empty data."""
        bp = BatchProcessor()
        results = bp.process_batches([], lambda i, batch: len(batch))
        self.assertEqual(results, [])


class TestProgressTracker(unittest.TestCase):
    """Test ProgressTracker functionality."""
    
    def test_progress_tracker_initialization(self):
        """Test ProgressTracker initialization."""
        tracker = ProgressTracker(total=100, desc="Test")
        self.assertEqual(tracker.total, 100)
        self.assertEqual(tracker.desc, "Test")
        self.assertEqual(tracker.completed, 0)
    
    def test_progress_tracker_update(self):
        """Test ProgressTracker update."""
        tracker = ProgressTracker(total=10)
        
        tracker.update(3)
        self.assertEqual(tracker.completed, 3)
        
        tracker.update(2)
        self.assertEqual(tracker.completed, 5)
        
        tracker.update()  # Default increment of 1
        self.assertEqual(tracker.completed, 6)
    
    def test_progress_tracker_no_total(self):
        """Test ProgressTracker without total."""
        tracker = ProgressTracker()
        self.assertIsNone(tracker.total)
        
        tracker.update(5)
        self.assertEqual(tracker.completed, 5)


class TestResultCollector(unittest.TestCase):
    """Test ResultCollector utility functions."""
    
    def test_result_collector_ordered(self):
        """Test ordered result collection."""
        data = [3, 1, 4, 1, 5]
        result = ResultCollector.ordered(data)
        self.assertEqual(result, [3, 1, 4, 1, 5])
    
    def test_result_collector_unordered(self):
        """Test unordered result collection."""
        data = [3, 1, 4, 1, 5]
        result = ResultCollector.unordered(data)
        # For now, our implementation maintains order
        self.assertEqual(result, [3, 1, 4, 1, 5])
    
    def test_result_collector_as_completed(self):
        """Test as_completed result collection."""
        futures = [1, 2, 3, 4, 5]
        results = list(ResultCollector.as_completed(futures))
        self.assertEqual(results, futures)


class TestLevel2Integration(unittest.TestCase):
    """Test Level 2 feature integration."""
    
    def test_data_processing_pipeline(self):
        """Test a complete data processing pipeline using Level 2 features."""
        # Generate sample data
        data = list(range(100))
        
        # Step 1: Filter even numbers
        evens, _ = parallel_partition(lambda x: x % 2 == 0, data)
        
        # Step 2: Group by remainder when divided by 4
        groups = parallel_group_by(evens, lambda x: x % 4)
        
        # Step 3: Sort each group
        sorted_groups = {}
        for key, group in groups.items():
            sorted_groups[key] = parallel_sort(group, reverse=True)
        
        # Verify results
        self.assertIn(0, sorted_groups)
        self.assertIn(2, sorted_groups)
        
        # Group 0 should have numbers divisible by 4 (0, 4, 8, ...)
        group_0 = sorted_groups[0]
        for num in group_0:
            self.assertEqual(num % 4, 0)
        
        # Should be sorted in descending order
        self.assertEqual(group_0, sorted(group_0, reverse=True))
    
    def test_batch_processing_workflow(self):
        """Test batch processing workflow."""
        # Create large dataset
        data = list(range(1000))
        
        # Process in batches
        bp = BatchProcessor(batch_size=50)
        
        def process_batch(batch_idx, batch_data):
            # Simulate some processing
            unique_items = parallel_unique(batch_data)
            return {
                'batch': batch_idx,
                'processed': len(unique_items),
                'sum': sum(unique_items)
            }
        
        results = bp.process_batches(data, process_batch)
        
        # Should have 20 batches
        self.assertEqual(len(results), 20)
        
        # Verify processing
        total_processed = sum(r['processed'] for r in results)
        total_sum = sum(r['sum'] for r in results)
        
        self.assertEqual(total_processed, 1000)  # All items should be unique
        self.assertEqual(total_sum, sum(data))   # Sum should match


if __name__ == '__main__':
    unittest.main(verbosity=2)
