"""
Simple IO Examples for Pyferris

This example demonstrates basic file I/O capabilities:
- Basic file operations (read, write)
- Parallel file processing
"""

import os
import tempfile
import pyferris.simple_io as pio


def demonstrate_basic_file_operations():
    """Demonstrate basic file read/write operations"""
    print("=== Basic File Operations ===")
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        temp_file = f.name
        f.write("Hello, Pyferris!\nThis is a test file.\nWith multiple lines.")
    
    try:
        # Read entire file
        content = pio.read_file(temp_file)
        print(f"File content:\n{content}")
        
        # Check file exists and get size
        print(f"File exists: {pio.file_exists(temp_file)}")
        print(f"File size: {pio.file_size(temp_file)} bytes")
        
        # Using SimpleFileReader class
        reader = pio.SimpleFileReader(temp_file)
        lines = reader.read_lines()
        print(f"Lines: {lines}")
        
        # Using SimpleFileWriter class
        new_file = temp_file + ".new"
        writer = pio.SimpleFileWriter(new_file)
        writer.write_text("New content written via SimpleFileWriter")
        
        # Read the new file
        new_content = pio.read_file(new_file)
        print(f"New file content: {new_content}")
        
        # Append to file
        writer.append_text("\nAppended line!")
        
        # Read again
        updated_content = pio.read_file(new_file)
        print(f"Updated content: {updated_content}")
        
        # Clean up
        pio.delete_file(new_file)
        
    finally:
        # Clean up
        pio.delete_file(temp_file)
        print("Temporary files deleted")


def demonstrate_parallel_operations():
    """Demonstrate parallel file operations"""
    print("\n=== Parallel File Operations ===")
    
    # Create temporary directory and files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create multiple test files
        file_data = []
        for i in range(5):
            file_path = os.path.join(temp_dir, f"test_{i}.txt")
            content = f"This is test file {i}\n" * (i + 1)
            file_data.append((file_path, content))
        
        # Write files in parallel
        pio.write_files_parallel(file_data)
        print(f"Created {len(file_data)} files in parallel")
        
        # Read files in parallel
        file_paths = [path for path, _ in file_data]
        contents = pio.read_files_parallel(file_paths)
        print(f"Read {len(contents)} files in parallel")
        
        # Verify contents
        for i, content in enumerate(contents):
            expected_lines = i + 1
            actual_lines = len(content.strip().split('\n'))
            print(f"File {i}: expected {expected_lines} lines, got {actual_lines} lines")
        
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        print("Temporary directory cleaned up")


def demonstrate_file_management():
    """Demonstrate file management operations"""
    print("\n=== File Management ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a test file
        test_file = os.path.join(temp_dir, "test.txt")
        pio.write_file(test_file, "Original content")
        
        # Copy file
        copied_file = os.path.join(temp_dir, "test_copy.txt")
        pio.copy_file(test_file, copied_file)
        print(f"Copied file: {pio.file_exists(copied_file)}")
        
        # Verify copy content
        copy_content = pio.read_file(copied_file)
        print(f"Copy content: {copy_content}")
        
        # Move file
        moved_file = os.path.join(temp_dir, "test_moved.txt")
        pio.move_file(copied_file, moved_file)
        print(f"Original copy exists: {pio.file_exists(copied_file)}")
        print(f"Moved file exists: {pio.file_exists(moved_file)}")
        
        # Create subdirectory
        sub_dir = os.path.join(temp_dir, "subdir")
        pio.create_directory(sub_dir)
        print(f"Subdirectory created: {os.path.exists(sub_dir)}")
        
        # File sizes
        print(f"Test file size: {pio.file_size(test_file)} bytes")
        print(f"Moved file size: {pio.file_size(moved_file)} bytes")
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)
        print("Temporary directory cleaned up")


def main():
    """Run all simple IO examples"""
    print("Pyferris Simple IO Examples")
    print("============================")
    
    demonstrate_basic_file_operations()
    demonstrate_parallel_operations()
    demonstrate_file_management()
    
    print("\n=== Performance Test ===")
    
    # Simple performance comparison
    import time
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Create test files
        file_data = []
        for i in range(10):
            file_path = os.path.join(temp_dir, f"perf_test_{i}.txt")
            content = f"Performance test file {i}\n" * 50
            file_data.append((file_path, content))
        
        # Sequential write
        start_time = time.time()
        for file_path, content in file_data:
            pio.write_file(file_path, content)
        sequential_time = time.time() - start_time
        
        # Delete files
        for file_path, _ in file_data:
            pio.delete_file(file_path)
        
        # Parallel write
        start_time = time.time()
        pio.write_files_parallel(file_data)
        parallel_time = time.time() - start_time
        
        print(f"Sequential write: {sequential_time:.4f} seconds")
        print(f"Parallel write: {parallel_time:.4f} seconds")
        
        if parallel_time > 0:
            speedup = sequential_time / parallel_time
            print(f"Speedup: {speedup:.2f}x")
        
        # Test reading
        file_paths = [path for path, _ in file_data]
        
        start_time = time.time()
        sequential_reads = []
        for file_path in file_paths:
            content = pio.read_file(file_path)
            sequential_reads.append(content)
        sequential_read_time = time.time() - start_time
        
        start_time = time.time()
        parallel_reads = pio.read_files_parallel(file_paths)
        parallel_read_time = time.time() - start_time
        
        print(f"Sequential read: {sequential_read_time:.4f} seconds")
        print(f"Parallel read: {parallel_read_time:.4f} seconds")
        
        if parallel_read_time > 0:
            read_speedup = sequential_read_time / parallel_read_time
            print(f"Read speedup: {read_speedup:.2f}x")
        
        # Verify results are the same
        assert len(sequential_reads) == len(parallel_reads), "Result count mismatch"
        for i, (seq, par) in enumerate(zip(sequential_reads, parallel_reads)):
            assert seq == par, f"Content mismatch in file {i}"
        
        print("✓ Results verified - parallel processing is correct!")
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)
    
    print("\n🎉 All simple IO examples completed successfully!")


if __name__ == "__main__":
    main()
