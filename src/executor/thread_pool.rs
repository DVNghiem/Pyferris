use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};
use rayon::prelude::*;
use std::sync::Arc;
use std::sync::atomic::AtomicUsize;

/// Task executor for managing parallel tasks
#[pyclass]
pub struct Executor {
    #[pyo3(get, set)]
    pub max_workers: usize,
    thread_pool: Option<rayon::ThreadPool>,
    // Minimum chunk size for parallel processing
    min_chunk_size: AtomicUsize,
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
        })
    }

    /// Submit a single task with explicit arguments
    pub fn submit_with_args(&self, func: Bound<PyAny>, args: Bound<PyTuple>) -> PyResult<PyObject> {
        // For single tasks with args, we use the thread pool but wait for completion
        let py = func.py();
        
        if let Some(ref pool) = self.thread_pool {
            let func_obj: Arc<PyObject> = Arc::new(func.into());
            let args_obj: Arc<PyObject> = Arc::new(args.into());
            
            py.allow_threads(|| {
                pool.install(|| {
                    Python::with_gil(|py| {
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
    /// Note: For CPU-bound Python tasks, parallelism is limited by GIL.
    /// Use map() for better performance with multiple tasks.
    pub fn submit(&self, func: Bound<PyAny>) -> PyResult<PyObject> {
        let py = func.py();
        
        if let Some(ref pool) = self.thread_pool {
            let func_obj: Arc<PyObject> = Arc::new(func.into());
            
            // For single tasks, the overhead of thread pool might not be worth it
            // But we still use it to maintain consistent behavior and allow
            // better CPU utilization in some cases
            py.allow_threads(|| {
                pool.install(|| {
                    Python::with_gil(|py| {
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

    /// Submit multiple tasks and collect results
    pub fn map(&self, func: Bound<PyAny>, iterable: Bound<PyAny>) -> PyResult<Py<PyList>> {
        let py = func.py();
        // Convert to PyObjects to avoid Sync issues
        let items: Vec<PyObject> = iterable.try_iter()?.map(|item| item.map(|i| i.into())).collect::<PyResult<Vec<_>>>()?;
        
        if items.is_empty() {
            return Ok(PyList::empty(py).into());
        }
        
        // For small datasets, use sequential processing to avoid overhead
        let min_chunk_size = self.min_chunk_size.load(std::sync::atomic::Ordering::Relaxed);
        if items.len() < min_chunk_size.min(self.max_workers * 2) {
            let results: PyResult<Vec<PyObject>> = items
                .iter()
                .map(|item| -> PyResult<PyObject> {
                    let bound_item = item.bind(py);
                    let result = func.call1((bound_item,))?;
                    Ok(result.into())
                })
                .collect();
            
            let py_list = PyList::new(py, results?)?;
            return Ok(py_list.into());
        }
        
        let func: Arc<PyObject> = Arc::new(func.into());
        
        // Use our custom thread pool if available, otherwise fall back to global pool
        let results: Vec<PyObject> = if let Some(ref pool) = self.thread_pool {
            py.allow_threads(|| {
                pool.install(|| {
                    // Process in chunks to reduce GIL contention
                    let chunk_size = (items.len() / self.max_workers).max(1).min(1000);
                    
                    let chunk_results: PyResult<Vec<Vec<PyObject>>> = items
                        .par_chunks(chunk_size)
                        .map(|chunk| -> PyResult<Vec<PyObject>> {
                            Python::with_gil(|py| {
                                let bound_func = func.bind(py);
                                let mut chunk_results = Vec::with_capacity(chunk.len());
                                
                                for item in chunk {
                                    let bound_item = item.bind(py);
                                    let result = bound_func.call1((bound_item,))?;
                                    chunk_results.push(result.into());
                                }
                                
                                Ok(chunk_results)
                            })
                        })
                        .collect();
                    
                    // Flatten the results
                    chunk_results.map(|chunks| chunks.into_iter().flatten().collect())
                })
            })?
        } else {
            // Use global pool as fallback with chunking
            py.allow_threads(|| {
                let chunk_size = (items.len() / rayon::current_num_threads()).max(1).min(1000);
                
                let chunk_results: PyResult<Vec<Vec<PyObject>>> = items
                    .par_chunks(chunk_size)
                    .map(|chunk| -> PyResult<Vec<PyObject>> {
                        Python::with_gil(|py| {
                            let bound_func = func.bind(py);
                            let mut chunk_results = Vec::with_capacity(chunk.len());
                            
                            for item in chunk {
                                let bound_item = item.bind(py);
                                let result = bound_func.call1((bound_item,))?;
                                chunk_results.push(result.into());
                            }
                            
                            Ok(chunk_results)
                        })
                    })
                    .collect();
                
                // Flatten the results
                chunk_results.map(|chunks| chunks.into_iter().flatten().collect())
            })?
        };

        let py_list = PyList::new(py, results)?;
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
        let task_objects: Vec<(Arc<PyObject>, Option<Arc<PyObject>>)> = tasks
            .into_iter()
            .map(|(func, args)| {
                let func_obj = Arc::new(func.into());
                let args_obj = args.map(|a| Arc::new(a.into()));
                (func_obj, args_obj)
            })
            .collect();
        
        if let Some(ref pool) = self.thread_pool {
            let results = py.allow_threads(|| {
                pool.install(|| {
                    let chunk_results: PyResult<Vec<PyObject>> = task_objects
                        .par_iter()
                        .map(|(func_obj, args_obj)| -> PyResult<PyObject> {
                            Python::with_gil(|py| {
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
            let results: PyResult<Vec<PyObject>> = task_objects
                .iter()
                .map(|(func_obj, args_obj)| -> PyResult<PyObject> {
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
        self.thread_pool.is_some()
    }

    /// Set the minimum chunk size for parallel processing
    pub fn set_chunk_size(&self, chunk_size: usize) {
        self.min_chunk_size.store(chunk_size, std::sync::atomic::Ordering::Relaxed);
    }

    /// Get the current chunk size
    pub fn get_chunk_size(&self) -> usize {
        self.min_chunk_size.load(std::sync::atomic::Ordering::Relaxed)
    }

    /// Shutdown the executor
    pub fn shutdown(&mut self) {
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
            let result = pool.install(|| {
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
