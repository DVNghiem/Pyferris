# Contributing to PyFerris

Thank you for your interest in contributing to PyFerris! This guide will help you get started with contributing to the project, whether you're fixing bugs, adding features, improving documentation, or enhancing performance.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Code Structure](#code-structure)
4. [Contribution Guidelines](#contribution-guidelines)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Performance Optimization](#performance-optimization)
8. [Rust Development](#rust-development)
9. [Python Development](#python-development)
10. [Submitting Changes](#submitting-changes)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Rust 1.60 or higher
- Git
- A GitHub account

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix issues in existing functionality
- **New features**: Add new parallel processing capabilities
- **Performance improvements**: Optimize existing algorithms
- **Documentation**: Improve guides, examples, and API documentation
- **Tests**: Add or improve test coverage
- **Examples**: Create real-world usage examples

## Development Environment Setup

### 1. Fork and Clone the Repository

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/pyferris.git
cd pyferris

# Add the upstream remote
git remote add upstream https://github.com/original/pyferris.git
```

### 2. Set Up Python Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]
```

### 3. Set Up Rust Environment

```bash
# Install Rust if you haven't already
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install development tools
cargo install cargo-watch
cargo install cargo-audit
cargo install cargo-tarpaulin  # For code coverage
```

### 4. Build the Project

```bash
# Build Rust components
cargo build --release

# Build Python extension
python setup.py develop

# Or use maturin for development builds
pip install maturin
maturin develop
```

### 5. Verify Installation

```bash
# Run basic tests
python -c "import pyferris; print('PyFerris imported successfully')"
pytest tests/ -v
```

## Code Structure

Understanding the codebase structure helps you navigate and contribute effectively:

```
pyferris/
├── src/                    # Rust source code
│   ├── lib.rs             # Main Rust library entry point
│   ├── core/              # Core parallel operations
│   ├── executor/          # Task execution engine
│   ├── io/                # File I/O operations
│   ├── memory/            # Memory management
│   ├── concurrent/        # Concurrent data structures
│   ├── async_ops/         # Async operations
│   ├── distributed/       # Distributed computing
│   └── utils/             # Utility functions
├── pyferris/              # Python package
│   ├── __init__.py        # Main Python interface
│   ├── core.py            # Core function wrappers
│   ├── executor.py        # Executor Python interface
│   └── io/                # I/O Python modules
├── tests/                 # Test suite
│   ├── test_core.py       # Core functionality tests
│   ├── test_executor.py   # Executor tests
│   └── conftest.py        # Test configuration
├── docs/                  # Documentation
├── examples/              # Usage examples
├── benchmarks/            # Performance benchmarks
├── Cargo.toml             # Rust dependencies
├── pyproject.toml         # Python project configuration
└── README.md
```

### Key Components

1. **Rust Core (`src/`)**: High-performance implementations
2. **Python Interface (`pyferris/`)**: Python bindings and convenience functions
3. **Tests (`tests/`)**: Comprehensive test suite
4. **Documentation (`docs/`)**: User guides and API documentation

## Contribution Guidelines

### Code Style

#### Python Code Style

We follow PEP 8 with some specific guidelines:

```python
# Good: Clear function names and type hints
def parallel_process_data(
    data: List[Any], 
    processor_func: Callable[[Any], Any],
    max_workers: Optional[int] = None
) -> Iterator[Any]:
    """Process data items in parallel.
    
    Args:
        data: List of items to process
        processor_func: Function to apply to each item
        max_workers: Maximum number of worker threads
        
    Returns:
        Iterator of processed results
    """
    pass

# Good: Use descriptive variable names
processing_results = []
worker_count = get_optimal_worker_count()

# Good: Handle errors gracefully
try:
    result = risky_operation()
except SpecificError as e:
    logger.warning(f"Operation failed: {e}")
    result = default_value
```

#### Rust Code Style

We follow standard Rust conventions:

```rust
// Good: Clear function signatures with proper error handling
pub fn parallel_map<T, U, F>(
    data: &[T],
    func: F,
    max_workers: Option<usize>,
) -> Result<Vec<U>, PyFerrisError>
where
    T: Send + Sync,
    U: Send,
    F: Fn(&T) -> U + Send + Sync,
{
    // Implementation
}

// Good: Use descriptive names and proper error types
pub struct ProcessingConfig {
    pub max_workers: usize,
    pub chunk_size: usize,
    pub timeout: Duration,
}

// Good: Document public APIs
/// Represents a parallel processing executor.
/// 
/// This executor manages a pool of worker threads and distributes
/// tasks across them for parallel execution.
pub struct Executor {
    thread_pool: ThreadPool,
    config: ProcessingConfig,
}
```

### Git Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make small, focused commits**:
   ```bash
   git add specific_files
   git commit -m "Add: specific feature description"
   ```

3. **Keep your branch up to date**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

4. **Write good commit messages**:
   ```
   Add: parallel CSV reader with chunking support
   
   - Implement chunked reading for large CSV files
   - Add progress tracking for long-running operations
   - Include comprehensive error handling
   - Add tests for various CSV formats
   ```

### Commit Message Format

Use the following prefixes:
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for improvements to existing features
- `Remove:` for removing code/features
- `Doc:` for documentation changes
- `Test:` for test-related changes
- `Perf:` for performance improvements

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_core.py -v

# Run with coverage
pytest tests/ --cov=pyferris --cov-report=html

# Run Rust tests
cargo test

# Run specific Rust test
cargo test test_parallel_map
```

### Writing Tests

#### Python Tests

```python
import pytest
import numpy as np
from pyferris import parallel_map

class TestParallelMap:
    """Test suite for parallel_map function."""
    
    def test_basic_functionality(self):
        """Test basic parallel mapping."""
        data = list(range(100))
        results = list(parallel_map(lambda x: x * 2, data))
        expected = [x * 2 for x in data]
        assert results == expected
    
    def test_empty_input(self):
        """Test handling of empty input."""
        results = list(parallel_map(lambda x: x, []))
        assert results == []
    
    def test_error_handling(self):
        """Test error handling in worker functions."""
        def failing_func(x):
            if x == 5:
                raise ValueError("Test error")
            return x * 2
        
        data = list(range(10))
        with pytest.raises(ValueError, match="Test error"):
            list(parallel_map(failing_func, data))
    
    @pytest.mark.parametrize("worker_count", [1, 2, 4, 8])
    def test_different_worker_counts(self, worker_count):
        """Test with different numbers of workers."""
        data = list(range(50))
        results = list(parallel_map(
            lambda x: x ** 2, 
            data, 
            max_workers=worker_count
        ))
        expected = [x ** 2 for x in data]
        assert results == expected
    
    def test_large_dataset(self):
        """Test performance with large dataset."""
        data = list(range(10000))
        results = list(parallel_map(lambda x: x + 1, data))
        assert len(results) == len(data)
        assert all(r == d + 1 for r, d in zip(results, data))
```

#### Rust Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Arc;
    
    #[test]
    fn test_parallel_map_basic() {
        let data = vec![1, 2, 3, 4, 5];
        let func = |x: &i32| x * 2;
        
        let result = parallel_map(&data, func, Some(2)).unwrap();
        let expected = vec![2, 4, 6, 8, 10];
        
        assert_eq!(result, expected);
    }
    
    #[test]
    fn test_parallel_map_empty() {
        let data: Vec<i32> = vec![];
        let func = |x: &i32| x * 2;
        
        let result = parallel_map(&data, func, None).unwrap();
        assert!(result.is_empty());
    }
    
    #[test]
    fn test_concurrent_access() {
        use std::sync::atomic::{AtomicUsize, Ordering};
        
        let counter = Arc::new(AtomicUsize::new(0));
        let data = vec![1; 1000];
        
        let counter_clone = Arc::clone(&counter);
        let func = move |_: &i32| {
            counter_clone.fetch_add(1, Ordering::SeqCst);
            1
        };
        
        let _result = parallel_map(&data, func, Some(4)).unwrap();
        assert_eq!(counter.load(Ordering::SeqCst), 1000);
    }
    
    #[test]
    fn test_error_propagation() {
        let data = vec![1, 2, 3, 4, 5];
        let func = |x: &i32| -> Result<i32, &'static str> {
            if *x == 3 {
                Err("Test error")
            } else {
                Ok(x * 2)
            }
        };
        
        // This should fail because of the error in processing
        // (Implementation depends on error handling strategy)
    }
}
```

### Performance Tests

```python
import time
import pytest
from pyferris import parallel_map

class TestPerformance:
    """Performance regression tests."""
    
    def test_parallel_speedup(self):
        """Test that parallel processing provides speedup."""
        
        def cpu_intensive_task(n):
            # Simulate CPU-intensive work
            total = 0
            for i in range(n * 1000):
                total += i * i
            return total
        
        data = [100] * 100
        
        # Sequential processing
        start_time = time.time()
        sequential_results = [cpu_intensive_task(x) for x in data]
        sequential_time = time.time() - start_time
        
        # Parallel processing
        start_time = time.time()
        parallel_results = list(parallel_map(cpu_intensive_task, data, max_workers=4))
        parallel_time = time.time() - start_time
        
        # Verify results are the same
        assert parallel_results == sequential_results
        
        # Verify speedup (should be at least 1.5x on multi-core systems)
        speedup = sequential_time / parallel_time
        assert speedup > 1.5, f"Expected speedup > 1.5, got {speedup:.2f}"
    
    @pytest.mark.benchmark
    def test_memory_efficiency(self):
        """Test memory usage doesn't grow excessively."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process large dataset
        large_data = list(range(100000))
        results = list(parallel_map(lambda x: x * 2, large_data))
        
        final_memory = process.memory_info().rss
        memory_growth = (final_memory - initial_memory) / (1024 * 1024)  # MB
        
        # Memory growth should be reasonable (less than 100MB for this test)
        assert memory_growth < 100, f"Memory growth too high: {memory_growth:.2f}MB"
```

## Documentation

### Writing Documentation

#### API Documentation

```python
def parallel_map(
    func: Callable[[T], U], 
    iterable: Iterable[T],
    max_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
    progress: Optional[ProgressTracker] = None
) -> Iterator[U]:
    """Apply a function to every item in an iterable in parallel.
    
    This function distributes the work across multiple worker processes,
    making it ideal for CPU-bound tasks that can benefit from parallelization.
    
    Args:
        func: Function to apply to each item. Must be picklable.
        iterable: Input data to process. Can be any iterable.
        max_workers: Maximum number of worker processes. If None,
            uses the number of CPU cores.
        chunk_size: Number of items to process per worker at once.
            If None, automatically determined based on data size.
        progress: Optional progress tracker for monitoring execution.
            
    Returns:
        Iterator yielding results in the same order as input.
        
    Raises:
        ValueError: If max_workers is less than 1.
        TypeError: If func is not callable.
        RuntimeError: If worker processes fail to start.
        
    Example:
        >>> data = range(1000)
        >>> results = parallel_map(lambda x: x * x, data)
        >>> squared_values = list(results)
        
    Note:
        The function must be picklable to be sent to worker processes.
        Lambda functions work in most cases, but complex closures may not.
        
    See Also:
        - parallel_filter: For filtering operations
        - parallel_reduce: For reduction operations
        - Executor: For more advanced task management
    """
```

#### User Guide Documentation

Use clear, practical examples:

```markdown
# Working with Large Datasets

When processing large datasets, PyFerris provides several strategies 
to optimize performance and memory usage.

## Chunking Strategy

For very large datasets, process data in chunks:

```python
from pyferris import parallel_map

def process_large_dataset(data_source, chunk_size=10000):
    """Process a large dataset efficiently."""
    
    def process_chunk(chunk):
        # Your processing logic here
        return [item * 2 for item in chunk]
    
    # Read and process data in chunks
    results = []
    for i in range(0, len(data_source), chunk_size):
        chunk = data_source[i:i + chunk_size]
        chunk_results = parallel_map(process_item, chunk)
        results.extend(list(chunk_results))
    
    return results
```

## Memory Management

Monitor memory usage during processing:

```python
import psutil
from pyferris import parallel_map

def memory_aware_processing(data):
    """Process data with memory monitoring."""
    
    def check_memory():
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 80:
            print(f"Warning: Memory usage at {memory_percent}%")
    
    # Process with periodic memory checks
    results = []
    for i, item in enumerate(data):
        if i % 1000 == 0:
            check_memory()
        
        result = process_item(item)
        results.append(result)
    
    return results
```
```

### Documentation Standards

1. **All public APIs must have docstrings**
2. **Include practical examples**
3. **Document error conditions**
4. **Provide cross-references to related functions**
5. **Keep examples runnable and testable**

## Performance Optimization

### Profiling

Use profiling tools to identify bottlenecks:

```python
import cProfile
import pstats
from pyferris import parallel_map

def profile_parallel_operation():
    """Profile a parallel operation to identify bottlenecks."""
    
    def test_function(n):
        return sum(i * i for i in range(n))
    
    data = [1000] * 1000
    
    # Profile the operation
    profiler = cProfile.Profile()
    profiler.enable()
    
    results = list(parallel_map(test_function, data))
    
    profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions

if __name__ == "__main__":
    profile_parallel_operation()
```

### Benchmarking

Create reproducible benchmarks:

```python
import time
import statistics
from pyferris import parallel_map

class ParallelMapBenchmark:
    """Benchmark suite for parallel_map performance."""
    
    def __init__(self, iterations=10):
        self.iterations = iterations
    
    def benchmark_cpu_bound(self, data_sizes, worker_counts):
        """Benchmark CPU-bound operations."""
        
        def cpu_task(n):
            return sum(i * i for i in range(n))
        
        results = {}
        
        for data_size in data_sizes:
            data = [100] * data_size
            results[data_size] = {}
            
            for workers in worker_counts:
                times = []
                
                for _ in range(self.iterations):
                    start = time.time()
                    list(parallel_map(cpu_task, data, max_workers=workers))
                    times.append(time.time() - start)
                
                results[data_size][workers] = {
                    'mean': statistics.mean(times),
                    'stdev': statistics.stdev(times),
                    'min': min(times),
                    'max': max(times)
                }
        
        return results
    
    def print_results(self, results):
        """Print benchmark results in a readable format."""
        
        for data_size, worker_results in results.items():
            print(f"\nData size: {data_size}")
            print("Workers | Mean (s) | StdDev | Min (s) | Max (s)")
            print("-" * 50)
            
            for workers, stats in worker_results.items():
                print(f"{workers:7d} | {stats['mean']:8.3f} | "
                      f"{stats['stdev']:6.3f} | {stats['min']:7.3f} | "
                      f"{stats['max']:7.3f}")

# Run benchmark
if __name__ == "__main__":
    benchmark = ParallelMapBenchmark(iterations=5)
    results = benchmark.benchmark_cpu_bound(
        data_sizes=[100, 500, 1000], 
        worker_counts=[1, 2, 4, 8]
    )
    benchmark.print_results(results)
```

## Rust Development

### Setting Up Rust Development

```bash
# Install additional tools
cargo install cargo-expand  # For macro expansion
cargo install cargo-edit    # For editing Cargo.toml
rustup component add rustfmt
rustup component add clippy
```

### Rust Best Practices

```rust
// Use proper error handling
use thiserror::Error;

#[derive(Error, Debug)]
pub enum PyFerrisError {
    #[error("Invalid worker count: {0}")]
    InvalidWorkerCount(usize),
    
    #[error("Processing failed: {source}")]
    ProcessingError {
        #[from]
        source: Box<dyn std::error::Error + Send + Sync>,
    },
}

// Use proper logging
use log::{debug, info, warn, error};

pub fn parallel_process<T, U, F>(
    data: &[T],
    func: F,
    workers: usize,
) -> Result<Vec<U>, PyFerrisError>
where
    T: Send + Sync,
    U: Send,
    F: Fn(&T) -> U + Send + Sync,
{
    info!("Starting parallel processing with {} workers", workers);
    
    if workers == 0 {
        return Err(PyFerrisError::InvalidWorkerCount(workers));
    }
    
    debug!("Processing {} items", data.len());
    
    // Implementation...
    
    info!("Parallel processing completed successfully");
    Ok(results)
}
```

### Python-Rust Integration

```rust
use pyo3::prelude::*;
use pyo3::types::PyList;

#[pyfunction]
#[pyo3(name = "parallel_map")]
pub fn py_parallel_map(
    py: Python,
    func: PyObject,
    data: &PyList,
    max_workers: Option<usize>,
) -> PyResult<PyObject> {
    // Convert Python data to Rust
    let rust_data: Vec<PyObject> = data.iter()
        .map(|item| item.to_object(py))
        .collect();
    
    // Process in parallel
    let results = parallel_map_impl(&rust_data, |item| {
        // Call Python function from Rust
        Python::with_gil(|py| {
            func.call1(py, (item,))
        })
    }, max_workers)?;
    
    // Convert results back to Python
    let py_results = PyList::new(py, results);
    Ok(py_results.to_object(py))
}
```

## Python Development

### Python Interface Design

```python
from typing import Any, Callable, Iterable, Iterator, Optional, TypeVar
from abc import ABC, abstractmethod

T = TypeVar('T')
U = TypeVar('U')

class ProgressTracker(ABC):
    """Abstract base class for progress tracking."""
    
    @abstractmethod
    def update(self, amount: int = 1) -> None:
        """Update progress by specified amount."""
        pass
    
    @abstractmethod
    def set_description(self, desc: str) -> None:
        """Set progress description."""
        pass

class DefaultProgressTracker(ProgressTracker):
    """Default progress tracker implementation."""
    
    def __init__(self, total: Optional[int] = None, desc: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = desc
    
    def update(self, amount: int = 1) -> None:
        self.current += amount
        if self.total:
            percent = (self.current / self.total) * 100
            print(f"\r{self.description}: {percent:.1f}%", end="", flush=True)
    
    def set_description(self, desc: str) -> None:
        self.description = desc

def parallel_map(
    func: Callable[[T], U],
    iterable: Iterable[T],
    max_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
    progress: Optional[ProgressTracker] = None
) -> Iterator[U]:
    """High-level interface to parallel mapping."""
    
    # Import the Rust implementation
    from ._pyferris import py_parallel_map
    
    # Convert iterable to list if needed
    if not isinstance(iterable, (list, tuple)):
        iterable = list(iterable)
    
    # Set up progress tracking
    if progress is None and len(iterable) > 1000:
        progress = DefaultProgressTracker(total=len(iterable))
    
    # Call Rust implementation
    results = py_parallel_map(func, iterable, max_workers)
    
    # Yield results with progress updates
    for i, result in enumerate(results):
        if progress:
            progress.update()
        yield result
```

## Submitting Changes

### Before Submitting

1. **Run all tests**:
   ```bash
   pytest tests/ -v
   cargo test
   ```

2. **Check code formatting**:
   ```bash
   black pyferris/
   isort pyferris/
   cargo fmt
   ```

3. **Run linting**:
   ```bash
   flake8 pyferris/
   mypy pyferris/
   cargo clippy
   ```

4. **Update documentation** if needed

5. **Add tests** for new functionality

### Creating a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create pull request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Links to related issues
   - Screenshots if applicable

3. **Pull request template**:
   ```markdown
   ## Description
   Brief description of changes made.

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Performance improvement
   - [ ] Documentation update
   - [ ] Breaking change

   ## Testing
   - [ ] Added tests for new functionality
   - [ ] All existing tests pass
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes (or clearly documented)
   ```

### Review Process

1. **Automated checks** will run (CI/CD pipeline)
2. **Code review** by maintainers
3. **Feedback incorporation** if needed
4. **Final approval** and merge

## Community Guidelines

- **Be respectful** and constructive in discussions
- **Ask questions** if something is unclear
- **Help others** who are contributing
- **Follow the code of conduct**

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check existing docs first
- **Examples**: Look at example code for patterns

Thank you for contributing to PyFerris! Your efforts help make parallel processing in Python faster and more accessible for everyone.
