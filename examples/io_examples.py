"""
Level 2 Examples: File I/O Operations

This example demonstrates the file I/O capabilities of Pyferris:
- Basic file operations (read, write, append)
- CSV file handling
- JSON file operations
- Parallel file processing
- Directory operations
"""

import os
import tempfile
import pyferris.io as pio


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
        
        # Append to file
        pio.append_file(temp_file, "\nAppended line!")
        
        # Read again to see the change
        updated_content = pio.read_file(temp_file)
        print(f"Updated content:\n{updated_content}")
        
        # Using FileReader class for advanced operations
        reader = pio.FileReader(temp_file)
        lines = reader.read_lines()
        print(f"Lines: {lines}")
        
        # Process lines in parallel
        def process_line(line):
            return f"Processed: {line.upper()}"
        
        processed = reader.process_lines_parallel(process_line)
        print(f"Processed lines: {processed}")
        
    finally:
        # Clean up
        pio.delete_file(temp_file)
        print("Temporary file deleted")


def demonstrate_csv_operations():
    """Demonstrate CSV file operations"""
    print("\n=== CSV Operations ===")
    
    # Sample CSV data
    csv_data = [
        {"name": "Alice", "age": "30", "city": "New York"},
        {"name": "Bob", "age": "25", "city": "San Francisco"},
        {"name": "Charlie", "age": "35", "city": "Chicago"},
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        csv_file = f.name
    
    try:
        # Write CSV using convenience function
        pio.write_csv(csv_file, csv_data)
        print(f"CSV written to {csv_file}")
        
        # Read CSV back
        read_data = pio.read_csv(csv_file)
        print(f"Read CSV data: {read_data}")
        
        # Using CsvReader/Writer classes for more control
        writer = pio.CsvWriter(csv_file, delimiter=';', write_headers=True)
        writer.write_dict(csv_data)
        
        reader = pio.CsvReader(csv_file, delimiter=';', has_headers=True)
        headers = reader.get_headers()
        print(f"CSV headers: {headers}")
        
        rows = reader.read_rows()
        print(f"CSV rows: {rows}")
        
    finally:
        pio.delete_file(csv_file)


def demonstrate_json_operations():
    """Demonstrate JSON file operations"""
    print("\n=== JSON Operations ===")
    
    # Sample JSON data
    json_data = {
        "users": [
            {"id": 1, "name": "Alice", "active": True},
            {"id": 2, "name": "Bob", "active": False},
            {"id": 3, "name": "Charlie", "active": True},
        ],
        "metadata": {
            "version": "1.0",
            "created": "2024-01-01"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        jsonl_file = f.name
    
    try:
        # Write and read JSON
        pio.write_json(json_file, json_data, pretty_print=True)
        read_data = pio.read_json(json_file)
        print(f"JSON data: {read_data}")
        
        # JSON Lines operations
        jsonl_data = [
            {"event": "login", "user": "alice", "timestamp": "2024-01-01T10:00:00"},
            {"event": "logout", "user": "bob", "timestamp": "2024-01-01T11:00:00"},
            {"event": "login", "user": "charlie", "timestamp": "2024-01-01T12:00:00"},
        ]
        
        pio.write_jsonl(jsonl_file, jsonl_data)
        read_jsonl = pio.read_jsonl(jsonl_file)
        print(f"JSONL data: {read_jsonl}")
        
        # Append to JSONL
        pio.append_jsonl(jsonl_file, {"event": "new_event", "user": "david"})
        updated_jsonl = pio.read_jsonl(jsonl_file)
        print(f"Updated JSONL: {updated_jsonl}")
        
        # Parse JSON string
        json_str = '{"test": "value", "number": 42}'
        parsed = pio.parse_json(json_str)
        print(f"Parsed JSON: {parsed}")
        
        # Convert to JSON string
        obj = {"converted": True, "values": [1, 2, 3]}
        json_string = pio.to_json_string(obj, pretty_print=True)
        print(f"JSON string:\n{json_string}")
        
    finally:
        pio.delete_file(json_file)
        pio.delete_file(jsonl_file)


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
        
        # Process files with custom function
        def file_processor(file_path, content):
            line_count = len(content.strip().split('\n'))
            word_count = len(content.split())
            return {"file": os.path.basename(file_path), "lines": line_count, "words": word_count}
        
        results = pio.process_files_parallel(file_paths, file_processor)
        print(f"File processing results: {results}")
        
        # Find files matching pattern
        found_files = pio.find_files(temp_dir, "test_*.txt")
        print(f"Found files: {found_files}")
        
        # Count total lines across all files
        total_lines = pio.count_lines(file_paths)
        print(f"Total lines across all files: {total_lines}")
        
        # Get directory size
        dir_size = pio.directory_size(temp_dir)
        print(f"Directory size: {dir_size} bytes")
        
        # Using ParallelFileProcessor class
        processor = pio.ParallelFileProcessor(max_workers=4)
        
        # Get file statistics in parallel
        stats = processor.get_file_stats_parallel(file_paths)
        for stat in stats:
            print(f"File: {os.path.basename(stat['path'])}, Size: {stat['size']} bytes")
        
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        print("Temporary directory cleaned up")


def demonstrate_chunk_processing():
    """Demonstrate file chunk processing"""
    print("\n=== Chunk Processing ===")
    
    # Create a large test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        large_file = f.name
        for i in range(100):
            f.write(f"Line {i+1}: This is a test line with some content.\n")
    
    try:
        # Process file in chunks
        def chunk_processor(chunk_idx, lines):
            word_count = sum(len(line.split()) for line in lines)
            return {"chunk": chunk_idx, "lines": len(lines), "words": word_count}
        
        chunk_size = 10  # Process 10 lines at a time
        results = pio.process_file_chunks(large_file, chunk_size, chunk_processor)
        
        print(f"Processed {len(results)} chunks:")
        for result in results[:3]:  # Show first 3 chunks
            print(f"  Chunk {result['chunk']}: {result['lines']} lines, {result['words']} words")
        
        total_words = sum(r['words'] for r in results)
        total_lines = sum(r['lines'] for r in results)
        print(f"Total: {total_lines} lines, {total_words} words")
        
    finally:
        pio.delete_file(large_file)


def demonstrate_directory_operations():
    """Demonstrate directory operations"""
    print("\n=== Directory Operations ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create subdirectories and files
        sub_dir = os.path.join(temp_dir, "subdir")
        pio.create_directory(sub_dir)
        
        # Create files in different directories
        files = [
            (os.path.join(temp_dir, "file1.txt"), "Content 1"),
            (os.path.join(temp_dir, "file2.json"), '{"key": "value"}'),
            (os.path.join(sub_dir, "file3.txt"), "Content 3"),
            (os.path.join(sub_dir, "file4.csv"), "name,age\nAlice,30"),
        ]
        
        for file_path, content in files:
            pio.write_file(file_path, content)
        
        # Process directory recursively
        processor = pio.ParallelFileProcessor()
        
        def file_filter(file_path):
            return file_path.endswith('.txt')
        
        def process_txt_file(file_path, content):
            return {
                "file": os.path.basename(file_path),
                "lines": len(content.strip().split('\n')),
                "chars": len(content)
            }
        
        txt_results = processor.process_directory(temp_dir, process_txt_file, file_filter)
        print(f"Processed .txt files: {txt_results}")
        
        # Copy files
        backup_dir = os.path.join(temp_dir, "backup")
        pio.create_directory(backup_dir)
        
        copy_pairs = []
        for file_path, _ in files:
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            copy_pairs.append((file_path, backup_path))
        
        processor.copy_files_parallel(copy_pairs)
        print(f"Copied {len(copy_pairs)} files to backup directory")
        
        # Verify backup
        backup_files = pio.find_files(backup_dir, "*")
        print(f"Backup files: {[os.path.basename(f) for f in backup_files]}")
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)
        print("Temporary directory cleaned up")


def main():
    """Run all I/O examples"""
    print("Pyferris Level 2 - File I/O Examples")
    print("=====================================")
    
    demonstrate_basic_file_operations()
    demonstrate_csv_operations()
    demonstrate_json_operations()
    demonstrate_parallel_operations()
    demonstrate_chunk_processing()
    demonstrate_directory_operations()
    
    print("\n=== Performance Comparison ===")
    
    # Compare parallel vs sequential file processing
    import time
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Create test files
        file_data = []
        for i in range(20):
            file_path = os.path.join(temp_dir, f"perf_test_{i}.txt")
            content = f"Performance test file {i}\n" * 100
            file_data.append((file_path, content))
        
        # Write files
        pio.write_files_parallel(file_data)
        file_paths = [path for path, _ in file_data]
        
        # Sequential processing
        start_time = time.time()
        sequential_results = []
        for file_path in file_paths:
            content = pio.read_file(file_path)
            result = len(content.split())
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Parallel processing
        start_time = time.time()
        def word_counter(file_path, content):
            return len(content.split())
        
        parallel_results = pio.process_files_parallel(file_paths, word_counter)
        parallel_time = time.time() - start_time
        
        print(f"Sequential processing: {sequential_time:.4f} seconds")
        print(f"Parallel processing: {parallel_time:.4f} seconds")
        speedup = sequential_time / parallel_time if parallel_time > 0 else 0
        print(f"Speedup: {speedup:.2f}x")
        
        # Verify results are the same
        assert sequential_results == parallel_results, "Results should match"
        print("✓ Results verified - parallel processing is correct!")
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)
    
    print("\n🎉 All I/O examples completed successfully!")


if __name__ == "__main__":
    main()
