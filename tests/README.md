# Pyferris Comprehensive Test Suite

This directory contains comprehensive unit tests for all Pyferris features, covering core parallel operations, I/O functionality, configuration management, and more.

## Test Structure

### Test Files

- **`test_all.py`** - Comprehensive test runner for all modules
- **`test_core.py`** - Tests for core parallel operations (map, filter, reduce, starmap)
- **`test_config.py`** - Tests for configuration management (worker count, chunk size)
- **`test_simple_io.py`** - Tests for simple I/O operations
- **`test_csv.py`** - Tests for CSV reading and writing operations
- **`test_json.py`** - Tests for JSON reading and writing operations
- **`test_executor.py`** - Tests for Executor functionality
- **`test_parallel_io.py`** - Tests for parallel I/O operations

### Test Categories

The test suite covers the following components:

1. **Core Parallel Operations** (`test_core.py`)
   - `parallel_map` functionality
   - `parallel_filter` functionality
   - `parallel_reduce` functionality
   - `parallel_starmap` functionality
   - Performance characteristics
   - Edge cases and error handling

2. **Configuration Management** (`test_config.py`)
   - Worker count configuration
   - Chunk size configuration
   - Config class functionality
   - Integration with parallel operations

3. **Simple I/O Operations** (`test_simple_io.py`)
   - Basic file operations
   - Parallel file operations
   - SimpleFileReader and SimpleFileWriter classes
   - Error handling and performance testing

4. **CSV I/O Operations** (`test_csv.py`)
   - CsvReader and CsvWriter classes
   - Reading/writing with headers and custom delimiters
   - Utility functions (read_csv, write_csv, etc.)
   - Edge cases and performance testing

5. **JSON I/O Operations** (`test_json.py`)
   - JsonReader and JsonWriter classes
   - JSON and JSON Lines format support
   - Utility functions (read_json, write_json, etc.)
   - Unicode handling and performance testing

6. **Executor Functionality** (`test_executor.py`)
   - Executor class instantiation and methods
   - Task execution capabilities
   - Resource management
   - Integration with other components

7. **Parallel I/O Operations** (`test_parallel_io.py`)
   - ParallelFileProcessor class
   - Parallel utility functions
   - File chunk processing
   - Performance comparisons

## Running Tests

### Run All Tests (Recommended)

```bash
cd /path/to/Pyferris
python tests/test_all.py
```

This will run all test modules and provide a comprehensive summary.

### Run All Tests with Different Verbosity

```bash
# Quiet mode (minimal output)
python tests/test_all.py --quiet

# Normal verbosity
python tests/test_all.py

# High verbosity (detailed output)
python tests/test_all.py -v

# Maximum verbosity
python tests/test_all.py -vv
```

### Run Specific Test Module

```bash
# Run only core tests
python tests/test_all.py --module core

# Run only CSV tests
python tests/test_all.py --module csv

# Run only JSON tests
python tests/test_all.py --module json
```

Available modules: `core`, `config`, `simple_io`, `csv`, `json`, `executor`, `parallel_io`

### Run Individual Test Files

```bash
# Run specific test file directly
python tests/test_core.py
python tests/test_csv.py
python tests/test_json.py

# Run with unittest module
python -m unittest tests.test_core
python -m unittest tests.test_csv
python -m unittest tests.test_json
```

### Run Specific Test Classes or Methods

```bash
# Run specific test class
python -m unittest tests.test_core.TestParallelMap

# Run specific test method
python -m unittest tests.test_core.TestParallelMap.test_simple_map

# Run with verbose output
python -m unittest tests.test_csv.TestCsvReader -v
```

## Test Coverage

The test suite provides comprehensive coverage of:

- ✅ **Core functionality**: All parallel operations
- ✅ **Configuration**: Worker and chunk size management
- ✅ **I/O operations**: File, CSV, and JSON handling
- ✅ **Parallel processing**: Concurrent file operations
- ✅ **Error handling**: Exception cases and edge conditions
- ✅ **Performance**: Benchmarking and optimization tests
- ✅ **Integration**: Component interaction testing

## Understanding Test Results

### Test Output

The comprehensive test runner provides:

1. **Module-by-module results** with success rates
2. **Overall statistics** and performance metrics
3. **Detailed failure/error reports** with troubleshooting info
4. **Performance analysis** and recommendations

### Success Rates

- **100%**: All tests passed - installation is perfect
- **90-99%**: Minor issues - mostly functional
- **70-89%**: Some problems - review failures
- **<70%**: Significant issues - check installation

### Common Issues and Solutions

1. **Import Errors**: Ensure Pyferris is properly installed
2. **Rust Extension Issues**: Recompile with `maturin develop`
3. **File Permission Errors**: Check directory permissions
4. **Performance Issues**: May indicate system resource constraints

## Adding New Tests

When adding new functionality to Pyferris:

1. **Create test file**: Follow naming convention `test_<module>.py`
2. **Add to test runner**: Update `test_all.py` to include new module
3. **Follow patterns**: Use existing tests as templates
4. **Include edge cases**: Test error conditions and boundary cases
5. **Add performance tests**: Include benchmarking where appropriate

## Test Development Guidelines

- **Use descriptive names**: Test methods should clearly indicate what they test
- **Include docstrings**: Document what each test verifies
- **Test edge cases**: Empty inputs, large datasets, error conditions
- **Verify correctness**: Always check that results are correct, not just that code runs
- **Performance awareness**: Include timing information for performance-critical operations
- **Clean up resources**: Use setUp/tearDown to manage test fixtures

## Continuous Integration

These tests are designed to be run in CI/CD environments:

- **Exit codes**: Test runner returns appropriate exit codes
- **Output formats**: Supports various verbosity levels
- **Modular execution**: Can run subsets of tests
- **Performance monitoring**: Tracks execution times

## Test Coverage

### Functional Interface Coverage

| Function | Test Coverage | Notes |
|----------|---------------|-------|
| `write_file()` | ✅ Complete | Basic and edge cases |
| `read_file()` | ✅ Complete | Various content types |
| `file_exists()` | ✅ Complete | Existing and non-existing files |
| `file_size()` | ✅ Complete | Various file sizes |
| `copy_file()` | ✅ Complete | Success and error cases |
| `move_file()` | ✅ Complete | Rename and move operations |
| `delete_file()` | ✅ Complete | File deletion and cleanup |
| `create_directory()` | ✅ Complete | Nested directory creation |
| `read_files_parallel()` | ✅ Complete | Multiple files, performance |
| `write_files_parallel()` | ✅ Complete | Batch writing, verification |

### Object-Oriented Interface Coverage

| Class/Method | Test Coverage | Notes |
|--------------|---------------|-------|
| `SimpleFileReader.__init__()` | ✅ Complete | Constructor validation |
| `SimpleFileReader.read_text()` | ✅ Complete | Full file reading |
| `SimpleFileReader.read_lines()` | ✅ Complete | Line-by-line reading |
| `SimpleFileWriter.__init__()` | ✅ Complete | Constructor validation |
| `SimpleFileWriter.write_text()` | ✅ Complete | Text writing |
| `SimpleFileWriter.append_text()` | ✅ Complete | Text appending |

### Error Handling Coverage

| Error Type | Test Coverage | Scenarios Tested |
|------------|---------------|------------------|
| File Not Found | ✅ Complete | Reading non-existent files |
| Permission Denied | ✅ Complete | Invalid write locations |
| Invalid Paths | ✅ Complete | Malformed file paths |
| Class Method Errors | ✅ Complete | Reader/Writer error cases |

### Performance Testing Coverage

| Performance Test | Coverage | Purpose |
|------------------|----------|---------|
| Large File Operations | ✅ Complete | 1MB+ file handling |
| Parallel vs Sequential | ✅ Complete | Speed comparison |
| Memory Usage | ✅ Partial | Basic memory tracking |
| Batch Processing | ✅ Complete | Multiple file performance |

## Test Results and Expectations

### Expected Test Results

When all tests pass, you should see output similar to:

```
test_copy_file (TestSimpleFileOperations.test_copy_file) ... ok
test_create_directory (TestSimpleFileOperations.test_create_directory) ... ok
test_delete_file (TestSimpleFileOperations.test_delete_file) ... ok
test_file_exists (TestSimpleFileOperations.test_file_exists) ... ok
test_file_size (TestSimpleFileOperations.test_file_size) ... ok
test_move_file (TestSimpleFileOperations.test_move_file) ... ok
test_write_and_read_file (TestSimpleFileOperations.test_write_and_read_file) ... ok
test_parallel_read_files (TestParallelFileOperations.test_parallel_read_files) ... ok
test_parallel_write_files (TestParallelFileOperations.test_parallel_write_files) ... ok
test_read_lines (TestSimpleFileReader.test_read_lines) ... ok
test_read_text (TestSimpleFileReader.test_read_text) ... ok
test_reader_initialization (TestSimpleFileReader.test_reader_initialization) ... ok
test_append_text (TestSimpleFileWriter.test_append_text) ... ok
test_write_text (TestSimpleFileWriter.test_write_text) ... ok
test_writer_initialization (TestSimpleFileWriter.test_writer_initialization) ... ok
test_copy_nonexistent_file (TestErrorHandling.test_copy_nonexistent_file) ... ok
test_read_nonexistent_file (TestErrorHandling.test_read_nonexistent_file) ... ok
test_reader_nonexistent_file (TestErrorHandling.test_reader_nonexistent_file) ... ok
test_write_to_invalid_path (TestErrorHandling.test_write_to_invalid_path) ... ok
test_large_file_operations (TestPerformance.test_large_file_operations) ... ok
test_parallel_vs_sequential_performance (TestPerformance.test_parallel_vs_sequential_performance) ... ok

----------------------------------------------------------------------
Ran 21 tests in 0.030s

OK

============================================================
TEST SUMMARY
============================================================
Tests run: 21
Failures: 0
Errors: 0
Success rate: 100.0%
```

### Performance Benchmarks

The performance tests will show output like:

```
Sequential time: 0.0001s
Parallel time: 0.0009s  
Speedup: 0.16x
```

**Note**: Parallel operations may be slower than sequential for small files due to overhead. This is expected and normal behavior.

## Test Environment

### Requirements

- Python 3.7+
- Pyferris module installed and working
- Sufficient disk space for temporary test files
- Write permissions in the test directory

### Test Data

Tests create temporary files and directories during execution:
- Small text files (few bytes to KB)
- Medium files (several KB)
- Large files (1MB+ for performance tests)
- Multiple files for parallel testing

All test data is automatically cleaned up after each test.

### Platform Compatibility

Tests are designed to work on:
- ✅ Linux (primary development platform)
- ✅ macOS (compatible)
- ✅ Windows (compatible with path handling)

## Interpreting Test Results

### Success Indicators

- **All tests pass**: Module is working correctly
- **Performance tests complete**: Parallel operations are functional
- **Error tests pass**: Error handling is robust
- **100% success rate**: Full feature compatibility

### Warning Signs

- **Individual test failures**: Specific functionality issues
- **Performance test failures**: Timing or resource issues
- **Error handling failures**: Exception handling problems
- **Setup/teardown issues**: File system or permission problems

### Common Issues

#### Permission Errors
```
PermissionError: [Errno 13] Permission denied
```
**Solution**: Run tests with appropriate permissions or in a writable directory.

#### Import Errors
```
ModuleNotFoundError: No module named 'pyferris'
```
**Solution**: Ensure Pyferris is properly installed: `pip install pyferris`

#### Path Issues on Windows
```
OSError: [Errno 22] Invalid argument
```
**Solution**: Use proper path separators or run in compatible environment.

## Extending Tests

### Adding New Tests

To add tests for new functionality:

1. **Create test method** in appropriate test class:
```python
def test_new_feature(self):
    """Test new feature functionality."""
    # Test implementation
    self.assertEqual(expected, actual)
```

2. **Follow naming convention**: `test_` prefix for methods

3. **Include setup/teardown**: Use `setUp()` and `tearDown()` methods

4. **Add documentation**: Clear docstrings explaining test purpose

### Test Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always clean up temporary files
3. **Descriptive names**: Clear test method names
4. **Edge cases**: Test boundary conditions
5. **Error conditions**: Test both success and failure paths

### Adding Performance Tests

For new performance-critical features:

```python
def test_performance_feature(self):
    """Test performance of new feature."""
    import time
    
    # Setup test data
    setup_data()
    
    # Measure performance
    start_time = time.time()
    perform_operation()
    execution_time = time.time() - start_time
    
    # Assert reasonable performance
    self.assertLess(execution_time, expected_max_time)
    
    # Cleanup
    cleanup_data()
```

## Continuous Integration

### Automated Testing

Tests are designed to be run in CI/CD environments:

```bash
# CI script example
python -m pytest tests/ -v --tb=short
```

### Test Reporting

Generate test reports:

```bash
# With coverage (if coverage.py is installed)
coverage run tests/test_simple_io.py
coverage report -m

# With XML output for CI
python -m unittest tests.test_simple_io 2>&1 | tee test_results.log
```

## Maintenance

### Regular Test Updates

- Update tests when adding new features
- Verify tests pass on new Python versions  
- Update performance baselines as needed
- Review and update error handling tests

### Test Data Management

- Monitor test execution time
- Clean up any orphaned test files
- Verify disk space usage during tests
- Update test data sizes for performance tests

## Contributing

When contributing to the test suite:

1. **Run existing tests** before making changes
2. **Add tests for new features** 
3. **Update tests for modified features**
4. **Ensure all tests pass** before submitting
5. **Document test changes** in commit messages

## Support

For test-related issues:

1. **Check test output** for specific error messages
2. **Verify environment setup** (Python version, dependencies)
3. **Run individual tests** to isolate issues
4. **Check file permissions** and disk space
5. **Report bugs** with full test output and environment details
