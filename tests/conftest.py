"""
PyFerris Test Configuration and Fixtures

This module provides shared test fixtures and configuration for all PyFerris tests.
"""

import pytest
import os
import tempfile
import shutil
import random
import time


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data files."""
    temp_dir = tempfile.mkdtemp(prefix="pyferris_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_numbers():
    """Generate sample numeric data for testing."""
    return list(range(100))


@pytest.fixture
def large_dataset():
    """Generate a larger dataset for performance testing."""
    return [random.randint(1, 1000) for _ in range(1000)]


@pytest.fixture
def sample_strings():
    """Generate sample string data for testing."""
    return [f"string_{i}" for i in range(50)]


@pytest.fixture
def cpu_intensive_task():
    """A CPU-intensive task for testing parallel performance."""
    def task(x):
        # Simulate CPU-intensive work
        result = 0
        for i in range(x * 100):
            result += i * i
        return result
    return task


@pytest.fixture
def io_intensive_task():
    """An I/O-intensive task for testing."""
    def task(x):
        # Simulate I/O work
        time.sleep(0.001)  # Small delay to simulate I/O
        return f"processed_{x}"
    return task


@pytest.fixture
def sample_csv_data():
    """Generate sample CSV data for testing."""
    return [
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "Los Angeles"},
        {"name": "Charlie", "age": 35, "city": "Chicago"},
        {"name": "Diana", "age": 28, "city": "Houston"},
        {"name": "Eve", "age": 32, "city": "Phoenix"},
    ]


@pytest.fixture
def sample_json_data():
    """Generate sample JSON data for testing."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "active": True},
            {"id": 2, "name": "Bob", "active": False},
            {"id": 3, "name": "Charlie", "active": True},
        ],
        "metadata": {
            "version": "1.0",
            "created": "2023-01-01",
            "total_users": 3
        }
    }


@pytest.fixture
def predicate_functions():
    """Generate common predicate functions for testing."""
    return {
        "is_even": lambda x: x % 2 == 0,
        "is_positive": lambda x: x > 0,
        "is_greater_than_50": lambda x: x > 50,
        "is_string_long": lambda s: len(s) > 8,
    }


@pytest.fixture
def transformation_functions():
    """Generate common transformation functions for testing."""
    return {
        "square": lambda x: x * x,
        "double": lambda x: x * 2,
        "add_one": lambda x: x + 1,
        "to_string": lambda x: str(x),
        "uppercase": lambda s: s.upper(),
    }


@pytest.fixture
def reduction_functions():
    """Generate common reduction functions for testing."""
    return {
        "sum": lambda x, y: x + y,
        "product": lambda x, y: x * y,
        "max": lambda x, y: max(x, y),
        "min": lambda x, y: min(x, y),
        "concat": lambda x, y: str(x) + str(y),
    }


@pytest.fixture
def performance_threshold():
    """Performance improvement threshold for parallel operations."""
    return 0.8  # Parallel should be at least 80% as fast as sequential (accounting for overhead)


@pytest.fixture
def temp_files(test_data_dir):
    """Create temporary files for I/O testing."""
    files = []
    for i in range(5):
        file_path = os.path.join(test_data_dir, f"test_file_{i}.txt")
        with open(file_path, 'w') as f:
            f.write(f"Content of file {i}\n" * 10)
        files.append(file_path)
    return files


@pytest.fixture
def async_task():
    """Generate an async task for testing."""
    import asyncio
    
    async def task(x):
        await asyncio.sleep(0.001)  # Small async delay
        return x * 2
    
    return task


# Helper functions for tests
def assert_results_equal(actual, expected, message="Results should be equal"):
    """Helper to assert that results are equal, handling different types."""
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        assert list(actual) == list(expected), message
    else:
        assert actual == expected, message


def assert_performance_improvement(parallel_time, sequential_time, threshold=0.8):
    """Helper to assert that parallel execution shows reasonable performance."""
    # For small datasets, parallel might be slower due to overhead
    # We check that it's not drastically slower
    if sequential_time > 0.1:  # Only check for longer operations
        assert parallel_time <= sequential_time / threshold, \
            f"Parallel execution ({parallel_time:.4f}s) should be faster than sequential ({sequential_time:.4f}s)"


# Test markers
pytest.fixture(autouse=True)
def add_markers(request):
    """Add markers for different test categories."""
    if "slow" in request.keywords:
        pytest.skip("Skipping slow test")
