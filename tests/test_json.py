"""
Unit tests for Pyferris JSON I/O operations.

This module contains comprehensive tests for all JSON functionality
including JsonReader, JsonWriter, and JSON utility functions.
"""

import unittest
import tempfile
import os
import shutil
import json
from pyferris.io.json import (
    JsonReader, JsonWriter,
    read_json, write_json, read_jsonl, write_jsonl, append_jsonl,
    parse_json, to_json_string
)


class TestJsonReader(unittest.TestCase):
    """Test JsonReader class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.json")
        
        # Create test JSON data
        self.test_data = {
            "name": "John Doe",
            "age": 30,
            "city": "New York",
            "hobbies": ["reading", "swimming", "coding"],
            "address": {
                "street": "123 Main St",
                "zipcode": "10001"
            }
        }
        
        # Write test JSON file
        with open(self.test_file, 'w') as f:
            json.dump(self.test_data, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_json_reader_initialization(self):
        """Test JsonReader initialization."""
        reader = JsonReader(self.test_file)
        self.assertIsInstance(reader, JsonReader)
    
    def test_read_json_object(self):
        """Test reading JSON object."""
        reader = JsonReader(self.test_file)
        result = reader.read()
        
        self.assertEqual(result, self.test_data)
    
    def test_read_json_array(self):
        """Test reading JSON array."""
        array_file = os.path.join(self.test_dir, "array.json")
        test_array = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"}
        ]
        
        with open(array_file, 'w') as f:
            json.dump(test_array, f)
        
        reader = JsonReader(array_file)
        result = reader.read()
        
        self.assertEqual(result, test_array)
    
    def test_read_jsonl_file(self):
        """Test reading JSON Lines file."""
        jsonl_file = os.path.join(self.test_dir, "test.jsonl")
        test_lines = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"}
        ]
        
        with open(jsonl_file, 'w') as f:
            for line in test_lines:
                f.write(json.dumps(line) + '\n')
        
        reader = JsonReader(jsonl_file)
        result = reader.read_lines()
        
        self.assertEqual(result, test_lines)
    
    def test_read_array_stream(self):
        """Test reading large JSON array in streaming mode."""
        large_array_file = os.path.join(self.test_dir, "large_array.json")
        test_array = [{"id": i, "value": f"item_{i}"} for i in range(100)]
        
        with open(large_array_file, 'w') as f:
            json.dump(test_array, f)
        
        reader = JsonReader(large_array_file)
        result = reader.read_array_stream()
        
        self.assertEqual(result, test_array)


class TestJsonWriter(unittest.TestCase):
    """Test JsonWriter class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "output.json")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_json_writer_initialization(self):
        """Test JsonWriter initialization."""
        writer = JsonWriter(self.test_file)
        self.assertIsInstance(writer, JsonWriter)
    
    def test_json_writer_with_pretty_print(self):
        """Test JsonWriter with pretty printing."""
        writer = JsonWriter(self.test_file, pretty_print=True)
        self.assertIsInstance(writer, JsonWriter)
    
    def test_write_json_object(self):
        """Test writing JSON object."""
        test_data = {
            "name": "Alice",
            "age": 25,
            "skills": ["Python", "Rust", "JavaScript"]
        }
        
        writer = JsonWriter(self.test_file)
        writer.write(test_data)
        
        # Verify the written file
        with open(self.test_file, 'r') as f:
            result = json.load(f)
        
        self.assertEqual(result, test_data)
    
    def test_write_json_array(self):
        """Test writing JSON array."""
        test_data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"}
        ]
        
        writer = JsonWriter(self.test_file)
        writer.write(test_data)
        
        # Verify the written file
        with open(self.test_file, 'r') as f:
            result = json.load(f)
        
        self.assertEqual(result, test_data)
    
    def test_write_jsonl(self):
        """Test writing JSON Lines format."""
        test_data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"}
        ]
        
        jsonl_file = os.path.join(self.test_dir, "output.jsonl")
        writer = JsonWriter(jsonl_file)
        writer.write_lines(test_data)
        
        # Verify the written file
        result = []
        with open(jsonl_file, 'r') as f:
            for line in f:
                result.append(json.loads(line.strip()))
        
        self.assertEqual(result, test_data)
    
    def test_append_jsonl(self):
        """Test appending to JSON Lines file."""
        jsonl_file = os.path.join(self.test_dir, "append.jsonl")
        
        # Write initial data
        initial_data = [{"id": 1, "name": "Alice"}]
        writer = JsonWriter(jsonl_file)
        writer.write_lines(initial_data)
        
        # Append more data
        append_data = [{"id": 2, "name": "Bob"}]
        writer.append_lines(append_data)
        
        # Verify the combined result
        result = []
        with open(jsonl_file, 'r') as f:
            for line in f:
                result.append(json.loads(line.strip()))
        
        expected = initial_data + append_data
        self.assertEqual(result, expected)
    
    def test_pretty_print_formatting(self):
        """Test pretty print formatting."""
        test_data = {
            "nested": {
                "array": [1, 2, 3],
                "object": {"key": "value"}
            }
        }
        
        writer = JsonWriter(self.test_file, pretty_print=True)
        writer.write(test_data)
        
        # Verify the file is formatted with indentation
        with open(self.test_file, 'r') as f:
            content = f.read()
        
        # Pretty printed JSON should have newlines and indentation
        self.assertIn('\n', content)
        self.assertIn('  ', content)  # Should have indentation


class TestJsonUtilityFunctions(unittest.TestCase):
    """Test JSON utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.input_file = os.path.join(self.test_dir, "input.json")
        self.output_file = os.path.join(self.test_dir, "output.json")
        
        # Create test JSON data
        self.test_data = {
            "users": [
                {"id": 1, "name": "John", "active": True},
                {"id": 2, "name": "Jane", "active": False}
            ],
            "meta": {"count": 2, "version": "1.0"}
        }
        
        with open(self.input_file, 'w') as f:
            json.dump(self.test_data, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_read_json_function(self):
        """Test read_json utility function."""
        result = read_json(self.input_file)
        self.assertEqual(result, self.test_data)
    
    def test_write_json_function(self):
        """Test write_json utility function."""
        new_data = {"message": "Hello World", "numbers": [1, 2, 3]}
        
        write_json(self.output_file, new_data)
        
        # Verify the written file
        result = read_json(self.output_file)
        self.assertEqual(result, new_data)
    
    def test_read_jsonl_function(self):
        """Test read_jsonl utility function."""
        jsonl_file = os.path.join(self.test_dir, "test.jsonl")
        test_lines = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        
        with open(jsonl_file, 'w') as f:
            for line in test_lines:
                f.write(json.dumps(line) + '\n')
        
        result = read_jsonl(jsonl_file)
        self.assertEqual(result, test_lines)
    
    def test_write_jsonl_function(self):
        """Test write_jsonl utility function."""
        jsonl_file = os.path.join(self.test_dir, "output.jsonl")
        test_data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
        
        write_jsonl(jsonl_file, test_data)
        
        # Verify the written file
        result = read_jsonl(jsonl_file)
        self.assertEqual(result, test_data)
    
    def test_append_jsonl_function(self):
        """Test append_jsonl utility function."""
        jsonl_file = os.path.join(self.test_dir, "append.jsonl")
        
        # Write initial data
        initial_data = [{"id": 1, "name": "Alice"}]
        write_jsonl(jsonl_file, initial_data)
        
        # Append more data
        append_data = [{"id": 2, "name": "Bob"}]
        append_jsonl(jsonl_file, append_data)
        
        # Verify the combined result
        result = read_jsonl(jsonl_file)
        expected = initial_data + append_data
        self.assertEqual(result, expected)
    
    def test_parse_json_function(self):
        """Test parse_json utility function."""
        json_string = '{"name": "John", "age": 30, "active": true}'
        result = parse_json(json_string)
        
        expected = {"name": "John", "age": 30, "active": True}
        self.assertEqual(result, expected)
    
    def test_to_json_string_function(self):
        """Test to_json_string utility function."""
        data = {"name": "John", "age": 30, "active": True}
        result = to_json_string(data)
        
        # Parse it back to verify
        parsed = json.loads(result)
        self.assertEqual(parsed, data)


class TestJsonEdgeCases(unittest.TestCase):
    """Test JSON edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_empty_json_object(self):
        """Test handling empty JSON object."""
        empty_file = os.path.join(self.test_dir, "empty.json")
        with open(empty_file, 'w') as f:
            json.dump({}, f)
        
        reader = JsonReader(empty_file)
        result = reader.read()
        self.assertEqual(result, {})
    
    def test_empty_json_array(self):
        """Test handling empty JSON array."""
        empty_array_file = os.path.join(self.test_dir, "empty_array.json")
        with open(empty_array_file, 'w') as f:
            json.dump([], f)
        
        reader = JsonReader(empty_array_file)
        result = reader.read()
        self.assertEqual(result, [])
    
    def test_nested_json_structures(self):
        """Test deeply nested JSON structures."""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "data": "deep value",
                            "array": [
                                {"nested_obj": {"key": "value"}}
                            ]
                        }
                    }
                }
            }
        }
        
        nested_file = os.path.join(self.test_dir, "nested.json")
        write_json(nested_file, nested_data)
        
        result = read_json(nested_file)
        self.assertEqual(result, nested_data)
    
    def test_unicode_handling(self):
        """Test Unicode character handling."""
        unicode_data = {
            "english": "Hello World",
            "spanish": "Hola Mundo",
            "chinese": "你好世界",
            "japanese": "こんにちは世界",
            "emoji": "🌍🚀🎉",
            "special_chars": "\"quotes\" & <tags> & symbols: @#$%"
        }
        
        unicode_file = os.path.join(self.test_dir, "unicode.json")
        write_json(unicode_file, unicode_data)
        
        result = read_json(unicode_file)
        self.assertEqual(result, unicode_data)
    
    def test_large_numbers(self):
        """Test handling of large numbers."""
        number_data = {
            "small_int": 42,
            "large_int": 123456789012345,
            "float": 3.141592653589793,
            "scientific": 1.23e-10,
            "negative": -999999
        }
        
        number_file = os.path.join(self.test_dir, "numbers.json")
        write_json(number_file, number_data)
        
        result = read_json(number_file)
        self.assertEqual(result, number_data)
    
    def test_null_values(self):
        """Test handling of null values."""
        null_data = {
            "not_null": "value",
            "null_value": None,
            "array_with_null": [1, None, 3],
            "nested": {"inner_null": None}
        }
        
        null_file = os.path.join(self.test_dir, "nulls.json")
        write_json(null_file, null_data)
        
        result = read_json(null_file)
        self.assertEqual(result, null_data)
    
    def test_invalid_json_error(self):
        """Test error handling for invalid JSON."""
        invalid_file = os.path.join(self.test_dir, "invalid.json")
        with open(invalid_file, 'w') as f:
            f.write('{"invalid": json content}')  # Invalid JSON
        
        reader = JsonReader(invalid_file)
        with self.assertRaises(Exception):
            reader.read()
    
    def test_nonexistent_file_error(self):
        """Test error handling for nonexistent files."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.json")
        
        with self.assertRaises(Exception):
            reader = JsonReader(nonexistent_file)
            reader.read()


class TestJsonPerformance(unittest.TestCase):
    """Test JSON performance characteristics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_large_json_object_performance(self):
        """Test performance with large JSON objects."""
        import time
        
        # Create a large JSON object
        large_data = {
            "users": [
                {
                    "id": i,
                    "name": f"user_{i}",
                    "email": f"user_{i}@example.com",
                    "profile": {
                        "age": i % 100,
                        "location": f"City_{i % 50}",
                        "interests": [f"hobby_{j}" for j in range(i % 5)]
                    }
                } for i in range(5000)
            ],
            "metadata": {
                "total_users": 5000,
                "generated_at": "2023-01-01T00:00:00Z",
                "version": "1.0"
            }
        }
        
        large_file = os.path.join(self.test_dir, "large.json")
        
        # Test write performance
        start_time = time.time()
        write_json(large_file, large_data)
        write_time = time.time() - start_time
        
        # Test read performance
        start_time = time.time()
        result = read_json(large_file)
        read_time = time.time() - start_time
        
        # Verify correctness
        self.assertEqual(len(result["users"]), 5000)
        self.assertEqual(result["metadata"]["total_users"], 5000)
        
        # Performance should be reasonable
        print(f"JSON write time for large object: {write_time:.4f}s")
        print(f"JSON read time for large object: {read_time:.4f}s")
        self.assertLess(write_time, 10.0, "JSON writing took too long")
        self.assertLess(read_time, 10.0, "JSON reading took too long")
    
    def test_jsonl_performance(self):
        """Test performance with JSON Lines format."""
        import time
        
        # Create test data
        test_data = [
            {"id": i, "name": f"user_{i}", "score": i * 2}
            for i in range(10000)
        ]
        
        jsonl_file = os.path.join(self.test_dir, "performance.jsonl")
        
        # Test write performance
        start_time = time.time()
        write_jsonl(jsonl_file, test_data)
        write_time = time.time() - start_time
        
        # Test read performance
        start_time = time.time()
        result = read_jsonl(jsonl_file)
        read_time = time.time() - start_time
        
        # Verify correctness
        self.assertEqual(len(result), 10000)
        self.assertEqual(result[0]["id"], 0)
        self.assertEqual(result[9999]["id"], 9999)
        
        # Performance should be reasonable
        print(f"JSONL write time for 10k records: {write_time:.4f}s")
        print(f"JSONL read time for 10k records: {read_time:.4f}s")
        self.assertLess(write_time, 5.0, "JSONL writing took too long")
        self.assertLess(read_time, 5.0, "JSONL reading took too long")


if __name__ == '__main__':
    unittest.main(verbosity=2)
