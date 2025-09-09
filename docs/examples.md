# Examples

This section provides practical examples and real-world use cases for PyFerris, demonstrating how to leverage its parallel processing capabilities across various domains.

## Table of Contents

1. [Data Processing Examples](#data-processing-examples)
2. [Scientific Computing](#scientific-computing)
3. [Web Scraping and API Processing](#web-scraping-and-api-processing)
4. [File Processing](#file-processing)
5. [Machine Learning Workflows](#machine-learning-workflows)
6. [Image and Media Processing](#image-and-media-processing)
7. [Financial Data Analysis](#financial-data-analysis)
8. [Log Analysis](#log-analysis)
9. [Performance Benchmarks](#performance-benchmarks)
10. [Common Patterns](#common-patterns)

## Data Processing Examples

### Large Dataset Transformation

```python
from pyferris import parallel_map, parallel_filter, ProgressTracker
import json
import time

def process_customer_record(record):
    """Transform customer data for analysis."""
    return {
        'customer_id': record['id'],
        'full_name': f"{record['first_name']} {record['last_name']}",
        'age': 2024 - record['birth_year'],
        'email_domain': record['email'].split('@')[1],
        'total_orders': len(record.get('orders', [])),
        'lifetime_value': sum(order['amount'] for order in record.get('orders', [])),
        'is_premium': record.get('subscription_tier', 'basic') in ['premium', 'enterprise']
    }

def is_active_customer(record):
    """Filter for customers with recent activity."""
    if not record.get('orders'):
        return False
    
    # Check if customer has orders in the last 6 months
    recent_threshold = time.time() - (6 * 30 * 24 * 3600)  # 6 months ago
    recent_orders = [o for o in record['orders'] if o['timestamp'] > recent_threshold]
    return len(recent_orders) > 0

# Load large customer dataset
with open('customer_data.json', 'r') as f:
    customer_data = json.load(f)

print(f"Processing {len(customer_data)} customer records...")

# Create progress tracker
tracker = ProgressTracker(total=len(customer_data), desc="Processing customers")

# Transform customer data in parallel
start_time = time.time()
processed_customers = list(parallel_map(
    process_customer_record, 
    customer_data, 
    progress=tracker
))

# Filter for active customers
active_customers = list(parallel_filter(is_active_customer, customer_data))

processing_time = time.time() - start_time
print(f"Processed {len(processed_customers)} records in {processing_time:.2f} seconds")
print(f"Found {len(active_customers)} active customers")

# Calculate statistics
total_revenue = sum(customer['lifetime_value'] for customer in processed_customers)
premium_customers = sum(1 for customer in processed_customers if customer['is_premium'])

print(f"Total revenue: ${total_revenue:,.2f}")
print(f"Premium customers: {premium_customers} ({premium_customers/len(processed_customers)*100:.1f}%)")
```

### Data Aggregation and Analysis

```python
from pyferris import parallel_group_by, parallel_reduce, parallel_map
from collections import defaultdict

def analyze_sales_data(sales_records):
    """Comprehensive sales data analysis using PyFerris."""
    
    # Group sales by region
    def get_region(record):
        return record['region']
    
    sales_by_region = parallel_group_by(sales_records, key=get_region)
    
    # Calculate regional statistics
    def calculate_region_stats(region_data):
        region, sales = region_data
        
        total_sales = parallel_reduce(
            lambda x, y: x + y['amount'], 
            sales, 
            initial=0
        )
        
        avg_sale = total_sales / len(sales) if sales else 0
        
        # Find top products in region
        product_sales = parallel_group_by(sales, key=lambda s: s['product'])
        top_products = sorted(
            [(product, sum(s['amount'] for s in product_sales)) 
             for product, product_sales in product_sales.items()],
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            'region': region,
            'total_sales': total_sales,
            'num_transactions': len(sales),
            'avg_transaction': avg_sale,
            'top_products': top_products
        }
    
    # Process all regions in parallel
    region_stats = list(parallel_map(
        calculate_region_stats, 
        sales_by_region.items()
    ))
    
    return region_stats

# Example usage
sales_data = [
    {'region': 'North', 'product': 'Widget A', 'amount': 100, 'date': '2024-01-15'},
    {'region': 'South', 'product': 'Widget B', 'amount': 150, 'date': '2024-01-16'},
    # ... thousands more records
]

regional_analysis = analyze_sales_data(sales_data)
for stats in regional_analysis:
    print(f"Region: {stats['region']}")
    print(f"  Total Sales: ${stats['total_sales']:,.2f}")
    print(f"  Transactions: {stats['num_transactions']}")
    print(f"  Average: ${stats['avg_transaction']:.2f}")
    print(f"  Top Product: {stats['top_products'][0][0]} (${stats['top_products'][0][1]:,.2f})")
    print()
```

## Scientific Computing

### Monte Carlo Simulation

```python
from pyferris import parallel_map, parallel_reduce
import random
import math

def monte_carlo_pi_estimation(num_simulations=1000000, num_workers=None):
    """Estimate π using Monte Carlo method with parallel processing."""
    
    def simulate_batch(batch_size):
        """Simulate a batch of points for π estimation."""
        inside_circle = 0
        for _ in range(batch_size):
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            if x*x + y*y <= 1:
                inside_circle += 1
        return inside_circle, batch_size
    
    # Divide work into batches
    batch_size = 10000
    num_batches = num_simulations // batch_size
    batches = [batch_size] * num_batches
    
    print(f"Running {num_simulations:,} simulations across {num_batches} batches...")
    
    # Run simulations in parallel
    results = list(parallel_map(simulate_batch, batches))
    
    # Combine results
    total_inside = parallel_reduce(lambda x, y: x + y[0], results, initial=0)
    total_points = parallel_reduce(lambda x, y: x + y[1], results, initial=0)
    
    # Estimate π
    pi_estimate = 4.0 * total_inside / total_points
    error = abs(pi_estimate - math.pi) / math.pi * 100
    
    print(f"π estimate: {pi_estimate:.6f}")
    print(f"Actual π: {math.pi:.6f}")
    print(f"Error: {error:.4f}%")
    
    return pi_estimate

# Run estimation
pi_value = monte_carlo_pi_estimation(10000000)
```

### Numerical Integration

```python
from pyferris import parallel_map, parallel_reduce
import math

def parallel_numerical_integration(func, a, b, n=1000000):
    """Compute definite integral using trapezoidal rule in parallel."""
    
    def integrate_segment(segment):
        """Integrate a segment of the function."""
        start, end, num_points = segment
        h = (end - start) / num_points
        
        # Trapezoidal rule for this segment
        integral = 0.5 * (func(start) + func(end))
        for i in range(1, num_points):
            x = start + i * h
            integral += func(x)
        
        return integral * h
    
    # Divide integration domain into segments
    num_segments = 100
    segment_width = (b - a) / num_segments
    points_per_segment = n // num_segments
    
    segments = []
    for i in range(num_segments):
        start = a + i * segment_width
        end = a + (i + 1) * segment_width
        segments.append((start, end, points_per_segment))
    
    # Integrate segments in parallel
    segment_results = list(parallel_map(integrate_segment, segments))
    
    # Sum all segment results
    total_integral = parallel_reduce(lambda x, y: x + y, segment_results, initial=0)
    
    return total_integral

# Example: integrate sin(x) from 0 to π
def sine_function(x):
    return math.sin(x)

result = parallel_numerical_integration(sine_function, 0, math.pi, n=1000000)
expected = 2.0  # Analytical result for ∫sin(x)dx from 0 to π

print(f"Numerical integration result: {result:.6f}")
print(f"Expected result: {expected:.6f}")
print(f"Error: {abs(result - expected):.6f}")
```

## Web Scraping and API Processing

### Parallel Web Scraping

```python
from pyferris import parallel_map, ProgressTracker
import requests
import time
from urllib.parse import urljoin, urlparse

class WebScraper:
    def __init__(self, base_url, max_workers=10, delay=1):
        self.base_url = base_url
        self.max_workers = max_workers
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PyFerris Web Scraper 1.0'
        })
    
    def scrape_url(self, url_info):
        """Scrape a single URL."""
        url, metadata = url_info if isinstance(url_info, tuple) else (url_info, {})
        
        try:
            time.sleep(self.delay)  # Rate limiting
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return {
                'url': url,
                'status_code': response.status_code,
                'content_length': len(response.content),
                'title': self._extract_title(response.text),
                'links': self._extract_links(response.text, url),
                'metadata': metadata,
                'scraped_at': time.time()
            }
        
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'metadata': metadata,
                'scraped_at': time.time()
            }
    
    def _extract_title(self, html):
        """Extract page title from HTML."""
        import re
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else None
    
    def _extract_links(self, html, base_url):
        """Extract links from HTML."""
        import re
        links = re.findall(r'href=["\'](.*?)["\']', html, re.IGNORECASE)
        absolute_links = []
        
        for link in links:
            absolute_link = urljoin(base_url, link)
            if urlparse(absolute_link).netloc:  # Only external links
                absolute_links.append(absolute_link)
        
        return absolute_links[:10]  # Limit to first 10 links
    
    def scrape_urls(self, urls):
        """Scrape multiple URLs in parallel."""
        tracker = ProgressTracker(total=len(urls), desc="Scraping URLs")
        
        results = list(parallel_map(
            self.scrape_url, 
            urls, 
            progress=tracker
        ))
        
        successful = [r for r in results if 'error' not in r]
        failed = [r for r in results if 'error' in r]
        
        print(f"Successfully scraped: {len(successful)}")
        print(f"Failed to scrape: {len(failed)}")
        
        return results

# Example usage
scraper = WebScraper("https://example.com", max_workers=5, delay=0.5)

urls_to_scrape = [
    "https://httpbin.org/get",
    "https://httpbin.org/json",
    "https://httpbin.org/html",
    # ... more URLs
]

scraping_results = scraper.scrape_urls(urls_to_scrape)

# Analyze results
for result in scraping_results[:5]:  # Show first 5 results
    if 'error' not in result:
        print(f"URL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"Content Length: {result['content_length']} bytes")
        print(f"Links found: {len(result['links'])}")
        print()
    else:
        print(f"Failed to scrape {result['url']}: {result['error']}")
```

### API Data Processing

```python
from pyferris import parallel_map, parallel_filter, BatchProcessor
import requests
import json
import time

class APIProcessor:
    def __init__(self, api_key=None, rate_limit=10):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.last_request_time = 0
    
    def fetch_user_data(self, user_id):
        """Fetch user data from API with rate limiting."""
        # Simple rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < (1.0 / self.rate_limit):
            time.sleep((1.0 / self.rate_limit) - time_since_last)
        
        self.last_request_time = time.time()
        
        try:
            # Mock API call - replace with actual API
            response = requests.get(
                f"https://jsonplaceholder.typicode.com/users/{user_id}",
                timeout=10
            )
            response.raise_for_status()
            
            user_data = response.json()
            
            # Enhance user data
            user_data['processed_at'] = time.time()
            user_data['email_domain'] = user_data['email'].split('@')[1]
            user_data['coordinate_distance'] = (
                float(user_data['address']['geo']['lat'])**2 + 
                float(user_data['address']['geo']['lng'])**2
            )**0.5
            
            return user_data
            
        except Exception as e:
            return {'user_id': user_id, 'error': str(e)}
    
    def process_user_batch(self, user_ids):
        """Process a batch of users."""
        processor = APIProcessor(self.api_key, self.rate_limit)
        return [processor.fetch_user_data(uid) for uid in user_ids]

def analyze_user_data(users):
    """Analyze processed user data."""
    
    # Filter successful results
    valid_users = parallel_filter(lambda u: 'error' not in u, users)
    
    def extract_company_info(user):
        return {
            'company': user['company']['name'],
            'user_name': user['name'],
            'city': user['address']['city']
        }
    
    # Extract company information
    company_data = list(parallel_map(extract_company_info, valid_users))
    
    # Group by company
    from pyferris import parallel_group_by
    by_company = parallel_group_by(company_data, key=lambda x: x['company'])
    
    # Calculate company statistics
    def calc_company_stats(company_info):
        company, employees = company_info
        cities = list(set(emp['city'] for emp in employees))
        return {
            'company': company,
            'employee_count': len(employees),
            'cities': cities,
            'geographic_spread': len(cities)
        }
    
    company_stats = list(parallel_map(calc_company_stats, by_company.items()))
    
    return company_stats

# Example usage
api_processor = APIProcessor(rate_limit=5)  # 5 requests per second

# Process users in batches to manage rate limiting
user_ids = list(range(1, 101))  # Process users 1-100
batch_processor = BatchProcessor(batch_size=10, progress=True)

all_users = []
for batch_result in batch_processor.process(user_ids, api_processor.process_user_batch):
    all_users.extend(batch_result)

print(f"Processed {len(all_users)} users")

# Analyze the data
company_analysis = analyze_user_data(all_users)

print("\nCompany Analysis:")
for company in sorted(company_analysis, key=lambda x: x['employee_count'], reverse=True)[:5]:
    print(f"{company['company']}: {company['employee_count']} employees across {company['geographic_spread']} cities")
```

## File Processing

### Log File Analysis

```python
from pyferris import parallel_map, parallel_filter, parallel_group_by
from pyferris.io import simple_io
import re
import json
from datetime import datetime

class LogAnalyzer:
    def __init__(self, log_pattern=None):
        # Common log pattern (Apache/Nginx style)
        self.log_pattern = log_pattern or re.compile(
            r'(\S+) \S+ \S+ \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+|-) "([^"]*)" "([^"]*)"'
        )
    
    def parse_log_line(self, line):
        """Parse a single log line."""
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        
        match = self.log_pattern.match(line)
        if not match:
            return {'raw_line': line, 'parse_error': True}
        
        ip, timestamp, method, path, protocol, status, size, referer, user_agent = match.groups()
        
        try:
            # Parse timestamp
            dt = datetime.strptime(timestamp.split()[0], '%d/%b/%Y:%H:%M:%S')
            
            return {
                'ip': ip,
                'timestamp': dt.isoformat(),
                'method': method,
                'path': path,
                'protocol': protocol,
                'status': int(status),
                'size': int(size) if size != '-' else 0,
                'referer': referer if referer != '-' else None,
                'user_agent': user_agent,
                'hour': dt.hour,
                'date': dt.date().isoformat()
            }
        except Exception as e:
            return {'raw_line': line, 'parse_error': True, 'error': str(e)}

def analyze_log_file(log_file_path):
    """Comprehensive log file analysis."""
    
    # Read log file
    print(f"Reading log file: {log_file_path}")
    log_content = simple_io.read_file(log_file_path)
    log_lines = log_content.strip().split('\n')
    
    print(f"Processing {len(log_lines):,} log lines...")
    
    # Parse log lines in parallel
    analyzer = LogAnalyzer()
    parsed_logs = list(parallel_map(analyzer.parse_log_line, log_lines))
    
    # Filter valid log entries
    valid_logs = list(parallel_filter(
        lambda log: log is not None and not log.get('parse_error', False), 
        parsed_logs
    ))
    
    print(f"Successfully parsed {len(valid_logs):,} log entries")
    
    # Analysis 1: Status code distribution
    status_groups = parallel_group_by(valid_logs, key=lambda log: log['status'])
    status_stats = {status: len(logs) for status, logs in status_groups.items()}
    
    # Analysis 2: Top IP addresses
    ip_groups = parallel_group_by(valid_logs, key=lambda log: log['ip'])
    top_ips = sorted(
        [(ip, len(logs)) for ip, logs in ip_groups.items()], 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    
    # Analysis 3: Hourly traffic distribution
    hourly_groups = parallel_group_by(valid_logs, key=lambda log: log['hour'])
    hourly_stats = {hour: len(logs) for hour, logs in hourly_groups.items()}
    
    # Analysis 4: Error analysis (4xx and 5xx status codes)
    error_logs = list(parallel_filter(lambda log: log['status'] >= 400, valid_logs))
    error_paths = parallel_group_by(error_logs, key=lambda log: log['path'])
    top_error_paths = sorted(
        [(path, len(logs)) for path, logs in error_paths.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Analysis 5: Bandwidth usage
    def calculate_bandwidth(log_entry):
        return log_entry['size']
    
    total_bandwidth = sum(parallel_map(calculate_bandwidth, valid_logs))
    
    return {
        'total_requests': len(valid_logs),
        'status_distribution': status_stats,
        'top_ips': top_ips,
        'hourly_distribution': hourly_stats,
        'top_error_paths': top_error_paths,
        'total_bandwidth_bytes': total_bandwidth,
        'total_bandwidth_mb': total_bandwidth / (1024 * 1024)
    }

# Example usage
def create_sample_log_file():
    """Create a sample log file for testing."""
    import random
    from datetime import datetime, timedelta
    
    ips = ['192.168.1.1', '10.0.0.1', '172.16.0.1', '203.0.113.1']
    paths = ['/index.html', '/api/users', '/api/orders', '/images/logo.png', '/css/style.css']
    statuses = [200, 200, 200, 200, 404, 500, 301]
    
    log_lines = []
    base_time = datetime.now() - timedelta(days=1)
    
    for i in range(10000):
        timestamp = base_time + timedelta(seconds=i)
        ip = random.choice(ips)
        path = random.choice(paths)
        status = random.choice(statuses)
        size = random.randint(100, 10000)
        
        log_line = f'{ip} - - [{timestamp.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET {path} HTTP/1.1" {status} {size} "-" "Mozilla/5.0"'
        log_lines.append(log_line)
    
    with open('sample.log', 'w') as f:
        f.write('\n'.join(log_lines))

# Create sample log and analyze it
create_sample_log_file()
results = analyze_log_file('sample.log')

print("\n=== Log Analysis Results ===")
print(f"Total Requests: {results['total_requests']:,}")
print(f"Total Bandwidth: {results['total_bandwidth_mb']:.2f} MB")

print("\nStatus Code Distribution:")
for status, count in sorted(results['status_distribution'].items()):
    print(f"  {status}: {count:,} requests")

print("\nTop IP Addresses:")
for ip, count in results['top_ips'][:5]:
    print(f"  {ip}: {count:,} requests")

print("\nTop Error Paths:")
for path, count in results['top_error_paths'][:5]:
    print(f"  {path}: {count:,} errors")
```

### CSV Data Processing Pipeline

```python
from pyferris import parallel_map, parallel_filter, Pipeline
from pyferris.io import csv
import statistics

def process_sales_csv(file_path):
    """Complete sales data processing pipeline."""
    
    # Read CSV data
    print(f"Reading sales data from {file_path}...")
    sales_data = csv.read_csv(file_path)
    print(f"Loaded {len(sales_data):,} sales records")
    
    # Create processing pipeline
    pipeline = Pipeline(sales_data)
    
    # Step 1: Clean and validate data
    def clean_record(record):
        try:
            return {
                'date': record['date'],
                'product': record['product'].strip(),
                'category': record['category'].strip(),
                'amount': float(record['amount']),
                'quantity': int(record['quantity']),
                'region': record['region'].strip(),
                'salesperson': record['salesperson'].strip()
            }
        except (ValueError, KeyError):
            return None
    
    # Step 2: Filter valid records
    def is_valid_record(record):
        return (record is not None and 
                record['amount'] > 0 and 
                record['quantity'] > 0)
    
    # Step 3: Add calculated fields
    def add_calculated_fields(record):
        record['unit_price'] = record['amount'] / record['quantity']
        record['month'] = record['date'][:7]  # YYYY-MM format
        return record
    
    # Execute pipeline
    processed_data = (pipeline
                     .map(clean_record)
                     .filter(is_valid_record)
                     .map(add_calculated_fields)
                     .collect())
    
    print(f"Processed {len(processed_data):,} valid records")
    
    # Advanced analysis
    def analyze_by_category(data):
        """Analyze sales by category."""
        from pyferris import parallel_group_by, parallel_reduce
        
        # Group by category
        by_category = parallel_group_by(data, key=lambda r: r['category'])
        
        def calculate_category_metrics(category_data):
            category, records = category_data
            
            amounts = [r['amount'] for r in records]
            quantities = [r['quantity'] for r in records]
            
            return {
                'category': category,
                'total_sales': sum(amounts),
                'total_quantity': sum(quantities),
                'avg_sale': statistics.mean(amounts),
                'num_transactions': len(records),
                'top_product': max(
                    parallel_group_by(records, key=lambda r: r['product']).items(),
                    key=lambda x: len(x[1])
                )[0]
            }
        
        return list(parallel_map(calculate_category_metrics, by_category.items()))
    
    # Perform analysis
    category_analysis = analyze_by_category(processed_data)
    
    # Regional performance
    def analyze_by_region(data):
        from pyferris import parallel_group_by
        
        by_region = parallel_group_by(data, key=lambda r: r['region'])
        
        def calculate_region_metrics(region_data):
            region, records = region_data
            
            monthly_sales = parallel_group_by(records, key=lambda r: r['month'])
            monthly_totals = {
                month: sum(r['amount'] for r in month_records)
                for month, month_records in monthly_sales.items()
            }
            
            return {
                'region': region,
                'total_sales': sum(r['amount'] for r in records),
                'monthly_performance': monthly_totals,
                'avg_monthly_sales': statistics.mean(monthly_totals.values()) if monthly_totals else 0,
                'best_month': max(monthly_totals.items(), key=lambda x: x[1]) if monthly_totals else None
            }
        
        return list(parallel_map(calculate_region_metrics, by_region.items()))
    
    regional_analysis = analyze_by_region(processed_data)
    
    return {
        'processed_records': len(processed_data),
        'category_analysis': category_analysis,
        'regional_analysis': regional_analysis,
        'raw_data': processed_data
    }

# Create sample sales data
def create_sample_sales_csv():
    import random
    from datetime import datetime, timedelta
    
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden']
    products = {
        'Electronics': ['Laptop', 'Phone', 'Tablet', 'Headphones'],
        'Clothing': ['Shirt', 'Pants', 'Shoes', 'Jacket'],
        'Books': ['Fiction', 'Non-fiction', 'Textbook', 'Magazine'],
        'Home & Garden': ['Tools', 'Plants', 'Furniture', 'Decor']
    }
    regions = ['North', 'South', 'East', 'West']
    salespeople = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
    
    sales_records = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(50000):  # 50,000 records
        date = base_date + timedelta(days=random.randint(0, 365))
        category = random.choice(categories)
        product = random.choice(products[category])
        quantity = random.randint(1, 10)
        unit_price = random.uniform(10, 500)
        amount = quantity * unit_price
        
        record = {
            'date': date.strftime('%Y-%m-%d'),
            'product': product,
            'category': category,
            'amount': f'{amount:.2f}',
            'quantity': str(quantity),
            'region': random.choice(regions),
            'salesperson': random.choice(salespeople)
        }
        sales_records.append(record)
    
    # Write to CSV
    csv.write_csv('sample_sales.csv', sales_records)
    print("Created sample_sales.csv with 50,000 records")

# Generate sample data and process it
create_sample_sales_csv()
results = process_sales_csv('sample_sales.csv')

print("\n=== Sales Analysis Results ===")
print(f"Processed Records: {results['processed_records']:,}")

print("\nTop Categories by Sales:")
category_analysis = sorted(results['category_analysis'], key=lambda x: x['total_sales'], reverse=True)
for category in category_analysis[:3]:
    print(f"  {category['category']}: ${category['total_sales']:,.2f} ({category['num_transactions']:,} transactions)")

print("\nRegional Performance:")
regional_analysis = sorted(results['regional_analysis'], key=lambda x: x['total_sales'], reverse=True)
for region in regional_analysis:
    print(f"  {region['region']}: ${region['total_sales']:,.2f} (avg monthly: ${region['avg_monthly_sales']:,.2f})")
```

## Performance Benchmarks

### Comparing PyFerris with Standard Libraries

```python
from pyferris import parallel_map, parallel_filter, parallel_reduce
import multiprocessing
import time
import statistics

def benchmark_parallel_operations():
    """Comprehensive benchmarking of PyFerris vs standard libraries."""
    
    def cpu_intensive_task(n):
        """CPU-intensive computation for benchmarking."""
        result = 0
        for i in range(n % 1000):
            result += i * i
        return result
    
    def is_even(n):
        """Simple predicate for filtering."""
        return n % 2 == 0
    
    def add(x, y):
        """Simple reduction function."""
        return x + y
    
    # Test datasets of different sizes
    test_sizes = [1000, 10000, 100000, 1000000]
    
    print("Performance Comparison: PyFerris vs Python Standard Library")
    print("=" * 70)
    
    for size in test_sizes:
        print(f"\nDataset size: {size:,} items")
        print("-" * 40)
        
        data = list(range(size))
        
        # Benchmark parallel_map
        print("Map Operation:")
        
        # PyFerris
        start_time = time.time()
        pyferris_map_result = list(parallel_map(cpu_intensive_task, data))
        pyferris_map_time = time.time() - start_time
        
        # Standard multiprocessing
        start_time = time.time()
        with multiprocessing.Pool() as pool:
            mp_map_result = pool.map(cpu_intensive_task, data)
        mp_map_time = time.time() - start_time
        
        # Sequential
        start_time = time.time()
        seq_map_result = [cpu_intensive_task(x) for x in data]
        seq_map_time = time.time() - start_time
        
        print(f"  PyFerris:      {pyferris_map_time:.3f}s")
        print(f"  Multiprocessing: {mp_map_time:.3f}s")
        print(f"  Sequential:    {seq_map_time:.3f}s")
        print(f"  PyFerris speedup vs MP: {mp_map_time/pyferris_map_time:.2f}x")
        print(f"  PyFerris speedup vs Seq: {seq_map_time/pyferris_map_time:.2f}x")
        
        # Benchmark parallel_filter
        print("\nFilter Operation:")
        
        # PyFerris
        start_time = time.time()
        pyferris_filter_result = list(parallel_filter(is_even, data))
        pyferris_filter_time = time.time() - start_time
        
        # Sequential
        start_time = time.time()
        seq_filter_result = [x for x in data if is_even(x)]
        seq_filter_time = time.time() - start_time
        
        print(f"  PyFerris:   {pyferris_filter_time:.3f}s")
        print(f"  Sequential: {seq_filter_time:.3f}s")
        print(f"  Speedup: {seq_filter_time/pyferris_filter_time:.2f}x")
        
        # Benchmark parallel_reduce
        print("\nReduce Operation:")
        
        # PyFerris
        start_time = time.time()
        pyferris_reduce_result = parallel_reduce(add, data, initial=0)
        pyferris_reduce_time = time.time() - start_time
        
        # Sequential
        start_time = time.time()
        seq_reduce_result = sum(data)
        seq_reduce_time = time.time() - start_time
        
        print(f"  PyFerris:   {pyferris_reduce_time:.3f}s")
        print(f"  Sequential: {seq_reduce_time:.3f}s")
        print(f"  Speedup: {seq_reduce_time/pyferris_reduce_time:.2f}x")

def memory_usage_benchmark():
    """Benchmark memory usage patterns."""
    import psutil
    import os
    
    def get_memory_usage():
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # MB
    
    def memory_intensive_task(n):
        # Create and process large list
        data = list(range(n))
        return sum(x * x for x in data)
    
    print("\nMemory Usage Benchmark")
    print("=" * 30)
    
    sizes = [1000, 5000, 10000]
    
    for size in sizes:
        print(f"\nProcessing {size} items:")
        
        # Measure PyFerris memory usage
        initial_memory = get_memory_usage()
        data = list(range(size))
        results = list(parallel_map(memory_intensive_task, data))
        peak_memory = get_memory_usage()
        memory_increase = peak_memory - initial_memory
        
        print(f"  Memory increase: {memory_increase:.1f} MB")
        print(f"  Peak memory: {peak_memory:.1f} MB")

# Run benchmarks
if __name__ == "__main__":
    benchmark_parallel_operations()
    memory_usage_benchmark()
```

## Common Patterns

### Producer-Consumer Pattern

```python
from pyferris import parallel_map
from pyferris.shared_memory import SharedQueue
import threading
import time
import random

class ProducerConsumerExample:
    def __init__(self, queue_size=100):
        self.work_queue = SharedQueue(maxsize=queue_size)
        self.result_queue = SharedQueue()
        self.producers_done = threading.Event()
    
    def producer(self, data_source, producer_id):
        """Producer function that generates work items."""
        for item in data_source:
            # Simulate work item creation
            work_item = {
                'data': item,
                'producer_id': producer_id,
                'created_at': time.time()
            }
            self.work_queue.put(work_item)
            time.sleep(0.01)  # Simulate production time
        
        print(f"Producer {producer_id} finished")
    
    def consumer(self, consumer_id):
        """Consumer function that processes work items."""
        processed_count = 0
        
        while not (self.producers_done.is_set() and self.work_queue.empty()):
            try:
                work_item = self.work_queue.get(timeout=1)
                
                # Process the work item
                result = {
                    'original_data': work_item['data'],
                    'processed_value': work_item['data'] ** 2,
                    'consumer_id': consumer_id,
                    'processing_time': time.time() - work_item['created_at']
                }
                
                # Simulate processing time
                time.sleep(random.uniform(0.01, 0.05))
                
                self.result_queue.put(result)
                processed_count += 1
                
            except:
                continue  # Timeout or empty queue
        
        print(f"Consumer {consumer_id} processed {processed_count} items")
    
    def run_parallel_processing(self, data_sources, num_consumers=4):
        """Run the producer-consumer pattern with multiple producers and consumers."""
        
        # Start producers
        producer_threads = []
        for i, data_source in enumerate(data_sources):
            thread = threading.Thread(
                target=self.producer, 
                args=(data_source, i)
            )
            thread.start()
            producer_threads.append(thread)
        
        # Start consumers
        consumer_threads = []
        for i in range(num_consumers):
            thread = threading.Thread(
                target=self.consumer, 
                args=(i,)
            )
            thread.start()
            consumer_threads.append(thread)
        
        # Wait for all producers to finish
        for thread in producer_threads:
            thread.join()
        
        # Signal that producers are done
        self.producers_done.set()
        
        # Wait for all consumers to finish
        for thread in consumer_threads:
            thread.join()
        
        # Collect all results
        results = []
        while not self.result_queue.empty():
            results.append(self.result_queue.get())
        
        return results

# Example usage
example = ProducerConsumerExample()

# Multiple data sources (producers)
data_sources = [
    range(100, 200),    # Producer 0: 100 items
    range(200, 250),    # Producer 1: 50 items
    range(300, 400),    # Producer 2: 100 items
]

print("Starting producer-consumer example...")
start_time = time.time()

results = example.run_parallel_processing(data_sources, num_consumers=4)

end_time = time.time()

print(f"\nProcessed {len(results)} items in {end_time - start_time:.2f} seconds")

# Analyze results
processing_times = [r['processing_time'] for r in results]
avg_processing_time = sum(processing_times) / len(processing_times)

print(f"Average processing time per item: {avg_processing_time:.4f} seconds")

# Show consumer workload distribution
consumer_workload = {}
for result in results:
    consumer_id = result['consumer_id']
    consumer_workload[consumer_id] = consumer_workload.get(consumer_id, 0) + 1

print("\nConsumer workload distribution:")
for consumer_id, count in consumer_workload.items():
    print(f"  Consumer {consumer_id}: {count} items ({count/len(results)*100:.1f}%)")
```

### Map-Reduce Pattern

```python
from pyferris import parallel_map, parallel_reduce, parallel_group_by
import json

def map_reduce_word_count(text_files):
    """Implement distributed word count using map-reduce pattern."""
    
    def mapper(file_path):
        """Map phase: extract words from a file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read().lower()
            
            # Simple word extraction (remove punctuation)
            import re
            words = re.findall(r'\b\w+\b', content)
            
            # Return word-count pairs
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            return word_counts
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return {}
    
    def reducer(word_count_dicts):
        """Reduce phase: combine word counts from all files."""
        total_counts = {}
        
        for word_dict in word_count_dicts:
            for word, count in word_dict.items():
                total_counts[word] = total_counts.get(word, 0) + count
        
        return total_counts
    
    print(f"Processing {len(text_files)} files...")
    
    # Map phase: process all files in parallel
    map_results = list(parallel_map(mapper, text_files))
    
    # Reduce phase: combine all results
    final_word_counts = reducer(map_results)
    
    return final_word_counts

def create_sample_text_files():
    """Create sample text files for the word count example."""
    sample_texts = [
        "The quick brown fox jumps over the lazy dog. The dog was very lazy.",
        "Python is a powerful programming language. Python makes programming easy.",
        "Parallel processing improves performance. Processing large datasets requires parallel algorithms.",
        "Data science involves analyzing large datasets. Data analysis requires powerful tools.",
        "Machine learning algorithms process data efficiently. Learning from data improves predictions."
    ]
    
    for i, text in enumerate(sample_texts):
        with open(f'sample_text_{i}.txt', 'w') as f:
            f.write(text * 100)  # Repeat text to make larger files
    
    return [f'sample_text_{i}.txt' for i in range(len(sample_texts))]

# Example usage
print("Creating sample text files...")
text_files = create_sample_text_files()

print("Running map-reduce word count...")
start_time = time.time()
word_counts = map_reduce_word_count(text_files)
end_time = time.time()

print(f"Processed {len(text_files)} files in {end_time - start_time:.2f} seconds")
print(f"Found {len(word_counts)} unique words")

# Show top 10 most frequent words
top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nTop 10 most frequent words:")
for word, count in top_words:
    print(f"  {word}: {count:,}")
```

These examples demonstrate the power and versatility of PyFerris across various domains and use cases. Each example includes complete, runnable code that showcases different aspects of the library's capabilities.

## Next Steps

- Explore the [API Reference](api_reference.md) for detailed function documentation
- Read the [Performance Guide](performance.md) for optimization tips
- Check out specialized modules like [Distributed Computing](distributed.md) and [Shared Memory](shared_memory.md)
