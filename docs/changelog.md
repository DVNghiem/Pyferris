# Changelog

All notable changes to PyFerris will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite with user guides and examples
- Advanced async operations with backpressure control
- Enhanced shared memory operations with multi-dimensional arrays
- Performance optimization guides and benchmarking tools
- Contributing guidelines for developers

### Changed
- Improved error handling across all modules
- Better memory management in large dataset processing
- Enhanced progress tracking with customizable reporters

### Fixed
- Memory leaks in long-running operations
- Race conditions in shared memory access
- Error propagation in nested parallel operations

## [0.3.1] - 2024-01-15

### Added
- Distributed computing support with cluster management
- Advanced caching mechanisms with LRU and TTL policies
- Shared memory operations for zero-copy data sharing
- Async operations module for I/O-bound workloads
- Comprehensive scheduler implementations (priority, work-stealing)
- Memory pools for efficient buffer management
- Pipeline operations for chaining transformations

### Changed
- Improved parallel I/O performance by 40%
- Better error handling with detailed error types
- Enhanced executor with callback support
- Optimized memory usage in large dataset operations

### Fixed
- Deadlock issues in nested parallel operations
- Memory fragmentation in long-running processes
- Incorrect error propagation in worker threads
- Performance regression in small dataset processing

### Security
- Added input validation for all public APIs
- Improved memory safety in Rust components

## [0.3.0] - 2023-12-10

### Added
- New executor framework for advanced task management
- Concurrent data structures (HashMap, Queue)
- Memory-mapped file operations
- Progress tracking with customizable callbacks
- Batch processing capabilities
- Result collectors with filtering options

### Changed
- **BREAKING**: Renamed `map_parallel` to `parallel_map` for consistency
- **BREAKING**: Changed executor interface for better usability
- Improved performance for CPU-intensive operations by 25%
- Better integration with NumPy arrays

### Deprecated
- Old-style configuration syntax (will be removed in 0.4.0)
- Legacy executor methods (use new Executor class instead)

### Removed
- Python 3.8 support (minimum version is now 3.10)
- Deprecated utility functions from 0.2.x

### Fixed
- Memory leaks in repeated parallel operations
- Incorrect handling of empty iterables
- Race conditions in progress reporting

## [0.2.5] - 2023-11-20

### Added
- CSV and JSON parallel processing utilities
- File reader/writer with automatic format detection
- Simple I/O operations for common use cases

### Fixed
- Handle Unicode errors in file processing
- Improve error messages for I/O operations
- Fix hanging on malformed input files

## [0.2.4] - 2023-11-05

### Added
- Configuration management system
- Automatic worker count optimization
- Memory usage monitoring

### Changed
- Improved error handling in worker processes
- Better resource cleanup on process termination

### Fixed
- Windows compatibility issues
- Process cleanup on KeyboardInterrupt
- Memory usage spikes with large datasets

## [0.2.3] - 2023-10-15

### Added
- Support for Python 3.12
- Enhanced error reporting with stack traces
- Timeout support for long-running operations

### Fixed
- Segmentation faults on macOS with large datasets
- Incorrect results order in some edge cases
- Resource leaks in error conditions

## [0.2.2] - 2023-09-28

### Added
- Parallel filter operations
- Parallel reduce operations with custom combiners
- Group-by operations for data aggregation

### Changed
- Optimized chunk size calculation for better performance
- Improved load balancing across workers

### Fixed
- Handle exceptions in user functions properly
- Fix ordering issues in parallel reduce
- Correct handling of generator inputs

## [0.2.1] - 2023-09-10

### Added
- Basic sorting operations (parallel sort, argsort)
- Integration with common Python libraries (NumPy, Pandas)
- Examples and tutorials in documentation

### Fixed
- Installation issues on older Linux distributions
- Compatibility with PyPy
- Memory usage optimization for small datasets

## [0.2.0] - 2023-08-25

### Added
- Core parallel operations (map, filter, reduce)
- Basic executor with thread pool management
- Simple caching mechanisms
- Cross-platform support (Linux, macOS, Windows)

### Changed
- **BREAKING**: New API design with better ergonomics
- Significant performance improvements over 0.1.x
- Better integration with Python ecosystem

### Fixed
- Stability issues with high worker counts
- Memory management improvements
- Better error handling and reporting

## [0.1.5] - 2023-08-01

### Added
- Initial async operations support
- Basic shared memory capabilities
- Rudimentary progress tracking

### Fixed
- Critical bugs in worker synchronization
- Memory leaks in repeated operations
- Platform-specific compilation issues

## [0.1.4] - 2023-07-15

### Added
- Support for custom chunk sizes
- Basic performance monitoring
- Initial documentation

### Changed
- Improved worker management
- Better error propagation

### Fixed
- Handle empty inputs correctly
- Fix worker process cleanup
- Resolve packaging issues

## [0.1.3] - 2023-07-01

### Added
- Basic parallel map functionality
- Simple executor implementation
- Core error types

### Fixed
- Installation problems on Windows
- Basic functionality bugs
- Documentation issues

## [0.1.2] - 2023-06-20

### Added
- Initial project structure
- Basic Rust-Python bindings
- Simple parallel operations

### Fixed
- Build system issues
- Import problems
- Basic stability issues

## [0.1.1] - 2023-06-10

### Added
- Project initialization
- Basic PyO3 setup
- Initial parallel processing proof of concept

### Fixed
- Compilation issues
- Basic functionality

## [0.1.0] - 2023-06-01

### Added
- Initial release
- Basic parallel processing framework
- Core Rust implementation with Python bindings

---

## Legend

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

## Migration Guides

### Migrating from 0.2.x to 0.3.x

The main breaking changes in 0.3.x are:

1. **Function naming**: `map_parallel` → `parallel_map`
   ```python
   # Old (0.2.x)
   from pyferris import map_parallel
   results = map_parallel(func, data)
   
   # New (0.3.x)
   from pyferris import parallel_map
   results = parallel_map(func, data)
   ```

2. **Executor interface**: New class-based approach
   ```python
   # Old (0.2.x)
   from pyferris import execute_parallel
   results = execute_parallel(tasks, workers=4)
   
   # New (0.3.x)
   from pyferris import Executor
   with Executor(max_workers=4) as executor:
       results = executor.map(func, data)
   ```

3. **Configuration**: New structured configuration
   ```python
   # Old (0.2.x)
   import pyferris
   pyferris.set_workers(4)
   pyferris.set_chunk_size(100)
   
   # New (0.3.x)
   from pyferris import Config
   config = Config(max_workers=4, chunk_size=100)
   # Pass config to operations as needed
   ```

### Migrating from 0.1.x to 0.2.x

Major API redesign in 0.2.x:

1. **Import structure**: Consolidated imports
   ```python
   # Old (0.1.x)
   from pyferris.core import parallel_map
   from pyferris.executor import Executor
   
   # New (0.2.x+)
   from pyferris import parallel_map, Executor
   ```

2. **Error handling**: New exception types
   ```python
   # Old (0.1.x)
   try:
       results = parallel_map(func, data)
   except Exception as e:
       # Generic exception handling
       
   # New (0.2.x+)
   from pyferris import PyFerrisError, WorkerError
   try:
       results = parallel_map(func, data)
   except WorkerError as e:
       # Handle worker-specific errors
   except PyFerrisError as e:
       # Handle other PyFerris errors
   ```

## Support Policy

- **Latest major version** (0.3.x): Full support with new features and bug fixes
- **Previous major version** (0.2.x): Security fixes and critical bug fixes only
- **Older versions** (0.1.x): No longer supported

We recommend upgrading to the latest version for the best performance and security.
