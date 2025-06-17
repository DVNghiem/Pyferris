"""
Unit tests for Pyferris Simple IO module.

This module contains comprehensive tests for all simple IO functionality
including file operations, parallel processing, and class-based interfaces.
"""

import unittest
import tempfile
import os
import shutil
import pyferris.simple_io as sio
from pyferris import SimpleFileReader, SimpleFileWriter


class TestSimpleFileOperations(unittest.TestCase):
    """Test basic file operations (functions)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        self.test_content = "Hello, World! This is a test file."
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_write_and_read_file(self):
        """Test basic file write and read operations."""
        # Write file
        sio.write_file(self.test_file, self.test_content)
        self.assertTrue(os.path.exists(self.test_file))
        
        # Read file
        content = sio.read_file(self.test_file)
        self.assertEqual(content, self.test_content)
    
    def test_file_exists(self):
        """Test file existence checking."""
        # Non-existent file
        self.assertFalse(sio.file_exists(self.test_file))
        
        # Create file and test again
        sio.write_file(self.test_file, self.test_content)
        self.assertTrue(sio.file_exists(self.test_file))
    
    def test_file_size(self):
        """Test file size calculation."""
        sio.write_file(self.test_file, self.test_content)
        size = sio.file_size(self.test_file)
        expected_size = len(self.test_content.encode('utf-8'))
        self.assertEqual(size, expected_size)
    
    def test_copy_file(self):
        """Test file copying."""
        # Create source file
        sio.write_file(self.test_file, self.test_content)
        
        # Copy file
        dest_file = os.path.join(self.test_dir, "copy.txt")
        sio.copy_file(self.test_file, dest_file)
        
        # Verify copy
        self.assertTrue(sio.file_exists(dest_file))
        copied_content = sio.read_file(dest_file)
        self.assertEqual(copied_content, self.test_content)
    
    def test_move_file(self):
        """Test file moving."""
        # Create source file
        sio.write_file(self.test_file, self.test_content)
        
        # Move file
        dest_file = os.path.join(self.test_dir, "moved.txt")
        sio.move_file(self.test_file, dest_file)
        
        # Verify move
        self.assertFalse(sio.file_exists(self.test_file))
        self.assertTrue(sio.file_exists(dest_file))
        moved_content = sio.read_file(dest_file)
        self.assertEqual(moved_content, self.test_content)
    
    def test_delete_file(self):
        """Test file deletion."""
        # Create file
        sio.write_file(self.test_file, self.test_content)
        self.assertTrue(sio.file_exists(self.test_file))
        
        # Delete file
        sio.delete_file(self.test_file)
        self.assertFalse(sio.file_exists(self.test_file))
    
    def test_create_directory(self):
        """Test directory creation."""
        new_dir = os.path.join(self.test_dir, "subdir", "nested")
        sio.create_directory(new_dir)
        self.assertTrue(os.path.isdir(new_dir))


class TestParallelFileOperations(unittest.TestCase):
    """Test parallel file operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_files = []
        self.test_contents = []
        
        # Create multiple test files
        for i in range(5):
            file_path = os.path.join(self.test_dir, f"test_{i}.txt")
            content = f"Test content for file {i}. Line 1.\nLine 2 of file {i}."
            self.test_files.append(file_path)
            self.test_contents.append(content)
            
            with open(file_path, 'w') as f:
                f.write(content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_parallel_read_files(self):
        """Test parallel reading of multiple files."""
        contents = sio.read_files_parallel(self.test_files)
        
        # Verify all files were read
        self.assertEqual(len(contents), len(self.test_files))
        
        # Verify contents match (order might differ due to parallelism)
        for content in contents:
            self.assertIn(content, self.test_contents)
    
    def test_parallel_write_files(self):
        """Test parallel writing of multiple files."""
        # Prepare write data (file_path, content) tuples
        write_files = []
        write_contents = []
        
        for i in range(3):
            file_path = os.path.join(self.test_dir, f"parallel_write_{i}.txt")
            content = f"Parallel write content {i}"
            write_files.append(file_path)
            write_contents.append(content)
        
        write_data = list(zip(write_files, write_contents))
        
        # Perform parallel write
        sio.write_files_parallel(write_data)
        
        # Verify files were written correctly
        for file_path, expected_content in write_data:
            self.assertTrue(os.path.exists(file_path))
            actual_content = sio.read_file(file_path)
            self.assertEqual(actual_content, expected_content)


class TestSimpleFileReader(unittest.TestCase):
    """Test SimpleFileReader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "reader_test.txt")
        self.test_content = "Reader test content.\nSecond line.\nThird line."
        
        with open(self.test_file, 'w') as f:
            f.write(self.test_content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_reader_initialization(self):
        """Test SimpleFileReader initialization."""
        reader = SimpleFileReader(self.test_file)
        self.assertIsInstance(reader, SimpleFileReader)
    
    def test_read_text(self):
        """Test reading text content."""
        reader = SimpleFileReader(self.test_file)
        content = reader.read_text()
        self.assertEqual(content, self.test_content)
    
    def test_read_lines(self):
        """Test reading lines."""
        reader = SimpleFileReader(self.test_file)
        lines = reader.read_lines()
        expected_lines = self.test_content.split('\n')
        self.assertEqual(lines, expected_lines)


class TestSimpleFileWriter(unittest.TestCase):
    """Test SimpleFileWriter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "writer_test.txt")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_writer_initialization(self):
        """Test SimpleFileWriter initialization."""
        writer = SimpleFileWriter(self.test_file)
        self.assertIsInstance(writer, SimpleFileWriter)
    
    def test_write_text(self):
        """Test writing text content."""
        writer = SimpleFileWriter(self.test_file)
        test_content = "Writer test content."
        
        writer.write_text(test_content)
        
        # Verify content was written
        with open(self.test_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, test_content)
    
    def test_append_text(self):
        """Test appending text content."""
        writer = SimpleFileWriter(self.test_file)
        
        # Write initial content
        initial_content = "Initial content."
        writer.write_text(initial_content)
        
        # Append content
        append_content = "\nAppended content."
        writer.append_text(append_content)
        
        # Verify both contents are present
        with open(self.test_file, 'r') as f:
            content = f.read()
        expected_content = initial_content + append_content
        self.assertEqual(content, expected_content)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in IO operations."""
    
    def test_read_nonexistent_file(self):
        """Test reading a non-existent file raises appropriate error."""
        with self.assertRaises(Exception):
            sio.read_file("/nonexistent/path/file.txt")
    
    def test_write_to_invalid_path(self):
        """Test writing to an invalid path raises appropriate error."""
        with self.assertRaises(Exception):
            sio.write_file("/root/restricted/file.txt", "content")
    
    def test_reader_nonexistent_file(self):
        """Test SimpleFileReader with non-existent file."""
        reader = SimpleFileReader("/nonexistent/file.txt")
        with self.assertRaises(Exception):
            reader.read_text()
    
    def test_copy_nonexistent_file(self):
        """Test copying a non-existent file."""
        with self.assertRaises(Exception):
            sio.copy_file("/nonexistent/source.txt", "/tmp/dest.txt")


class TestPerformance(unittest.TestCase):
    """Test performance characteristics of IO operations."""
    
    def setUp(self):
        """Set up performance test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up performance test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_large_file_operations(self):
        """Test operations with larger files."""
        # Create a larger test file (1MB)
        large_content = "A" * (1024 * 1024)  # 1MB of 'A's
        large_file = os.path.join(self.test_dir, "large_file.txt")
        
        # Test write performance
        import time
        start_time = time.time()
        sio.write_file(large_file, large_content)
        write_time = time.time() - start_time
        
        # Test read performance
        start_time = time.time()
        read_content = sio.read_file(large_file)
        read_time = time.time() - start_time
        
        # Verify content integrity
        self.assertEqual(len(read_content), len(large_content))
        self.assertEqual(read_content, large_content)
        
        # Performance should be reasonable (adjust thresholds as needed)
        self.assertLess(write_time, 5.0, "Large file write took too long")
        self.assertLess(read_time, 5.0, "Large file read took too long")
    
    def test_parallel_vs_sequential_performance(self):
        """Compare parallel vs sequential file operations."""
        import time
        
        # Create test files
        test_files = []
        test_contents = []
        
        for i in range(10):
            file_path = os.path.join(self.test_dir, f"perf_test_{i}.txt")
            content = f"Performance test content {i}. " * 100  # Longer content
            test_files.append(file_path)
            test_contents.append(content)
            
            # Write files sequentially for setup
            sio.write_file(file_path, content)
        
        # Test sequential read
        start_time = time.time()
        sequential_contents = []
        for file_path in test_files:
            sequential_contents.append(sio.read_file(file_path))
        sequential_time = time.time() - start_time
        
        # Test parallel read
        start_time = time.time()
        parallel_contents = sio.read_files_parallel(test_files)
        parallel_time = time.time() - start_time
        
        # Verify results are equivalent
        self.assertEqual(len(sequential_contents), len(parallel_contents))
        
        # Parallel should be faster or at least not significantly slower
        print(f"Sequential time: {sequential_time:.4f}s")
        print(f"Parallel time: {parallel_time:.4f}s")
        print(f"Speedup: {sequential_time/parallel_time:.2f}x")


if __name__ == '__main__':
    # Create a test suite combining all test cases
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestSimpleFileOperations,
        TestParallelFileOperations,
        TestSimpleFileReader,
        TestSimpleFileWriter,
        TestErrorHandling,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
