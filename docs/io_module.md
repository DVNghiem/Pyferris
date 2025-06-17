# Pyferris IO Module Documentation

The Pyferris IO module provides high-performance file I/O operations with parallel processing capabilities, implemented in Rust for maximum efficiency.

## Features

- **Simple File Operations**: Basic read/write operations for text files
- **Parallel Processing**: Read and write multiple files concurrently
- **Memory Efficient**: Optimized for handling large files and datasets
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Type Safe**: Full type annotations for better development experience

## Classes

### SimpleFileReader

A simple file reader for text files.

```python
from pyferris.simple_io import SimpleFileReader

# Create a reader
reader = SimpleFileReader("data.txt")

# Read entire file
content = reader.read_text()

# Read file line by line
lines = reader.read_lines()
```

### SimpleFileWriter

A simple file writer for text files.

```python
from pyferris.simple_io import SimpleFileWriter

# Create a writer
writer = SimpleFileWriter("output.txt")

# Write text
writer.write_text("Hello, World!")

# Append text
writer.append_text("\nAppended content")
```

## Functions

### Basic File Operations

#### read_file(file_path: str) -> str
Read the entire content of a text file.

```python
import pyferris.simple_io as pio

content = pio.read_file("example.txt")
print(content)
```

#### write_file(file_path: str, content: str) -> None
Write text content to a file (overwrites existing content).

```python
pio.write_file("output.txt", "Hello, Pyferris!")
```

#### file_exists(file_path: str) -> bool
Check if a file exists.

```python
if pio.file_exists("data.txt"):
    print("File exists!")
```

#### file_size(file_path: str) -> int
Get the size of a file in bytes.

```python
size = pio.file_size("data.txt")
print(f"File size: {size} bytes")
```

### Directory Operations

#### create_directory(dir_path: str) -> None
Create a directory (including parent directories if needed).

```python
pio.create_directory("path/to/new/directory")
```

### File Management

#### delete_file(file_path: str) -> None
Delete a file.

```python
pio.delete_file("unwanted.txt")
```

#### copy_file(src_path: str, dst_path: str) -> None
Copy a file to a new location.

```python
pio.copy_file("source.txt", "backup.txt")
```

#### move_file(src_path: str, dst_path: str) -> None
Move or rename a file.

```python
pio.move_file("old_name.txt", "new_name.txt")
```

### Parallel Operations

#### read_files_parallel(file_paths: List[str]) -> List[str]
Read multiple files in parallel, returning their contents.

```python
file_paths = ["file1.txt", "file2.txt", "file3.txt"]
contents = pio.read_files_parallel(file_paths)

for i, content in enumerate(contents):
    print(f"File {file_paths[i]}: {len(content)} characters")
```

#### write_files_parallel(file_data: List[Tuple[str, str]]) -> None
Write multiple files in parallel.

```python
file_data = [
    ("file1.txt", "Content for file 1"),
    ("file2.txt", "Content for file 2"),
    ("file3.txt", "Content for file 3"),
]

pio.write_files_parallel(file_data)
```

## Usage Examples

### Basic File Operations

```python
import pyferris.simple_io as pio

# Write a file
pio.write_file("example.txt", "Hello, Pyferris!\nThis is a test file.")

# Read the file
content = pio.read_file("example.txt")
print(content)

# Check file properties
print(f"File exists: {pio.file_exists('example.txt')}")
print(f"File size: {pio.file_size('example.txt')} bytes")

# Clean up
pio.delete_file("example.txt")
```

### Working with Classes

```python
from pyferris.simple_io import SimpleFileReader, SimpleFileWriter

# Write using class
writer = SimpleFileWriter("data.txt")
writer.write_text("Line 1\nLine 2\nLine 3")
writer.append_text("\nLine 4")

# Read using class
reader = SimpleFileReader("data.txt")
lines = reader.read_lines()
print(f"File has {len(lines)} lines")

for i, line in enumerate(lines, 1):
    print(f"Line {i}: {line}")
```

### Parallel File Processing

```python
import pyferris.simple_io as pio
import os

# Create multiple files in parallel
file_data = []
for i in range(10):
    file_path = f"data_{i}.txt"
    content = f"This is file {i}\n" * (i + 1)
    file_data.append((file_path, content))

# Write all files at once
pio.write_files_parallel(file_data)

# Read all files at once
file_paths = [path for path, _ in file_data]
contents = pio.read_files_parallel(file_paths)

# Process results
total_lines = 0
for content in contents:
    total_lines += len(content.strip().split('\n'))

print(f"Total lines across all files: {total_lines}")

# Clean up
for file_path in file_paths:
    pio.delete_file(file_path)
```

### Error Handling

```python
import pyferris.simple_io as pio
from pyferris import ParallelExecutionError

try:
    content = pio.read_file("nonexistent.txt")
except ParallelExecutionError as e:
    print(f"Error reading file: {e}")

try:
    pio.write_file("/invalid/path/file.txt", "content")
except ParallelExecutionError as e:
    print(f"Error writing file: {e}")
```

## Performance Considerations

### When to Use Parallel Operations

- **Multiple Files**: When processing many files simultaneously
- **I/O Bound Tasks**: When disk I/O is the bottleneck
- **Independent Operations**: When file operations don't depend on each other

### When to Use Sequential Operations

- **Single Files**: For single file operations
- **Small Files**: When overhead of parallelization exceeds benefits
- **Memory Constraints**: When processing very large files that might not fit in memory

### Example Performance Comparison

```python
import time
import pyferris.simple_io as pio

# Create test data
file_data = [(f"test_{i}.txt", f"Content {i}\n" * 100) for i in range(20)]

# Sequential write
start = time.time()
for file_path, content in file_data:
    pio.write_file(file_path, content)
sequential_time = time.time() - start

# Clean up
for file_path, _ in file_data:
    pio.delete_file(file_path)

# Parallel write
start = time.time()
pio.write_files_parallel(file_data)
parallel_time = time.time() - start

print(f"Sequential: {sequential_time:.4f}s")
print(f"Parallel: {parallel_time:.4f}s")
print(f"Speedup: {sequential_time/parallel_time:.2f}x")

# Clean up
for file_path, _ in file_data:
    pio.delete_file(file_path)
```

## Integration with Other Pyferris Modules

The IO module works seamlessly with other Pyferris components:

```python
import pyferris.simple_io as pio
from pyferris import parallel_map

# Read multiple files and process them in parallel
file_paths = ["data1.txt", "data2.txt", "data3.txt"]
contents = pio.read_files_parallel(file_paths)

# Process contents using parallel_map
def count_words(text):
    return len(text.split())

word_counts = parallel_map(count_words, contents)
print(f"Word counts: {word_counts}")
```

## Best Practices

1. **Use appropriate functions**: Use parallel operations for multiple files, sequential for single files
2. **Handle errors**: Always wrap file operations in try-catch blocks
3. **Clean up resources**: Delete temporary files when done
4. **Check file existence**: Verify files exist before operations
5. **Use absolute paths**: When possible, use absolute file paths to avoid confusion

## Limitations

- Currently supports text files only (UTF-8 encoding)
- Binary file operations not yet implemented
- CSV and JSON support planned for future releases
- No streaming support for very large files yet

## Future Enhancements

- Binary file support
- CSV read/write operations
- JSON file operations
- Streaming support for large files
- Compression support
- Advanced file filtering and pattern matching
