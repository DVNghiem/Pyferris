# I/O Operations

PyFerris provides high-performance parallel I/O operations for reading and writing files efficiently. The I/O module includes specialized functions for handling various file formats and optimizations for different I/O patterns.

## Overview

The I/O module provides:
- Parallel file reading and writing
- Support for multiple file formats (CSV, JSON, text)
- Memory-efficient streaming operations
- Batch processing for large files
- Automatic encoding detection and handling

## Simple I/O Operations

### Reading Files

```python
from pyferris.io import simple_io

# Read a single file
content = simple_io.read_file('data.txt')
print(f"File size: {len(content)} characters")

# Read multiple files in parallel
file_list = ['file1.txt', 'file2.txt', 'file3.txt']
contents = simple_io.read_files_parallel(file_list)

for i, content in enumerate(contents):
    print(f"File {i+1}: {len(content)} characters")

# Read files with custom encoding
content = simple_io.read_file('data.txt', encoding='utf-8')

# Read binary files
binary_data = simple_io.read_file('image.jpg', mode='rb')
```

### Writing Files

```python
from pyferris.io import simple_io

# Write a single file
text_data = "Hello, PyFerris!\nThis is parallel I/O."
simple_io.write_file('output.txt', text_data)

# Write multiple files in parallel
file_data = [
    ('output1.txt', 'Content for file 1'),
    ('output2.txt', 'Content for file 2'),
    ('output3.txt', 'Content for file 3')
]
simple_io.write_files_parallel(file_data)

# Write with custom encoding
simple_io.write_file('unicode_output.txt', text_data, encoding='utf-8')

# Write binary data
with open('source_image.jpg', 'rb') as f:
    binary_data = f.read()
simple_io.write_file('copy_image.jpg', binary_data, mode='wb')
```

## CSV Operations

### Reading CSV Files

```python
from pyferris.io import csv

# Read CSV file
data = csv.read_csv('dataset.csv')
print(f"Loaded {len(data)} rows")

# Read with custom delimiter
data = csv.read_csv('data.tsv', delimiter='\t')

# Read with specific columns
data = csv.read_csv('dataset.csv', columns=['name', 'age', 'city'])

# Read large CSV in chunks
for chunk in csv.read_csv_chunked('large_dataset.csv', chunk_size=10000):
    print(f"Processing chunk with {len(chunk)} rows")
    # Process chunk here
```

### Writing CSV Files

```python
from pyferris.io import csv

# Sample data
data = [
    {'name': 'Alice', 'age': 30, 'city': 'New York'},
    {'name': 'Bob', 'age': 25, 'city': 'San Francisco'},
    {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}
]

# Write CSV file
csv.write_csv('output.csv', data)

# Write with custom delimiter
csv.write_csv('output.tsv', data, delimiter='\t')

# Write specific columns only
csv.write_csv('names_only.csv', data, columns=['name'])

# Append to existing CSV
new_data = [{'name': 'Diana', 'age': 28, 'city': 'Boston'}]
csv.write_csv('output.csv', new_data, mode='append')
```

### Advanced CSV Processing

```python
from pyferris.io import csv
from pyferris import parallel_map, parallel_filter

def process_row(row):
    """Process a single CSV row."""
    row['age'] = int(row['age'])
    row['age_group'] = 'adult' if row['age'] >= 18 else 'minor'
    return row

def filter_adults(row):
    """Filter to keep only adult records."""
    return row['age'] >= 18

# Read and process CSV in parallel
raw_data = csv.read_csv('people.csv')

# Process all rows in parallel
processed_data = list(parallel_map(process_row, raw_data))

# Filter data in parallel
adult_data = list(parallel_filter(filter_adults, processed_data))

# Write processed data
csv.write_csv('processed_people.csv', adult_data)
```

## JSON Operations

### Reading JSON Files

```python
from pyferris.io import json

# Read JSON file
data = json.read_json('data.json')
print(f"Loaded data: {type(data)}")

# Read multiple JSON files in parallel
json_files = ['config1.json', 'config2.json', 'config3.json']
all_data = json.read_json_parallel(json_files)

for i, data in enumerate(all_data):
    print(f"File {i+1}: {len(data) if isinstance(data, (list, dict)) else 'scalar'}")

# Read JSON Lines format (JSONL)
records = json.read_jsonl('logs.jsonl')
print(f"Loaded {len(records)} log records")
```

### Writing JSON Files

```python
from pyferris.io import json

# Sample data
data = {
    'users': [
        {'id': 1, 'name': 'Alice', 'active': True},
        {'id': 2, 'name': 'Bob', 'active': False}
    ],
    'metadata': {
        'total_users': 2,
        'created_at': '2024-01-15'
    }
}

# Write JSON file
json.write_json('output.json', data)

# Write with pretty formatting
json.write_json('formatted_output.json', data, indent=2)

# Write multiple files in parallel
file_data = [
    ('output1.json', {'data': 'file1'}),
    ('output2.json', {'data': 'file2'}),
    ('output3.json', {'data': 'file3'})
]
json.write_json_parallel(file_data)

# Write JSON Lines format
records = [
    {'timestamp': '2024-01-15T10:00:00', 'level': 'INFO', 'message': 'Application started'},
    {'timestamp': '2024-01-15T10:01:00', 'level': 'ERROR', 'message': 'Connection failed'}
]
json.write_jsonl('logs.jsonl', records)
```

## Parallel I/O Operations

### Advanced Parallel Reading

```python
from pyferris.io import parallel_io
from pyferris import ProgressTracker

def process_file_content(content):
    """Process the content of a file."""
    lines = content.split('\n')
    return len([line for line in lines if line.strip()])

# Read and process multiple files in parallel
file_list = [f'log_{i}.txt' for i in range(100)]

tracker = ProgressTracker(total=len(file_list), desc="Processing files")

results = parallel_io.read_and_process_files(
    file_list,
    process_function=process_file_content,
    progress=tracker
)

print(f"Total non-empty lines: {sum(results)}")
```

### Batch File Processing

```python
from pyferris.io import parallel_io
import os

def process_file_batch(file_paths):
    """Process a batch of files."""
    results = []
    for path in file_paths:
        try:
            with open(path, 'r') as f:
                content = f.read()
                word_count = len(content.split())
                results.append({
                    'file': path,
                    'size': os.path.getsize(path),
                    'words': word_count
                })
        except Exception as e:
            results.append({
                'file': path,
                'error': str(e)
            })
    return results

# Process files in batches
all_files = [f'document_{i}.txt' for i in range(1000)]
batch_size = 50

all_results = []
for batch_results in parallel_io.process_files_in_batches(
    all_files, 
    process_file_batch, 
    batch_size=batch_size
):
    all_results.extend(batch_results)

print(f"Processed {len(all_results)} files")
```

### Memory-Efficient File Streaming

```python
from pyferris.io import parallel_io

def process_large_file_stream(file_path, chunk_size=8192):
    """Process a large file in chunks to manage memory."""
    results = []
    
    def process_chunk(chunk):
        # Process each chunk of the file
        lines = chunk.split('\n')
        return len([line for line in lines if 'ERROR' in line])
    
    error_count = 0
    for chunk in parallel_io.read_file_stream(file_path, chunk_size=chunk_size):
        error_count += process_chunk(chunk)
    
    return error_count

# Process very large log file without loading entire file into memory
large_file = 'application.log'
total_errors = process_large_file_stream(large_file)
print(f"Found {total_errors} error lines")
```

## File Format Detection and Conversion

### Automatic Format Detection

```python
from pyferris.io import file_reader

def smart_read_file(file_path):
    """Automatically detect file format and read appropriately."""
    file_format = file_reader.detect_format(file_path)
    
    if file_format == 'csv':
        from pyferris.io import csv
        return csv.read_csv(file_path)
    elif file_format == 'json':
        from pyferris.io import json
        return json.read_json(file_path)
    elif file_format == 'txt':
        from pyferris.io import simple_io
        return simple_io.read_file(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")

# Usage
files = ['data.csv', 'config.json', 'readme.txt']
for file_path in files:
    data = smart_read_file(file_path)
    print(f"{file_path}: {type(data)}")
```

### Format Conversion

```python
from pyferris.io import csv, json
from pyferris import parallel_map

def convert_csv_to_json(csv_file, json_file):
    """Convert CSV file to JSON format."""
    # Read CSV data
    csv_data = csv.read_csv(csv_file)
    
    # Convert to appropriate JSON structure
    json_data = {
        'records': csv_data,
        'metadata': {
            'source': csv_file,
            'record_count': len(csv_data)
        }
    }
    
    # Write JSON file
    json.write_json(json_file, json_data, indent=2)

def batch_convert_files(file_pairs):
    """Convert multiple CSV files to JSON in parallel."""
    def convert_pair(pair):
        csv_file, json_file = pair
        convert_csv_to_json(csv_file, json_file)
        return f"Converted {csv_file} -> {json_file}"
    
    results = parallel_map(convert_pair, file_pairs)
    return list(results)

# Convert multiple files
conversion_pairs = [
    ('data1.csv', 'data1.json'),
    ('data2.csv', 'data2.json'),
    ('data3.csv', 'data3.json')
]

conversion_results = batch_convert_files(conversion_pairs)
for result in conversion_results:
    print(result)
```

## Advanced I/O Patterns

### Producer-Consumer Pattern

```python
from pyferris.io import parallel_io
from pyferris.shared_memory import SharedQueue
import threading
import time

def file_producer(file_queue, file_list):
    """Producer: Read files and put content in queue."""
    for file_path in file_list:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                file_queue.put((file_path, content))
        except Exception as e:
            file_queue.put((file_path, None, str(e)))
    
    # Signal completion
    file_queue.put(None)

def file_consumer(file_queue, results_queue):
    """Consumer: Process file content from queue."""
    while True:
        item = file_queue.get()
        if item is None:  # End signal
            break
        
        file_path, content = item
        if content is not None:
            # Process content
            word_count = len(content.split())
            results_queue.put((file_path, word_count))
        else:
            results_queue.put((file_path, 0))

# Setup queues
file_queue = SharedQueue(maxsize=100)
results_queue = SharedQueue()

# File list
file_list = [f'document_{i}.txt' for i in range(100)]

# Start producer and consumer threads
producer_thread = threading.Thread(
    target=file_producer, 
    args=(file_queue, file_list)
)
consumer_thread = threading.Thread(
    target=file_consumer, 
    args=(file_queue, results_queue)
)

producer_thread.start()
consumer_thread.start()

# Collect results
results = []
for _ in file_list:
    result = results_queue.get()
    results.append(result)

producer_thread.join()
consumer_thread.join()

print(f"Processed {len(results)} files")
```

### Parallel File Validation

```python
from pyferris.io import parallel_io
from pyferris import parallel_map
import hashlib
import os

def validate_file(file_info):
    """Validate a file's integrity and metadata."""
    file_path, expected_size, expected_hash = file_info
    
    result = {
        'file': file_path,
        'exists': os.path.exists(file_path),
        'size_match': False,
        'hash_match': False,
        'errors': []
    }
    
    try:
        if not result['exists']:
            result['errors'].append('File does not exist')
            return result
        
        # Check file size
        actual_size = os.path.getsize(file_path)
        result['size_match'] = actual_size == expected_size
        if not result['size_match']:
            result['errors'].append(f'Size mismatch: expected {expected_size}, got {actual_size}')
        
        # Check file hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        result['hash_match'] = file_hash == expected_hash
        if not result['hash_match']:
            result['errors'].append('Hash mismatch')
            
    except Exception as e:
        result['errors'].append(str(e))
    
    return result

# File validation data
file_validations = [
    ('file1.txt', 1024, 'abc123def456'),
    ('file2.txt', 2048, 'def456ghi789'),
    ('file3.txt', 512, 'ghi789jkl012')
]

# Validate files in parallel
validation_results = list(parallel_map(validate_file, file_validations))

# Report results
for result in validation_results:
    status = "✓" if not result['errors'] else "✗"
    print(f"{status} {result['file']}")
    for error in result['errors']:
        print(f"  Error: {error}")
```

## Performance Optimization

### I/O Buffer Management

```python
from pyferris.io import parallel_io

class OptimizedFileProcessor:
    def __init__(self, buffer_size=64*1024):  # 64KB buffer
        self.buffer_size = buffer_size
    
    def read_large_file_optimized(self, file_path):
        """Read large file with optimized buffering."""
        chunks = []
        
        with open(file_path, 'r', buffering=self.buffer_size) as f:
            while True:
                chunk = f.read(self.buffer_size)
                if not chunk:
                    break
                chunks.append(chunk)
        
        return ''.join(chunks)
    
    def process_files_batch(self, file_paths):
        """Process multiple files with optimized I/O."""
        results = []
        
        for file_path in file_paths:
            try:
                content = self.read_large_file_optimized(file_path)
                line_count = content.count('\n')
                results.append({
                    'file': file_path,
                    'lines': line_count,
                    'size': len(content)
                })
            except Exception as e:
                results.append({
                    'file': file_path,
                    'error': str(e)
                })
        
        return results

# Usage
processor = OptimizedFileProcessor(buffer_size=128*1024)  # 128KB buffer
large_files = [f'large_file_{i}.txt' for i in range(10)]

from pyferris import parallel_map
results = list(parallel_map(processor.process_files_batch, [large_files]))
```

### Asynchronous I/O Integration

```python
import asyncio
from pyferris.io import parallel_io
from pyferris import async_parallel_map

async def async_read_file(file_path):
    """Asynchronously read a file."""
    loop = asyncio.get_event_loop()
    
    def read_file_sync():
        with open(file_path, 'r') as f:
            return f.read()
    
    # Run synchronous I/O in thread pool
    content = await loop.run_in_executor(None, read_file_sync)
    return len(content.split('\n'))

async def process_files_async(file_list):
    """Process files asynchronously."""
    line_counts = await async_parallel_map(async_read_file, file_list)
    return list(line_counts)

# Usage
async def main():
    files = [f'async_file_{i}.txt' for i in range(20)]
    results = await process_files_async(files)
    print(f"Total lines across all files: {sum(results)}")

# Run async processing
asyncio.run(main())
```

## Error Handling and Recovery

### Robust File Processing

```python
from pyferris.io import parallel_io
from pyferris import parallel_map
import logging

def robust_file_processor(file_path):
    """Process file with comprehensive error handling."""
    result = {
        'file': file_path,
        'success': False,
        'data': None,
        'error': None,
        'retry_count': 0
    }
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Process content
            lines = content.split('\n')
            word_count = sum(len(line.split()) for line in lines)
            
            result.update({
                'success': True,
                'data': {
                    'lines': len(lines),
                    'words': word_count,
                    'chars': len(content)
                },
                'retry_count': attempt
            })
            break
            
        except FileNotFoundError:
            result['error'] = f"File not found: {file_path}"
            break  # Don't retry for missing files
            
        except PermissionError:
            result['error'] = f"Permission denied: {file_path}"
            break  # Don't retry for permission issues
            
        except Exception as e:
            result['error'] = str(e)
            if attempt < max_retries - 1:
                import time
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
            else:
                result['retry_count'] = attempt + 1
    
    return result

# Process files with error handling
file_list = [f'data_{i}.txt' for i in range(100)]
results = list(parallel_map(robust_file_processor, file_list))

# Analyze results
successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"Successfully processed: {len(successful)}")
print(f"Failed to process: {len(failed)}")

for failure in failed:
    print(f"Failed: {failure['file']} - {failure['error']}")
```

## Best Practices

1. **Choose Appropriate Buffer Sizes**: Larger buffers for large files, smaller for many small files
2. **Handle Encoding Properly**: Always specify encoding for text files
3. **Use Streaming for Large Files**: Process large files in chunks to manage memory
4. **Implement Error Recovery**: Handle common I/O errors gracefully
5. **Monitor Memory Usage**: Be aware of memory consumption when processing many files
6. **Validate File Integrity**: Check file hashes and sizes for critical data
7. **Use Appropriate Data Formats**: Choose formats that match your performance requirements

## Next Steps

- Learn about [Async Operations](async_ops.md) for asynchronous I/O patterns
- Explore [Memory Management](memory.md) for efficient data handling
- Check out [Examples](examples.md) for real-world I/O use cases
