# Pyferris IO Module - API Reference

## Module: pyferris.simple_io

### Functions

#### File I/O Operations

---

##### `write_file(file_path: str, content: str) -> None`

Write text content to a file.

**Parameters:**
- `file_path` (str): Absolute or relative path to the output file
- `content` (str): Text content to write to the file

**Raises:**
- `Exception`: If the file cannot be written due to:
  - Invalid file path
  - Insufficient permissions
  - Disk space issues
  - Hardware failures

**Example:**
```python
import pyferris.simple_io as sio
sio.write_file("output.txt", "Hello, World!")
```

---

##### `read_file(file_path: str) -> str`

Read the entire content of a text file.

**Parameters:**
- `file_path` (str): Absolute or relative path to the input file

**Returns:**
- `str`: The complete file content as a string

**Raises:**
- `Exception`: If the file cannot be read due to:
  - File does not exist
  - Insufficient permissions
  - File is not readable as text
  - Hardware failures

**Example:**
```python
import pyferris.simple_io as sio
content = sio.read_file("input.txt")
```

---

#### File Utilities

---

##### `file_exists(file_path: str) -> bool`

Check whether a file exists at the specified path.

**Parameters:**
- `file_path` (str): Path to check for file existence

**Returns:**
- `bool`: True if the file exists, False otherwise

**Example:**
```python
import pyferris.simple_io as sio
if sio.file_exists("data.txt"):
    print("File found")
```

---

##### `file_size(file_path: str) -> int`

Get the size of a file in bytes.

**Parameters:**
- `file_path` (str): Path to the file

**Returns:**
- `int`: Size of the file in bytes

**Raises:**
- `Exception`: If the file does not exist or cannot be accessed

**Example:**
```python
import pyferris.simple_io as sio
size = sio.file_size("large_file.txt")
print(f"File size: {size} bytes")
```

---

##### `copy_file(src_path: str, dst_path: str) -> None`

Copy a file from source to destination.

**Parameters:**
- `src_path` (str): Path to the source file
- `dst_path` (str): Path to the destination file

**Raises:**
- `Exception`: If the operation fails due to:
  - Source file does not exist
  - Insufficient permissions
  - Destination path is invalid
  - Disk space issues

**Example:**
```python
import pyferris.simple_io as sio
sio.copy_file("original.txt", "backup.txt")
```

---

##### `move_file(src_path: str, dst_path: str) -> None`

Move (rename) a file from source to destination.

**Parameters:**
- `src_path` (str): Path to the source file
- `dst_path` (str): Path to the destination file

**Raises:**
- `Exception`: If the operation fails due to:
  - Source file does not exist
  - Insufficient permissions
  - Destination path is invalid
  - Cross-device moves not supported

**Example:**
```python
import pyferris.simple_io as sio
sio.move_file("old_name.txt", "new_name.txt")
```

---

##### `delete_file(file_path: str) -> None`

Delete a file from the filesystem.

**Parameters:**
- `file_path` (str): Path to the file to delete

**Raises:**
- `Exception`: If the operation fails due to:
  - File does not exist
  - Insufficient permissions
  - File is in use by another process

**Example:**
```python
import pyferris.simple_io as sio
sio.delete_file("temporary.txt")
```

---

##### `create_directory(dir_path: str) -> None`

Create a directory, including any necessary parent directories.

**Parameters:**
- `dir_path` (str): Path to the directory to create

**Raises:**
- `Exception`: If the operation fails due to:
  - Insufficient permissions
  - Invalid path
  - Disk space issues

**Example:**
```python
import pyferris.simple_io as sio
sio.create_directory("data/processed/output")
```

---

#### Parallel Operations

---

##### `read_files_parallel(file_paths: List[str]) -> List[str]`

Read multiple files in parallel for improved performance.

**Parameters:**
- `file_paths` (List[str]): List of file paths to read

**Returns:**
- `List[str]`: List of file contents in the same order as input paths

**Raises:**
- `Exception`: If any file cannot be read. The exception will contain details about which files failed.

**Performance Notes:**
- Most beneficial with 10+ files
- Best when files are on different storage devices
- Overhead may make it slower for very small files

**Example:**
```python
import pyferris.simple_io as sio
files = ["file1.txt", "file2.txt", "file3.txt"]
contents = sio.read_files_parallel(files)
```

---

##### `write_files_parallel(file_data: List[Tuple[str, str]]) -> None`

Write multiple files in parallel for improved performance.

**Parameters:**
- `file_data` (List[Tuple[str, str]]): List of (file_path, content) tuples

**Raises:**
- `Exception`: If any file cannot be written. The exception will contain details about which files failed.

**Performance Notes:**
- Most beneficial with 10+ files
- Best when files are on different storage devices
- May use more memory due to parallel processing

**Example:**
```python
import pyferris.simple_io as sio
data = [
    ("output1.txt", "Content 1"),
    ("output2.txt", "Content 2")
]
sio.write_files_parallel(data)
```

---

## Classes

### SimpleFileReader

Object-oriented interface for reading files.

#### Constructor

---

##### `SimpleFileReader(file_path: str)`

Initialize a new file reader.

**Parameters:**
- `file_path` (str): Path to the file to read

**Example:**
```python
from pyferris import SimpleFileReader
reader = SimpleFileReader("data.txt")
```

#### Methods

---

##### `read_text() -> str`

Read the entire file content as text.

**Returns:**
- `str`: The complete file content

**Raises:**
- `Exception`: If the file cannot be read

**Example:**
```python
reader = SimpleFileReader("document.txt")
content = reader.read_text()
```

---

##### `read_lines() -> List[str]`

Read the file and return a list of lines.

**Returns:**
- `List[str]`: List of lines from the file

**Raises:**
- `Exception`: If the file cannot be read

**Example:**
```python
reader = SimpleFileReader("log.txt")
lines = reader.read_lines()
for line in lines:
    print(line)
```

---

### SimpleFileWriter

Object-oriented interface for writing files.

#### Constructor

---

##### `SimpleFileWriter(file_path: str)`

Initialize a new file writer.

**Parameters:**
- `file_path` (str): Path to the file to write

**Example:**
```python
from pyferris import SimpleFileWriter
writer = SimpleFileWriter("output.txt")
```

#### Methods

---

##### `write_text(content: str) -> None`

Write text content to the file, overwriting existing content.

**Parameters:**
- `content` (str): Text content to write

**Raises:**
- `Exception`: If the file cannot be written

**Example:**
```python
writer = SimpleFileWriter("report.txt")
writer.write_text("Report content...")
```

---

##### `append_text(content: str) -> None`

Append text content to the end of the file.

**Parameters:**
- `content` (str): Text content to append

**Raises:**
- `Exception`: If the file cannot be written

**Example:**
```python
writer = SimpleFileWriter("log.txt")
writer.append_text("\\nNew log entry")
```

---

## Exception Handling

All functions and methods in the IO module may raise exceptions. Common exception scenarios include:

### File Not Found
Raised when attempting to read a file that doesn't exist.

```python
try:
    content = sio.read_file("nonexistent.txt")
except Exception as e:
    print(f"File not found: {e}")
```

### Permission Denied
Raised when insufficient permissions for the requested operation.

```python
try:
    sio.write_file("/root/protected.txt", "content")
except Exception as e:
    print(f"Permission denied: {e}")
```

### Invalid Path
Raised when the file path is malformed or invalid.

```python
try:
    sio.read_file("\\0invalid\\path")
except Exception as e:
    print(f"Invalid path: {e}")
```

### Disk Space Issues
Raised when there's insufficient disk space for write operations.

```python
try:
    sio.write_file("large_file.txt", "x" * 10**9)  # 1GB
except Exception as e:
    print(f"Disk space issue: {e}")
```

## Performance Characteristics

### Time Complexity
- **Single file operations**: O(n) where n is file size
- **Parallel operations**: O(n/p) where p is number of parallel workers
- **File utilities**: O(1) for most operations

### Space Complexity
- **Single file operations**: O(n) where n is file size (entire file loaded into memory)
- **Parallel operations**: O(n*p) where p is number of files processed in parallel

### Benchmarks

Typical performance on modern hardware:

| Operation | File Size | Time (Sequential) | Time (Parallel) | Speedup |
|-----------|-----------|-------------------|-----------------|---------|
| Read 100 files | 1KB each | 50ms | 15ms | 3.3x |
| Read 100 files | 10KB each | 200ms | 60ms | 3.3x |
| Read 10 files | 1MB each | 500ms | 200ms | 2.5x |
| Write 100 files | 1KB each | 60ms | 20ms | 3.0x |

*Note: Actual performance depends on hardware, file system, and system load.*

## Thread Safety

- **Functional interface**: Thread-safe for different files, not thread-safe for same file
- **Class instances**: Not thread-safe - use separate instances per thread
- **Parallel operations**: Internally thread-safe, handles parallelism automatically

## Memory Management

- Files are loaded entirely into memory
- For very large files (>1GB), consider processing in chunks
- Parallel operations use additional memory proportional to number of files
- Python's garbage collector handles memory cleanup automatically

## Platform Compatibility

| Feature | Linux | macOS | Windows |
|---------|-------|-------|---------|
| Basic I/O | ✅ | ✅ | ✅ |
| Parallel I/O | ✅ | ✅ | ✅ |
| File utilities | ✅ | ✅ | ✅ |
| Path handling | ✅ | ✅ | ✅ |
| Unicode support | ✅ | ✅ | ✅ |

## Versioning

This API follows semantic versioning:
- **Major**: Breaking changes to public API
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

Current version: 0.3.2

## Migration Guide

### From Standard Library

```python
# Standard library
with open("file.txt", "r") as f:
    content = f.read()

# Pyferris
import pyferris.simple_io as sio
content = sio.read_file("file.txt")
```

### From Other Libraries

```python
# Other libraries often require more boilerplate
import os
import shutil

if os.path.exists("source.txt"):
    shutil.copy("source.txt", "dest.txt")

# Pyferris
import pyferris.simple_io as sio
if sio.file_exists("source.txt"):
    sio.copy_file("source.txt", "dest.txt")
```
