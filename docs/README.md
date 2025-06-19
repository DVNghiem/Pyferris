# PyFerris Documentation

Welcome to the PyFerris documentation! This guide provides comprehensive information about PyFerris features, APIs, and usage examples.

## Table of Contents

- [Core Features](core.md) - Parallel operations and basic functionality
- [Executor](executor.md) - Task execution and Rayon-powered thread pool management
- [Advanced Features](advanced.md) - Advanced parallel operations and batch processing
- [I/O Operations](io.md) - File I/O and parallel data processing
- [Examples](examples.md) - Practical usage examples

## Quick Start

```python
import pyferris

# Basic parallel map operation
results = pyferris.parallel_map(lambda x: x ** 2, range(1000))

# Parallel file operations
from pyferris.io import read_csv, write_json
data = read_csv("data.csv")
write_json("output.json", data)
```

## Installation

```bash
pip install pyferris
```

## Key Features

PyFerris is designed for high-performance parallel processing with:

- **Rust-powered backend** for maximum performance
- **GIL-free execution** for true parallelism
- **Pythonic API** for ease of use
- **Comprehensive I/O support** for various file formats
- **Flexible task execution** with thread pool management

## Support

For questions, issues, or contributions, please visit our [GitHub repository](https://github.com/your-org/pyferris).
