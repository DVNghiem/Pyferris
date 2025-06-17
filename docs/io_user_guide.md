# Pyferris IO Module - User Guide

## Overview

The Pyferris IO module provides high-performance file input/output operations with both simple and advanced features. It offers both functional and object-oriented interfaces, with built-in parallel processing capabilities for batch operations.

## Features

- **Simple File Operations**: Basic read/write with high performance
- **Parallel Processing**: Batch operations on multiple files
- **Object-Oriented Interface**: Class-based file readers and writers
- **Error Handling**: Robust error management with clear exceptions
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Memory Efficient**: Optimized for large files and batch operations

## Installation

Pyferris should be installed as part of the main package:

```bash
pip install pyferris
```

## Quick Start

```python
import pyferris.simple_io as sio

# Write a file
sio.write_file("example.txt", "Hello, World!")

# Read a file
content = sio.read_file("example.txt")
print(content)  # Output: Hello, World!

# Check if file exists
if sio.file_exists("example.txt"):
    print("File exists!")
```

## API Reference

### Functional Interface

#### Basic File Operations

##### `write_file(file_path: str, content: str)`
Write text content to a file.

```python
import pyferris.simple_io as sio

sio.write_file("output.txt", "This is the file content.")
```

**Parameters:**
- `file_path` (str): Path to the output file
- `content` (str): Text content to write

**Raises:**
- Exception: If the file cannot be written (permissions, invalid path, etc.)

##### `read_file(file_path: str) -> str`
Read text content from a file.

```python
import pyferris.simple_io as sio

content = sio.read_file("input.txt")
print(f"File contains: {content}")
```

**Parameters:**
- `file_path` (str): Path to the input file

**Returns:**
- str: The file content as text

**Raises:**
- Exception: If the file cannot be read (doesn't exist, permissions, etc.)

#### File Utilities

##### `file_exists(file_path: str) -> bool`
Check if a file exists.

```python
import pyferris.simple_io as sio

if sio.file_exists("data.txt"):
    print("File exists")
else:
    print("File not found")
```

##### `file_size(file_path: str) -> int`
Get the size of a file in bytes.

```python
import pyferris.simple_io as sio

size = sio.file_size("large_file.txt")
print(f"File size: {size} bytes ({size/1024/1024:.2f} MB)")
```

##### `copy_file(src_path: str, dst_path: str)`
Copy a file from source to destination.

```python
import pyferris.simple_io as sio

sio.copy_file("original.txt", "backup.txt")
```

##### `move_file(src_path: str, dst_path: str)`
Move/rename a file.

```python
import pyferris.simple_io as sio

sio.move_file("old_name.txt", "new_name.txt")
```

##### `delete_file(file_path: str)`
Delete a file.

```python
import pyferris.simple_io as sio

sio.delete_file("temporary.txt")
```

##### `create_directory(dir_path: str)`
Create a directory (including parent directories if needed).

```python
import pyferris.simple_io as sio

sio.create_directory("data/processed/output")
```

#### Parallel Operations

##### `read_files_parallel(file_paths: List[str]) -> List[str]`
Read multiple files in parallel.

```python
import pyferris.simple_io as sio

file_paths = ["file1.txt", "file2.txt", "file3.txt"]
contents = sio.read_files_parallel(file_paths)

for i, content in enumerate(contents):
    print(f"File {i+1} content: {content}")
```

**Parameters:**
- `file_paths` (List[str]): List of file paths to read

**Returns:**
- List[str]: List of file contents (same order as input paths)

**Performance Note:** 
Parallel reading is most beneficial when:
- Reading many files (10+ files)
- Files are on different storage devices
- Files are moderately large (>1KB each)

##### `write_files_parallel(file_data: List[Tuple[str, str]])`
Write multiple files in parallel.

```python
import pyferris.simple_io as sio

# List of (file_path, content) tuples
file_data = [
    ("output1.txt", "Content for file 1"),
    ("output2.txt", "Content for file 2"),
    ("output3.txt", "Content for file 3")
]

sio.write_files_parallel(file_data)
```

**Parameters:**
- `file_data` (List[Tuple[str, str]]): List of (file_path, content) tuples

### Object-Oriented Interface

#### SimpleFileReader Class

The `SimpleFileReader` class provides an object-oriented interface for reading files.

```python
from pyferris import SimpleFileReader

reader = SimpleFileReader("data.txt")
content = reader.read_text()
```

##### Constructor

```python
SimpleFileReader(file_path: str)
```

**Parameters:**
- `file_path` (str): Path to the file to read

##### Methods

###### `read_text() -> str`
Read the entire file as text.

```python
reader = SimpleFileReader("document.txt")
text = reader.read_text()
print(text)
```

###### `read_lines() -> List[str]`
Read the file and return a list of lines.

```python
reader = SimpleFileReader("log.txt")
lines = reader.read_lines()

for i, line in enumerate(lines, 1):
    print(f"Line {i}: {line}")
```

#### SimpleFileWriter Class

The `SimpleFileWriter` class provides an object-oriented interface for writing files.

```python
from pyferris import SimpleFileWriter

writer = SimpleFileWriter("output.txt")
writer.write_text("Hello, World!")
```

##### Constructor

```python
SimpleFileWriter(file_path: str)
```

**Parameters:**
- `file_path` (str): Path to the file to write

##### Methods

###### `write_text(content: str)`
Write text content to the file (overwrites existing content).

```python
writer = SimpleFileWriter("report.txt")
writer.write_text("Report Title\n============\n\nReport content...")
```

###### `append_text(content: str)`
Append text content to the end of the file.

```python
writer = SimpleFileWriter("log.txt")
writer.append_text("\n[INFO] New log entry")
```

## Usage Examples

### Example 1: Basic File Operations

```python
import pyferris.simple_io as sio

# Create a sample file
content = """This is a sample file.
It contains multiple lines.
Each line will be processed."""

sio.write_file("sample.txt", content)

# Read and display the file
if sio.file_exists("sample.txt"):
    file_content = sio.read_file("sample.txt")
    print(f"File size: {sio.file_size('sample.txt')} bytes")
    print(f"Content:\n{file_content}")

# Create a backup
sio.copy_file("sample.txt", "sample_backup.txt")

# Clean up
sio.delete_file("sample.txt")
sio.delete_file("sample_backup.txt")
```

### Example 2: Processing Multiple Files

```python
import pyferris.simple_io as sio
import os

# Create multiple input files
input_data = {
    "data1.txt": "Dataset 1: values 1, 2, 3",
    "data2.txt": "Dataset 2: values 4, 5, 6", 
    "data3.txt": "Dataset 3: values 7, 8, 9"
}

# Write input files
for filename, content in input_data.items():
    sio.write_file(filename, content)

# Read all files in parallel
file_paths = list(input_data.keys())
contents = sio.read_files_parallel(file_paths)

# Process and write results in parallel
processed_data = []
for i, content in enumerate(contents):
    processed_content = f"Processed: {content.upper()}"
    output_filename = f"processed_{i+1}.txt"
    processed_data.append((output_filename, processed_content))

sio.write_files_parallel(processed_data)

print("Processing complete!")

# Clean up
for filename in input_data.keys():
    sio.delete_file(filename)
for filename, _ in processed_data:
    sio.delete_file(filename)
```

### Example 3: Using Object-Oriented Interface

```python
from pyferris import SimpleFileReader, SimpleFileWriter

# Create a log file using the writer
log_writer = SimpleFileWriter("application.log")
log_writer.write_text("[START] Application initialized")
log_writer.append_text("\n[INFO] Processing data...")
log_writer.append_text("\n[INFO] Data processing complete")
log_writer.append_text("\n[END] Application finished")

# Read and analyze the log using the reader
log_reader = SimpleFileReader("application.log")
log_lines = log_reader.read_lines()

print(f"Log contains {len(log_lines)} entries:")
for line in log_lines:
    if "[ERROR]" in line:
        print(f"❌ {line}")
    elif "[INFO]" in line:
        print(f"ℹ️  {line}")
    else:
        print(f"📝 {line}")

# Clean up
import pyferris.simple_io as sio
sio.delete_file("application.log")
```

### Example 4: Large File Processing

```python
import pyferris.simple_io as sio
import time

# Create a large file
large_content = "Sample line with data\n" * 100000  # 100K lines
print("Creating large file...")
start_time = time.time()
sio.write_file("large_file.txt", large_content)
write_time = time.time() - start_time

print(f"Write completed in {write_time:.3f} seconds")
print(f"File size: {sio.file_size('large_file.txt')} bytes")

# Read the large file
print("Reading large file...")
start_time = time.time()
content = sio.read_file("large_file.txt")
read_time = time.time() - start_time

print(f"Read completed in {read_time:.3f} seconds")
print(f"Content length: {len(content)} characters")

# Clean up
sio.delete_file("large_file.txt")
```

### Example 5: Error Handling

```python
import pyferris.simple_io as sio

def safe_file_operation():
    try:
        # Attempt to read a non-existent file
        content = sio.read_file("nonexistent.txt")
        print(content)
    except Exception as e:
        print(f"Error reading file: {e}")
    
    try:
        # Attempt to write to an invalid path
        sio.write_file("/root/restricted.txt", "content")
    except Exception as e:
        print(f"Error writing file: {e}")
    
    # Safe way to check before reading
    filename = "maybe_exists.txt"
    if sio.file_exists(filename):
        content = sio.read_file(filename)
        print(f"File content: {content}")
    else:
        print(f"File {filename} does not exist")

safe_file_operation()
```

## Performance Considerations

### When to Use Parallel Operations

**Use parallel operations when:**
- Processing 10+ files
- Files are on different storage devices
- Each file is moderately large (>1KB)
- I/O is the bottleneck (not CPU processing)

**Use sequential operations when:**
- Processing few files (<10)
- Files are very small (<1KB)
- All files are on the same slow storage device
- Memory usage is a concern

### Memory Usage

- **Functional interface**: Loads entire file content into memory
- **Class-based interface**: Same memory usage as functional interface
- **Parallel operations**: Memory usage scales with number of files processed simultaneously

### Performance Tips

1. **Use appropriate batch sizes** for parallel operations (10-100 files per batch)
2. **Pre-check file existence** when processing many files to avoid exceptions
3. **Use absolute paths** when possible to avoid path resolution overhead
4. **Consider file system limitations** (number of open files, disk I/O limits)

## Error Handling

The IO module raises exceptions for various error conditions:

- **File not found**: When trying to read non-existent files
- **Permission denied**: When lacking read/write permissions  
- **Invalid path**: When file path is malformed or points to invalid location
- **Disk full**: When insufficient space for write operations
- **I/O errors**: For hardware-related failures

Always use try-catch blocks for robust error handling:

```python
import pyferris.simple_io as sio

try:
    content = sio.read_file("important_data.txt")
    # Process content...
except Exception as e:
    print(f"Failed to process file: {e}")
    # Handle error appropriately
```

## Advanced Features (Coming Soon)

The following advanced features are implemented in Rust but not yet exposed in Python:

- **CSV Operations**: High-performance CSV reading/writing with custom delimiters
- **JSON Operations**: Efficient JSON and JSON Lines processing
- **Advanced Parallel Processing**: Custom parallel processing with user-defined functions
- **Buffered I/O**: Memory-efficient operations for very large files
- **Compression Support**: Built-in support for compressed file formats

## Best Practices

1. **Always handle exceptions** when performing file operations
2. **Use parallel operations judiciously** - they're not always faster
3. **Check file existence** before operations to provide better error messages
4. **Use absolute paths** when working with files in different directories
5. **Clean up temporary files** to avoid disk space issues
6. **Consider memory usage** when processing very large files
7. **Use appropriate file paths** for cross-platform compatibility

## Troubleshooting

### Common Issues

**Problem**: `ImportError: No module named 'pyferris'`
**Solution**: Ensure pyferris is properly installed: `pip install pyferris`

**Problem**: Permission denied errors
**Solution**: Check file/directory permissions and ensure your process has appropriate access

**Problem**: Parallel operations slower than sequential
**Solution**: Try reducing batch size or use sequential operations for small files

**Problem**: Memory usage too high
**Solution**: Process files in smaller batches or use streaming approaches for very large files

### Performance Issues

If you experience performance issues:

1. **Check disk I/O**: Use system monitoring tools to identify bottlenecks
2. **Reduce batch size**: For parallel operations, try smaller batches
3. **Profile your code**: Identify which operations are taking the most time
4. **Consider file system**: Some filesystems handle concurrent access better than others

## Support

For bug reports, feature requests, or questions:
- GitHub Issues: [Report issues](https://github.com/your-repo/pyferris/issues)
- Documentation: [Full documentation](https://pyferris.readthedocs.io)
- Examples: Check the `examples/` directory in the repository

## License

Pyferris is released under the MIT License. See LICENSE file for details.
