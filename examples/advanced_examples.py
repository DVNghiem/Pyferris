"""
PyFerris Level 2 Examples: Advanced Parallel Operations

This file demonstrates the intermediate features of PyFerris Level 2:
- Advanced parallel operations (sort, group_by, unique, partition)
- Batch processing with BatchProcessor
- Progress tracking with ProgressTracker
- Result collection modes
"""

import time
import random
import sys
import os

# Add the project root to Python path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def advanced_parallel_operations():
    """Demonstrate advanced parallel operations."""
    print("=== Advanced Parallel Operations ===")
    
    try:
        from pyferris.advanced import (
            parallel_sort, parallel_group_by, parallel_unique, parallel_partition
        )
        
        # Sample data
        print("\n1. Parallel Sort:")
        numbers = [random.randint(1, 100) for _ in range(20)]
        print(f"Original: {numbers}")
        
        sorted_asc = parallel_sort(numbers)
        print(f"Sorted (ascending): {sorted_asc}")
        
        sorted_desc = parallel_sort(numbers, reverse=True)
        print(f"Sorted (descending): {sorted_desc}")
        
        # Sort with key function
        words = ['apple', 'pie', 'banana', 'cherry', 'date']
        sorted_by_length = parallel_sort(words, key=len)
        print(f"Words sorted by length: {sorted_by_length}")
        
        print("\n2. Parallel Group By:")
        data = list(range(1, 21))
        groups = parallel_group_by(data, lambda x: x % 3)
        print("Numbers 1-20 grouped by remainder when divided by 3:")
        for key, group in sorted(groups.items()):
            print(f"  Remainder {key}: {sorted(group)}")
        
        # Group strings by first letter
        fruits = ['apple', 'apricot', 'banana', 'blueberry', 'cherry', 'coconut']
        fruit_groups = parallel_group_by(fruits, lambda word: word[0])
        print("\nFruits grouped by first letter:")
        for letter, fruit_list in sorted(fruit_groups.items()):
            print(f"  {letter.upper()}: {sorted(fruit_list)}")
        
        print("\n3. Parallel Unique:")
        duplicated_data = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]
        unique_items = parallel_unique(duplicated_data)
        print(f"Original with duplicates: {duplicated_data}")
        print(f"Unique items: {sorted(unique_items)}")
        
        # Unique with key function (case-insensitive)
        mixed_case = ['Apple', 'APPLE', 'banana', 'BANANA', 'Cherry', 'cherry']
        unique_words = parallel_unique(mixed_case, key=str.lower)
        print(f"Mixed case words: {mixed_case}")
        print(f"Unique (case-insensitive): {unique_words}")
        
        print("\n4. Parallel Partition:")
        numbers = list(range(20))
        evens, odds = parallel_partition(lambda x: x % 2 == 0, numbers)
        print(f"Numbers: {numbers}")
        print(f"Even numbers: {sorted(evens)}")
        print(f"Odd numbers: {sorted(odds)}")
        
        # Partition strings by length
        words = ['cat', 'dog', 'elephant', 'mouse', 'hippopotamus', 'ant']
        short_words, long_words = parallel_partition(lambda w: len(w) <= 4, words)
        print(f"Words: {words}")
        print(f"Short words (<=4 chars): {sorted(short_words)}")
        print(f"Long words (>4 chars): {sorted(long_words)}")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please build the project first with: maturin develop")


def batch_processing_examples():
    """Demonstrate batch processing capabilities."""
    print("\n=== Batch Processing Examples ===")
    
    try:
        from pyferris.advanced import BatchProcessor, parallel_chunks
        
        print("\n1. BatchProcessor:")
        # Create a large dataset
        large_dataset = list(range(1000))
        
        # Initialize batch processor
        bp = BatchProcessor(batch_size=100, max_workers=4)
        print(f"Batch size: {bp.batch_size}, Max workers: {bp.max_workers}")
        
        def process_batch(batch_idx, batch_data):
            """Process a single batch."""
            # Simulate some computational work
            batch_sum = sum(batch_data)
            batch_avg = batch_sum / len(batch_data)
            return {
                'batch_id': batch_idx,
                'size': len(batch_data),
                'sum': batch_sum,
                'average': batch_avg,
                'min': min(batch_data),
                'max': max(batch_data)
            }
        
        print("Processing 1000 items in batches of 100...")
        start_time = time.time()
        results = bp.process_batches(large_dataset, process_batch)
        end_time = time.time()
        
        print(f"Processed {len(results)} batches in {end_time - start_time:.3f} seconds")
        print("Sample batch results:")
        for i, result in enumerate(results[:3]):
            print(f"  Batch {result['batch_id']}: {result['size']} items, "
                  f"sum={result['sum']}, avg={result['average']:.1f}")
        
        print("\n2. Parallel Chunks:")
        data = list(range(50))
        
        def analyze_chunk(chunk_idx, chunk_data):
            """Analyze a chunk of data."""
            return {
                'chunk': chunk_idx,
                'size': len(chunk_data),
                'sum': sum(chunk_data),
                'product': 1 if not chunk_data else eval('*'.join(map(str, chunk_data)) if len(chunk_data) <= 3 else '1')  # Simple product for small chunks
            }
        
        chunk_results = parallel_chunks(data, 5, analyze_chunk)
        
        print(f"Processed {len(chunk_results)} chunks:")
        for result in chunk_results[:5]:  # Show first 5
            print(f"  Chunk {result['chunk']}: {result['size']} items, sum={result['sum']}")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please build the project first with: maturin develop")


def progress_tracking_example():
    """Demonstrate progress tracking."""
    print("\n=== Progress Tracking Example ===")
    
    try:
        from pyferris.advanced import ProgressTracker
        
        # Simulate a long-running task
        data = list(range(1000))
        
        def slow_process(chunk_idx, chunk_data):
            """Simulate slow processing with progress updates."""
            time.sleep(0.01)  # Simulate work
            return sum(chunk_data)
        
        print("Processing with progress tracking...")
        
        # Create progress tracker
        tracker = ProgressTracker(total=10, desc="Processing chunks")
        
        # Process in chunks and update progress
        chunk_size = len(data) // 10
        results = []
        
        for i in range(10):
            start_idx = i * chunk_size
            end_idx = (i + 1) * chunk_size if i < 9 else len(data)
            chunk = data[start_idx:end_idx]
            
            result = slow_process(i, chunk)
            results.append(result)
            tracker.update(1)
        
        tracker.close()
        
        print(f"Final results: Total sum = {sum(results)}")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please build the project first with: maturin develop")


def result_collection_example():
    """Demonstrate different result collection modes."""
    print("\n=== Result Collection Example ===")
    
    try:
        from pyferris.advanced import ResultCollector
        
        # Sample results from different sources
        results_a = [1, 3, 5, 7, 9]
        results_b = [2, 4, 6, 8, 10]
        results_c = [11, 12, 13, 14, 15]
        
        print("Sample results from different sources:")
        print(f"Source A: {results_a}")
        print(f"Source B: {results_b}")
        print(f"Source C: {results_c}")
        
        print("\n1. Ordered collection:")
        ordered_a = ResultCollector.ordered(results_a)
        print(f"Ordered A: {ordered_a}")
        
        print("\n2. Unordered collection:")
        unordered_b = ResultCollector.unordered(results_b)
        print(f"Unordered B: {unordered_b}")
        
        print("\n3. As-completed simulation:")
        all_results = [results_a, results_b, results_c]
        completed_results = list(ResultCollector.as_completed(all_results))
        print(f"As completed: {len(completed_results)} result sets")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please build the project first with: maturin develop")


def comprehensive_data_pipeline():
    """Demonstrate a comprehensive data processing pipeline."""
    print("\n=== Comprehensive Data Processing Pipeline ===")
    
    try:
        from pyferris.advanced import (
            parallel_sort, parallel_group_by, parallel_unique, parallel_partition,
            BatchProcessor
        )
        
        print("Simulating a real-world data processing scenario...")
        
        # Step 1: Generate synthetic data
        print("\n1. Generating synthetic data...")
        random.seed(42)  # For reproducible results
        
        # Simulate user transaction data
        transactions = []
        user_ids = list(range(1, 101))  # 100 users
        categories = ['food', 'transport', 'entertainment', 'shopping', 'utilities']
        
        for _ in range(1000):
            transaction = {
                'user_id': random.choice(user_ids),
                'amount': round(random.uniform(5.0, 500.0), 2),
                'category': random.choice(categories),
                'timestamp': time.time() - random.randint(0, 86400 * 30)  # Last 30 days
            }
            transactions.append(transaction)
        
        print(f"Generated {len(transactions)} transactions")
        
        # Step 2: Filter valid transactions (amount > 10)
        print("\n2. Filtering valid transactions...")
        valid_txns, invalid_txns = parallel_partition(
            lambda t: t['amount'] > 10.0, 
            transactions
        )
        print(f"Valid transactions: {len(valid_txns)}")
        print(f"Invalid transactions: {len(invalid_txns)}")
        
        # Step 3: Group by category
        print("\n3. Grouping by category...")
        category_groups = parallel_group_by(valid_txns, lambda t: t['category'])
        
        print("Transactions by category:")
        for category, txns in sorted(category_groups.items()):
            total_amount = sum(t['amount'] for t in txns)
            print(f"  {category.capitalize()}: {len(txns)} transactions, ${total_amount:.2f} total")
        
        # Step 4: Find top spenders
        print("\n4. Finding top spenders...")
        user_groups = parallel_group_by(valid_txns, lambda t: t['user_id'])
        
        user_totals = []
        for user_id, user_txns in user_groups.items():
            total_spent = sum(t['amount'] for t in user_txns)
            user_totals.append({
                'user_id': user_id,
                'total_spent': total_spent,
                'transaction_count': len(user_txns)
            })
        
        # Sort by total spent (descending)
        top_spenders = parallel_sort(user_totals, key=lambda u: u['total_spent'], reverse=True)
        
        print("Top 5 spenders:")
        for i, user in enumerate(top_spenders[:5]):
            print(f"  {i+1}. User {user['user_id']}: ${user['total_spent']:.2f} "
                  f"({user['transaction_count']} transactions)")
        
        # Step 5: Process high-value transactions in batches
        print("\n5. Processing high-value transactions...")
        high_value_txns, _ = parallel_partition(lambda t: t['amount'] > 100.0, valid_txns)
        
        bp = BatchProcessor(batch_size=20)
        
        def analyze_high_value_batch(batch_idx, batch_data):
            categories = [t['category'] for t in batch_data]
            unique_categories = list(set(categories))
            avg_amount = sum(t['amount'] for t in batch_data) / len(batch_data)
            
            return {
                'batch': batch_idx,
                'count': len(batch_data),
                'categories': unique_categories,
                'avg_amount': avg_amount
            }
        
        batch_results = bp.process_batches(high_value_txns, analyze_high_value_batch)
        
        print(f"Processed {len(high_value_txns)} high-value transactions in {len(batch_results)} batches")
        print("Batch analysis summary:")
        for result in batch_results[:3]:  # Show first 3 batches
            print(f"  Batch {result['batch']}: {result['count']} txns, "
                  f"categories: {result['categories']}, "
                  f"avg: ${result['avg_amount']:.2f}")
        
        print("\n6. Final summary:")
        total_amount = sum(t['amount'] for t in valid_txns)
        unique_users = len(parallel_unique(valid_txns, key=lambda t: t['user_id']))
        unique_categories = len(parallel_unique(valid_txns, key=lambda t: t['category']))
        
        print(f"  Total processed amount: ${total_amount:.2f}")
        print(f"  Unique users: {unique_users}")
        print(f"  Categories: {unique_categories}")
        print(f"  Average transaction: ${total_amount / len(valid_txns):.2f}")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please build the project first with: maturin develop")


def performance_comparison_level2():
    """Compare Level 2 parallel operations vs sequential."""
    print("\n=== Performance Comparison: Level 2 Operations ===")
    
    try:
        from pyferris.advanced import parallel_sort, parallel_group_by, parallel_unique
        
        # Test data
        large_dataset = [random.randint(1, 1000) for _ in range(10000)]
        
        print("Testing with 10,000 random integers...")
        
        # Sequential sort vs parallel sort
        print("\n1. Sorting comparison:")
        
        start_time = time.time()
        sequential_sorted = sorted(large_dataset)
        sequential_time = time.time() - start_time
        
        start_time = time.time()
        parallel_sorted = parallel_sort(large_dataset)
        parallel_time = time.time() - start_time
        
        print(f"Sequential sort: {sequential_time:.4f} seconds")
        print(f"Parallel sort: {parallel_time:.4f} seconds")
        print(f"Speedup: {sequential_time / parallel_time:.2f}x")
        print(f"Results match: {sequential_sorted == parallel_sorted}")
        
        # Sequential unique vs parallel unique
        print("\n2. Unique elements comparison:")
        
        start_time = time.time()
        sequential_unique = list(set(large_dataset))
        sequential_time = time.time() - start_time
        
        start_time = time.time()
        parallel_unique_result = parallel_unique(large_dataset)
        parallel_time = time.time() - start_time
        
        print(f"Sequential unique (set): {sequential_time:.4f} seconds")
        print(f"Parallel unique: {parallel_time:.4f} seconds")
        print(f"Sequential count: {len(sequential_unique)}")
        print(f"Parallel count: {len(parallel_unique_result)}")
        
        # Group by comparison
        print("\n3. Group by comparison:")
        
        start_time = time.time()
        sequential_groups = {}
        for item in large_dataset:
            key = item % 10
            if key not in sequential_groups:
                sequential_groups[key] = []
            sequential_groups[key].append(item)
        sequential_time = time.time() - start_time
        
        start_time = time.time()
        parallel_groups = parallel_group_by(large_dataset, lambda x: x % 10)
        parallel_time = time.time() - start_time
        
        print(f"Sequential group_by: {sequential_time:.4f} seconds")
        print(f"Parallel group_by: {parallel_time:.4f} seconds")
        print(f"Speedup: {sequential_time / parallel_time:.2f}x")
        print(f"Group count matches: {len(sequential_groups) == len(parallel_groups)}")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please build the project first with: maturin develop")


if __name__ == "__main__":
    print("PyFerris Level 2 Examples")
    print("=" * 50)
    
    advanced_parallel_operations()
    batch_processing_examples()
    progress_tracking_example()
    result_collection_example()
    comprehensive_data_pipeline()
    performance_comparison_level2()
    
    print("\n" + "=" * 50)
    print("Level 2 examples completed!")
    print("\nLevel 2 Features Summary:")
    print("✓ Advanced parallel operations (sort, group_by, unique, partition)")
    print("✓ Batch processing with configurable batch sizes")
    print("✓ Progress tracking for long-running operations")
    print("✓ Result collection in different modes")
    print("✓ Comprehensive data processing pipelines")
    print("✓ Performance optimizations for large datasets")
