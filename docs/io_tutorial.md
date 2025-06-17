# Pyferris IO Tutorial - Step by Step Guide

## Introduction

Welcome to the Pyferris IO tutorial! This guide will walk you through all the features of the IO module with practical examples. By the end of this tutorial, you'll be able to efficiently handle file operations in Python using Pyferris.

## Prerequisites

- Python 3.7+
- Pyferris installed (`pip install pyferris`)
- Basic Python knowledge

## Tutorial Structure

1. [Getting Started](#getting-started)
2. [Basic File Operations](#basic-file-operations)
3. [File Utilities](#file-utilities)
4. [Object-Oriented Interface](#object-oriented-interface)
5. [Parallel Processing](#parallel-processing)
6. [Error Handling](#error-handling)
7. [Performance Optimization](#performance-optimization)
8. [Real-World Examples](#real-world-examples)

## Getting Started

Let's start by importing the module and creating our first file:

```python
import pyferris.simple_io as sio

# Create our first file
sio.write_file("hello.txt", "Hello, Pyferris!")
print("File created successfully!")

# Read it back
content = sio.read_file("hello.txt")
print(f"File content: {content}")

# Clean up
sio.delete_file("hello.txt")
```

**Output:**
```
File created successfully!
File content: Hello, Pyferris!
```

## Basic File Operations

### Writing Files

```python
import pyferris.simple_io as sio

# Write simple text
sio.write_file("simple.txt", "This is simple text.")

# Write multi-line content
multi_line_content = """Line 1: Introduction
Line 2: Main content
Line 3: Conclusion"""

sio.write_file("multi_line.txt", multi_line_content)

# Write data with special characters
data_content = "Special chars: äöü, 中文, 🚀, \\n\\t\\r"
sio.write_file("special_chars.txt", data_content)

print("All files written successfully!")
```

### Reading Files

```python
import pyferris.simple_io as sio

# Read simple file
simple_content = sio.read_file("simple.txt")
print(f"Simple: {simple_content}")

# Read multi-line file
multi_content = sio.read_file("multi_line.txt")
print(f"Multi-line:\\n{multi_content}")

# Read file with special characters
special_content = sio.read_file("special_chars.txt")
print(f"Special: {special_content}")
```

**Output:**
```
Simple: This is simple text.
Multi-line:
Line 1: Introduction
Line 2: Main content
Line 3: Conclusion
Special: Special chars: äöü, 中文, 🚀, 
	
```

### Exercise 1: Basic I/O

Create a program that:
1. Writes your favorite quote to a file
2. Reads it back and displays it
3. Counts the number of characters
4. Saves the character count to another file

<details>
<summary>Solution</summary>

```python
import pyferris.simple_io as sio

# Step 1: Write favorite quote
quote = "The only way to do great work is to love what you do. - Steve Jobs"
sio.write_file("quote.txt", quote)

# Step 2: Read and display
content = sio.read_file("quote.txt")
print(f"Quote: {content}")

# Step 3: Count characters
char_count = len(content)
print(f"Character count: {char_count}")

# Step 4: Save count to another file
count_info = f"The quote has {char_count} characters."
sio.write_file("quote_stats.txt", count_info)

print("Exercise completed!")

# Clean up
sio.delete_file("quote.txt")
sio.delete_file("quote_stats.txt")
```
</details>

## File Utilities

### Checking File Existence and Properties

```python
import pyferris.simple_io as sio

# Create a test file
test_content = "This is a test file for utilities demonstration."
sio.write_file("test_file.txt", test_content)

# Check if file exists
if sio.file_exists("test_file.txt"):
    print("✅ File exists!")
    
    # Get file size
    size = sio.file_size("test_file.txt")
    print(f"📏 File size: {size} bytes")
    
    # Calculate size in different units
    if size > 1024*1024:
        print(f"   ({size/1024/1024:.2f} MB)")
    elif size > 1024:
        print(f"   ({size/1024:.2f} KB)")
else:
    print("❌ File does not exist!")

# Check non-existent file
if not sio.file_exists("nonexistent.txt"):
    print("✅ Correctly detected non-existent file")
```

### File Management Operations

```python
import pyferris.simple_io as sio

# Create original file
original_content = "This is the original file content."
sio.write_file("original.txt", original_content)

# Copy file
sio.copy_file("original.txt", "copy.txt")
print("✅ File copied")

# Verify copy
copy_content = sio.read_file("copy.txt")
print(f"Copy content: {copy_content}")

# Move (rename) file
sio.move_file("copy.txt", "renamed.txt")
print("✅ File moved/renamed")

# Verify move
if not sio.file_exists("copy.txt") and sio.file_exists("renamed.txt"):
    print("✅ Move operation successful")

# Create directory structure
sio.create_directory("data/processed/output")
print("✅ Directory structure created")

# Move file to new directory
sio.move_file("renamed.txt", "data/processed/output/final.txt")
print("✅ File moved to subdirectory")

# Clean up
sio.delete_file("original.txt")
sio.delete_file("data/processed/output/final.txt")
print("✅ Cleaned up files")
```

### Exercise 2: File Management

Create a file organization system that:
1. Creates several text files with different content
2. Creates a backup directory
3. Copies all files to the backup directory
4. Generates a report of all files and their sizes

<details>
<summary>Solution</summary>

```python
import pyferris.simple_io as sio

# Step 1: Create several files
files_data = {
    "doc1.txt": "Document 1: Project overview and goals.",
    "doc2.txt": "Document 2: Technical specifications and requirements.",
    "doc3.txt": "Document 3: Implementation details and timeline.",
    "readme.txt": "README: How to use this project."
}

print("Creating files...")
for filename, content in files_data.items():
    sio.write_file(filename, content)
    print(f"✅ Created {filename}")

# Step 2: Create backup directory
sio.create_directory("backup")
print("✅ Created backup directory")

# Step 3: Copy files to backup
print("\\nCopying files to backup...")
for filename in files_data.keys():
    backup_path = f"backup/{filename}"
    sio.copy_file(filename, backup_path)
    print(f"✅ Copied {filename} to backup")

# Step 4: Generate report
report_lines = ["File Organization Report", "=" * 30, ""]

print("\\nGenerating report...")
total_size = 0
for filename in files_data.keys():
    if sio.file_exists(filename):
        size = sio.file_size(filename)
        total_size += size
        report_lines.append(f"{filename}: {size} bytes")

report_lines.extend(["", f"Total size: {total_size} bytes"])
report_content = "\\n".join(report_lines)

sio.write_file("file_report.txt", report_content)
print("✅ Report generated")

# Display report
print("\\nReport content:")
print(sio.read_file("file_report.txt"))

# Clean up
for filename in list(files_data.keys()) + ["file_report.txt"]:
    sio.delete_file(filename)
for filename in files_data.keys():
    sio.delete_file(f"backup/{filename}")
print("\\n✅ Cleanup completed")
```
</details>

## Object-Oriented Interface

### Using SimpleFileReader

```python
from pyferris import SimpleFileReader
import pyferris.simple_io as sio

# Create a sample file with multiple lines
sample_content = """Python is awesome!
It's great for data science.
Machine learning is fun.
Web development with Python rocks!"""

sio.write_file("sample.txt", sample_content)

# Create reader instance
reader = SimpleFileReader("sample.txt")

# Read entire content
print("=== Reading entire content ===")
full_content = reader.read_text()
print(full_content)

# Read as lines
print("\\n=== Reading as lines ===")
lines = reader.read_lines()
for i, line in enumerate(lines, 1):
    print(f"Line {i}: {line}")

# Analyze the content
print(f"\\n=== Analysis ===")
print(f"Total lines: {len(lines)}")
print(f"Total characters: {len(full_content)}")
print(f"Lines containing 'Python': {sum(1 for line in lines if 'Python' in line)}")

# Clean up
sio.delete_file("sample.txt")
```

### Using SimpleFileWriter

```python
from pyferris import SimpleFileWriter
import pyferris.simple_io as sio

# Create writer instance
writer = SimpleFileWriter("log.txt")

# Write initial content
print("Writing initial log entry...")
writer.write_text("[START] Application initialized")

# Append log entries
print("Adding more log entries...")
writer.append_text("\\n[INFO] Loading configuration")
writer.append_text("\\n[INFO] Connecting to database")
writer.append_text("\\n[INFO] Processing data")
writer.append_text("\\n[ERROR] Network timeout occurred")
writer.append_text("\\n[INFO] Retrying operation")
writer.append_text("\\n[INFO] Operation completed successfully")
writer.append_text("\\n[END] Application finished")

# Read back and display
print("\\n=== Final log content ===")
final_content = sio.read_file("log.txt")
print(final_content)

# Analyze log
lines = final_content.split("\\n")
info_count = sum(1 for line in lines if "[INFO]" in line)
error_count = sum(1 for line in lines if "[ERROR]" in line)

print(f"\\n=== Log Analysis ===")
print(f"Total entries: {len(lines)}")
print(f"Info entries: {info_count}")
print(f"Error entries: {error_count}")

# Clean up
sio.delete_file("log.txt")
```

### Exercise 3: Log File Processor

Create a log file processor using the OOP interface that:
1. Creates a log file with various types of entries
2. Reads and categorizes log entries
3. Creates separate files for different log levels
4. Generates a summary report

<details>
<summary>Solution</summary>

```python
from pyferris import SimpleFileReader, SimpleFileWriter
import pyferris.simple_io as sio

# Step 1: Create log file with various entries
print("Creating log file...")
log_writer = SimpleFileWriter("application.log")

log_entries = [
    "[INFO] 2024-01-01 10:00:00 - Application started",
    "[DEBUG] 2024-01-01 10:00:01 - Loading configuration from config.json",
    "[INFO] 2024-01-01 10:00:02 - Database connection established",
    "[WARNING] 2024-01-01 10:00:05 - Database connection slow (500ms)",
    "[INFO] 2024-01-01 10:00:10 - Processing user request",
    "[ERROR] 2024-01-01 10:00:15 - Failed to process payment: timeout",
    "[INFO] 2024-01-01 10:00:20 - Retrying payment processing",
    "[INFO] 2024-01-01 10:00:25 - Payment processed successfully",
    "[DEBUG] 2024-01-01 10:00:30 - Cleaning up temporary files",
    "[WARNING] 2024-01-01 10:00:35 - High memory usage detected",
    "[ERROR] 2024-01-01 10:00:40 - Memory allocation failed",
    "[INFO] 2024-01-01 10:00:45 - Application shutdown initiated"
]

log_writer.write_text(log_entries[0])  # Write first entry
for entry in log_entries[1:]:  # Append the rest
    log_writer.append_text("\\n" + entry)

# Step 2: Read and categorize log entries
print("\\nReading and categorizing log entries...")
log_reader = SimpleFileReader("application.log")
all_lines = log_reader.read_lines()

# Categorize entries
categories = {
    "INFO": [],
    "DEBUG": [],
    "WARNING": [],
    "ERROR": []
}

for line in all_lines:
    for level in categories.keys():
        if f"[{level}]" in line:
            categories[level].append(line)
            break

# Step 3: Create separate files for each log level
print("Creating separate files for each log level...")
for level, entries in categories.items():
    if entries:  # Only create file if there are entries
        filename = f"{level.lower()}_logs.txt"
        level_writer = SimpleFileWriter(filename)
        
        level_writer.write_text(entries[0])
        for entry in entries[1:]:
            level_writer.append_text("\\n" + entry)
        
        print(f"✅ Created {filename} with {len(entries)} entries")

# Step 4: Generate summary report
print("\\nGenerating summary report...")
summary_writer = SimpleFileWriter("log_summary.txt")

report_lines = [
    "Log Processing Summary Report",
    "=" * 40,
    f"Processing date: 2024-01-01",
    f"Total log entries: {len(all_lines)}",
    ""
]

for level, entries in categories.items():
    report_lines.append(f"{level} entries: {len(entries)}")

report_lines.extend([
    "",
    "Files created:",
    "- application.log (original log)",
    "- info_logs.txt (INFO entries)",
    "- debug_logs.txt (DEBUG entries)", 
    "- warning_logs.txt (WARNING entries)",
    "- error_logs.txt (ERROR entries)",
    "- log_summary.txt (this report)"
])

summary_writer.write_text("\\n".join(report_lines))

# Display summary
print("\\n=== Summary Report ===")
summary_reader = SimpleFileReader("log_summary.txt")
print(summary_reader.read_text())

# Clean up
cleanup_files = [
    "application.log", "log_summary.txt",
    "info_logs.txt", "debug_logs.txt", 
    "warning_logs.txt", "error_logs.txt"
]

print("\\nCleaning up...")
for filename in cleanup_files:
    if sio.file_exists(filename):
        sio.delete_file(filename)
print("✅ Cleanup completed")
```
</details>

## Parallel Processing

### Parallel File Reading

```python
import pyferris.simple_io as sio
import time

# Create multiple test files
print("Creating test files...")
test_files = []
for i in range(5):
    filename = f"test_file_{i}.txt"
    content = f"This is test file {i}.\\n" * 100  # 100 lines each
    sio.write_file(filename, content)
    test_files.append(filename)

print(f"Created {len(test_files)} test files")

# Sequential reading
print("\\n=== Sequential Reading ===")
start_time = time.time()
sequential_contents = []
for filename in test_files:
    content = sio.read_file(filename)
    sequential_contents.append(content)
sequential_time = time.time() - start_time
print(f"Sequential read time: {sequential_time:.4f} seconds")

# Parallel reading
print("\\n=== Parallel Reading ===")
start_time = time.time()
parallel_contents = sio.read_files_parallel(test_files)
parallel_time = time.time() - start_time
print(f"Parallel read time: {parallel_time:.4f} seconds")

# Compare results
print(f"\\n=== Comparison ===")
print(f"Results identical: {sequential_contents == parallel_contents}")
speedup = sequential_time / parallel_time if parallel_time > 0 else float('inf')
print(f"Speedup: {speedup:.2f}x")

# Clean up
for filename in test_files:
    sio.delete_file(filename)
```

### Parallel File Writing

```python
import pyferris.simple_io as sio
import time

# Prepare data for parallel writing
print("Preparing data for parallel writing...")
write_data = []
for i in range(10):
    filename = f"parallel_output_{i}.txt"
    content = f"""File {i} Content
    
This is automatically generated content for file number {i}.
It contains multiple lines to simulate real file content.
Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}

End of file {i}."""
    write_data.append((filename, content))

# Sequential writing
print("\\n=== Sequential Writing ===")
start_time = time.time()
for filename, content in write_data:
    sio.write_file(filename, content)
sequential_write_time = time.time() - start_time
print(f"Sequential write time: {sequential_write_time:.4f} seconds")

# Clean up sequential files
for filename, _ in write_data:
    sio.delete_file(filename)

# Parallel writing
print("\\n=== Parallel Writing ===")
start_time = time.time()
sio.write_files_parallel(write_data)
parallel_write_time = time.time() - start_time
print(f"Parallel write time: {parallel_write_time:.4f} seconds")

# Verify parallel writing results
print("\\n=== Verification ===")
all_exist = all(sio.file_exists(filename) for filename, _ in write_data)
print(f"All files created: {all_exist}")

if all_exist:
    # Verify content
    for filename, expected_content in write_data[:3]:  # Check first 3
        actual_content = sio.read_file(filename)
        content_match = actual_content == expected_content
        print(f"Content match for {filename}: {content_match}")

# Performance comparison
speedup = sequential_write_time / parallel_write_time if parallel_write_time > 0 else float('inf')
print(f"\\nWrite speedup: {speedup:.2f}x")

# Clean up
for filename, _ in write_data:
    sio.delete_file(filename)
```

### Exercise 4: Batch File Processing

Create a batch file processor that:
1. Generates 20 files with random content
2. Processes them in parallel (converts to uppercase)
3. Saves processed files with "_processed" suffix
4. Compares sequential vs parallel performance

<details>
<summary>Solution</summary>

```python
import pyferris.simple_io as sio
import time
import random
import string

def generate_random_content(lines=50):
    """Generate random text content."""
    content = []
    for i in range(lines):
        # Random sentence
        words = [''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10))) 
                for _ in range(random.randint(5, 15))]
        sentence = ' '.join(words) + '.'
        content.append(sentence)
    return '\\n'.join(content)

# Step 1: Generate 20 files with random content
print("Step 1: Generating 20 files with random content...")
input_files = []
for i in range(20):
    filename = f"input_{i:02d}.txt"
    content = generate_random_content()
    sio.write_file(filename, content)
    input_files.append(filename)

print(f"✅ Generated {len(input_files)} files")

# Step 2: Sequential processing
print("\\nStep 2: Sequential processing...")
start_time = time.time()

sequential_processed = []
for filename in input_files:
    # Read file
    content = sio.read_file(filename)
    # Process (convert to uppercase)
    processed_content = content.upper()
    # Save with _processed suffix
    output_filename = filename.replace('.txt', '_processed.txt')
    sio.write_file(output_filename, processed_content)
    sequential_processed.append(output_filename)

sequential_time = time.time() - start_time
print(f"✅ Sequential processing completed in {sequential_time:.4f} seconds")

# Clean up sequential processed files
for filename in sequential_processed:
    sio.delete_file(filename)

# Step 3: Parallel processing
print("\\nStep 3: Parallel processing...")
start_time = time.time()

# Read all files in parallel
input_contents = sio.read_files_parallel(input_files)

# Process content (this is still sequential, but fast)
processed_data = []
for i, content in enumerate(input_contents):
    processed_content = content.upper()
    output_filename = input_files[i].replace('.txt', '_processed.txt')
    processed_data.append((output_filename, processed_content))

# Write all processed files in parallel
sio.write_files_parallel(processed_data)

parallel_time = time.time() - start_time
print(f"✅ Parallel processing completed in {parallel_time:.4f} seconds")

# Step 4: Performance comparison and verification
print("\\nStep 4: Performance Analysis")
print(f"Sequential time: {sequential_time:.4f} seconds")
print(f"Parallel time: {parallel_time:.4f} seconds")
speedup = sequential_time / parallel_time if parallel_time > 0 else float('inf')
print(f"Speedup: {speedup:.2f}x")

# Verify results
print("\\nVerification:")
all_processed_exist = all(sio.file_exists(filename) for filename, _ in processed_data)
print(f"All processed files created: {all_processed_exist}")

# Check a few files for correct processing
for i in range(min(3, len(input_files))):
    original_content = sio.read_file(input_files[i])
    processed_filename = processed_data[i][0]
    processed_content = sio.read_file(processed_filename)
    
    correct_processing = processed_content == original_content.upper()
    print(f"File {i+1} processed correctly: {correct_processing}")

# File size analysis
print("\\nFile size analysis:")
total_input_size = sum(sio.file_size(f) for f in input_files)
total_output_size = sum(sio.file_size(f) for f, _ in processed_data)

print(f"Total input size: {total_input_size} bytes ({total_input_size/1024:.1f} KB)")
print(f"Total output size: {total_output_size} bytes ({total_output_size/1024:.1f} KB)")

# Clean up all files
print("\\nCleaning up...")
all_files = input_files + [f for f, _ in processed_data]
for filename in all_files:
    if sio.file_exists(filename):
        sio.delete_file(filename)

print(f"✅ Cleaned up {len(all_files)} files")
print("\\nBatch processing exercise completed!")
```
</details>

## Error Handling

### Basic Error Handling

```python
import pyferris.simple_io as sio

def safe_file_operations():
    """Demonstrate proper error handling."""
    
    print("=== Error Handling Examples ===")
    
    # 1. File not found
    print("\\n1. Testing file not found:")
    try:
        content = sio.read_file("nonexistent_file.txt")
        print(f"Content: {content}")
    except Exception as e:
        print(f"❌ Expected error: {e}")
    
    # 2. Invalid path
    print("\\n2. Testing invalid path:")
    try:
        sio.write_file("", "content")  # Empty path
    except Exception as e:
        print(f"❌ Expected error: {e}")
    
    # 3. Permission issues (simulate)
    print("\\n3. Testing permission handling:")
    try:
        # Try to write to a typically restricted location
        sio.write_file("/root/restricted.txt", "content")
    except Exception as e:
        print(f"❌ Expected error: {e}")
    
    # 4. Safe file checking
    print("\\n4. Safe file operations:")
    filename = "safe_test.txt"
    
    # Always check before reading
    if sio.file_exists(filename):
        content = sio.read_file(filename)
        print(f"✅ File content: {content}")
    else:
        print(f"ℹ️  File {filename} doesn't exist, creating it...")
        sio.write_file(filename, "Safe content")
        print("✅ File created successfully")
    
    # Clean up
    if sio.file_exists(filename):
        sio.delete_file(filename)
        print("✅ Cleanup completed")

safe_file_operations()
```

### Robust File Processing

```python
import pyferris.simple_io as sio

def robust_file_processor(input_files, output_dir="processed"):
    """Process files with comprehensive error handling."""
    
    results = {
        'successful': [],
        'failed': [],
        'errors': []
    }
    
    # Create output directory
    try:
        sio.create_directory(output_dir)
        print(f"✅ Created output directory: {output_dir}")
    except Exception as e:
        print(f"❌ Failed to create directory: {e}")
        return results
    
    # Process each file
    for input_file in input_files:
        try:
            # Check if input file exists
            if not sio.file_exists(input_file):
                error_msg = f"Input file does not exist: {input_file}"
                results['failed'].append(input_file)
                results['errors'].append(error_msg)
                print(f"⚠️  {error_msg}")
                continue
            
            # Try to read the file
            try:
                content = sio.read_file(input_file)
            except Exception as e:
                error_msg = f"Failed to read {input_file}: {e}"
                results['failed'].append(input_file)
                results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                continue
            
            # Process content (example: add timestamp)
            import time
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            processed_content = f"Processed on: {timestamp}\\n\\n{content}"
            
            # Generate output filename
            import os
            base_name = os.path.basename(input_file)
            output_file = f"{output_dir}/processed_{base_name}"
            
            # Try to write processed file
            try:
                sio.write_file(output_file, processed_content)
                results['successful'].append(input_file)
                print(f"✅ Processed: {input_file} -> {output_file}")
            except Exception as e:
                error_msg = f"Failed to write {output_file}: {e}"
                results['failed'].append(input_file)
                results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                
        except Exception as e:
            # Catch any unexpected errors
            error_msg = f"Unexpected error processing {input_file}: {e}"
            results['failed'].append(input_file)
            results['errors'].append(error_msg)
            print(f"💥 {error_msg}")
    
    return results

# Test the robust processor
print("Testing robust file processor...")

# Create some test files (some valid, some invalid scenarios)
test_files = [
    "valid1.txt",
    "valid2.txt", 
    "nonexistent.txt",  # This won't exist
    "valid3.txt"
]

# Create the valid files
for filename in ["valid1.txt", "valid2.txt", "valid3.txt"]:
    sio.write_file(filename, f"Content of {filename}")

# Process files
results = robust_file_processor(test_files)

# Print summary
print(f"\\n=== Processing Summary ===")
print(f"Successful: {len(results['successful'])}")
print(f"Failed: {len(results['failed'])}")
print(f"Success rate: {len(results['successful'])/len(test_files)*100:.1f}%")

if results['errors']:
    print(f"\\nErrors encountered:")
    for error in results['errors']:
        print(f"  - {error}")

# Clean up
cleanup_files = ["valid1.txt", "valid2.txt", "valid3.txt"]
for filename in cleanup_files:
    if sio.file_exists(filename):
        sio.delete_file(filename)

# Clean up processed files
for filename in results['successful']:
    processed_file = f"processed/processed_{filename.split('/')[-1]}"
    if sio.file_exists(processed_file):
        sio.delete_file(processed_file)
```

## Performance Optimization

### Choosing the Right Method

```python
import pyferris.simple_io as sio
import time

def performance_comparison():
    """Compare different approaches for various scenarios."""
    
    print("=== Performance Optimization Guide ===")
    
    # Scenario 1: Few large files
    print("\\n1. Few Large Files (3 files, 100KB each)")
    large_files = []
    large_content = "Large file content line.\\n" * 5000  # ~100KB
    
    for i in range(3):
        filename = f"large_{i}.txt"
        sio.write_file(filename, large_content)
        large_files.append(filename)
    
    # Sequential
    start = time.time()
    for filename in large_files:
        content = sio.read_file(filename)
    seq_time = time.time() - start
    
    # Parallel
    start = time.time()
    contents = sio.read_files_parallel(large_files)
    par_time = time.time() - start
    
    print(f"Sequential: {seq_time:.4f}s, Parallel: {par_time:.4f}s")
    print(f"Recommendation: {'Parallel' if par_time < seq_time else 'Sequential'}")
    
    # Clean up
    for f in large_files:
        sio.delete_file(f)
    
    # Scenario 2: Many small files
    print("\\n2. Many Small Files (50 files, 100 bytes each)")
    small_files = []
    small_content = "Small content" * 10  # ~100 bytes
    
    for i in range(50):
        filename = f"small_{i}.txt"
        sio.write_file(filename, small_content)
        small_files.append(filename)
    
    # Sequential
    start = time.time()
    for filename in small_files:
        content = sio.read_file(filename)
    seq_time = time.time() - start
    
    # Parallel
    start = time.time()
    contents = sio.read_files_parallel(small_files)
    par_time = time.time() - start
    
    print(f"Sequential: {seq_time:.4f}s, Parallel: {par_time:.4f}s")
    print(f"Recommendation: {'Parallel' if par_time < seq_time else 'Sequential'}")
    
    # Clean up
    for f in small_files:
        sio.delete_file(f)
    
    print("\\n=== Optimization Tips ===")
    print("1. Use parallel operations for 10+ files")
    print("2. Sequential is often better for <5 files")  
    print("3. File size matters less than file count")
    print("4. Consider disk I/O limits on your system")

performance_comparison()
```

### Memory-Efficient Processing

```python
import pyferris.simple_io as sio

def memory_efficient_processing():
    """Demonstrate memory-efficient file processing patterns."""
    
    print("=== Memory-Efficient Processing ===")
    
    # Create test files
    test_files = []
    for i in range(10):
        filename = f"mem_test_{i}.txt"
        content = f"Line {j}: Data content for file {i}\\n" * 1000 for j in range(1000)
        content = "".join(content)
        sio.write_file(filename, content)
        test_files.append(filename)
    
    print(f"Created {len(test_files)} test files")
    
    # Method 1: Process all at once (memory intensive)
    print("\\n1. Processing all files at once:")
    try:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Read all files
        all_contents = sio.read_files_parallel(test_files)
        
        # Process all contents
        processed_contents = [content.upper() for content in all_contents]
        
        # Write all processed files
        write_data = [(f"processed_{f}", content) 
                     for f, content in zip(test_files, processed_contents)]
        sio.write_files_parallel(write_data)
        
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_used = mem_after - mem_before
        
        print(f"Memory used: {mem_used:.1f} MB")
        
        # Clean up processed files
        for filename, _ in write_data:
            sio.delete_file(filename)
            
    except ImportError:
        print("psutil not available, skipping memory measurement")
    
    # Method 2: Process in batches (memory efficient)
    print("\\n2. Processing in batches:")
    batch_size = 3
    processed_files = []
    
    for i in range(0, len(test_files), batch_size):
        batch = test_files[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}: {len(batch)} files")
        
        # Read batch
        batch_contents = sio.read_files_parallel(batch)
        
        # Process batch
        processed_batch = [content.upper() for content in batch_contents]
        
        # Write batch
        write_batch = [(f"batch_processed_{f}", content) 
                      for f, content in zip(batch, processed_batch)]
        sio.write_files_parallel(write_batch)
        
        processed_files.extend(write_batch)
    
    print(f"Processed {len(processed_files)} files in batches")
    
    # Clean up
    all_cleanup = test_files + [f for f, _ in processed_files]
    for filename in all_cleanup:
        if sio.file_exists(filename):
            sio.delete_file(filename)
    
    print("\\n=== Memory Optimization Tips ===")
    print("1. Process files in batches for large datasets")
    print("2. Delete temporary files as soon as possible")
    print("3. Use generators for very large file processing")
    print("4. Monitor memory usage in production")

memory_efficient_processing()
```

## Real-World Examples

### Example 1: Log File Analyzer

```python
import pyferris.simple_io as sio
from pyferris import SimpleFileReader, SimpleFileWriter
import re
from datetime import datetime

def log_analyzer(log_files):
    """Analyze multiple log files and generate reports."""
    
    print("=== Log File Analyzer ===")
    
    # Read all log files in parallel
    print(f"Reading {len(log_files)} log files...")
    log_contents = sio.read_files_parallel(log_files)
    
    # Initialize analysis data
    analysis = {
        'total_lines': 0,
        'error_count': 0,
        'warning_count': 0, 
        'info_count': 0,
        'unique_ips': set(),
        'error_messages': [],
        'hourly_stats': {}
    }
    
    # Analyze each log file
    for filename, content in zip(log_files, log_contents):
        print(f"Analyzing {filename}...")
        lines = content.split('\\n')
        analysis['total_lines'] += len(lines)
        
        for line in lines:
            if not line.strip():
                continue
                
            # Count log levels
            if '[ERROR]' in line:
                analysis['error_count'] += 1
                analysis['error_messages'].append(line)
            elif '[WARNING]' in line:
                analysis['warning_count'] += 1
            elif '[INFO]' in line:
                analysis['info_count'] += 1
            
            # Extract IP addresses
            ip_pattern = r'\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b'
            ips = re.findall(ip_pattern, line)
            analysis['unique_ips'].update(ips)
            
            # Extract timestamps for hourly analysis
            timestamp_pattern = r'(\\d{4}-\\d{2}-\\d{2} \\d{2}):'
            match = re.search(timestamp_pattern, line)
            if match:
                hour = match.group(1)
                analysis['hourly_stats'][hour] = analysis['hourly_stats'].get(hour, 0) + 1
    
    # Generate report
    report_lines = [
        "Log Analysis Report",
        "=" * 50,
        f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Files Analyzed: {len(log_files)}",
        "",
        "Summary Statistics:",
        f"  Total Lines: {analysis['total_lines']:,}",
        f"  Error Entries: {analysis['error_count']:,}",
        f"  Warning Entries: {analysis['warning_count']:,}",
        f"  Info Entries: {analysis['info_count']:,}",
        f"  Unique IP Addresses: {len(analysis['unique_ips'])}",
        ""
    ]
    
    # Top errors
    if analysis['error_messages']:
        report_lines.extend([
            "Recent Error Messages:",
            "-" * 30
        ])
        for error in analysis['error_messages'][-5:]:  # Last 5 errors
            report_lines.append(f"  {error}")
        report_lines.append("")
    
    # Hourly statistics
    if analysis['hourly_stats']:
        report_lines.extend([
            "Hourly Activity:",
            "-" * 20
        ])
        sorted_hours = sorted(analysis['hourly_stats'].items())
        for hour, count in sorted_hours[-10:]:  # Last 10 hours
            report_lines.append(f"  {hour}:xx - {count} entries")
    
    # Save report
    report_content = "\\n".join(report_lines)
    sio.write_file("log_analysis_report.txt", report_content)
    
    # Save detailed data
    if analysis['unique_ips']:
        ip_list = "\\n".join(sorted(analysis['unique_ips']))
        sio.write_file("unique_ips.txt", ip_list)
    
    if analysis['error_messages']:
        error_log = "\\n".join(analysis['error_messages'])
        sio.write_file("all_errors.txt", error_log)
    
    print("\\n✅ Analysis complete!")
    print(f"Report saved to: log_analysis_report.txt")
    print(f"Total errors found: {analysis['error_count']}")
    print(f"Unique IPs: {len(analysis['unique_ips'])}")
    
    return analysis

# Create sample log files for demo
sample_logs = [
    "web_server.log",
    "application.log", 
    "database.log"
]

log_data = {
    "web_server.log": """2024-01-01 10:15:23 [INFO] 192.168.1.100 GET /index.html 200
2024-01-01 10:15:45 [ERROR] 192.168.1.101 POST /api/login 500 - Database connection failed
2024-01-01 10:16:12 [INFO] 192.168.1.102 GET /about.html 200
2024-01-01 10:16:34 [WARNING] 192.168.1.100 GET /slow-page.html 200 - Response time: 5.2s""",
    
    "application.log": """2024-01-01 10:15:00 [INFO] Application started
2024-01-01 10:15:30 [ERROR] Failed to load configuration: config.json not found
2024-01-01 10:15:35 [INFO] Using default configuration
2024-01-01 10:16:00 [WARNING] High memory usage: 85%""",
    
    "database.log": """2024-01-01 10:14:55 [INFO] Database connection established
2024-01-01 10:15:44 [ERROR] Query timeout: SELECT * FROM users WHERE active=1
2024-01-01 10:15:50 [INFO] Connection restored
2024-01-01 10:16:20 [ERROR] Deadlock detected in transaction"""
}

# Create log files
print("Creating sample log files...")
for filename, content in log_data.items():
    sio.write_file(filename, content)

# Run analysis
analysis_results = log_analyzer(sample_logs)

# Display report
print("\\n" + "="*50)
print("GENERATED REPORT:")
print("="*50)
report_content = sio.read_file("log_analysis_report.txt")
print(report_content)

# Clean up
cleanup_files = sample_logs + ["log_analysis_report.txt", "unique_ips.txt", "all_errors.txt"]
for filename in cleanup_files:
    if sio.file_exists(filename):
        sio.delete_file(filename)
```

### Example 2: Data Migration Tool

```python
import pyferris.simple_io as sio
import json
import csv
from io import StringIO

def data_migration_tool():
    """Migrate data between different formats."""
    
    print("=== Data Migration Tool ===")
    
    # Create sample CSV data
    csv_data = """name,age,city,salary
John Doe,30,New York,75000
Jane Smith,25,Los Angeles,65000
Bob Johnson,35,Chicago,80000
Alice Brown,28,Houston,70000
Charlie Wilson,32,Phoenix,72000"""
    
    sio.write_file("employees.csv", csv_data)
    print("✅ Created sample CSV file")
    
    # Read and parse CSV
    csv_content = sio.read_file("employees.csv")
    csv_reader = csv.DictReader(StringIO(csv_content))
    employees = list(csv_reader)
    
    print(f"📊 Loaded {len(employees)} employee records")
    
    # Convert to different formats
    formats = {
        'json': convert_to_json,
        'xml': convert_to_xml,
        'txt': convert_to_text,
        'summary': generate_summary
    }
    
    # Process in parallel (prepare data)
    conversion_data = []
    for format_name, converter in formats.items():
        filename = f"employees.{format_name}"
        content = converter(employees)
        conversion_data.append((filename, content))
    
    # Write all formats in parallel
    print("\\n🔄 Converting to multiple formats...")
    sio.write_files_parallel(conversion_data)
    
    # Verify conversions
    print("\\n✅ Conversion complete!")
    for filename, _ in conversion_data:
        size = sio.file_size(filename)
        print(f"  {filename}: {size} bytes")
    
    # Create migration report
    report = generate_migration_report(employees, conversion_data)
    sio.write_file("migration_report.txt", report)
    print("\\n📋 Migration report generated")
    
    # Display report
    print("\\n" + "="*40)
    print("MIGRATION REPORT:")
    print("="*40)
    print(sio.read_file("migration_report.txt"))
    
    # Clean up
    cleanup_files = ["employees.csv"] + [f for f, _ in conversion_data] + ["migration_report.txt"]
    for filename in cleanup_files:
        if sio.file_exists(filename):
            sio.delete_file(filename)
    
    print("\\n✅ Migration tool demo completed")

def convert_to_json(employees):
    """Convert employee data to JSON format."""
    return json.dumps(employees, indent=2)

def convert_to_xml(employees):
    """Convert employee data to XML format."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<employees>']
    
    for emp in employees:
        lines.append('  <employee>')
        for key, value in emp.items():
            lines.append(f'    <{key}>{value}</{key}>')
        lines.append('  </employee>')
    
    lines.append('</employees>')
    return '\\n'.join(lines)

def convert_to_text(employees):
    """Convert employee data to formatted text."""
    lines = ['Employee Directory', '=' * 50, '']
    
    for i, emp in enumerate(employees, 1):
        lines.extend([
            f"Employee #{i}:",
            f"  Name: {emp['name']}",
            f"  Age: {emp['age']}",
            f"  City: {emp['city']}",
            f"  Salary: ${emp['salary']}",
            ""
        ])
    
    return '\\n'.join(lines)

def generate_summary(employees):
    """Generate summary statistics."""
    total_employees = len(employees)
    total_salary = sum(int(emp['salary']) for emp in employees)
    avg_salary = total_salary // total_employees
    avg_age = sum(int(emp['age']) for emp in employees) // total_employees
    
    cities = {}
    for emp in employees:
        city = emp['city']
        cities[city] = cities.get(city, 0) + 1
    
    lines = [
        'Employee Summary Report',
        '=' * 30,
        f'Total Employees: {total_employees}',
        f'Average Age: {avg_age}',
        f'Average Salary: ${avg_salary:,}',
        f'Total Payroll: ${total_salary:,}',
        '',
        'Employees by City:',
        '-' * 20
    ]
    
    for city, count in sorted(cities.items()):
        lines.append(f'{city}: {count} employees')
    
    return '\\n'.join(lines)

def generate_migration_report(employees, conversion_data):
    """Generate migration report."""
    import time
    
    lines = [
        'Data Migration Report',
        '=' * 40,
        f'Migration Date: {time.strftime("%Y-%m-%d %H:%M:%S")}',
        f'Source Records: {len(employees)}',
        '',
        'Generated Files:',
        '-' * 20
    ]
    
    for filename, content in conversion_data:
        lines.append(f'{filename}: {len(content)} characters')
    
    lines.extend([
        '',
        'Migration Status: SUCCESS',
        'All formats generated successfully.',
        '',
        'Next Steps:',
        '1. Verify data integrity in target systems',
        '2. Test application compatibility',
        '3. Schedule production migration'
    ])
    
    return '\\n'.join(lines)

# Run the migration tool
data_migration_tool()
```

## Conclusion

Congratulations! You've completed the Pyferris IO tutorial. You now know how to:

✅ **Perform basic file I/O operations**  
✅ **Use file utilities for management tasks**  
✅ **Leverage object-oriented interfaces**  
✅ **Implement parallel processing for performance**  
✅ **Handle errors gracefully**  
✅ **Optimize for different scenarios**  
✅ **Build real-world applications**

## Next Steps

1. **Practice**: Try the exercises in your own projects
2. **Experiment**: Test different batch sizes for parallel operations
3. **Measure**: Profile your applications to find bottlenecks
4. **Explore**: Check out the advanced features (CSV, JSON) when they become available
5. **Contribute**: Share your use cases and optimizations with the community

## Quick Reference

```python
# Import
import pyferris.simple_io as sio
from pyferris import SimpleFileReader, SimpleFileWriter

# Basic operations  
sio.write_file("file.txt", "content")
content = sio.read_file("file.txt")

# Utilities
sio.file_exists("file.txt")
sio.file_size("file.txt")
sio.copy_file("src.txt", "dst.txt")

# Parallel operations
contents = sio.read_files_parallel(["f1.txt", "f2.txt"])
sio.write_files_parallel([("out1.txt", "content1"), ("out2.txt", "content2")])

# Object-oriented
reader = SimpleFileReader("input.txt")
content = reader.read_text()
lines = reader.read_lines()

writer = SimpleFileWriter("output.txt")
writer.write_text("content")
writer.append_text("more content")
```

Happy coding with Pyferris! 🚀
