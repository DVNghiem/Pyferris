# PyFerris

**PyFerris** is a high-performance parallel processing library for Python, powered by Rust and PyO3. It provides a seamless, Pythonic API to leverage Rust's speed and memory safety for parallel and distributed computing, bypassing Python's Global Interpreter Lock (GIL). PyFerris is designed for data scientists, machine learning engineers, and developers who need efficient parallel processing for CPU-bound tasks, big data, machine learning pipelines, IoT streaming, and enterprise-grade applications.

## Key Features

PyFerris offers a comprehensive set of features, from basic parallel operations to advanced distributed processing and GPU support:

### Level 1: Basic Features
- **Core Parallel Operations**: `parallel_map`, `parallel_filter`, `parallel_reduce`, `parallel_starmap` for efficient parallel processing.
- **Task Executor**: A thread pool-like `Executor` for submitting and managing tasks.
- **Basic Configuration**: Control number of workers and chunk sizes with `set_worker_count` and `set_chunk_size`.
- **Error Handling**: Robust error propagation with `ParallelExecutionError` and flexible strategies (`raise`, `ignore`, `collect`).

### Level 2: Intermediate Features
- **Advanced Parallel Operations**: `parallel_sort`, `parallel_group_by`, `parallel_unique`, `parallel_partition` for complex data processing.
- **Batch Processing**: Process large datasets in chunks with `BatchProcessor` and `parallel_chunks`.
- **Result Collection**: Collect results in ordered, unordered, or as-completed modes.
- **Progress Tracking**: Monitor task progress with `tqdm` integration or custom `ProgressTracker`.

### Level 3: Advanced Features
- **Pipeline Processing**: Chain operations with `Pipeline` and `Chain` for streamlined data processing.
- **Async Support**: Asynchronous execution with `AsyncExecutor` for I/O-bound and CPU-bound tasks.
- **Shared Memory**: Zero-copy data sharing with `SharedArray`, `SharedDict`, `SharedQueue`, and `SharedCounter`.
- **Custom Schedulers**: Flexible scheduling with `WorkStealingScheduler`, `RoundRobinScheduler`, and `PriorityScheduler`.

### Level 4: Expert Features
- **Concurrent Data Structures**: Lock-free and thread-safe `ConcurrentHashMap`, `LockFreeQueue`, `AtomicCounter`, and `RwLockDict`.
- **Memory Management**: Efficient memory usage with `MemoryPool` and `memory_mapped_array`.
- **Performance Profiling**: Detailed profiling with `Profiler` for CPU, memory, and bottleneck analysis.
- **Dynamic Load Balancing**: Adaptive scheduling with `AdaptiveScheduler` and `auto_tune_workers`.

### Level 5: Enterprise Features
- **Distributed Processing**: Multi-machine support with `DistributedExecutor`, `cluster_map`, and `distributed_reduce`.
- **Fault Tolerance**: Reliable execution with `RetryExecutor` and `CheckpointManager`.
- **Resource Management**: Fine-grained control with `ResourceManager` and `ResourceMonitor`.
- **Framework Integrations**: Seamless integration with NumPy, Pandas, Dask, and Ray.
- **Advanced Analytics**: Performance analysis with `PerformanceAnalyzer` and Prometheus metrics export.
- **Custom Extensions**: Plugin system with `register_custom_operation` and `load_plugin`.

### Additional Features
- **GPU Parallel Processing**: Accelerate computations with GPU support (`gpu_parallel_map`).
- **Tensor Parallel Operations**: Optimize ML pipelines with tensor operations compatible with PyTorch/TensorFlow.
- **IoT Stream Processing**: Handle real-time data streams with `stream_parallel_process`.
- **Serverless Task Offloading**: Run tasks on AWS Lambda or Google Cloud Functions with `serverless_parallel_map`.
- **Interactive Mode**: Jupyter-friendly API with magic commands (`%%parallel_map`) and visual progress.
- **Auto-Tuning API**: Automatically optimize workers and chunk sizes with `auto_tune`.
- **Visualization Tools**: Visualize task execution and resource usage with `PerformanceVisualizer`.
- **Data Encryption**: Secure shared memory with `SharedArray.encrypt` for sensitive data.
- **Audit Logging**: Compliance-ready logging with `set_audit_log`.

## Installation

PyFerris is available on PyPI and can be installed with `pip` or `poetry`.

```bash
pip install pyferris
```

For optional dependencies (e.g., Pandas, Dask, GPU support):

```bash
pip install pyferris[pandas,dask,gpu]
```

To build from source (requires Rust and `maturin`):

```bash
git clone https://github.com/DVNghiem/Pyferris.git
cd pyferris
poetry install
maturin develop
```

## Quick Start

Here's a simple example of using `parallel_map` to square a large dataset:

```python
from pyferris import parallel_map

def square(x):
    return x * x

numbers = range(1000000)
results = parallel_map(square, numbers)
print(list(results)[:5])  # [0, 1, 4, 9, 16]
```

For an asynchronous example with progress tracking:

```python
import asyncio
from pyferris import async_parallel_map, ProgressTracker

async def process(x):
    await asyncio.sleep(0.1)
    return x * 2

async def main():
    data = range(1000)
    tracker = ProgressTracker(total=1000, desc="Processing")
    results = await async_parallel_map(process, data, progress=tracker)
    print(list(results)[:5])  # [0, 2, 4, 6, 8]

asyncio.run(main())
```

More examples are available in the `examples/` directory, covering all features from basic to enterprise-level.

## Documentation

Full documentation is available at [https://yourusername.github.io/pyferris](https://yourusername.github.io/pyferris). It includes:
- API reference for all functions and classes.
- Guides for getting started, advanced usage, and enterprise features.
- Examples for data science, machine learning, IoT, and distributed computing.

## Performance

PyFerris leverages Rust's performance and memory safety to outperform Python's built-in `multiprocessing` and `concurrent.futures` for CPU-bound tasks. For example, `parallel_map` can be 2-5x faster than `multiprocessing.Pool.map` for large datasets, thanks to Rust's zero-cost abstractions and GIL-free execution.

## Contributing

We welcome contributions! To get started:
1. Fork the repository on GitHub.
2. Clone your fork: `git clone https://github.com/DVNghiem/Pyferris.git`.
3. Install dependencies: `poetry install`.
4. Build the Rust extension: `maturin develop`.
5. Run tests: `poetry run pytest`.
6. Submit a pull request with your changes.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

PyFerris is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact

- **Issues**: Report bugs or request features at [GitHub Issues](https://github.com/DVNghiem/Pyferris/issues).
- **Email**: Contact the maintainer at your.email@example.com.
- **Community**: Join our community on [Discord/Slack] (TBD).

---

*PyFerris: Unleash the power of Rust in Python for parallel processing!*# PyFerris
