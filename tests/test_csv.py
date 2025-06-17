"""
Unit tests for Pyferris CSV I/O operations.

This module contains comprehensive tests for all CSV functionality
including CsvReader, CsvWriter, and CSV utility functions.
"""

import unittest
import tempfile
import os
import shutil
import csv
from pyferris.io.csv import (
    CsvReader, CsvWriter,
    read_csv, write_csv, read_csv_rows, write_csv_rows
)


class TestCsvReader(unittest.TestCase):
    """Test CsvReader class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.csv")
        
        # Create test CSV data
        self.test_data = [
            ["name", "age", "city"],
            ["John", "25", "New York"],
            ["Jane", "30", "San Francisco"],
            ["Bob", "35", "Chicago"]
        ]
        
        # Write test CSV file
        with open(self.test_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.test_data)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_csv_reader_initialization_with_headers(self):
        """Test CsvReader initialization with headers."""
        reader = CsvReader(self.test_file, delimiter=',', has_headers=True)
        self.assertIsInstance(reader, CsvReader)
    
    def test_csv_reader_initialization_without_headers(self):
        """Test CsvReader initialization without headers."""
        reader = CsvReader(self.test_file, delimiter=',', has_headers=False)
        self.assertIsInstance(reader, CsvReader)
    
    def test_read_dict_with_headers(self):
        """Test reading CSV as dictionary with headers."""
        reader = CsvReader(self.test_file, delimiter=',', has_headers=True)
        result = reader.read_dict()
        
        expected = [
            {"name": "John", "age": "25", "city": "New York"},
            {"name": "Jane", "age": "30", "city": "San Francisco"},
            {"name": "Bob", "age": "35", "city": "Chicago"}
        ]
        
        self.assertEqual(result, expected)
    
    def test_read_rows(self):
        """Test reading CSV as rows."""
        reader = CsvReader(self.test_file, delimiter=',', has_headers=True)
        result = reader.read_rows()
        
        # Should exclude header row when has_headers=True
        expected = [
            ["John", "25", "New York"],
            ["Jane", "30", "San Francisco"],
            ["Bob", "35", "Chicago"]
        ]
        
        self.assertEqual(result, expected)
    
    def test_get_headers(self):
        """Test getting CSV headers."""
        reader = CsvReader(self.test_file, delimiter=',', has_headers=True)
        headers = reader.get_headers()
        
        expected = ["name", "age", "city"]
        self.assertEqual(headers, expected)
    
    def test_custom_delimiter(self):
        """Test reading CSV with custom delimiter."""
        # Create CSV with semicolon delimiter
        custom_file = os.path.join(self.test_dir, "custom.csv")
        custom_data = [
            ["name;age;city"],
            ["John;25;New York"],
            ["Jane;30;San Francisco"]
        ]
        
        with open(custom_file, 'w', newline='') as f:
            for row in custom_data:
                f.write(row[0] + '\n')
        
        reader = CsvReader(custom_file, delimiter=';', has_headers=True)
        result = reader.read_dict()
        
        expected = [
            {"name": "John", "age": "25", "city": "New York"},
            {"name": "Jane", "age": "30", "city": "San Francisco"}
        ]
        
        self.assertEqual(result, expected)
    
    def test_read_without_headers(self):
        """Test reading CSV without headers."""
        reader = CsvReader(self.test_file, delimiter=',', has_headers=False)
        result = reader.read_rows()
        
        # Should include all rows including the header row
        expected = [
            ["name", "age", "city"],
            ["John", "25", "New York"],
            ["Jane", "30", "San Francisco"],
            ["Bob", "35", "Chicago"]
        ]
        
        self.assertEqual(result, expected)


class TestCsvWriter(unittest.TestCase):
    """Test CsvWriter class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "output.csv")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_csv_writer_initialization(self):
        """Test CsvWriter initialization."""
        writer = CsvWriter(self.test_file, delimiter=',', write_headers=True)
        self.assertIsInstance(writer, CsvWriter)
    
    def test_write_dict_with_headers(self):
        """Test writing dictionary data with headers."""
        data = [
            {"name": "Alice", "age": "28", "city": "Boston"},
            {"name": "Charlie", "age": "32", "city": "Seattle"}
        ]
        
        writer = CsvWriter(self.test_file, delimiter=',', write_headers=True)
        writer.write_dict(data)
        
        # Verify the written file
        with open(self.test_file, 'r') as f:
            reader = csv.DictReader(f)
            result = list(reader)
        
        self.assertEqual(result, data)
    
    def test_write_rows(self):
        """Test writing row data."""
        headers = ["name", "age", "city"]
        rows = [
            ["Alice", "28", "Boston"],
            ["Charlie", "32", "Seattle"]
        ]
        
        writer = CsvWriter(self.test_file, delimiter=',', write_headers=True)
        writer.write_rows(headers, rows)
        
        # Verify the written file
        with open(self.test_file, 'r') as f:
            reader = csv.reader(f)
            result = list(reader)
        
        expected = [headers] + rows
        self.assertEqual(result, expected)
    
    def test_custom_delimiter_writer(self):
        """Test writing CSV with custom delimiter."""
        data = [
            {"name": "Alice", "age": "28"},
            {"name": "Bob", "age": "32"}
        ]
        
        writer = CsvWriter(self.test_file, delimiter=';', write_headers=True)
        writer.write_dict(data)
        
        # Verify the written file has semicolon delimiter
        with open(self.test_file, 'r') as f:
            content = f.read()
        
        self.assertIn(';', content)
        self.assertIn('name;age', content)
    
    def test_write_without_headers(self):
        """Test writing CSV without headers."""
        rows = [
            ["Alice", "28", "Boston"],
            ["Charlie", "32", "Seattle"]
        ]
        
        writer = CsvWriter(self.test_file, delimiter=',', write_headers=False)
        writer.write_rows([], rows)
        
        # Verify the written file
        with open(self.test_file, 'r') as f:
            reader = csv.reader(f)
            result = list(reader)
        
        self.assertEqual(result, rows)


class TestCsvUtilityFunctions(unittest.TestCase):
    """Test CSV utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.input_file = os.path.join(self.test_dir, "input.csv")
        self.output_file = os.path.join(self.test_dir, "output.csv")
        
        # Create test CSV data
        self.test_data = [
            ["name", "age", "city"],
            ["John", "25", "New York"],
            ["Jane", "30", "San Francisco"]
        ]
        
        with open(self.input_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.test_data)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_read_csv_function(self):
        """Test read_csv utility function."""
        result = read_csv(self.input_file)
        
        expected = [
            {"name": "John", "age": "25", "city": "New York"},
            {"name": "Jane", "age": "30", "city": "San Francisco"}
        ]
        
        self.assertEqual(result, expected)
    
    def test_write_csv_function(self):
        """Test write_csv utility function."""
        data = [
            {"name": "Alice", "age": "28", "city": "Boston"},
            {"name": "Bob", "age": "32", "city": "Seattle"}
        ]
        
        write_csv(self.output_file, data)
        
        # Verify the written file
        result = read_csv(self.output_file)
        self.assertEqual(result, data)
    
    def test_read_csv_rows_function(self):
        """Test read_csv_rows utility function."""
        result = read_csv_rows(self.input_file)
        
        expected = [
            ["John", "25", "New York"],
            ["Jane", "30", "San Francisco"]
        ]
        
        self.assertEqual(result, expected)
    
    def test_write_csv_rows_function(self):
        """Test write_csv_rows utility function."""
        headers = ["name", "age", "city"]
        rows = [
            ["Alice", "28", "Boston"],
            ["Bob", "32", "Seattle"]
        ]
        
        write_csv_rows(self.output_file, headers, rows)
        
        # Verify the written file
        result_headers, result_rows = [], []
        with open(self.output_file, 'r') as f:
            reader = csv.reader(f)
            all_rows = list(reader)
            result_headers = all_rows[0]
            result_rows = all_rows[1:]
        
        self.assertEqual(result_headers, headers)
        self.assertEqual(result_rows, rows)


class TestCsvEdgeCases(unittest.TestCase):
    """Test CSV edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_empty_csv_file(self):
        """Test reading empty CSV file."""
        empty_file = os.path.join(self.test_dir, "empty.csv")
        with open(empty_file, 'w'):
            pass  # Create empty file
        
        reader = CsvReader(empty_file, has_headers=False)
        result = reader.read_rows()
        self.assertEqual(result, [])
    
    def test_csv_with_quotes(self):
        """Test CSV with quoted fields."""
        quoted_file = os.path.join(self.test_dir, "quoted.csv")
        quoted_data = [
            ['name', 'description', 'price'],
            ['Product A', 'A great product, with "quotes"', '29.99'],
            ['Product B', 'Another product\nwith newlines', '39.99']
        ]
        
        with open(quoted_file, 'w', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerows(quoted_data)
        
        reader = CsvReader(quoted_file, has_headers=True)
        result = reader.read_dict()
        
        expected = [
            {'name': 'Product A', 'description': 'A great product, with "quotes"', 'price': '29.99'},
            {'name': 'Product B', 'description': 'Another product\nwith newlines', 'price': '39.99'}
        ]
        
        self.assertEqual(result, expected)
    
    def test_csv_with_missing_fields(self):
        """Test CSV with missing fields."""
        incomplete_file = os.path.join(self.test_dir, "incomplete.csv")
        
        with open(incomplete_file, 'w') as f:
            f.write("name,age,city\n")
            f.write("John,25\n")  # Missing city
            f.write("Jane,,Boston\n")  # Missing age
        
        reader = CsvReader(incomplete_file, has_headers=True)
        result = reader.read_dict()
        
        expected = [
            {'name': 'John', 'age': '25', 'city': ''},
            {'name': 'Jane', 'age': '', 'city': 'Boston'}
        ]
        
        self.assertEqual(result, expected)
    
    def test_nonexistent_file_error(self):
        """Test error handling for nonexistent files."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.csv")
        
        with self.assertRaises(Exception):
            reader = CsvReader(nonexistent_file)
            reader.read_dict()
    
    def test_large_csv_file(self):
        """Test handling of larger CSV files."""
        large_file = os.path.join(self.test_dir, "large.csv")
        
        # Create a larger CSV file
        with open(large_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'value'])
            
            for i in range(1000):
                writer.writerow([str(i), f'name_{i}', str(i * 2)])
        
        reader = CsvReader(large_file, has_headers=True)
        result = reader.read_dict()
        
        # Verify correct number of rows
        self.assertEqual(len(result), 1000)
        
        # Verify some sample data
        self.assertEqual(result[0]['id'], '0')
        self.assertEqual(result[0]['name'], 'name_0')
        self.assertEqual(result[0]['value'], '0')
        
        self.assertEqual(result[999]['id'], '999')
        self.assertEqual(result[999]['name'], 'name_999')
        self.assertEqual(result[999]['value'], '1998')


class TestCsvPerformance(unittest.TestCase):
    """Test CSV performance characteristics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_read_performance(self):
        """Test CSV reading performance."""
        import time
        
        perf_file = os.path.join(self.test_dir, "performance.csv")
        
        # Create a moderately sized CSV file
        with open(perf_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'email', 'score'])
            
            for i in range(5000):
                writer.writerow([
                    str(i),
                    f'user_{i}',
                    f'user_{i}@example.com',
                    str(i % 100)
                ])
        
        # Test read performance
        start_time = time.time()
        reader = CsvReader(perf_file, has_headers=True)
        result = reader.read_dict()
        end_time = time.time()
        
        read_time = end_time - start_time
        
        # Verify correctness
        self.assertEqual(len(result), 5000)
        self.assertEqual(result[0]['id'], '0')
        self.assertEqual(result[4999]['id'], '4999')
        
        # Performance should be reasonable (adjust threshold as needed)
        print(f"CSV read time for 5000 rows: {read_time:.4f}s")
        self.assertLess(read_time, 5.0, "CSV reading took too long")
    
    def test_write_performance(self):
        """Test CSV writing performance."""
        import time
        
        perf_file = os.path.join(self.test_dir, "write_performance.csv")
        
        # Prepare data
        data = []
        for i in range(5000):
            data.append({
                'id': str(i),
                'name': f'user_{i}',
                'email': f'user_{i}@example.com',
                'score': str(i % 100)
            })
        
        # Test write performance
        start_time = time.time()
        writer = CsvWriter(perf_file, write_headers=True)
        writer.write_dict(data)
        end_time = time.time()
        
        write_time = end_time - start_time
        
        # Verify the file was written correctly
        self.assertTrue(os.path.exists(perf_file))
        
        # Read back and verify
        reader = CsvReader(perf_file, has_headers=True)
        result = reader.read_dict()
        self.assertEqual(len(result), 5000)
        
        # Performance should be reasonable
        print(f"CSV write time for 5000 rows: {write_time:.4f}s")
        self.assertLess(write_time, 5.0, "CSV writing took too long")


if __name__ == '__main__':
    unittest.main(verbosity=2)
