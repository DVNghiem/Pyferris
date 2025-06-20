# Pipeline Processing

PyFerris provides a powerful pipeline processing system that allows you to chain multiple operations together for efficient data transformation. Pipelines enable you to build complex data processing workflows with excellent performance and clean, readable code.

## Overview

The pipeline system includes:
- **Pipeline** - Main pipeline class for sequential processing
- **Chain** - Lightweight chaining utility for function composition
- **pipeline_map** - Functional approach to pipeline processing

## Quick Start

```python
import pyferris

# Create a simple pipeline
pipeline = pyferris.Pipeline()
pipeline.add_stage(lambda x: [i * 2 for i in x])      # Double each number
pipeline.add_stage(lambda x: [i + 1 for i in x])      # Add 1 to each
pipeline.add_stage(lambda x: [i for i in x if i > 5]) # Filter > 5

# Execute the pipeline
data = [1, 2, 3, 4, 5]
result = pipeline.execute(data)
print(result)  # [7, 9, 11] (filtered results)

# Using Chain for function composition
chain = pyferris.Chain()
chain.add(lambda x: x * 2)
chain.add(lambda x: x + 1)
chain.add(lambda x: x ** 2)

result = chain.execute(10)  # ((10 * 2) + 1) ** 2 = 441
print(result)
```

## Core Components

### Pipeline Class

The main pipeline class for building multi-stage data processing workflows.

```python
from pyferris import Pipeline

# Create pipeline
pipeline = Pipeline()

# Add processing stages
pipeline.add_stage(lambda data: [x.upper() for x in data])  # Convert to uppercase
pipeline.add_stage(lambda data: [x + "!" for x in data])    # Add exclamation
pipeline.add_stage(lambda data: sorted(data))               # Sort results

# Execute
words = ["hello", "world", "python"]
result = pipeline.execute(words)
print(result)  # ['HELLO!', 'PYTHON!', 'WORLD!']
```

### Chain Class

Lightweight function composition utility for single-value transformations.

```python
from pyferris import Chain

# Create transformation chain
transform = Chain()
transform.add(str.strip)           # Remove whitespace
transform.add(str.lower)           # Convert to lowercase  
transform.add(lambda x: x[::-1])   # Reverse string

# Apply transformation
result = transform.execute("  Hello World  ")
print(result)  # "dlrow olleh"
```

### pipeline_map Function

Functional programming approach for applying pipelines to data collections.

```python
from pyferris import pipeline_map

# Define transformation steps
steps = [
    lambda x: x * 2,      # Double
    lambda x: x + 10,     # Add 10
    lambda x: x // 3      # Integer division by 3
]

# Apply to list of numbers
numbers = [1, 2, 3, 4, 5]
result = pipeline_map(steps, numbers)
print(result)  # [4, 4, 5, 6, 6]
```

## Advanced Usage

### Complex Data Processing

```python
import pyferris

# Multi-stage data cleaning and transformation
data_pipeline = pyferris.Pipeline()

# Stage 1: Data validation
def validate_data(records):
    return [r for r in records if r.get('age', 0) > 0 and r.get('name')]

# Stage 2: Data normalization  
def normalize_data(records):
    for record in records:
        record['name'] = record['name'].strip().title()
        record['age'] = int(record['age'])
    return records

# Stage 3: Data enrichment
def enrich_data(records):
    for record in records:
        record['category'] = 'adult' if record['age'] >= 18 else 'minor'
        record['name_length'] = len(record['name'])
    return records

# Stage 4: Data filtering
def filter_data(records):
    return [r for r in records if r['category'] == 'adult']

# Build pipeline
data_pipeline.add_stage(validate_data)
data_pipeline.add_stage(normalize_data)
data_pipeline.add_stage(enrich_data)
data_pipeline.add_stage(filter_data)

# Sample data
raw_data = [
    {'name': '  john doe  ', 'age': '25'},
    {'name': 'jane smith', 'age': '17'},
    {'name': '  bob wilson  ', 'age': '30'},
    {'name': '', 'age': '22'},  # Invalid - no name
]

# Process data
clean_data = data_pipeline.execute(raw_data)
print(clean_data)
# [{'name': 'John Doe', 'age': 25, 'category': 'adult', 'name_length': 8},
#  {'name': 'Bob Wilson', 'age': 30, 'category': 'adult', 'name_length': 10}]
```

### Parallel Processing Integration

```python
import pyferris

# Pipeline with parallel operations
parallel_pipeline = pyferris.Pipeline()

# Stage 1: Parallel computation
def parallel_compute(data):
    return pyferris.parallel_map(lambda x: x ** 2 + x, data)

# Stage 2: Parallel filtering
def parallel_filter_stage(data):
    return pyferris.parallel_filter(lambda x: x > 10, data)

# Stage 3: Parallel transformation
def parallel_transform(data):
    return pyferris.parallel_map(lambda x: f"result_{x}", data)

parallel_pipeline.add_stage(parallel_compute)
parallel_pipeline.add_stage(parallel_filter_stage)
parallel_pipeline.add_stage(parallel_transform)

# Execute with large dataset
large_data = list(range(1000))
results = parallel_pipeline.execute(large_data)
print(f"Processed {len(results)} items")
```

### Error Handling in Pipelines

```python
import pyferris

def safe_divide(data):
    """Stage that safely handles division errors"""
    results = []
    for item in data:
        try:
            results.append(item['value'] / item['divisor'])
        except (ZeroDivisionError, KeyError):
            results.append(None)  # Handle errors gracefully
    return results

def filter_valid(data):
    """Remove None values from previous stage"""
    return [x for x in data if x is not None]

# Pipeline with error handling
safe_pipeline = pyferris.Pipeline()
safe_pipeline.add_stage(safe_divide)
safe_pipeline.add_stage(filter_valid)

# Data with potential errors
risky_data = [
    {'value': 10, 'divisor': 2},   # Valid
    {'value': 15, 'divisor': 0},   # Division by zero
    {'value': 20},                 # Missing 'divisor' key
    {'value': 12, 'divisor': 3},   # Valid
]

results = safe_pipeline.execute(risky_data)
print(results)  # [5.0, 4.0] - Only valid results
```

## Performance Optimization

### Stage Optimization

```python
import pyferris

# Efficient pipeline design
efficient_pipeline = pyferris.Pipeline()

# Combine related operations in single stages
def combined_string_ops(texts):
    """Combine multiple string operations for efficiency"""
    return [text.strip().lower().replace(' ', '_') for text in texts]

# Use list comprehensions for better performance
def efficient_filter_map(numbers):
    """Combined filter and map operation"""
    return [x * 2 for x in numbers if x % 2 == 0]

efficient_pipeline.add_stage(combined_string_ops)
efficient_pipeline.add_stage(efficient_filter_map)
```

### Memory Management

```python
import pyferris

# Memory-efficient pipeline for large datasets
def chunked_processing(data, chunk_size=1000):
    """Process data in chunks to manage memory usage"""
    pipeline = pyferris.Pipeline()
    pipeline.add_stage(lambda chunk: [x * 2 for x in chunk])
    pipeline.add_stage(lambda chunk: [x for x in chunk if x > 100])
    
    results = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        chunk_result = pipeline.execute(chunk)
        results.extend(chunk_result)
    
    return results

# Process large dataset efficiently
large_dataset = list(range(100000))
processed = chunked_processing(large_dataset)
print(f"Processed {len(processed)} items from {len(large_dataset)} total")
```

## Real-World Examples

### Data Analysis Pipeline

```python
import pyferris
import json

# Data analysis pipeline
analysis_pipeline = pyferris.Pipeline()

# Stage 1: Parse JSON data
def parse_json_stage(raw_data):
    return [json.loads(line) for line in raw_data if line.strip()]

# Stage 2: Extract relevant fields
def extract_fields(records):
    return [{
        'user_id': r.get('user_id'),
        'action': r.get('action'),
        'timestamp': r.get('timestamp'),
        'value': float(r.get('value', 0))
    } for r in records]

# Stage 3: Aggregate by user
def aggregate_by_user(records):
    user_stats = {}
    for record in records:
        user_id = record['user_id']
        if user_id not in user_stats:
            user_stats[user_id] = {'total_value': 0, 'action_count': 0}
        user_stats[user_id]['total_value'] += record['value']
        user_stats[user_id]['action_count'] += 1
    return user_stats

# Stage 4: Generate insights
def generate_insights(user_stats):
    insights = []
    for user_id, stats in user_stats.items():
        avg_value = stats['total_value'] / stats['action_count']
        insights.append({
            'user_id': user_id,
            'avg_value': avg_value,
            'total_actions': stats['action_count'],
            'category': 'high_value' if avg_value > 100 else 'low_value'
        })
    return sorted(insights, key=lambda x: x['avg_value'], reverse=True)

# Build analysis pipeline
analysis_pipeline.add_stage(parse_json_stage)
analysis_pipeline.add_stage(extract_fields)
analysis_pipeline.add_stage(aggregate_by_user)
analysis_pipeline.add_stage(generate_insights)

# Sample log data
log_data = [
    '{"user_id": "user1", "action": "purchase", "timestamp": 1234567890, "value": 150}',
    '{"user_id": "user2", "action": "view", "timestamp": 1234567891, "value": 0}',
    '{"user_id": "user1", "action": "purchase", "timestamp": 1234567892, "value": 200}',
    '{"user_id": "user3", "action": "purchase", "timestamp": 1234567893, "value": 75}',
]

insights = analysis_pipeline.execute(log_data)
print("User insights:", insights)
```

### Image Processing Pipeline

```python
import pyferris

# Image processing pipeline (conceptual example)
image_pipeline = pyferris.Pipeline()

def load_images(file_paths):
    """Load images from file paths"""
    # Placeholder for image loading logic
    return [{'path': path, 'data': f"image_data_{i}"} for i, path in enumerate(file_paths)]

def resize_images(images):
    """Resize images to standard dimensions"""
    for img in images:
        img['resized'] = True
        img['dimensions'] = (224, 224)
    return images

def apply_filters(images):
    """Apply image filters"""
    for img in images:
        img['filtered'] = True
        img['filters_applied'] = ['blur', 'sharpen']
    return images

def extract_features(images):
    """Extract features from processed images"""
    features = []
    for img in images:
        features.append({
            'path': img['path'],
            'feature_vector': [0.1, 0.2, 0.3, 0.4, 0.5],  # Placeholder
            'confidence': 0.95
        })
    return features

# Build image processing pipeline
image_pipeline.add_stage(load_images)
image_pipeline.add_stage(resize_images)
image_pipeline.add_stage(apply_filters)
image_pipeline.add_stage(extract_features)

# Process images
image_paths = ['img1.jpg', 'img2.jpg', 'img3.jpg']
features = image_pipeline.execute(image_paths)
print(f"Extracted features from {len(features)} images")
```

## Integration with Other Features

### With Shared Memory Arrays

```python
import pyferris

# Pipeline using shared memory arrays
shared_pipeline = pyferris.Pipeline()

def create_shared_stage(data):
    """Convert to shared array for efficient processing"""
    return pyferris.create_shared_array(data)

def parallel_process_stage(shared_array):
    """Use parallel processing on shared array"""
    return shared_array.parallel_map(lambda x: x * x + 1)

def aggregate_stage(processed_data):
    """Aggregate results"""
    return {
        'sum': sum(processed_data),
        'avg': sum(processed_data) / len(processed_data),
        'max': max(processed_data),
        'min': min(processed_data)
    }

shared_pipeline.add_stage(create_shared_stage)
shared_pipeline.add_stage(parallel_process_stage)  
shared_pipeline.add_stage(aggregate_stage)

# Execute with numeric data
numbers = list(range(1000))
stats = shared_pipeline.execute(numbers)
print("Statistics:", stats)
```

### With Async Processing

```python
import pyferris
import asyncio

# Async-compatible pipeline stages
async def async_fetch_stage(urls):
    """Asynchronously fetch data from URLs"""
    # Placeholder for async HTTP requests
    await asyncio.sleep(0.1)  # Simulate async operation
    return [f"data_from_{url}" for url in urls]

async def async_process_stage(data):
    """Asynchronously process fetched data"""
    await asyncio.sleep(0.1)  # Simulate async processing
    return [item.upper() + "_PROCESSED" for item in data]

async def run_async_pipeline():
    """Run pipeline with async stages"""
    urls = ["url1", "url2", "url3"]
    
    # Fetch data
    data = await async_fetch_stage(urls)
    
    # Process data
    processed = await async_process_stage(data)
    
    # Use regular pipeline for final stages
    final_pipeline = pyferris.Pipeline()
    final_pipeline.add_stage(lambda x: [item.replace("_", " ") for item in x])
    final_pipeline.add_stage(lambda x: sorted(x))
    
    return final_pipeline.execute(processed)

# Run async pipeline
# result = asyncio.run(run_async_pipeline())
```

## Best Practices

### Pipeline Design

1. **Keep stages focused** - Each stage should have a single responsibility
2. **Minimize data copying** - Pass references when possible
3. **Handle errors gracefully** - Use try-catch in stages for robust pipelines
4. **Document stage purposes** - Clear stage names and documentation

```python
# Good pipeline design
pipeline = pyferris.Pipeline()
pipeline.add_stage(validate_input_data)    # Clear purpose
pipeline.add_stage(normalize_formats)      # Single responsibility  
pipeline.add_stage(enrich_with_metadata)   # Focused functionality
pipeline.add_stage(filter_valid_records)   # Error handling built-in
```

### Performance Guidelines

1. **Combine related operations** in single stages
2. **Use parallel operations** for CPU-intensive tasks
3. **Process in chunks** for large datasets
4. **Profile bottlenecks** and optimize critical stages

### Error Recovery

```python
import pyferris

def resilient_stage(data):
    """Stage with built-in error recovery"""
    results = []
    errors = []
    
    for item in data:
        try:
            # Process item
            result = complex_operation(item)
            results.append(result)
        except Exception as e:
            errors.append({'item': item, 'error': str(e)})
            # Continue processing other items
    
    # Log errors but don't fail the pipeline
    if errors:
        print(f"Encountered {len(errors)} errors during processing")
    
    return results

def complex_operation(item):
    # Placeholder for complex operation that might fail
    if item < 0:
        raise ValueError("Negative values not supported")
    return item * 2
```

## API Reference

### Pipeline Class

```python
class Pipeline:
    def __init__(self)
    def add_stage(self, func: Callable) -> None
    def execute(self, data: Any) -> Any
    def clear(self) -> None
```

### Chain Class

```python
class Chain:
    def __init__(self)
    def add(self, func: Callable) -> None
    def execute(self, value: Any) -> Any
    def clear(self) -> None
```

### Functions

```python
def pipeline_map(stages: List[Callable], data: List[Any]) -> List[Any]
```

This comprehensive pipeline documentation shows how to build efficient, maintainable data processing workflows with PyFerris.
