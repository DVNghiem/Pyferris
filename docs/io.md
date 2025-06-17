# I/O Operations

The PyFerris I/O module provides high-performance file operations with parallel processing capabilities. Built on Rust's efficient I/O primitives, it offers comprehensive support for various file formats while maintaining excellent performance for both small files and large datasets.

## Overview

The I/O module includes support for:
- **Simple I/O**: Basic file operations (text files)
- **CSV Operations**: High-performance CSV reading and writing
- **JSON Operations**: Fast JSON and JSON Lines processing
- **Parallel I/O**: Batch file operations with parallel processing
- **Advanced File Operations**: File management utilities

## Module Structure

```
pyferris.io/
├── simple_io      # Basic text file operations
├── csv           # CSV file processing
├── json          # JSON file processing
└── parallel_io   # Parallel file operations
```

## Simple I/O Operations

### Basic File Operations

```python
from pyferris.io import simple_io

# Basic file operations
content = simple_io.read_file("example.txt")
simple_io.write_file("output.txt", "Hello, World!")

# Check file existence and properties
if simple_io.file_exists("data.txt"):
    size = simple_io.file_size("data.txt")
    print(f"File size: {size} bytes")

# Directory operations
simple_io.create_directory("data/processed")
simple_io.copy_file("source.txt", "backup.txt")
simple_io.move_file("old_name.txt", "new_name.txt")
```

### File Reader and Writer Classes

```python
from pyferris.io.simple_io import SimpleFileReader, SimpleFileWriter

# Reading files
reader = SimpleFileReader("large_file.txt")
content = reader.read_text()           # Read entire file
lines = reader.read_lines()            # Read as list of lines

# Writing files
writer = SimpleFileWriter("output.txt")
writer.write_text("Hello, World!")    # Write text
writer.append_text("\nAppended line") # Append text
```

### Parallel Simple I/O

```python
from pyferris.io.simple_io import read_files_parallel, write_files_parallel

# Read multiple files in parallel
file_paths = ["file1.txt", "file2.txt", "file3.txt"]
contents = read_files_parallel(file_paths)

# Write multiple files in parallel
file_data = [
    ("output1.txt", "Content for file 1"),
    ("output2.txt", "Content for file 2"),
    ("output3.txt", "Content for file 3"),
]
write_files_parallel(file_data)
```

## CSV Operations

### High-Performance CSV Processing

```python
from pyferris.io.csv import CsvReader, CsvWriter, read_csv, write_csv

# Simple CSV reading
data = read_csv("data.csv")
print(f"Loaded {len(data)} rows")
print(f"Columns: {list(data[0].keys())}")

# Simple CSV writing
output_data = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "London"},
    {"name": "Carol", "age": 35, "city": "Tokyo"},
]
write_csv("output.csv", output_data)
```

### Advanced CSV Operations

```python
from pyferris.io.csv import CsvReader, CsvWriter

# Custom CSV reader with configuration
reader = CsvReader(
    "data.csv",
    delimiter="|",      # Custom delimiter
    has_headers=True    # File has headers
)

# Read as dictionaries (using headers as keys)
data_dict = reader.read_dict()
print(f"First row: {data_dict[0]}")

# Read as raw rows (list of lists)
rows = reader.read_rows()
headers = reader.get_headers()
print(f"Headers: {headers}")
print(f"First row: {rows[0]}")

# Custom CSV writer
writer = CsvWriter(
    "output.csv",
    delimiter=",",
    write_headers=True
)

# Write from dictionaries
writer.write_dict(data_dict)

# Write from rows
writer.write_rows([headers] + rows)
```

### CSV Processing Examples

```python
# Process large CSV files efficiently
def process_large_csv(input_file, output_file):
    reader = CsvReader(input_file)
    writer = CsvWriter(output_file)
    
    # Read data
    data = reader.read_dict()
    
    # Process data (e.g., filter and transform)
    processed_data = []
    for row in data:
        if int(row["age"]) >= 18:  # Filter adults
            row["age_group"] = "adult" if int(row["age"]) < 65 else "senior"
            processed_data.append(row)
    
    # Write processed data
    writer.write_dict(processed_data)
    print(f"Processed {len(processed_data)} rows")

process_large_csv("input.csv", "processed.csv")

# Custom delimiter and no headers example
def process_pipe_delimited_csv():
    # Read pipe-delimited file without headers
    reader = CsvReader("data.txt", delimiter="|", has_headers=False)
    rows = reader.read_rows()
    
    # Process raw rows
    processed_rows = []
    for row in rows:
        # Assume columns: name, score, grade
        if len(row) >= 3:
            name, score, grade = row[0], float(row[1]), row[2]
            if score >= 85:
                processed_rows.append([name, score, "A"])
    
    # Write with tab delimiter
    writer = CsvWriter("results.tsv", delimiter="\t", write_headers=False)
    writer.write_rows(processed_rows)

process_pipe_delimited_csv()
```

## JSON Operations

### Basic JSON Processing

```python
from pyferris.io.json import read_json, write_json, parse_json, to_json_string

# Basic JSON operations
data = read_json("config.json")
print(f"Loaded configuration: {data}")

# Modify and save
data["updated"] = True
write_json("config_updated.json", data, pretty_print=True)

# String operations
json_string = '{"name": "Alice", "age": 30}'
parsed = parse_json(json_string)
back_to_string = to_json_string(parsed, pretty_print=True)
```

### JSON Lines Processing

```python
from pyferris.io.json import read_jsonl, write_jsonl, append_jsonl

# JSON Lines operations
records = [
    {"id": 1, "name": "Alice", "score": 95},
    {"id": 2, "name": "Bob", "score": 87},
    {"id": 3, "name": "Carol", "score": 92},
]

# Write JSON Lines file
write_jsonl("data.jsonl", records)

# Read JSON Lines file
loaded_records = read_jsonl("data.jsonl")
print(f"Loaded {len(loaded_records)} records")

# Append to JSON Lines file
new_record = {"id": 4, "name": "David", "score": 89}
append_jsonl("data.jsonl", new_record)
```

### Advanced JSON Operations

```python
from pyferris.io.json import JsonReader, JsonWriter

# Advanced JSON reader
reader = JsonReader("large_data.json")

# Read regular JSON
data = reader.read()

# Read JSON Lines
lines = reader.read_lines()

# Stream large JSON arrays
large_array = reader.read_array_stream()  # Memory-efficient for large arrays

# Advanced JSON writer
writer = JsonWriter("output.json", pretty_print=True)

# Write various data types
writer.write({"message": "Hello, World!"})

# Write JSON Lines
writer.write_lines([
    {"event": "user_login", "timestamp": "2023-01-01T10:00:00Z"},
    {"event": "page_view", "timestamp": "2023-01-01T10:01:00Z"},
])

# Append individual lines
writer.append_line({"event": "user_logout", "timestamp": "2023-01-01T11:00:00Z"})
```

### JSON Processing Examples

```python
# Process streaming JSON data
def process_json_stream(input_file, output_file):
    reader = JsonReader(input_file)
    writer = JsonWriter(output_file)
    
    # Process large JSON array in chunks
    array_data = reader.read_array_stream()
    
    processed_items = []
    for item in array_data:
        if item.get("status") == "active":
            item["processed_at"] = "2023-01-01T12:00:00Z"
            processed_items.append(item)
    
    writer.write(processed_items)
    print(f"Processed {len(processed_items)} active items")

# Log processing example
def analyze_json_logs(log_file):
    reader = JsonReader(log_file)
    log_entries = reader.read_lines()
    
    # Analyze logs
    error_count = 0
    warning_count = 0
    
    for entry in log_entries:
        level = entry.get("level", "").lower()
        if level == "error":
            error_count += 1
        elif level == "warning":
            warning_count += 1
    
    # Write summary
    summary = {
        "total_entries": len(log_entries),
        "errors": error_count,
        "warnings": warning_count,
        "analysis_time": "2023-01-01T12:00:00Z"
    }
    
    write_json("log_summary.json", summary, pretty_print=True)
    return summary

summary = analyze_json_logs("application.log.json")
print(f"Log analysis: {summary}")
```

## Parallel I/O Operations

### Parallel File Processing

```python
from pyferris.io.parallel_io import (
    ParallelFileProcessor, 
    process_files_parallel, 
    find_files,
    directory_size,
    count_lines
)

# Basic parallel file processing
def process_text_file(file_path, content):
    # Custom processing function
    lines = content.split('\n')
    word_count = sum(len(line.split()) for line in lines)
    return {"file": file_path, "lines": len(lines), "words": word_count}

file_paths = ["doc1.txt", "doc2.txt", "doc3.txt"]
results = process_files_parallel(file_paths, process_text_file)
print(f"Processed {len(results)} files")
```

### Advanced Parallel Processing

```python
from pyferris.io.parallel_io import ParallelFileProcessor

# Create processor with custom configuration
processor = ParallelFileProcessor(
    max_workers=8,      # Use 8 worker threads
    chunk_size=1000     # Process in chunks of 1000 items
)

# Parallel file operations
file_paths = find_files("./data", "*.txt")
print(f"Found {len(file_paths)} text files")

# Read multiple files in parallel
file_contents = processor.read_files_parallel(file_paths)
print(f"Read {len(file_contents)} files")

# Write multiple files in parallel
output_data = [
    (f"output_{i}.txt", f"Processed content {i}")
    for i in range(100)
]
processor.write_files_parallel(output_data)

# Copy files in parallel
copy_pairs = [(f"source_{i}.txt", f"backup_{i}.txt") for i in range(50)]
processor.copy_files_parallel(copy_pairs)
```

### Directory Processing

```python
from pyferris.io.parallel_io import ParallelFileProcessor

def analyze_code_files(file_path, content):
    """Analyze source code files."""
    lines = content.split('\n')
    code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    
    return {
        "file": file_path,
        "total_lines": len(lines),
        "code_lines": len(code_lines),
        "comment_lines": len(lines) - len(code_lines),
        "size_bytes": len(content)
    }

def is_python_file(file_path):
    """Filter for Python files."""
    return file_path.endswith('.py')

processor = ParallelFileProcessor(max_workers=6)

# Process entire directory in parallel
results = processor.process_directory(
    "./project",
    analyze_code_files,
    file_filter=is_python_file
)

# Aggregate statistics
total_files = len(results)
total_lines = sum(r["total_lines"] for r in results)
total_code_lines = sum(r["code_lines"] for r in results)

print(f"Analyzed {total_files} Python files")
print(f"Total lines: {total_lines}")
print(f"Code lines: {total_code_lines}")
```

### File Statistics and Utilities

```python
from pyferris.io.parallel_io import find_files, directory_size, count_lines

# Find files with pattern matching
python_files = find_files("./project", "*.py")
config_files = find_files("./config", "*.json")
all_text_files = find_files("./docs", "*.{txt,md,rst}")

print(f"Found {len(python_files)} Python files")
print(f"Found {len(config_files)} config files")

# Get directory size
project_size = directory_size("./project")
print(f"Project size: {project_size / 1024 / 1024:.2f} MB")

# Count lines across multiple files
log_files = find_files("./logs", "*.log")
total_log_lines = count_lines(log_files)
print(f"Total log lines: {total_log_lines}")
```

### Chunk Processing

```python
from pyferris.io.parallel_io import process_file_chunks

def process_large_log_file(log_file):
    """Process large log file in parallel chunks."""
    
    def analyze_chunk(chunk_id, lines):
        """Analyze a chunk of log lines."""
        error_count = 0
        warning_count = 0
        
        for line in lines:
            if "ERROR" in line:
                error_count += 1
            elif "WARNING" in line:
                warning_count += 1
        
        return {
            "chunk_id": chunk_id,
            "lines_processed": len(lines),
            "errors": error_count,
            "warnings": warning_count
        }
    
    # Process file in chunks of 10,000 lines
    chunk_results = process_file_chunks(log_file, 10000, analyze_chunk)
    
    # Aggregate results
    total_errors = sum(r["errors"] for r in chunk_results)
    total_warnings = sum(r["warnings"] for r in chunk_results)
    total_lines = sum(r["lines_processed"] for r in chunk_results)
    
    return {
        "total_lines": total_lines,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "chunks_processed": len(chunk_results)
    }

# Process large log file
results = process_large_log_file("application.log")
print(f"Log analysis results: {results}")
```

## Performance Optimization

### Choosing the Right I/O Method

```python
# For small files (< 1MB): Use simple operations
from pyferris.io.simple_io import read_file, write_file

small_content = read_file("config.txt")
write_file("output.txt", processed_content)

# For medium files (1MB - 100MB): Use class-based readers/writers
from pyferris.io.csv import CsvReader
from pyferris.io.json import JsonReader

reader = CsvReader("medium_data.csv")
data = reader.read_dict()

# For large files (> 100MB): Use parallel processing
from pyferris.io.parallel_io import ParallelFileProcessor

processor = ParallelFileProcessor(max_workers=8)
results = processor.process_files(large_file_list, process_function)
```

### Memory-Efficient Processing

```python
def process_large_dataset_efficiently():
    """Process large datasets without loading everything into memory."""
    
    # Process CSV in batches
    def process_csv_batch(file_path):
        reader = CsvReader(file_path)
        data = reader.read_dict()
        
        # Process in smaller chunks
        batch_size = 10000
        results = []
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            batch_result = process_batch(batch)
            results.extend(batch_result)
        
        return results
    
    # Use streaming for JSON Lines
    def process_jsonl_stream(file_path):
        reader = JsonReader(file_path)
        
        results = []
        for line in reader.read_lines():  # Streaming read
            processed_line = process_json_record(line)
            if processed_line:
                results.append(processed_line)
        
        return results
```

### Performance Benchmarks

```python
import time
from pyferris.io import simple_io, csv, json, parallel_io

def benchmark_io_operations():
    """Benchmark different I/O operations."""
    
    # Prepare test data
    test_files = [f"test_{i}.txt" for i in range(100)]
    
    # Benchmark 1: Sequential vs Parallel file reading
    start_time = time.time()
    sequential_results = [simple_io.read_file(f) for f in test_files]
    sequential_time = time.time() - start_time
    
    start_time = time.time()
    parallel_results = simple_io.read_files_parallel(test_files)
    parallel_time = time.time() - start_time
    
    print(f"Sequential reading: {sequential_time:.2f}s")
    print(f"Parallel reading: {parallel_time:.2f}s")
    print(f"Speedup: {sequential_time / parallel_time:.2f}x")
    
    # Benchmark 2: CSV processing
    start_time = time.time()
    csv_data = csv.read_csv("large_dataset.csv")
    csv_time = time.time() - start_time
    print(f"CSV reading: {csv_time:.2f}s for {len(csv_data)} rows")
    
    # Benchmark 3: JSON processing
    start_time = time.time()
    json_data = json.read_jsonl("large_dataset.jsonl")
    json_time = time.time() - start_time
    print(f"JSON Lines reading: {json_time:.2f}s for {len(json_data)} records")

benchmark_io_operations()
```

## Best Practices

### Error Handling

```python
from pyferris.io.simple_io import read_file, write_file
from pyferris.io.csv import CsvReader
import os

def robust_file_processing():
    """Demonstrate robust file processing with error handling."""
    
    def safe_read_file(file_path):
        try:
            if not simple_io.file_exists(file_path):
                print(f"File not found: {file_path}")
                return None
            
            content = read_file(file_path)
            return content
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def safe_csv_processing(csv_path):
        try:
            reader = CsvReader(csv_path)
            data = reader.read_dict()
            
            # Validate data structure
            if not data:
                print(f"Empty CSV file: {csv_path}")
                return []
            
            # Check required columns
            required_columns = ["id", "name", "value"]
            if not all(col in data[0] for col in required_columns):
                print(f"Missing required columns in {csv_path}")
                return []
            
            return data
        
        except Exception as e:
            print(f"Error processing CSV {csv_path}: {e}")
            return []

    # Process files with error handling
    file_list = ["data1.txt", "data2.txt", "missing.txt"]
    
    for file_path in file_list:
        content = safe_read_file(file_path)
        if content:
            # Process content
            processed = content.upper()
            output_path = f"processed_{os.path.basename(file_path)}"
            write_file(output_path, processed)
```

### Resource Management

```python
from pyferris.io.parallel_io import ParallelFileProcessor
import contextlib

@contextlib.contextmanager
def managed_file_processor(max_workers=4):
    """Context manager for proper resource cleanup."""
    processor = ParallelFileProcessor(max_workers=max_workers)
    try:
        yield processor
    finally:
        # Cleanup resources if needed
        processor.shutdown()

# Use with context manager
def process_files_safely(file_list):
    with managed_file_processor(max_workers=8) as processor:
        results = processor.read_files_parallel(file_list)
        
        # Process files
        processed_data = []
        for file_path, content in results:
            processed_content = content.upper()
            processed_data.append((f"processed_{file_path}", processed_content))
        
        # Write results
        processor.write_files_parallel(processed_data)
        
        return len(processed_data)
```

### Configuration and Tuning

```python
def optimize_io_configuration():
    """Guidelines for optimizing I/O performance."""
    
    # 1. Choose appropriate worker count
    import os
    cpu_count = os.cpu_count()
    
    # For I/O-bound tasks: use more workers
    io_workers = min(cpu_count * 2, 16)
    
    # For CPU-bound processing: use CPU count
    cpu_workers = cpu_count
    
    # 2. Tune chunk sizes based on file sizes
    def get_optimal_chunk_size(file_size_mb):
        if file_size_mb < 1:
            return 100      # Small chunks for small files
        elif file_size_mb < 10:
            return 1000     # Medium chunks for medium files
        else:
            return 10000    # Large chunks for large files
    
    # 3. Use appropriate I/O method based on data format
    def choose_io_method(file_path):
        if file_path.endswith('.csv'):
            return csv.CsvReader(file_path)
        elif file_path.endswith('.json'):
            return json.JsonReader(file_path)
        elif file_path.endswith('.jsonl'):
            reader = json.JsonReader(file_path)
            return reader.read_lines()  # Use streaming for JSON Lines
        else:
            return simple_io.SimpleFileReader(file_path)
```

## Integration Examples

### With Data Processing Libraries

```python
import pandas as pd
from pyferris.io.csv import read_csv
from pyferris.io.parallel_io import process_files_parallel

def integrate_with_pandas():
    """Integrate PyFerris I/O with pandas."""
    
    # Read CSV with PyFerris, process with pandas
    data = read_csv("large_dataset.csv")
    df = pd.DataFrame(data)
    
    # Process data
    processed_df = df.groupby('category').agg({
        'value': 'sum',
        'count': 'mean'
    })
    
    # Write back using PyFerris
    output_data = processed_df.reset_index().to_dict('records')
    write_csv("processed_data.csv", output_data)

def parallel_data_processing():
    """Process multiple datasets in parallel."""
    
    def process_dataset(file_path, content):
        # Convert to pandas DataFrame
        import io
        df = pd.read_csv(io.StringIO(content))
        
        # Perform analysis
        summary = {
            'file': file_path,
            'rows': len(df),
            'columns': len(df.columns),
            'numeric_columns': len(df.select_dtypes(include='number').columns),
            'missing_values': df.isnull().sum().sum()
        }
        
        return summary
    
    # Process multiple datasets
    dataset_files = ["dataset1.csv", "dataset2.csv", "dataset3.csv"]
    summaries = process_files_parallel(dataset_files, process_dataset)
    
    # Aggregate results
    total_rows = sum(s['rows'] for s in summaries)
    total_missing = sum(s['missing_values'] for s in summaries)
    
    print(f"Processed {len(summaries)} datasets")
    print(f"Total rows: {total_rows}")
    print(f"Total missing values: {total_missing}")
```

The PyFerris I/O module provides a comprehensive suite of tools for high-performance file processing, from simple text operations to complex parallel data processing workflows.
