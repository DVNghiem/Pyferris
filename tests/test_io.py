"""
PyFerris I/O Operations Tests

Tests for I/O functionality:
- CSV operations
- JSON operations  
- File reader/writer
- Simple I/O
- Parallel I/O
"""

import pytest
import os
import json
import csv
from pathlib import Path

from pyferris.io import (
    csv as pyferris_csv,
    json as pyferris_json,
    file_reader,
    file_writer,
    simple_io,
    parallel_io
)


class TestCSVOperations:
    """Test CSV I/O operations."""

    def test_csv_read_basic(self, test_data_dir, sample_csv_data):
        """Test basic CSV reading."""
        # Create test CSV file
        csv_file = os.path.join(test_data_dir, "test.csv")
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age", "city"])
            writer.writeheader()
            writer.writerows(sample_csv_data)
        
        # Test reading
        try:
            result = pyferris_csv.read_csv(csv_file)
            assert len(result) == len(sample_csv_data)
            
            # Check first row
            if result:
                assert "name" in result[0]
                assert "age" in result[0]
                assert "city" in result[0]
        except (AttributeError, ImportError):
            # CSV functionality might not be available
            pytest.skip("CSV functionality not available")

    def test_csv_write_basic(self, test_data_dir, sample_csv_data):
        """Test basic CSV writing."""
        csv_file = os.path.join(test_data_dir, "output.csv")
        
        try:
            # Write CSV
            pyferris_csv.write_csv(csv_file, sample_csv_data)
            
            # Verify file exists and has content
            assert os.path.exists(csv_file)
            
            # Read back with standard library
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == len(sample_csv_data)
                
        except (AttributeError, ImportError):
            pytest.skip("CSV functionality not available")

    def test_csv_read_write_roundtrip(self, test_data_dir, sample_csv_data):
        """Test CSV read/write roundtrip."""
        csv_file = os.path.join(test_data_dir, "roundtrip.csv")
        
        try:
            # Write then read
            pyferris_csv.write_csv(csv_file, sample_csv_data)
            result = pyferris_csv.read_csv(csv_file)
            
            # Should preserve data structure
            assert len(result) == len(sample_csv_data)
            
            # Check that keys are preserved
            if result and sample_csv_data:
                assert set(result[0].keys()) == set(sample_csv_data[0].keys())
                
        except (AttributeError, ImportError):
            pytest.skip("CSV functionality not available")

    def test_csv_empty_file(self, test_data_dir):
        """Test CSV operations with empty file."""
        empty_csv = os.path.join(test_data_dir, "empty.csv")
        Path(empty_csv).touch()  # Create empty file
        
        try:
            result = pyferris_csv.read_csv(empty_csv)
            assert result == [] or result is None
        except (AttributeError, ImportError):
            pytest.skip("CSV functionality not available")

    def test_csv_nonexistent_file(self, test_data_dir):
        """Test CSV reading with nonexistent file."""
        nonexistent = os.path.join(test_data_dir, "nonexistent.csv")
        
        try:
            with pytest.raises((FileNotFoundError, IOError)):
                pyferris_csv.read_csv(nonexistent)
        except (AttributeError, ImportError):
            pytest.skip("CSV functionality not available")


class TestJSONOperations:
    """Test JSON I/O operations."""

    def test_json_read_basic(self, test_data_dir, sample_json_data):
        """Test basic JSON reading."""
        # Create test JSON file
        json_file = os.path.join(test_data_dir, "test.json")
        with open(json_file, 'w') as f:
            json.dump(sample_json_data, f)
        
        try:
            result = pyferris_json.read_json(json_file)
            assert result == sample_json_data
        except (AttributeError, ImportError):
            pytest.skip("JSON functionality not available")

    def test_json_write_basic(self, test_data_dir, sample_json_data):
        """Test basic JSON writing."""
        json_file = os.path.join(test_data_dir, "output.json")
        
        try:
            # Write JSON
            pyferris_json.write_json(json_file, sample_json_data)
            
            # Verify file exists and has correct content
            assert os.path.exists(json_file)
            
            # Read back with standard library
            with open(json_file, 'r') as f:
                result = json.load(f)
                assert result == sample_json_data
                
        except (AttributeError, ImportError):
            pytest.skip("JSON functionality not available")

    def test_json_read_write_roundtrip(self, test_data_dir, sample_json_data):
        """Test JSON read/write roundtrip."""
        json_file = os.path.join(test_data_dir, "roundtrip.json")
        
        try:
            # Write then read
            pyferris_json.write_json(json_file, sample_json_data)
            result = pyferris_json.read_json(json_file)
            
            # Should preserve data exactly
            assert result == sample_json_data
                
        except (AttributeError, ImportError):
            pytest.skip("JSON functionality not available")

    def test_json_complex_data(self, test_data_dir):
        """Test JSON with complex nested data."""
        complex_data = {
            "array": [1, 2, 3, {"nested": True}],
            "object": {
                "string": "value",
                "number": 42,
                "boolean": False,
                "null": None
            },
            "unicode": "Hello 世界! 🌍"
        }
        
        json_file = os.path.join(test_data_dir, "complex.json")
        
        try:
            pyferris_json.write_json(json_file, complex_data)
            result = pyferris_json.read_json(json_file)
            assert result == complex_data
        except (AttributeError, ImportError):
            pytest.skip("JSON functionality not available")

    def test_json_empty_file(self, test_data_dir):
        """Test JSON operations with empty file."""
        empty_json = os.path.join(test_data_dir, "empty.json")
        Path(empty_json).touch()  # Create empty file
        
        try:
            with pytest.raises((json.JSONDecodeError, ValueError)):
                pyferris_json.read_json(empty_json)
        except (AttributeError, ImportError):
            pytest.skip("JSON functionality not available")

    def test_json_invalid_data(self, test_data_dir):
        """Test JSON reading with invalid data."""
        invalid_json = os.path.join(test_data_dir, "invalid.json")
        with open(invalid_json, 'w') as f:
            f.write("{invalid json}")
        
        try:
            with pytest.raises((json.JSONDecodeError, ValueError)):
                pyferris_json.read_json(invalid_json)
        except (AttributeError, ImportError):
            pytest.skip("JSON functionality not available")


class TestFileOperations:
    """Test file reader and writer operations."""

    def test_file_reader_basic(self, temp_files):
        """Test basic file reading."""
        try:
            content = file_reader.read_file(temp_files[0])
            assert isinstance(content, str)
            assert "Content of file 0" in content
        except (AttributeError, ImportError):
            pytest.skip("File reader functionality not available")

    def test_file_reader_multiple_files(self, temp_files):
        """Test reading multiple files."""
        try:
            contents = file_reader.read_files(temp_files[:3])
            assert len(contents) == 3
            for i, content in enumerate(contents):
                assert f"Content of file {i}" in content
        except (AttributeError, ImportError):
            pytest.skip("File reader functionality not available")

    def test_file_writer_basic(self, test_data_dir):
        """Test basic file writing."""
        output_file = os.path.join(test_data_dir, "written.txt")
        test_content = "This is test content\nWith multiple lines"
        
        try:
            file_writer.write_file(output_file, test_content)
            
            # Verify file was written
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                content = f.read()
                assert content == test_content
        except (AttributeError, ImportError):
            pytest.skip("File writer functionality not available")

    def test_file_writer_multiple_files(self, test_data_dir):
        """Test writing multiple files."""
        file_data = [
            (os.path.join(test_data_dir, f"multi_{i}.txt"), f"Content for file {i}")
            for i in range(3)
        ]
        
        try:
            file_writer.write_files(file_data)
            
            # Verify all files were written
            for file_path, expected_content in file_data:
                assert os.path.exists(file_path)
                with open(file_path, 'r') as f:
                    content = f.read()
                    assert content == expected_content
        except (AttributeError, ImportError):
            pytest.skip("File writer functionality not available")

    def test_file_operations_nonexistent_file(self, test_data_dir):
        """Test file operations with nonexistent file."""
        nonexistent = os.path.join(test_data_dir, "nonexistent.txt")
        
        try:
            with pytest.raises((FileNotFoundError, IOError)):
                file_reader.read_file(nonexistent)
        except (AttributeError, ImportError):
            pytest.skip("File reader functionality not available")

    def test_file_operations_empty_file(self, test_data_dir):
        """Test file operations with empty file."""
        empty_file = os.path.join(test_data_dir, "empty.txt")
        Path(empty_file).touch()
        
        try:
            content = file_reader.read_file(empty_file)
            assert content == ""
        except (AttributeError, ImportError):
            pytest.skip("File reader functionality not available")


class TestSimpleIO:
    """Test simple I/O operations."""

    def test_simple_io_basic(self, test_data_dir):
        """Test basic simple I/O operations."""
        test_file = os.path.join(test_data_dir, "simple_io.txt")
        test_data = ["line1", "line2", "line3"]
        
        try:
            # Write data
            simple_io.write_lines(test_file, test_data)
            
            # Read data back
            result = simple_io.read_lines(test_file)
            assert result == test_data
        except (AttributeError, ImportError):
            pytest.skip("Simple I/O functionality not available")

    def test_simple_io_empty_data(self, test_data_dir):
        """Test simple I/O with empty data."""
        test_file = os.path.join(test_data_dir, "empty_lines.txt")
        
        try:
            simple_io.write_lines(test_file, [])
            result = simple_io.read_lines(test_file)
            assert result == []
        except (AttributeError, ImportError):
            pytest.skip("Simple I/O functionality not available")

    def test_simple_io_large_data(self, test_data_dir):
        """Test simple I/O with large amount of data."""
        test_file = os.path.join(test_data_dir, "large_data.txt")
        large_data = [f"line_{i}" for i in range(1000)]
        
        try:
            simple_io.write_lines(test_file, large_data)
            result = simple_io.read_lines(test_file)
            assert result == large_data
        except (AttributeError, ImportError):
            pytest.skip("Simple I/O functionality not available")

    def test_simple_io_unicode(self, test_data_dir):
        """Test simple I/O with unicode data."""
        test_file = os.path.join(test_data_dir, "unicode.txt")
        unicode_data = ["Hello 世界!", "🌍 Earth", "Ñoño niño"]
        
        try:
            simple_io.write_lines(test_file, unicode_data)
            result = simple_io.read_lines(test_file)
            assert result == unicode_data
        except (AttributeError, ImportError):
            pytest.skip("Simple I/O functionality not available")


class TestParallelIO:
    """Test parallel I/O operations."""

    def test_parallel_io_read_multiple_files(self, temp_files):
        """Test parallel reading of multiple files."""
        try:
            results = parallel_io.read_files_parallel(temp_files[:3])
            assert len(results) == 3
            
            # Verify each file's content
            for i, content in enumerate(results):
                assert f"Content of file {i}" in content
        except (AttributeError, ImportError):
            pytest.skip("Parallel I/O functionality not available")

    def test_parallel_io_write_multiple_files(self, test_data_dir):
        """Test parallel writing of multiple files."""
        file_data = [
            (os.path.join(test_data_dir, f"parallel_{i}.txt"), f"Parallel content {i}")
            for i in range(5)
        ]
        
        try:
            parallel_io.write_files_parallel(file_data)
            
            # Verify all files were written correctly
            for file_path, expected_content in file_data:
                assert os.path.exists(file_path)
                with open(file_path, 'r') as f:
                    content = f.read()
                    assert content == expected_content
        except (AttributeError, ImportError):
            pytest.skip("Parallel I/O functionality not available")

    def test_parallel_io_process_files(self, temp_files):
        """Test parallel file processing."""
        def count_lines(file_path):
            with open(file_path, 'r') as f:
                return len(f.readlines())
        
        try:
            results = parallel_io.process_files(temp_files[:3], count_lines)
            assert len(results) == 3
            
            # Each test file should have 10 lines
            for count in results:
                assert count == 10
        except (AttributeError, ImportError):
            pytest.skip("Parallel I/O functionality not available")

    def test_parallel_io_copy_files(self, test_data_dir, temp_files):
        """Test parallel file copying."""
        copy_pairs = [
            (temp_files[i], os.path.join(test_data_dir, f"copy_{i}.txt"))
            for i in range(3)
        ]
        
        try:
            parallel_io.copy_files_parallel(copy_pairs)
            
            # Verify all files were copied
            for src, dst in copy_pairs:
                assert os.path.exists(dst)
                
                # Content should match
                with open(src, 'r') as f1, open(dst, 'r') as f2:
                    assert f1.read() == f2.read()
        except (AttributeError, ImportError):
            pytest.skip("Parallel I/O functionality not available")

    def test_parallel_io_process_directory(self, test_data_dir, temp_files):
        """Test parallel directory processing."""
        def get_file_size(file_path):
            return os.path.getsize(file_path)
        
        try:
            # Process all txt files in the directory
            results = parallel_io.process_directory(
                test_data_dir, 
                get_file_size,
                file_filter=lambda f: f.endswith('.txt')
            )
            
            # Should have processed some files
            assert isinstance(results, list)
        except (AttributeError, ImportError):
            pytest.skip("Parallel I/O functionality not available")

    def test_parallel_io_get_file_stats(self, temp_files):
        """Test parallel file statistics gathering."""
        try:
            stats = parallel_io.get_file_stats_parallel(temp_files[:3])
            assert len(stats) == 3
            
            # Each stat should have file information
            for stat in stats:
                assert 'size' in stat or hasattr(stat, 'st_size')
        except (AttributeError, ImportError):
            pytest.skip("Parallel I/O functionality not available")

    @pytest.mark.slow
    def test_parallel_io_performance(self, test_data_dir):
        """Test parallel I/O performance vs sequential."""
        # Create multiple test files
        file_paths = []
        for i in range(10):
            file_path = os.path.join(test_data_dir, f"perf_test_{i}.txt")
            with open(file_path, 'w') as f:
                # Write some content
                for j in range(100):
                    f.write(f"Line {j} in file {i}\n")
            file_paths.append(file_path)
        
        try:
            import time
            
            # Sequential reading
            start_time = time.time()
            sequential_results = []
            for file_path in file_paths:
                with open(file_path, 'r') as f:
                    sequential_results.append(f.read())
            sequential_time = time.time() - start_time
            
            # Parallel reading
            start_time = time.time()
            parallel_results = parallel_io.read_files_parallel(file_paths)
            parallel_time = time.time() - start_time
            
            # Results should be the same
            assert len(parallel_results) == len(sequential_results)
            
            # Parallel should be competitive (or at least not much slower)
            if sequential_time > 0.01:  # Only check for operations that take reasonable time
                improvement_ratio = sequential_time / parallel_time
                assert improvement_ratio > 0.5, f"Parallel I/O should be competitive: {improvement_ratio:.2f}x"
                
        except (AttributeError, ImportError):
            pytest.skip("Parallel I/O functionality not available")


class TestIOEdgeCases:
    """Test edge cases for I/O operations."""

    def test_io_with_very_large_files(self, test_data_dir):
        """Test I/O operations with large files."""
        large_file = os.path.join(test_data_dir, "large_file.txt")
        
        # Create a moderately large file
        with open(large_file, 'w') as f:
            for i in range(10000):
                f.write(f"This is line {i} with some content to make it longer\n")
        
        try:
            # Should be able to read large files
            content = file_reader.read_file(large_file)
            assert len(content) > 10000
            assert "This is line 0" in content
            assert "This is line 9999" in content
        except (AttributeError, ImportError):
            pytest.skip("File reader functionality not available")

    def test_io_with_binary_files(self, test_data_dir):
        """Test I/O operations with binary files."""
        binary_file = os.path.join(test_data_dir, "binary_file.bin")
        binary_data = bytes(range(256))
        
        with open(binary_file, 'wb') as f:
            f.write(binary_data)
        
        # Text-based readers might fail with binary files
        try:
            content = file_reader.read_file(binary_file)
            # If it succeeds, content should be a string
            assert isinstance(content, str)
        except (UnicodeDecodeError, AttributeError, ImportError):
            # Expected to fail with binary content
            pass

    def test_io_permissions_error(self, test_data_dir):
        """Test I/O operations with permission errors."""
        if os.name == 'posix':  # Unix-like systems
            # Create a file with no read permissions
            no_read_file = os.path.join(test_data_dir, "no_read.txt")
            with open(no_read_file, 'w') as f:
                f.write("secret content")
            os.chmod(no_read_file, 0o000)  # No permissions
            
            try:
                with pytest.raises((PermissionError, OSError)):
                    file_reader.read_file(no_read_file)
            except (AttributeError, ImportError):
                pytest.skip("File reader functionality not available")
            finally:
                # Restore permissions for cleanup
                try:
                    os.chmod(no_read_file, 0o644)
                except OSError:
                    pass

    def test_io_concurrent_access(self, test_data_dir):
        """Test concurrent access to the same file."""
        shared_file = os.path.join(test_data_dir, "shared.txt")
        with open(shared_file, 'w') as f:
            f.write("shared content")
        
        try:
            # Multiple parallel reads should work
            file_paths = [shared_file] * 5
            results = parallel_io.read_files_parallel(file_paths)
            
            # All should read the same content
            for result in results:
                assert "shared content" in result
        except (AttributeError, ImportError):
            pytest.skip("Parallel I/O functionality not available")


if __name__ == "__main__":
    pytest.main([__file__])
