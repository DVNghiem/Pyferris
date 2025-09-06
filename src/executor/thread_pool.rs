use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};
use rayon::prelude::*;
use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, AtomicBool, Ordering};
use smallvec::SmallVec;

/// High-performance task executor with advanced optimizations
#[pyclass]
pub struct Executor {
    #[pyo3(get, set)]
    pub max_workers: usize,
    thread_pool: Option<rayon::ThreadPool>,
    // Minimum chunk size for parallel processing
    min_chunk_size: AtomicUsize,
    // Track if executor is active
    is_active: AtomicBool,
    // Performance counters
    task_count: AtomicUsize,
}

#[pymethods]
impl Executor {
    #[new]
    #[pyo3(signature = (max_workers = None))]
    pub fn new(max_workers: Option<usize>) -> PyResult<Self> {
        let max_workers = max_workers.unwrap_or_else(|| rayon::current_num_threads());
        
        // Create a custom thread pool with the specified number of workers
        let thread_pool = rayon::ThreadPoolBuilder::new()
            .num_threads(max_workers)
            .build()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create thread pool: {}", e)))?;
        
        Ok(Self {
            max_workers,
            thread_pool: Some(thread_pool),
            // Start with a reasonable chunk size based on worker count
            min_chunk_size: AtomicUsize::new((1000.max(max_workers * 4)).min(10000)),
            is_active: AtomicBool::new(true),
            task_count: AtomicUsize::new(0),
        })
    }

    /// Submit a single task with explicit arguments
    pub fn submit_with_args(&self, func: Bound<PyAny>, args: Bound<PyTuple>) -> PyResult<Py<PyAny>> {
        // For single tasks with args, we use the thread pool but wait for completion
        let py = func.py();
        
        if let Some(ref pool) = self.thread_pool {
            let func_obj: Arc<Py<PyAny>> = Arc::new(func.into());
            let args_obj: Arc<Py<PyAny>> = Arc::new(args.into());
            
            py.detach(|| {
                pool.install(|| -> PyResult<Py<PyAny>> {
                    Python::attach(|py| {
                        let bound_func = func_obj.bind(py);
                        let bound_args = args_obj.bind(py).downcast::<PyTuple>()?;
                        let result = bound_func.call1(bound_args)?;
                        Ok(result.into())
                    })
                })
            })
        } else {
            // Fallback to immediate execution
            let result = func.call1(&args)?;
            Ok(result.into())
        }
    }

    /// Submit a single task (for compatibility with asyncio.run_in_executor)
    pub fn submit(&self, func: Bound<PyAny>) -> PyResult<Py<PyAny>> {
        let py = func.py();
        
        if let Some(ref pool) = self.thread_pool {
            let func_obj: Arc<Py<PyAny>> = Arc::new(func.into());
            
            py.detach(|| {
                pool.install(|| -> PyResult<Py<PyAny>> {
                    Python::attach(|py| {
                        let bound_func = func_obj.bind(py);
                        let result = bound_func.call0()?;
                        Ok(result.into())
                    })
                })
            })
        } else {
            // Fallback to immediate execution
            let result = func.call0()?;
            Ok(result.into())
        }
    }

    /// Submit multiple tasks and collect results with advanced optimizations
    pub fn map(&self, func: Bound<PyAny>, iterable: Bound<PyAny>) -> PyResult<Py<PyList>> {
        let py = func.py();
        self.task_count.fetch_add(1, Ordering::Relaxed);
        
        // Convert to Py<PyAny> with optimized allocation
        let items: Vec<Py<PyAny>> = {
            let iter = iterable.try_iter()?;
            let mut items = Vec::new();
            
            // Try to get size hint for better allocation
            let (lower, upper) = iter.size_hint();
            if let Some(upper) = upper {
                items.reserve(upper);
            } else if lower > 0 {
                items.reserve(lower);
            }
            
            for item in iter {
                items.push(item?.into());
            }
            items
        };
        
        if items.is_empty() {
            return Ok(PyList::empty(py).into());
        }
        
        // Advanced chunking strategy
        let min_chunk_size = self.min_chunk_size.load(Ordering::Relaxed);
        let optimal_chunk_size = match items.len() {
            0..=1000 => {
                // For small datasets, consider sequential processing
                if items.len() < min_chunk_size.min(self.max_workers * 2) {
                    // Sequential processing for very small datasets
                    let results: PyResult<Vec<Py<PyAny>>> = items
                        .iter()
                        .map(|item| -> PyResult<Py<PyAny>> {
                            let bound_item = item.bind(py);
                            let result = func.call1((bound_item,))?;
                            Ok(result.into())
                        })
                        .collect();
                    
                    let py_list = PyList::new(py, results?)?;
                    return Ok(py_list.into());
                }
                items.len().max(1)
            }
            1001..=10000 => (items.len() / self.max_workers).max(100).min(1000),
            10001..=100000 => (items.len() / (self.max_workers * 2)).max(500).min(2000),
            _ => (items.len() / (self.max_workers * 4)).max(1000).min(5000),
        };
        
        let func: Arc<Py<PyAny>> = Arc::new(func.into());
        
        // Use our custom thread pool if available, otherwise fall back to global pool
        let results: Vec<SmallVec<[Py<PyAny>; 8]>> = if let Some(ref pool) = self.thread_pool {
            py.detach(|| {
                pool.install(|| -> PyResult<Vec<SmallVec<[Py<PyAny>; 8]>>> {
                    let chunk_results: PyResult<Vec<SmallVec<[Py<PyAny>; 8]>>> = items
                        .par_chunks(optimal_chunk_size)
                        .map(|chunk| -> PyResult<SmallVec<[Py<PyAny>; 8]>> {
                            Python::attach(|py| {
                                let mut chunk_results = SmallVec::with_capacity(chunk.len());
                                let bound_func = func.bind(py);
                                
                                for item in chunk {
                                    let bound_item = item.bind(py);
                                    let result = bound_func.call1((bound_item,))?;
                                    chunk_results.push(result.into());
                                }
                                
                                Ok(chunk_results)
                            })
                        })
                        .collect();
                    
                    chunk_results
                })
            })?
        } else {
            // Use global pool as fallback with chunking
            py.detach(|| -> PyResult<Vec<SmallVec<[Py<PyAny>; 8]>>> {
                let chunk_results: PyResult<Vec<SmallVec<[Py<PyAny>; 8]>>> = items
                    .par_chunks(optimal_chunk_size)
                    .map(|chunk| -> PyResult<SmallVec<[Py<PyAny>; 8]>> {
                        Python::attach(|py| {
                            let mut chunk_results = SmallVec::with_capacity(chunk.len());
                            let bound_func = func.bind(py);
                            
                            for item in chunk {
                                let bound_item = item.bind(py);
                                let result = bound_func.call1((bound_item,))?;
                                chunk_results.push(result.into());
                            }
                            
                            Ok(chunk_results)
                        })
                    })
                    .collect();
                
                chunk_results
            })?
        };

        // Flatten with capacity hint for better performance
        let total_capacity: usize = results.iter().map(|v| v.len()).sum();
        let mut final_results = Vec::with_capacity(total_capacity);
        
        for chunk in results {
            final_results.extend(chunk);
        }

        let py_list = PyList::new(py, final_results)?;
        Ok(py_list.into())
    }

    /// Submit multiple tasks for batch execution
    pub fn submit_batch(&self, tasks: Vec<(Bound<PyAny>, Option<Bound<PyTuple>>)>) -> PyResult<Py<PyList>> {
        let py = tasks.first().map(|(func, _)| func.py()).ok_or_else(|| 
            pyo3::exceptions::PyValueError::new_err("Empty task list"))?;
        
        if tasks.is_empty() {
            return Ok(PyList::empty(py).into());
        }
        
        // Convert tasks to thread-safe format
        let task_objects: Vec<(Arc<Py<PyAny>>, Option<Arc<Py<PyAny>>>)> = tasks
            .into_iter()
            .map(|(func, args)| {
                let func_obj = Arc::new(func.into());
                let args_obj = args.map(|a| Arc::new(a.into()));
                (func_obj, args_obj)
            })
            .collect();
        
        if let Some(ref pool) = self.thread_pool {
            let results = py.detach(|| {
                pool.install(|| -> PyResult<Vec<Py<PyAny>>> {
                    let chunk_results: PyResult<Vec<Py<PyAny>>> = task_objects
                        .par_iter()
                        .map(|(func_obj, args_obj)| -> PyResult<Py<PyAny>> {
                            Python::attach(|py| {
                                let bound_func = func_obj.bind(py);
                                let result = if let Some(args) = args_obj {
                                    let bound_args = args.bind(py).downcast::<PyTuple>()?;
                                    bound_func.call1(bound_args)?
                                } else {
                                    bound_func.call0()?
                                };
                                Ok(result.into())
                            })
                        })
                        .collect();
                    chunk_results
                })
            })?;
            
            let py_list = PyList::new(py, results)?;
            Ok(py_list.into())
        } else {
            // Fallback to sequential execution
            let results: PyResult<Vec<Py<PyAny>>> = task_objects
                .iter()
                .map(|(func_obj, args_obj)| -> PyResult<Py<PyAny>> {
                    let bound_func = func_obj.bind(py);
                    let result = if let Some(args) = args_obj {
                        let bound_args = args.bind(py).downcast::<PyTuple>()?;
                        bound_func.call1(bound_args)?
                    } else {
                        bound_func.call0()?
                    };
                    Ok(result.into())
                })
                .collect();
            
            let py_list = PyList::new(py, results?)?;
            Ok(py_list.into())
        }
    }

    /// Get the number of worker threads
    pub fn get_worker_count(&self) -> usize {
        self.max_workers
    }

    /// Check if the executor is active
    pub fn is_active(&self) -> bool {
        self.is_active.load(Ordering::Relaxed) && self.thread_pool.is_some()
    }

    /// Get performance statistics
    pub fn get_stats(&self) -> (usize, usize, bool) {
        (
            self.max_workers,
            self.task_count.load(Ordering::Relaxed),
            self.is_active()
        )
    }

    /// Set the minimum chunk size for parallel processing
    pub fn set_chunk_size(&self, chunk_size: usize) {
        self.min_chunk_size.store(chunk_size, Ordering::Relaxed);
    }

    /// Get the current chunk size setting
    pub fn get_chunk_size(&self) -> usize {
        self.min_chunk_size.load(Ordering::Relaxed)
    }

    /// Shutdown the executor
    pub fn shutdown(&mut self) {
        self.is_active.store(false, Ordering::Relaxed);
        // Drop the thread pool to shut it down
        self.thread_pool = None;
    }

    pub fn __enter__(pyself: PyRef<'_, Self>) -> PyRef<'_, Self> {
        pyself
    }

    pub fn __exit__(
        &mut self,
        _exc_type: Option<&Bound<'_, PyAny>>,
        _exc_value: Option<&Bound<'_, PyAny>>,
        _traceback: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<bool> {
        self.shutdown();
        Ok(false)
    }

    /// Submit a task that performs pure computation without Python callbacks
    /// This is useful for CPU-bound tasks that can be entirely done in Rust
    pub fn submit_computation(&self, computation_type: &str, data: Vec<f64>) -> PyResult<f64> {        
        if let Some(ref pool) = self.thread_pool {
            let computation_type = computation_type.to_string();
            let result = pool.install(|| -> Result<f64, &'static str> {
                match computation_type.as_str() {
                    "sum" => {
                        let sum: f64 = data.par_iter().sum();
                        Ok(sum)
                    },
                    "product" => {
                        let product: f64 = data.par_iter().product();
                        Ok(product)
                    },
                    "square_sum" => {
                        let sum: f64 = data.par_iter().map(|x| x * x).sum();
                        Ok(sum)
                    },
                    "heavy_computation" => {
                        // Simulate heavy computation that benefits from parallelism
                        let result: f64 = data.par_iter().map(|&x| {
                            let mut total = 0.0;
                            for i in 0..100000 {
                                for j in 0..10 {
                                    total += (i as f64) * (j as f64) * x;
                                }
                            }
                            total % 1000000.0
                        }).sum();
                        Ok(result)
                    },
                    _ => Err("Unknown computation type"),
                }
            });
            
            match result {
                Ok(value) => Ok(value),
                Err(e) => Err(pyo3::exceptions::PyValueError::new_err(e)),
            }
        } else {
            // Sequential fallback
            let result = match computation_type {
                "sum" => data.iter().sum::<f64>(),
                "product" => data.iter().product::<f64>(),
                "square_sum" => data.iter().map(|x| x * x).sum::<f64>(),
                "heavy_computation" => {
                    data.iter().map(|&x| {
                        let mut total = 0.0;
                        for i in 0..100000 {
                            for j in 0..10 {
                                total += (i as f64) * (j as f64) * x;
                            }
                        }
                        total % 1000000.0
                    }).sum::<f64>()
                },
                _ => return Err(pyo3::exceptions::PyValueError::new_err("Unknown computation type")),
            };
            Ok(result)
        }
    }
}
