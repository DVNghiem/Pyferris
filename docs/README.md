# PyFerris Documentation

Welcome to the comprehensive documentation for **PyFerris**, a high-performance parallel processing library for Python, powered by Rust and PyO3.

## Table of Contents

### Getting Started
1. [Getting Started](getting_started.md) - Installation, setup, and your first PyFerris program
2. [Core Features](core.md) - Parallel operations, batch processing, and progress tracking

### Core Components
3. [Executor](executor.md) - Task execution and thread pool management
4. [I/O Operations](io.md) - File I/O and parallel data processing
5. [Async Operations](async_ops.md) - Asynchronous parallel processing for I/O-bound workloads
6. [Shared Memory](shared_memory.md) - Zero-copy data sharing between parallel workers

### Reference and Examples
7. [API Reference](api_reference.md) - Complete API documentation
8. [Examples](examples.md) - Practical usage examples and real-world use cases

### Performance and Optimization
9. [Performance Guide](performance.md) - Optimization tips and benchmarks
10. [Troubleshooting](troubleshooting.md) - Common issues and solutions

### Development
11. [Contributing Guide](contributing.md) - How to contribute to PyFerris development
12. [Changelog](changelog.md) - Version history and migration guides

## Quick Links

- **[Installation Guide](getting_started.md#installation)** - Get PyFerris up and running
- **[Quick Start](getting_started.md#quick-start)** - Your first PyFerris program
- **[Core Operations](core.md)** - Basic parallel processing functions
- **[Examples](examples.md)** - Real-world usage examples
- **[Performance Tips](performance.md)** - How to get the best performance
- **[API Reference](api_reference.md)** - Complete function and class documentation
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[Contributing](contributing.md)** - How to contribute to the project

## About PyFerris

PyFerris is designed to provide seamless, high-performance parallel processing for Python applications by leveraging Rust's speed and memory safety. It bypasses Python's Global Interpreter Lock (GIL) for true parallel execution and is suitable for everything from embedded systems to enterprise-grade applications.

### Key Features

- **True Parallel Execution**: Bypass Python's GIL using Rust
- **High Performance**: 2-5x faster than Python's built-in parallel libraries
- **Memory Safe**: Rust's memory safety guarantees
- **Easy to Use**: Pythonic API with minimal learning curve
- **Comprehensive**: Full suite of parallel operations and data structures
- **Cross-Platform**: Works on Linux, macOS, and Windows

### Architecture

PyFerris uses PyO3 to create Python bindings for Rust code, allowing Python developers to leverage Rust's performance without learning Rust. The library is structured into several modules:

- **Core**: Basic parallel operations (map, filter, reduce, etc.)
- **Executor**: Advanced task execution and thread management
- **I/O**: Parallel file operations
- **Async**: Asynchronous parallel processing
- **Shared Memory**: Inter-process data sharing
- **Concurrent**: Thread-safe data structures
- **Distributed**: Cluster computing capabilities

## Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for details on how to get started with development, testing, and submitting changes.

## License

PyFerris is licensed under the MIT License. See [LICENSE](../LICENSE) for details.
