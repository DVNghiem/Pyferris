# API Reference

## pyferris.core

### Functions

#### `parallel_map(func, iterable, chunk_size=None)`
Apply a function to every item of an iterable in parallel.

**Parameters:**
- `func` (callable): Function to apply to each item
- `iterable` (iterable): Input data to process  
- `chunk_size` (int, optional): Size of work chunks for load balancing

**Returns:**
- `list`: Results in the same order as input

**Example:**
```python
results = parallel_map(lambda x: x**2, range(1000))
```

#### `parallel_starmap(func, iterable, chunk_size=None)`
Apply a function to arguments unpacked from tuples in parallel.

**Parameters:**
- `func` (callable): Function to apply to unpacked arguments
- `iterable` (iterable): Iterable of argument tuples
- `chunk_size` (int, optional): Size of work chunks

**Returns:**
- `list`: Results in the same order as input

**Example:**
```python
def add(x, y):
    return x + y
args = [(1, 2), (3, 4), (5, 6)]
results = parallel_starmap(add, args)
```

#### `parallel_filter(predicate, iterable, chunk_size=None)`
Filter items from an iterable in parallel using a predicate function.

**Parameters:**
- `predicate` (callable): Function that returns True for items to keep
- `iterable` (iterable): Input data to filter
- `chunk_size` (int, optional): Size of work chunks

**Returns:**
- `list`: Filtered items that satisfy the predicate

**Example:**
```python
evens = parallel_filter(lambda x: x % 2 == 0, range(100))
```

#### `parallel_reduce(func, iterable, initializer=None, chunk_size=None)`  
Apply a function of two arguments cumulatively to items in parallel.

**Parameters:**
- `func` (callable): Binary function to apply cumulatively
- `iterable` (iterable): Input data to reduce
- `initializer` (any, optional): Initial value for the reduction
- `chunk_size` (int, optional): Size of work chunks

**Returns:**
- `any`: Single reduced result

**Example:**
```python
total = parallel_reduce(lambda x, y: x + y, range(1000))
```

## pyferris.executor

### Classes

#### `Executor(max_workers=None, queue_capacity=10000, thread_stack_size=None)`
Task executor for managing parallel tasks.

**Parameters:**
- `max_workers` (int, optional): Maximum number of worker threads. Defaults to CPU count.
- `queue_capacity` (int, optional): Maximum task queue size. Defaults to 10,000.
- `thread_stack_size` (int, optional): Stack size per thread in bytes.

**Methods:**

##### `submit(func, *args, **kwargs)`
Submit a task for execution.

**Parameters:**
- `func` (callable): Function to execute
- `*args`: Positional arguments for the function
- `**kwargs`: Keyword arguments for the function

**Returns:**
- `Future`: Future object representing the task

##### `map(func, iterable)`
Apply function to each item in iterable.

**Parameters:**
- `func` (callable): Function to apply
- `iterable` (iterable): Items to process

**Returns:**
- `iterator`: Iterator of results

##### `shutdown(wait=True)`
Shutdown the executor.

**Parameters:**
- `wait` (bool): Whether to wait for pending tasks to complete

##### `wait(futures, timeout=None)`
Wait for futures to complete.

**Parameters:**
- `futures` (list): List of Future objects
- `timeout` (float, optional): Maximum time to wait in seconds

**Returns:**
- `list`: List of completed futures

##### `as_completed(futures)`
Iterate over futures as they complete.

**Parameters:**
- `futures` (list): List of Future objects

**Returns:**
- `iterator`: Iterator of completed futures

**Example:**
```python
with Executor(max_workers=4) as executor:
    future = executor.submit(some_function, arg1, arg2)
    result = future.result()
```

## pyferris.io

### pyferris.io.simple_io

#### Functions

##### `read_file(file_path)`
Read text file content.

**Parameters:**
- `file_path` (str): Path to the file

**Returns:**
- `str`: File content

##### `write_file(file_path, content)`
Write text content to file.

**Parameters:**
- `file_path` (str): Path to the file
- `content` (str): Content to write

##### `file_exists(file_path)`
Check if file exists.

**Parameters:**
- `file_path` (str): Path to check

**Returns:**
- `bool`: True if file exists

##### `file_size(file_path)`
Get file size in bytes.

**Parameters:**
- `file_path` (str): Path to the file

**Returns:**
- `int`: File size in bytes

##### `create_directory(dir_path)`
Create directory if it doesn't exist.

**Parameters:**
- `dir_path` (str): Directory path to create

##### `delete_file(file_path)`
Delete file.

**Parameters:**
- `file_path` (str): Path to file to delete

##### `copy_file(src_path, dst_path)`
Copy file.

**Parameters:**
- `src_path` (str): Source file path
- `dst_path` (str): Destination file path

##### `move_file(src_path, dst_path)`
Move/rename file.

**Parameters:**
- `src_path` (str): Source file path
- `dst_path` (str): Destination file path

##### `read_files_parallel(file_paths)`
Read multiple files in parallel.

**Parameters:**
- `file_paths` (list): List of file paths to read

**Returns:**
- `list`: List of file contents

##### `write_files_parallel(file_data)`
Write multiple files in parallel.

**Parameters:**
- `file_data` (list): List of (file_path, content) tuples

#### Classes

##### `SimpleFileReader(file_path)`
Simple file reader class.

**Methods:**
- `read_text()`: Read entire file as text
- `read_lines()`: Read file line by line

##### `SimpleFileWriter(file_path)`
Simple file writer class.

**Methods:**
- `write_text(content)`: Write text to file
- `append_text(content)`: Append text to file

### pyferris.io.csv

#### Functions

##### `read_csv(file_path, delimiter=',', has_headers=True)`
Read CSV file as list of dictionaries.

**Parameters:**
- `file_path` (str): Path to CSV file
- `delimiter` (str): Field delimiter (default: ',')
- `has_headers` (bool): Whether file has headers (default: True)

**Returns:**
- `list`: List of dictionaries representing rows

##### `write_csv(file_path, data, delimiter=',', write_headers=True)`
Write CSV file from list of dictionaries.

**Parameters:**
- `file_path` (str): Path to output CSV file
- `data` (list): List of dictionaries to write
- `delimiter` (str): Field delimiter (default: ',')
- `write_headers` (bool): Whether to write headers (default: True)

##### `read_csv_rows(file_path, delimiter=',', has_headers=True)`
Read CSV file as list of lists.

**Parameters:**
- `file_path` (str): Path to CSV file
- `delimiter` (str): Field delimiter (default: ',')
- `has_headers` (bool): Whether file has headers (default: True)

**Returns:**
- `list`: List of lists representing rows

##### `write_csv_rows(file_path, data, delimiter=',')`
Write CSV file from list of lists.

**Parameters:**
- `file_path` (str): Path to output CSV file
- `data` (list): List of lists to write
- `delimiter` (str): Field delimiter (default: ',')

#### Classes

##### `CsvReader(file_path, delimiter=',', has_headers=True)`
High-performance CSV reader.

**Methods:**
- `read_dict()`: Read CSV as list of dictionaries
- `read_rows()`: Read CSV as list of lists
- `get_headers()`: Get column headers

##### `CsvWriter(file_path, delimiter=',', write_headers=True)`
High-performance CSV writer.

**Methods:**
- `write_dict(data)`: Write data from list of dictionaries
- `write_rows(data)`: Write data from list of lists

### pyferris.io.json

#### Functions

##### `read_json(file_path)`
Read JSON file as Python object.

**Parameters:**
- `file_path` (str): Path to JSON file

**Returns:**
- `any`: Parsed JSON data

##### `write_json(file_path, data, pretty_print=False)`
Write Python object as JSON file.

**Parameters:**
- `file_path` (str): Path to output JSON file
- `data` (any): Data to write as JSON
- `pretty_print` (bool): Whether to format with indentation

##### `read_jsonl(file_path)`
Read JSON Lines file as list.

**Parameters:**
- `file_path` (str): Path to JSON Lines file

**Returns:**
- `list`: List of parsed JSON objects

##### `write_jsonl(file_path, data)`
Write list as JSON Lines file.

**Parameters:**
- `file_path` (str): Path to output JSON Lines file
- `data` (list): List of objects to write

##### `append_jsonl(file_path, data)`
Append object to JSON Lines file.

**Parameters:**
- `file_path` (str): Path to JSON Lines file
- `data` (any): Object to append

##### `parse_json(json_str)`
Parse JSON string to Python object.

**Parameters:**
- `json_str` (str): JSON string to parse

**Returns:**
- `any`: Parsed JSON data

##### `to_json_string(data, pretty_print=False)`
Convert Python object to JSON string.

**Parameters:**
- `data` (any): Data to convert
- `pretty_print` (bool): Whether to format with indentation

**Returns:**
- `str`: JSON string

#### Classes

##### `JsonReader(file_path)`
High-performance JSON reader.

**Methods:**
- `read()`: Read JSON file as Python object
- `read_lines()`: Read JSON Lines file as list of objects
- `read_array_stream()`: Read large JSON array in streaming mode

##### `JsonWriter(file_path, pretty_print=False)`
High-performance JSON writer.

**Methods:**
- `write(data)`: Write Python object as JSON
- `write_lines(data)`: Write list of objects as JSON Lines
- `append_line(data)`: Append object to JSON Lines file

### pyferris.io.parallel_io

#### Functions

##### `process_files_parallel(file_paths, processor_func)`
Process multiple files in parallel with custom function.

**Parameters:**
- `file_paths` (list): List of file paths to process
- `processor_func` (callable): Function to process each file

**Returns:**
- `list`: List of processing results

##### `find_files(root_dir, pattern)`
Find files matching pattern in parallel.

**Parameters:**
- `root_dir` (str): Root directory to search
- `pattern` (str): File pattern to match

**Returns:**
- `list`: List of matching file paths

##### `directory_size(dir_path)`
Get directory size in parallel.

**Parameters:**
- `dir_path` (str): Directory path

**Returns:**
- `int`: Directory size in bytes

##### `count_lines(file_paths)`
Count lines in multiple files in parallel.

**Parameters:**
- `file_paths` (list): List of file paths

**Returns:**
- `int`: Total line count

##### `process_file_chunks(file_path, chunk_size, processor_func)`
Process file in chunks with parallel execution.

**Parameters:**
- `file_path` (str): Path to file to process
- `chunk_size` (int): Size of each chunk
- `processor_func` (callable): Function to process each chunk

**Returns:**
- `list`: List of chunk processing results

#### Classes

##### `ParallelFileProcessor(max_workers=0)`
Parallel file operations for batch processing.

**Methods:**
- `process_files(file_paths, processor_func)`: Process multiple files with custom function
- `read_files_parallel(file_paths)`: Read multiple files in parallel
- `write_files_parallel(file_data)`: Write multiple files in parallel
- `copy_files_parallel(file_pairs)`: Copy multiple files in parallel
- `process_directory(dir_path, processor_func, file_filter=None)`: Process directory recursively
- `get_file_stats_parallel(file_paths)`: Get file statistics in parallel

## Error Handling

All PyFerris functions may raise the following exceptions:

- `PyFerrisError`: Base exception for PyFerris-specific errors
- `ParallelExecutionError`: Errors during parallel execution
- `FileIOError`: File I/O related errors
- `InvalidArgumentError`: Invalid function arguments

## Performance Notes

- PyFerris automatically determines optimal chunk sizes when not specified
- All parallel operations bypass Python's GIL for true parallelism
- Memory usage is optimized for large datasets
- Thread pool sizes default to CPU core count but can be customized

## Type Hints

PyFerris includes comprehensive type hints for better IDE support and code safety:

```python
from typing import List, Dict, Any, Optional, Callable, Iterator
from pyferris import parallel_map

def process_data(items: List[int]) -> List[int]:
    return parallel_map(lambda x: x * 2, items)
```
