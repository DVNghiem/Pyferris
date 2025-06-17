# PyFerris Examples

This document provides comprehensive examples demonstrating PyFerris features across core operations, executor functionality, and I/O operations.

## Table of Contents

1. [Core Operations Examples](#core-operations-examples)
2. [Executor Examples](#executor-examples) 
3. [I/O Operations Examples](#io-operations-examples)
4. [Real-World Use Cases](#real-world-use-cases)
5. [Performance Comparisons](#performance-comparisons)

## Core Operations Examples

### Basic Parallel Operations

```python
from pyferris import parallel_map, parallel_filter, parallel_reduce, parallel_starmap
import time
import math

# Example 1: Parallel Map - CPU-intensive calculations
def complex_calculation(n):
    """Simulate complex mathematical operation."""
    result = 0
    for i in range(n * 1000):
        result += math.sin(i) * math.cos(i)
    return result

# Process 100 complex calculations in parallel
numbers = range(1, 101)
start_time = time.time()
results = parallel_map(complex_calculation, numbers)
parallel_time = time.time() - start_time

print(f"Parallel processing: {parallel_time:.2f}s")
print(f"First 10 results: {list(results)[:10]}")

# Example 2: Parallel Filter - Finding specific patterns
def is_perfect_number(n):
    """Check if a number is perfect (sum of divisors equals the number)."""
    if n < 2:
        return False
    
    divisors_sum = 1  # 1 is always a divisor
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            divisors_sum += i
            if i != n // i:  # Avoid counting square root twice
                divisors_sum += n // i
    
    return divisors_sum == n

# Find perfect numbers up to 10000
numbers = range(1, 10001)
perfect_numbers = parallel_filter(is_perfect_number, numbers)
print(f"Perfect numbers: {perfect_numbers}")

# Example 3: Parallel Starmap - Multiple argument functions
def distance_3d(point1, point2):
    """Calculate 3D distance between two points."""
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    return math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

# Calculate distances between pairs of 3D points
point_pairs = [
    ((0, 0, 0), (1, 1, 1)),
    ((1, 2, 3), (4, 5, 6)),
    ((10, 20, 30), (40, 50, 60)),
]
distances = parallel_starmap(distance_3d, point_pairs)
print(f"3D distances: {distances}")

# Example 4: Parallel Reduce - Statistical calculations
def variance_reducer(acc, value):
    """Accumulator for variance calculation."""
    if acc is None:
        return {'sum': value, 'sum_sq': value**2, 'count': 1}
    
    return {
        'sum': acc['sum'] + value,
        'sum_sq': acc['sum_sq'] + value**2,
        'count': acc['count'] + 1
    }

# Calculate variance of large dataset
import random
data = [random.gauss(100, 15) for _ in range(100000)]

variance_data = parallel_reduce(variance_reducer, data)
mean = variance_data['sum'] / variance_data['count']
variance = (variance_data['sum_sq'] / variance_data['count']) - mean**2

print(f"Dataset statistics:")
print(f"  Count: {variance_data['count']}")
print(f"  Mean: {mean:.2f}")
print(f"  Variance: {variance:.2f}")
print(f"  Standard deviation: {math.sqrt(variance):.2f}")
```

### Advanced Core Operations

```python
# Chaining operations for data pipeline
def data_processing_pipeline():
    """Demonstrate chaining parallel operations."""
    
    # Step 1: Generate synthetic data
    def generate_data_point(i):
        import random
        return {
            'id': i,
            'value': random.uniform(0, 100),
            'category': random.choice(['A', 'B', 'C']),
            'valid': random.choice([True, False])
        }
    
    # Generate 10000 data points
    raw_data = parallel_map(generate_data_point, range(10000))
    
    # Step 2: Filter valid data points
    def is_valid_point(point):
        return point['valid'] and point['value'] > 10
    
    valid_data = parallel_filter(is_valid_point, raw_data)
    print(f"Valid data points: {len(valid_data)}")
    
    # Step 3: Transform data
    def transform_point(point):
        point['normalized_value'] = point['value'] / 100.0
        point['squared_value'] = point['value'] ** 2
        return point
    
    transformed_data = parallel_map(transform_point, valid_data)
    
    # Step 4: Aggregate by category
    def category_aggregator(acc, point):
        if acc is None:
            acc = {}
        
        category = point['category']
        if category not in acc:
            acc[category] = {'sum': 0, 'count': 0, 'sum_squares': 0}
        
        acc[category]['sum'] += point['value']
        acc[category]['count'] += 1
        acc[category]['sum_squares'] += point['squared_value']
        
        return acc
    
    category_stats = parallel_reduce(category_aggregator, transformed_data)
    
    # Calculate final statistics
    for category, stats in category_stats.items():
        mean = stats['sum'] / stats['count']
        variance = (stats['sum_squares'] / stats['count']) - mean**2
        print(f"Category {category}:")
        print(f"  Count: {stats['count']}")
        print(f"  Mean: {mean:.2f}")
        print(f"  Std Dev: {math.sqrt(variance):.2f}")

data_processing_pipeline()
```

## Executor Examples

### Basic Task Management

```python
from pyferris import Executor
import time
import random

# Example 1: Basic task submission and result collection
def simulate_work(task_id, duration):
    """Simulate work that takes variable time."""
    time.sleep(duration)
    return f"Task {task_id} completed in {duration:.2f}s"

def basic_executor_example():
    with Executor(max_workers=4) as executor:
        # Submit tasks with different durations
        futures = []
        for i in range(10):
            duration = random.uniform(0.1, 2.0)
            future = executor.submit(simulate_work, i, duration)
            futures.append((future, i, duration))
        
        # Collect results as they complete
        print("Tasks completed:")
        for future, task_id, expected_duration in futures:
            result = future.result()
            print(f"  {result}")

basic_executor_example()

# Example 2: Batch processing with executor
def batch_processing_example():
    """Process large dataset in batches using executor."""
    
    def process_batch(batch_id, data_batch):
        """Process a batch of data."""
        # Simulate processing time
        processing_time = len(data_batch) * 0.001
        time.sleep(processing_time)
        
        # Calculate batch statistics
        batch_sum = sum(data_batch)
        batch_mean = batch_sum / len(data_batch)
        
        return {
            'batch_id': batch_id,
            'size': len(data_batch),
            'sum': batch_sum,
            'mean': batch_mean,
            'processing_time': processing_time
        }
    
    # Generate large dataset
    dataset = list(range(100000))
    batch_size = 5000
    
    # Create batches
    batches = []
    for i in range(0, len(dataset), batch_size):
        batch = dataset[i:i + batch_size]
        batches.append((i // batch_size, batch))
    
    # Process batches in parallel
    with Executor(max_workers=8) as executor:
        futures = [executor.submit(process_batch, batch_id, batch) 
                  for batch_id, batch in batches]
        
        results = [future.result() for future in futures]
    
    # Aggregate results
    total_sum = sum(r['sum'] for r in results)
    total_size = sum(r['size'] for r in results)
    total_time = sum(r['processing_time'] for r in results)
    
    print(f"Batch processing results:")
    print(f"  Batches processed: {len(results)}")
    print(f"  Total items: {total_size}")
    print(f"  Dataset sum: {total_sum}")
    print(f"  Average: {total_sum / total_size:.2f}")
    print(f"  Total processing time: {total_time:.2f}s")

batch_processing_example()
```

### Advanced Executor Usage

```python
# Example 3: Priority-based task execution
from pyferris import Executor
import heapq
import threading
import time

class PriorityExecutor:
    """Executor wrapper that supports task priorities."""
    
    def __init__(self, max_workers=4):
        self.executor = Executor(max_workers=max_workers)
        self.priority_queue = []
        self.queue_lock = threading.Lock()
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler)
        self.scheduler_thread.start()
    
    def submit_priority(self, priority, func, *args, **kwargs):
        """Submit task with priority (lower number = higher priority)."""
        future = self.executor.submit(func, *args, **kwargs)
        
        with self.queue_lock:
            heapq.heappush(self.priority_queue, (priority, time.time(), future))
        
        return future
    
    def _scheduler(self):
        """Background scheduler for priority tasks."""
        while self.running:
            with self.queue_lock:
                if self.priority_queue:
                    priority, timestamp, future = heapq.heappop(self.priority_queue)
                    # In real implementation, you'd reschedule based on priority
            time.sleep(0.1)
    
    def shutdown(self):
        self.running = False
        self.scheduler_thread.join()
        self.executor.shutdown()

def priority_task_example():
    """Demonstrate priority-based task execution."""
    
    def important_task(task_id):
        time.sleep(0.5)
        return f"Important task {task_id} completed"
    
    def normal_task(task_id):
        time.sleep(1.0)
        return f"Normal task {task_id} completed"
    
    def background_task(task_id):
        time.sleep(2.0)
        return f"Background task {task_id} completed"
    
    priority_executor = PriorityExecutor(max_workers=2)
    
    try:
        # Submit tasks with different priorities
        futures = []
        
        # Low priority (background tasks)
        for i in range(3):
            future = priority_executor.submit_priority(3, background_task, i)
            futures.append(('background', future))
        
        # Normal priority
        for i in range(3):
            future = priority_executor.submit_priority(2, normal_task, i)
            futures.append(('normal', future))
        
        # High priority (should execute first)
        for i in range(3):
            future = priority_executor.submit_priority(1, important_task, i)
            futures.append(('important', future))
        
        # Collect results
        print("Task execution order:")
        for task_type, future in futures:
            result = future.result()
            print(f"  {task_type}: {result}")
    
    finally:
        priority_executor.shutdown()

priority_task_example()
```

## I/O Operations Examples

### File Processing Examples

```python
from pyferris.io import simple_io, csv, json
from pyferris.io.parallel_io import ParallelFileProcessor
import os
import tempfile

# Example 1: Text file processing
def text_processing_example():
    """Demonstrate text file processing capabilities."""
    
    # Create sample text files
    sample_texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Python is a high-level programming language.",
        "Machine learning algorithms process large datasets.",
        "PyFerris provides high-performance parallel processing.",
    ]
    
    # Write sample files
    file_paths = []
    for i, text in enumerate(sample_texts):
        file_path = f"sample_{i}.txt"
        simple_io.write_file(file_path, text * 100)  # Make files larger
        file_paths.append(file_path)
    
    # Read files in parallel
    contents = simple_io.read_files_parallel(file_paths)
    
    # Process text files
    def analyze_text(content):
        words = content.split()
        return {
            'word_count': len(words),
            'char_count': len(content),
            'unique_words': len(set(words)),
            'avg_word_length': sum(len(word) for word in words) / len(words)
        }
    
    # Analyze each file
    analyses = [analyze_text(content) for content in contents]
    
    # Print results
    for i, analysis in enumerate(analyses):
        print(f"File {i} analysis:")
        for key, value in analysis.items():
            print(f"  {key}: {value:.2f}")
    
    # Cleanup
    for file_path in file_paths:
        simple_io.delete_file(file_path)

text_processing_example()

# Example 2: CSV data processing
def csv_processing_example():
    """Demonstrate CSV processing with real-world-like data."""
    
    # Generate sample CSV data
    import random
    from datetime import datetime, timedelta
    
    # Create employee data
    departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance']
    positions = ['Junior', 'Senior', 'Lead', 'Manager', 'Director']
    
    employees = []
    for i in range(1000):
        employee = {
            'id': i + 1,
            'name': f'Employee_{i+1}',
            'department': random.choice(departments),
            'position': random.choice(positions),
            'salary': random.randint(40000, 150000),
            'hire_date': (datetime.now() - timedelta(days=random.randint(0, 3650))).strftime('%Y-%m-%d'),
            'performance_score': random.uniform(1.0, 5.0)
        }
        employees.append(employee)
    
    # Write CSV file
    csv.write_csv('employees.csv', employees)
    print(f"Created CSV file with {len(employees)} employees")
    
    # Read and analyze CSV data
    employee_data = csv.read_csv('employees.csv')
    
    # Department analysis
    dept_analysis = {}
    for emp in employee_data:
        dept = emp['department']
        if dept not in dept_analysis:
            dept_analysis[dept] = {
                'count': 0,
                'total_salary': 0,
                'total_performance': 0
            }
        
        dept_analysis[dept]['count'] += 1
        dept_analysis[dept]['total_salary'] += float(emp['salary'])
        dept_analysis[dept]['total_performance'] += float(emp['performance_score'])
    
    # Calculate averages and write summary
    summary_data = []
    for dept, stats in dept_analysis.items():
        summary = {
            'department': dept,
            'employee_count': stats['count'],
            'avg_salary': stats['total_salary'] / stats['count'],
            'avg_performance': stats['total_performance'] / stats['count']
        }
        summary_data.append(summary)
    
    csv.write_csv('department_summary.csv', summary_data)
    
    print("Department Analysis:")
    for summary in summary_data:
        print(f"  {summary['department']}:")
        print(f"    Employees: {summary['employee_count']}")
        print(f"    Avg Salary: ${summary['avg_salary']:,.2f}")
        print(f"    Avg Performance: {summary['avg_performance']:.2f}")
    
    # Cleanup
    simple_io.delete_file('employees.csv')
    simple_io.delete_file('department_summary.csv')

csv_processing_example()

# Example 3: JSON processing for log analysis
def json_log_processing_example():
    """Demonstrate JSON log processing."""
    
    import random
    from datetime import datetime, timedelta
    
    # Generate sample log entries
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    services = ['auth', 'api', 'database', 'cache', 'frontend']
    
    log_entries = []
    start_time = datetime.now() - timedelta(hours=24)
    
    for i in range(10000):
        entry = {
            'timestamp': (start_time + timedelta(seconds=i*8.64)).isoformat(),
            'level': random.choice(log_levels),
            'service': random.choice(services),
            'message': f'Log message {i}',
            'request_id': f'req_{random.randint(1000, 9999)}',
            'response_time': random.uniform(0.1, 5.0),
            'status_code': random.choice([200, 201, 400, 404, 500])
        }
        log_entries.append(entry)
    
    # Write JSON Lines log file
    json.write_jsonl('application.log.jsonl', log_entries)
    print(f"Created log file with {len(log_entries)} entries")
    
    # Analyze logs
    log_data = json.read_jsonl('application.log.jsonl')
    
    # Analyze by service and level
    analysis = {}
    for entry in log_data:
        service = entry['service']
        level = entry['level']
        
        if service not in analysis:
            analysis[service] = {}
        if level not in analysis[service]:
            analysis[service][level] = {
                'count': 0,
                'total_response_time': 0,
                'error_codes': []
            }
        
        analysis[service][level]['count'] += 1
        analysis[service][level]['total_response_time'] += entry['response_time']
        
        if entry['status_code'] >= 400:
            analysis[service][level]['error_codes'].append(entry['status_code'])
    
    # Generate analysis report
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'total_entries': len(log_data),
        'services': {}
    }
    
    for service, levels in analysis.items():
        service_summary = {
            'total_entries': sum(level_data['count'] for level_data in levels.values()),
            'levels': {}
        }
        
        for level, level_data in levels.items():
            avg_response_time = level_data['total_response_time'] / level_data['count']
            service_summary['levels'][level] = {
                'count': level_data['count'],
                'avg_response_time': avg_response_time,
                'error_count': len(level_data['error_codes'])
            }
        
        report['services'][service] = service_summary
    
    # Write analysis report
    json.write_json('log_analysis_report.json', report, pretty_print=True)
    
    print("Log Analysis Summary:")
    for service, summary in report['services'].items():
        print(f"  {service}: {summary['total_entries']} entries")
        for level, level_stats in summary['levels'].items():
            print(f"    {level}: {level_stats['count']} entries, "
                  f"avg response: {level_stats['avg_response_time']:.3f}s")
    
    # Cleanup
    simple_io.delete_file('application.log.jsonl')
    simple_io.delete_file('log_analysis_report.json')

json_log_processing_example()
```

### Parallel File Processing

```python
# Example 4: Large-scale parallel file processing
def parallel_file_processing_example():
    """Demonstrate large-scale parallel file processing."""
    
    # Create multiple data files
    file_count = 50
    file_paths = []
    
    print(f"Creating {file_count} sample data files...")
    
    for i in range(file_count):
        # Generate sample data for each file
        data = []
        for j in range(1000):  # 1000 records per file
            record = {
                'id': i * 1000 + j,
                'value': random.uniform(0, 1000),
                'category': random.choice(['A', 'B', 'C', 'D']),
                'timestamp': datetime.now().isoformat()
            }
            data.append(record)
        
        file_path = f'data_file_{i:03d}.json'
        json.write_json(file_path, data)
        file_paths.append(file_path)
    
    print(f"Created {len(file_paths)} data files")
    
    # Process files in parallel
    def analyze_data_file(file_path, content):
        """Analyze a single data file."""
        data = json.parse_json(content)
        
        # Calculate statistics
        values = [record['value'] for record in data]
        categories = {}
        
        for record in data:
            cat = record['category']
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        return {
            'file': file_path,
            'record_count': len(data),
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': sum(values) / len(values),
            'categories': categories
        }
    
    # Use parallel file processor
    processor = ParallelFileProcessor(max_workers=8)
    
    start_time = time.time()
    analysis_results = processor.process_files(file_paths, analyze_data_file)
    processing_time = time.time() - start_time
    
    print(f"Processed {len(analysis_results)} files in {processing_time:.2f}s")
    
    # Aggregate results
    total_records = sum(r['record_count'] for r in analysis_results)
    all_values = []
    all_categories = {}
    
    for result in analysis_results:
        # Collect all values for overall statistics
        # Note: In practice, you'd use the individual file statistics
        for cat, count in result['categories'].items():
            if cat not in all_categories:
                all_categories[cat] = 0
            all_categories[cat] += count
    
    print(f"\nAggregate Analysis:")
    print(f"  Total records processed: {total_records}")
    print(f"  Category distribution:")
    for cat, count in all_categories.items():
        percentage = (count / total_records) * 100
        print(f"    {cat}: {count} ({percentage:.1f}%)")
    
    # Write summary report
    summary_report = {
        'processing_timestamp': datetime.now().isoformat(),
        'files_processed': len(analysis_results),
        'total_records': total_records,
        'processing_time_seconds': processing_time,
        'category_distribution': all_categories,
        'file_details': analysis_results
    }
    
    json.write_json('processing_summary.json', summary_report, pretty_print=True)
    print(f"Summary report written to 'processing_summary.json'")
    
    # Cleanup data files
    for file_path in file_paths:
        simple_io.delete_file(file_path)
    simple_io.delete_file('processing_summary.json')
    
    print("Cleanup completed")

parallel_file_processing_example()
```

## Real-World Use Cases

### Data Science Pipeline

```python
def data_science_pipeline_example():
    """Complete data science pipeline using PyFerris."""
    
    print("=== Data Science Pipeline Example ===")
    
    # Step 1: Data Generation (simulating data collection)
    def generate_sensor_data(sensor_id):
        """Generate sensor data for one sensor."""
        import random
        from datetime import datetime, timedelta
        
        data_points = []
        start_time = datetime.now() - timedelta(hours=24)
        
        for i in range(1440):  # One reading per minute for 24 hours
            timestamp = start_time + timedelta(minutes=i)
            
            # Simulate sensor readings with some noise
            base_temp = 20 + 10 * math.sin(i * math.pi / 720)  # Daily temperature cycle
            temperature = base_temp + random.gauss(0, 2)
            
            humidity = 50 + 20 * math.sin(i * math.pi / 720 + math.pi/4) + random.gauss(0, 5)
            pressure = 1013 + random.gauss(0, 10)
            
            data_points.append({
                'sensor_id': sensor_id,
                'timestamp': timestamp.isoformat(),
                'temperature': round(temperature, 2),
                'humidity': max(0, min(100, round(humidity, 2))),
                'pressure': round(pressure, 2)
            })
        
        return data_points
    
    # Generate data for 100 sensors in parallel
    sensor_ids = list(range(1, 101))
    print("Generating sensor data...")
    all_sensor_data = parallel_map(generate_sensor_data, sensor_ids)
    
    # Flatten the data
    all_data = []
    for sensor_data in all_sensor_data:
        all_data.extend(sensor_data)
    
    print(f"Generated {len(all_data)} data points from {len(sensor_ids)} sensors")
    
    # Step 2: Data Validation (parallel filtering)
    def is_valid_reading(reading):
        """Validate sensor reading."""
        return (
            -50 <= reading['temperature'] <= 100 and
            0 <= reading['humidity'] <= 100 and
            900 <= reading['pressure'] <= 1100
        )
    
    print("Validating data...")
    valid_data = parallel_filter(is_valid_reading, all_data)
    print(f"Valid readings: {len(valid_data)} ({len(valid_data)/len(all_data)*100:.1f}%)")
    
    # Step 3: Feature Engineering (parallel transformation)
    def add_features(reading):
        """Add computed features to reading."""
        # Calculate heat index (simplified formula)
        temp_f = reading['temperature'] * 9/5 + 32
        humidity = reading['humidity']
        
        if temp_f >= 80:
            heat_index = temp_f + humidity * 0.1
        else:
            heat_index = temp_f
        
        reading['heat_index'] = round(heat_index, 2)
        reading['comfort_score'] = round(
            100 - abs(reading['temperature'] - 22) * 2 - abs(reading['humidity'] - 45), 2
        )
        
        return reading
    
    print("Engineering features...")
    featured_data = parallel_map(add_features, valid_data)
    
    # Step 4: Data Aggregation (parallel reduce by sensor)
    def group_by_sensor(data):
        """Group data by sensor for aggregation."""
        sensor_groups = {}
        for reading in data:
            sensor_id = reading['sensor_id']
            if sensor_id not in sensor_groups:
                sensor_groups[sensor_id] = []
            sensor_groups[sensor_id].append(reading)
        return sensor_groups
    
    sensor_groups = group_by_sensor(featured_data)
    
    def calculate_sensor_stats(sensor_data):
        """Calculate statistics for one sensor."""
        sensor_id, readings = sensor_data
        
        temperatures = [r['temperature'] for r in readings]
        humidities = [r['humidity'] for r in readings]
        pressures = [r['pressure'] for r in readings]
        comfort_scores = [r['comfort_score'] for r in readings]
        
        return {
            'sensor_id': sensor_id,
            'reading_count': len(readings),
            'avg_temperature': sum(temperatures) / len(temperatures),
            'min_temperature': min(temperatures),
            'max_temperature': max(temperatures),
            'avg_humidity': sum(humidities) / len(humidities),
            'avg_pressure': sum(pressures) / len(pressures),
            'avg_comfort_score': sum(comfort_scores) / len(comfort_scores),
            'temperature_std': math.sqrt(
                sum((t - sum(temperatures)/len(temperatures))**2 for t in temperatures) / len(temperatures)
            )
        }
    
    print("Calculating sensor statistics...")
    sensor_stats = parallel_map(calculate_sensor_stats, list(sensor_groups.items()))
    
    # Step 5: Results Analysis and Reporting
    overall_stats = {
        'total_sensors': len(sensor_stats),
        'total_readings': sum(s['reading_count'] for s in sensor_stats),
        'avg_temperature_all': sum(s['avg_temperature'] for s in sensor_stats) / len(sensor_stats),
        'avg_comfort_all': sum(s['avg_comfort_score'] for s in sensor_stats) / len(sensor_stats)
    }
    
    # Find sensors with anomalies
    avg_temp_overall = overall_stats['avg_temperature_all']
    anomalous_sensors = [
        s for s in sensor_stats 
        if abs(s['avg_temperature'] - avg_temp_overall) > 5 or s['temperature_std'] > 10
    ]
    
    print("\n=== Pipeline Results ===")
    print(f"Processed {overall_stats['total_readings']} readings from {overall_stats['total_sensors']} sensors")
    print(f"Average temperature across all sensors: {overall_stats['avg_temperature_all']:.2f}°C")
    print(f"Average comfort score: {overall_stats['avg_comfort_all']:.2f}")
    print(f"Anomalous sensors detected: {len(anomalous_sensors)}")
    
    if anomalous_sensors:
        print("Sensors requiring attention:")
        for sensor in anomalous_sensors[:5]:  # Show first 5
            print(f"  Sensor {sensor['sensor_id']}: avg_temp={sensor['avg_temperature']:.2f}°C, "
                  f"std={sensor['temperature_std']:.2f}")
    
    # Save results
    results = {
        'pipeline_timestamp': datetime.now().isoformat(),
        'overall_statistics': overall_stats,
        'sensor_statistics': sensor_stats,
        'anomalous_sensors': anomalous_sensors
    }
    
    json.write_json('sensor_analysis_results.json', results, pretty_print=True)
    print("Results saved to 'sensor_analysis_results.json'")
    
    # Cleanup
    simple_io.delete_file('sensor_analysis_results.json')

data_science_pipeline_example()
```

### Log Processing System

```python
def log_processing_system_example():
    """Enterprise log processing system example."""
    
    print("=== Log Processing System Example ===")
    
    # Simulate generating log files from different services
    services = ['auth', 'api', 'database', 'cache', 'frontend', 'payment']
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def generate_service_logs(service_name):
        """Generate logs for a specific service."""
        import random
        from datetime import datetime, timedelta
        
        logs = []
        start_time = datetime.now() - timedelta(hours=24)
        
        # Different services have different log patterns
        if service_name == 'database':
            log_count = random.randint(800, 1200)  # Database logs more
        elif service_name == 'payment':
            log_count = random.randint(200, 400)   # Payment logs less
        else:
            log_count = random.randint(400, 800)
        
        for i in range(log_count):
            # Simulate realistic timestamp distribution
            timestamp = start_time + timedelta(
                seconds=random.randint(0, 86400),
                microseconds=random.randint(0, 999999)
            )
            
            # Different error rates by service
            if service_name == 'payment':
                level_weights = [1, 8, 2, 1, 0.1]  # Payment service more critical
            elif service_name == 'database':
                level_weights = [2, 10, 3, 1, 0.2]  # Database moderate errors
            else:
                level_weights = [5, 15, 2, 1, 0.1]  # Other services fewer errors
            
            level = random.choices(log_levels, weights=level_weights)[0]
            
            # Generate realistic log messages
            if level == 'ERROR':
                messages = [
                    f"Connection timeout to {service_name}",
                    f"Failed to process request in {service_name}",
                    f"Authentication failed in {service_name}",
                    f"Resource not found in {service_name}"
                ]
            elif level == 'WARNING':
                messages = [
                    f"High memory usage in {service_name}",
                    f"Slow response time in {service_name}",
                    f"Rate limit approaching in {service_name}"
                ]
            else:
                messages = [
                    f"Request processed successfully in {service_name}",
                    f"User authentication successful in {service_name}",
                    f"Data retrieved from {service_name}"
                ]
            
            log_entry = {
                'timestamp': timestamp.isoformat(),
                'service': service_name,
                'level': level,
                'message': random.choice(messages),
                'request_id': f"req_{random.randint(100000, 999999)}",
                'user_id': random.randint(1, 10000) if random.random() > 0.3 else None,
                'response_time_ms': random.randint(10, 5000),
                'memory_usage_mb': random.randint(100, 2000)
            }
            
            logs.append(log_entry)
        
        return service_name, logs
    
    # Generate logs for all services in parallel
    print("Generating service logs...")
    service_log_results = parallel_map(generate_service_logs, services)
    
    # Write individual service log files
    log_files = []
    total_entries = 0
    
    for service_name, logs in service_log_results:
        filename = f"{service_name}_service.log.jsonl"
        json.write_jsonl(filename, logs)
        log_files.append(filename)
        total_entries += len(logs)
        print(f"  {service_name}: {len(logs)} log entries")
    
    print(f"Total log entries: {total_entries}")
    
    # Process log files in parallel
    def analyze_log_file(file_path, content):
        """Analyze a single log file."""
        logs = [json.parse_json(line) for line in content.strip().split('\n')]
        
        # Analyze log patterns
        level_counts = {}
        response_times = []
        memory_usage = []
        error_patterns = {}
        hourly_distribution = {}
        
        for log in logs:
            # Count by level
            level = log['level']
            level_counts[level] = level_counts.get(level, 0) + 1
            
            # Collect performance metrics
            response_times.append(log['response_time_ms'])
            memory_usage.append(log['memory_usage_mb'])
            
            # Track error patterns
            if level in ['ERROR', 'CRITICAL']:
                message = log['message']
                error_patterns[message] = error_patterns.get(message, 0) + 1
            
            # Hourly distribution
            hour = log['timestamp'][:13]  # YYYY-MM-DDTHH
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
        
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times)
        avg_memory = sum(memory_usage) / len(memory_usage)
        error_rate = (level_counts.get('ERROR', 0) + level_counts.get('CRITICAL', 0)) / len(logs)
        
        return {
            'service': file_path.replace('_service.log.jsonl', ''),
            'total_entries': len(logs),
            'level_distribution': level_counts,
            'avg_response_time_ms': avg_response_time,
            'avg_memory_usage_mb': avg_memory,
            'error_rate': error_rate,
            'top_errors': dict(sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:5]),
            'hourly_peak': max(hourly_distribution.items(), key=lambda x: x[1]) if hourly_distribution else None
        }
    
    print("\nAnalyzing log files...")
    processor = ParallelFileProcessor(max_workers=6)
    analysis_results = processor.process_files(log_files, analyze_log_file)
    
    # Generate comprehensive report
    print("\n=== Log Analysis Report ===")
    
    # Overall system health
    total_errors = sum(r['level_distribution'].get('ERROR', 0) + 
                      r['level_distribution'].get('CRITICAL', 0) 
                      for r in analysis_results)
    overall_error_rate = total_errors / total_entries
    
    print(f"System Overview:")
    print(f"  Total log entries: {total_entries}")
    print(f"  Overall error rate: {overall_error_rate:.2%}")
    print(f"  Services monitored: {len(analysis_results)}")
    
    # Service-specific analysis
    print(f"\nService Analysis:")
    for result in sorted(analysis_results, key=lambda x: x['error_rate'], reverse=True):
        print(f"  {result['service'].upper()}:")
        print(f"    Entries: {result['total_entries']}")
        print(f"    Error rate: {result['error_rate']:.2%}")
        print(f"    Avg response time: {result['avg_response_time_ms']:.1f}ms")
        print(f"    Avg memory usage: {result['avg_memory_usage_mb']:.1f}MB")
        
        if result['top_errors']:
            print(f"    Top error: {list(result['top_errors'].keys())[0]}")
    
    # Identify services needing attention
    critical_services = [r for r in analysis_results if r['error_rate'] > 0.05]  # > 5% error rate
    high_response_services = [r for r in analysis_results if r['avg_response_time_ms'] > 1000]  # > 1s
    
    if critical_services:
        print(f"\n⚠️  Services with high error rates:")
        for service in critical_services:
            print(f"    {service['service']}: {service['error_rate']:.2%} error rate")
    
    if high_response_services:
        print(f"\n🐌 Services with slow response times:")
        for service in high_response_services:
            print(f"    {service['service']}: {service['avg_response_time_ms']:.1f}ms avg response")
    
    # Generate alerts/recommendations
    alerts = []
    
    for result in analysis_results:
        if result['error_rate'] > 0.1:  # > 10% error rate
            alerts.append(f"CRITICAL: {result['service']} has {result['error_rate']:.1%} error rate")
        elif result['error_rate'] > 0.05:  # > 5% error rate
            alerts.append(f"WARNING: {result['service']} has {result['error_rate']:.1%} error rate")
        
        if result['avg_response_time_ms'] > 2000:  # > 2 seconds
            alerts.append(f"PERFORMANCE: {result['service']} avg response time is {result['avg_response_time_ms']:.0f}ms")
    
    if alerts:
        print(f"\n🚨 Alerts ({len(alerts)}):")
        for alert in alerts[:10]:  # Show top 10 alerts
            print(f"    {alert}")
    
    # Save comprehensive report
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'summary': {
            'total_entries': total_entries,
            'overall_error_rate': overall_error_rate,
            'services_count': len(analysis_results)
        },
        'service_analysis': analysis_results,
        'alerts': alerts,
        'critical_services': [s['service'] for s in critical_services],
        'slow_services': [s['service'] for s in high_response_services]
    }
    
    json.write_json('log_analysis_report.json', report, pretty_print=True)
    print(f"\nDetailed report saved to 'log_analysis_report.json'")
    
    # Cleanup log files
    for log_file in log_files:
        simple_io.delete_file(log_file)
    simple_io.delete_file('log_analysis_report.json')
    
    print("Log processing completed and files cleaned up")

log_processing_system_example()
```

## Performance Comparisons

```python
def performance_comparison_example():
    """Compare PyFerris performance with standard Python approaches."""
    
    import time
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
    
    print("=== Performance Comparison ===")
    
    def cpu_intensive_task(n):
        """CPU-intensive task for benchmarking."""
        result = 0
        for i in range(n * 10000):
            result += math.sin(i) * math.cos(i)
        return result
    
    # Test data
    test_data = list(range(1, 101))  # 100 tasks
    
    print(f"Testing with {len(test_data)} CPU-intensive tasks...")
    
    # 1. Sequential processing (baseline)
    print("\n1. Sequential Processing:")
    start_time = time.time()
    sequential_results = [cpu_intensive_task(n) for n in test_data]
    sequential_time = time.time() - start_time
    print(f"   Time: {sequential_time:.2f}s")
    
    # 2. PyFerris parallel_map
    print("\n2. PyFerris parallel_map:")
    start_time = time.time()
    pyferris_results = parallel_map(cpu_intensive_task, test_data)
    pyferris_time = time.time() - start_time
    print(f"   Time: {pyferris_time:.2f}s")
    print(f"   Speedup: {sequential_time / pyferris_time:.2f}x")
    
    # 3. Python multiprocessing.Pool
    print("\n3. Python multiprocessing.Pool:")
    start_time = time.time()
    with multiprocessing.Pool() as pool:
        mp_results = pool.map(cpu_intensive_task, test_data)
    mp_time = time.time() - start_time
    print(f"   Time: {mp_time:.2f}s")
    print(f"   Speedup: {sequential_time / mp_time:.2f}x")
    
    # 4. concurrent.futures.ProcessPoolExecutor
    print("\n4. ProcessPoolExecutor:")
    start_time = time.time()
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(cpu_intensive_task, n) for n in test_data]
        ppe_results = [f.result() for f in futures]
    ppe_time = time.time() - start_time
    print(f"   Time: {ppe_time:.2f}s")
    print(f"   Speedup: {sequential_time / ppe_time:.2f}x")
    
    # 5. PyFerris Executor
    print("\n5. PyFerris Executor:")
    start_time = time.time()
    with Executor() as executor:
        futures = [executor.submit(cpu_intensive_task, n) for n in test_data]
        executor_results = [f.result() for f in futures]
    executor_time = time.time() - start_time
    print(f"   Time: {executor_time:.2f}s")
    print(f"   Speedup: {sequential_time / executor_time:.2f}x")
    
    # Verify results are consistent
    assert len(set([len(r) for r in [sequential_results, pyferris_results, mp_results, ppe_results, executor_results]])) == 1
    print(f"\n✅ All methods produced {len(sequential_results)} results")
    
    # Summary comparison
    results_summary = [
        ("Sequential", sequential_time, 1.0),
        ("PyFerris parallel_map", pyferris_time, sequential_time / pyferris_time),
        ("multiprocessing.Pool", mp_time, sequential_time / mp_time),
        ("ProcessPoolExecutor", ppe_time, sequential_time / ppe_time),
        ("PyFerris Executor", executor_time, sequential_time / executor_time),
    ]
    
    print(f"\n=== Performance Summary ===")
    print(f"{'Method':<25} {'Time (s)':<10} {'Speedup':<10}")
    print("-" * 45)
    for method, time_taken, speedup in results_summary:
        print(f"{method:<25} {time_taken:<10.2f} {speedup:<10.2f}x")
    
    # I/O Performance comparison
    print(f"\n=== I/O Performance Comparison ===")
    
    # Create test files
    test_files = []
    file_content = "Sample file content. " * 1000  # ~21KB per file
    
    for i in range(20):
        filename = f"test_file_{i:03d}.txt"
        simple_io.write_file(filename, file_content)
        test_files.append(filename)
    
    print(f"Created {len(test_files)} test files")
    
    # Sequential file reading
    start_time = time.time()
    sequential_content = [simple_io.read_file(f) for f in test_files]
    seq_io_time = time.time() - start_time
    
    # Parallel file reading with PyFerris
    start_time = time.time()
    parallel_content = simple_io.read_files_parallel(test_files)
    par_io_time = time.time() - start_time
    
    print(f"Sequential I/O: {seq_io_time:.3f}s")
    print(f"Parallel I/O: {par_io_time:.3f}s")
    print(f"I/O Speedup: {seq_io_time / par_io_time:.2f}x")
    
    # Verify content consistency
    assert len(sequential_content) == len(parallel_content)
    print(f"✅ I/O results consistent: {len(sequential_content)} files read")
    
    # Cleanup test files
    for filename in test_files:
        simple_io.delete_file(filename)
    
    print("Performance comparison completed")

performance_comparison_example()
```

This comprehensive examples documentation demonstrates the full capabilities of PyFerris across its core operations, executor functionality, and I/O operations, providing practical examples that users can adapt for their specific use cases.
