use pyo3::prelude::*;
use pyo3::types::{PyList, PyTuple};
use std::sync::{Arc, Mutex, Condvar};
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::thread;
use std::time::{Duration, Instant};
use std::task::Waker;
use crossbeam_deque::{Injector, Stealer, Worker};

/// Virtual Thread State
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum VirtualThreadState {
    Created,
    Runnable,
    Running,
    Terminated,
}

/// Virtual Thread ID type
pub type VirtualThreadId = u64;

/// Task that can be executed by a virtual thread
pub trait VirtualTask: Send + Sync {
    fn execute(&self) -> PyResult<Py<PyAny>>;
    fn is_blocking(&self) -> bool { false }
}

/// Python function wrapper for virtual tasks
#[derive(Clone)]
pub struct PythonVirtualTask {
    func: Arc<Py<PyAny>>,
    args: Option<Arc<Py<PyAny>>>,
    is_blocking_task: bool,
}

impl PythonVirtualTask {
    pub fn new(func: Py<PyAny>, args: Option<Py<PyAny>>, is_blocking: bool) -> Self {
        Self {
            func: Arc::new(func),
            args: args.map(Arc::new),
            is_blocking_task: is_blocking,
        }
    }
}

impl VirtualTask for PythonVirtualTask {
    fn execute(&self) -> PyResult<Py<PyAny>> {
        Python::attach(|py| {
            let bound_func = self.func.bind(py);
            let result = if let Some(ref args) = self.args {
                let bound_args = args.bind(py).downcast::<PyTuple>()?;
                bound_func.call1(bound_args)?
            } else {
                bound_func.call0()?
            };
            Ok(result.into())
        })
    }

    fn is_blocking(&self) -> bool {
        self.is_blocking_task
    }
}

/// Virtual Thread implementation inspired by Java's Project Loom
#[derive(Clone)]
pub struct VirtualThread {
    id: VirtualThreadId,
    state: Arc<Mutex<VirtualThreadState>>,
    task: Arc<dyn VirtualTask>,
    result: Arc<Mutex<Option<Result<Py<PyAny>, String>>>>,
    waker: Arc<Mutex<Option<Waker>>>,
    start_time: Arc<Mutex<Option<Instant>>>,
    end_time: Arc<Mutex<Option<Instant>>>,
}

impl VirtualThread {
    pub fn new(id: VirtualThreadId, task: Arc<dyn VirtualTask>) -> Self {
        Self {
            id,
            state: Arc::new(Mutex::new(VirtualThreadState::Created)),
            task,
            result: Arc::new(Mutex::new(None)),
            waker: Arc::new(Mutex::new(None)),
            start_time: Arc::new(Mutex::new(None)),
            end_time: Arc::new(Mutex::new(None)),
        }
    }

    pub fn id(&self) -> VirtualThreadId {
        self.id
    }

    pub fn state(&self) -> VirtualThreadState {
        self.state.lock().unwrap().clone()
    }

    pub fn set_state(&self, new_state: VirtualThreadState) {
        *self.state.lock().unwrap() = new_state;
        
        // Update timing
        match new_state {
            VirtualThreadState::Running => {
                *self.start_time.lock().unwrap() = Some(Instant::now());
            },
            VirtualThreadState::Terminated => {
                *self.end_time.lock().unwrap() = Some(Instant::now());
            },
            _ => {}
        }
    }

    pub fn execute(&self) -> PyResult<Py<PyAny>> {
        self.set_state(VirtualThreadState::Running);
        let result = self.task.execute();
        
        // Store result
        let stored_result = match &result {
            Ok(py_obj) => {
                Python::attach(|py| {
                    Ok(py_obj.clone_ref(py))
                })
            },
            Err(e) => Err(e.to_string()),
        };
        *self.result.lock().unwrap() = Some(stored_result);
        
        // Update state based on result
        self.set_state(VirtualThreadState::Terminated);
        
        // Wake any waiting tasks
        if let Some(waker) = self.waker.lock().unwrap().take() {
            waker.wake();
        }
        
        result
    }

    pub fn is_blocking(&self) -> bool {
        self.task.is_blocking()
    }

    pub fn get_result(&self) -> Option<PyResult<Py<PyAny>>> {
        self.result.lock().unwrap().as_ref().map(|r| match r {
            Ok(py_obj) => {
                Python::attach(|py| {
                    Ok(py_obj.clone_ref(py))
                })
            },
            Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.clone())),
        })
    }
}

/// Virtual Thread Executor that manages lightweight threads
#[pyclass]
pub struct VirtualThreadExecutor {
    // Core state
    is_running: Arc<AtomicBool>,
    max_platform_threads: usize,
    
    // Thread management
    virtual_threads: Arc<Mutex<Vec<VirtualThread>>>,
    platform_threads: Arc<Mutex<Vec<thread::JoinHandle<()>>>>,
    
    // Work scheduling
    work_queue: Arc<Injector<VirtualThread>>,
    stealers: Arc<Mutex<Vec<Stealer<VirtualThread>>>>,
    
    // Synchronization
    scheduler_notify: Arc<(Mutex<bool>, Condvar)>,
    
    // Metrics
    next_thread_id: Arc<AtomicU64>,
    total_threads_created: Arc<AtomicU64>,
    active_threads: Arc<AtomicUsize>,
    completed_threads: Arc<AtomicU64>,
    
    // Runtime
    runtime: Arc<Mutex<Option<tokio::runtime::Runtime>>>,
}

impl VirtualThreadExecutor {
    fn new_internal(max_virtual_threads: Option<usize>, max_platform_threads: Option<usize>) -> Self {
        let platform_threads = max_platform_threads.unwrap_or_else(|| {
            std::thread::available_parallelism().map(|n| n.get()).unwrap_or(4)
        });
        
        let _virtual_threads = max_virtual_threads.unwrap_or(1_000_000); // Default 1M virtual threads
        
        // Create work-stealing queues
        let mut stealers = Vec::new();
        
        for _ in 0..platform_threads {
            let worker = Worker::new_fifo();
            stealers.push(worker.stealer());
        }
        
        // Create async runtime for blocking operations
        let runtime = tokio::runtime::Builder::new_multi_thread()
            .worker_threads(platform_threads)
            .enable_all()
            .build()
            .ok();
        
        Self {
            is_running: Arc::new(AtomicBool::new(false)),
            max_platform_threads: platform_threads,
            virtual_threads: Arc::new(Mutex::new(Vec::new())),
            platform_threads: Arc::new(Mutex::new(Vec::new())),
            work_queue: Arc::new(Injector::new()),
            stealers: Arc::new(Mutex::new(stealers)),
            scheduler_notify: Arc::new((Mutex::new(false), Condvar::new())),
            next_thread_id: Arc::new(AtomicU64::new(1)),
            total_threads_created: Arc::new(AtomicU64::new(0)),
            active_threads: Arc::new(AtomicUsize::new(0)),
            completed_threads: Arc::new(AtomicU64::new(0)),
            runtime: Arc::new(Mutex::new(runtime)),
        }
    }

    fn start_platform_threads(&self) {
        if self.is_running.load(Ordering::Relaxed) {
            return;
        }
        
        self.is_running.store(true, Ordering::Relaxed);
        let mut handles = self.platform_threads.lock().unwrap();
        
        for i in 0..self.max_platform_threads {
            let work_queue = Arc::clone(&self.work_queue);
            let stealers = Arc::clone(&self.stealers);
            let is_running = Arc::clone(&self.is_running);
            let scheduler_notify = Arc::clone(&self.scheduler_notify);
            let active_threads = Arc::clone(&self.active_threads);
            let completed_threads = Arc::clone(&self.completed_threads);
            let runtime = Arc::clone(&self.runtime);
            
            let handle = thread::Builder::new()
                .name(format!("virtual-thread-carrier-{}", i))
                .spawn(move || {
                    Self::platform_thread_loop(
                        i,
                        work_queue,
                        stealers,
                        is_running,
                        scheduler_notify,
                        active_threads,
                        completed_threads,
                        runtime,
                    );
                })
                .expect("Failed to spawn platform thread");
            
            handles.push(handle);
        }
    }

    fn platform_thread_loop(
        _thread_id: usize,
        work_queue: Arc<Injector<VirtualThread>>,
        stealers: Arc<Mutex<Vec<Stealer<VirtualThread>>>>,
        is_running: Arc<AtomicBool>,
        scheduler_notify: Arc<(Mutex<bool>, Condvar)>,
        active_threads: Arc<AtomicUsize>,
        completed_threads: Arc<AtomicU64>,
        runtime: Arc<Mutex<Option<tokio::runtime::Runtime>>>,
    ) {
        let _local_worker: Worker<VirtualThread> = Worker::new_fifo();
        
        while is_running.load(Ordering::Relaxed) {
            // Try to get work from global queue first
            if let Some(vthread) = work_queue.steal().success() {
                Self::execute_virtual_thread(
                    vthread, 
                    &active_threads, 
                    &completed_threads,
                    &runtime
                );
                continue;
            }
            
            // Try work stealing from other threads
            let mut found_work = false;
            if let Ok(stealers_guard) = stealers.lock() {
                for stealer in stealers_guard.iter() {
                    if let Some(vthread) = stealer.steal().success() {
                        Self::execute_virtual_thread(
                            vthread, 
                            &active_threads, 
                            &completed_threads,
                            &runtime
                        );
                        found_work = true;
                        break;
                    }
                }
            }
            
            if !found_work {
                // Wait for notification or timeout
                let (lock, cvar) = &*scheduler_notify;
                let _result = cvar.wait_timeout(
                    lock.lock().unwrap(), 
                    Duration::from_millis(10)
                ).unwrap();
            }
        }
    }

    fn execute_virtual_thread(
        vthread: VirtualThread,
        active_threads: &Arc<AtomicUsize>,
        completed_threads: &Arc<AtomicU64>,
        runtime: &Arc<Mutex<Option<tokio::runtime::Runtime>>>,
    ) {
        active_threads.fetch_add(1, Ordering::Relaxed);
        
        // Execute the virtual thread task
        if vthread.is_blocking() {
            // Handle blocking operations asynchronously
            if let Some(runtime) = runtime.lock().unwrap().as_ref() {
                runtime.spawn(async move {
                    let _result = vthread.execute();
                });
            } else {
                // Fallback to direct execution
                let _result = vthread.execute();
            }
        } else {
            // Direct execution for non-blocking tasks
            let _result = vthread.execute();
        }
        
        active_threads.fetch_sub(1, Ordering::Relaxed);
        completed_threads.fetch_add(1, Ordering::Relaxed);
    }

    fn notify_scheduler(&self) {
        let (lock, cvar) = &*self.scheduler_notify;
        let mut notified = lock.lock().unwrap();
        *notified = true;
        cvar.notify_all();
    }
}

#[pymethods]
impl VirtualThreadExecutor {
    /// Create a new Virtual Thread Executor
    #[new]
    #[pyo3(signature = (max_virtual_threads = None, max_platform_threads = None))]
    pub fn new(max_virtual_threads: Option<usize>, max_platform_threads: Option<usize>) -> PyResult<Self> {
        Ok(Self::new_internal(max_virtual_threads, max_platform_threads))
    }

    /// Start the executor
    pub fn start(&self) -> PyResult<()> {
        self.start_platform_threads();
        Ok(())
    }

    /// Submit a task to be executed by a virtual thread
    #[pyo3(signature = (func, args = None, is_blocking = false))]
    pub fn submit_virtual_task(
        &self,
        func: Bound<PyAny>,
        args: Option<Bound<PyTuple>>,
        is_blocking: bool,
    ) -> PyResult<VirtualThreadId> {
        if !self.is_running.load(Ordering::Relaxed) {
            self.start_platform_threads();
        }

        let thread_id = self.next_thread_id.fetch_add(1, Ordering::Relaxed);
        
        // Create Python virtual task
        let task = Arc::new(PythonVirtualTask::new(
            func.into(),
            args.map(|a| a.into()),
            is_blocking,
        ));
        
        // Create virtual thread
        let vthread = VirtualThread::new(thread_id, task);
        vthread.set_state(VirtualThreadState::Runnable);
        
        // Add to thread registry
        self.virtual_threads.lock().unwrap().push(vthread.clone());
        
        // Submit to work queue
        self.work_queue.push(vthread);
        self.total_threads_created.fetch_add(1, Ordering::Relaxed);
        
        // Notify scheduler
        self.notify_scheduler();
        
        Ok(thread_id)
    }

    /// Submit multiple tasks as virtual threads
    pub fn submit_many(
        &self,
        tasks: Vec<(Bound<PyAny>, Option<Bound<PyTuple>>, Option<bool>)>,
    ) -> PyResult<Vec<VirtualThreadId>> {
        let mut thread_ids = Vec::with_capacity(tasks.len());
        
        for (func, args, is_blocking) in tasks {
            let id = self.submit_virtual_task(
                func,
                args,
                is_blocking.unwrap_or(false),
            )?;
            thread_ids.push(id);
        }
        
        Ok(thread_ids)
    }

    /// Wait for a virtual thread to complete and get its result
    pub fn join(&self, thread_id: VirtualThreadId) -> PyResult<Py<PyAny>> {
        let vthread = {
            let threads = self.virtual_threads.lock().unwrap();
            threads.iter()
                .find(|t| t.id() == thread_id)
                .cloned()
                .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Thread not found"))?
        };
        
        // Poll for completion with timeout
        let timeout = Duration::from_secs(30); // 30 second timeout
        let start = Instant::now();
        
        loop {
            if let Some(result) = vthread.get_result() {
                return result;
            }
            
            if start.elapsed() > timeout {
                return Err(pyo3::exceptions::PyTimeoutError::new_err("Thread execution timeout"));
            }
            
            thread::sleep(Duration::from_millis(1));
        }
    }

    /// Wait for multiple virtual threads to complete
    pub fn join_all(&self, thread_ids: Vec<VirtualThreadId>) -> PyResult<Vec<Py<PyAny>>> {
        let mut results = Vec::with_capacity(thread_ids.len());
        
        for thread_id in thread_ids {
            let result = self.join(thread_id)?;
            results.push(result);
        }
        
        Ok(results)
    }

    /// Get the state of a virtual thread
    pub fn get_thread_state(&self, thread_id: VirtualThreadId) -> PyResult<String> {
        let threads = self.virtual_threads.lock().unwrap();
        let vthread = threads.iter()
            .find(|t| t.id() == thread_id)
            .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Thread not found"))?;
        
        Ok(format!("{:?}", vthread.state()))
    }

    /// Get statistics about the virtual thread executor
    pub fn get_stats(&self) -> PyResult<(u64, usize, u64, usize)> {
        Ok((
            self.total_threads_created.load(Ordering::Relaxed),
            self.active_threads.load(Ordering::Relaxed),
            self.completed_threads.load(Ordering::Relaxed),
            self.max_platform_threads,
        ))
    }

    /// Shutdown the executor
    pub fn shutdown(&self) -> PyResult<()> {
        self.is_running.store(false, Ordering::Relaxed);
        
        // Notify all threads to wake up and check shutdown
        self.notify_scheduler();
        
        // Wait for platform threads to finish
        let mut handles = self.platform_threads.lock().unwrap();
        for handle in handles.drain(..) {
            let _ = handle.join();
        }
        
        Ok(())
    }

    /// Get active virtual thread count
    pub fn active_thread_count(&self) -> usize {
        self.active_threads.load(Ordering::Relaxed)
    }

    /// Get total virtual threads created
    pub fn total_thread_count(&self) -> u64 {
        self.total_threads_created.load(Ordering::Relaxed)
    }

    /// Get completed virtual threads count
    pub fn completed_thread_count(&self) -> u64 {
        self.completed_threads.load(Ordering::Relaxed)
    }

    /// Check if the executor is running
    pub fn is_running(&self) -> bool {
        self.is_running.load(Ordering::Relaxed)
    }

    /// Context manager support
    pub fn __enter__(pyself: PyRef<'_, Self>) -> PyRef<'_, Self> {
        let _ = pyself.start();
        pyself
    }

    pub fn __exit__(
        &self,
        _exc_type: Option<&Bound<'_, PyAny>>,
        _exc_value: Option<&Bound<'_, PyAny>>,
        _traceback: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<bool> {
        self.shutdown()?;
        Ok(false)
    }
}

/// Utility functions for creating virtual threads
#[pyfunction]
pub fn create_virtual_thread_executor(
    max_virtual_threads: Option<usize>,
    max_platform_threads: Option<usize>,
) -> PyResult<VirtualThreadExecutor> {
    VirtualThreadExecutor::new(max_virtual_threads, max_platform_threads)
}

/// Execute a function in a virtual thread
#[pyfunction]
#[pyo3(signature = (func, args = None, is_blocking = false))]
pub fn execute_in_virtual_thread(
    func: Bound<PyAny>,
    args: Option<Bound<PyTuple>>,
    is_blocking: bool,
) -> PyResult<Py<PyAny>> {
    let executor = VirtualThreadExecutor::new(None, None)?;
    executor.start()?;
    
    let thread_id = executor.submit_virtual_task(func, args, is_blocking)?;
    let result = executor.join(thread_id)?;
    
    executor.shutdown()?;
    Ok(result)
}

/// Parallel map using virtual threads
#[pyfunction]
#[pyo3(signature = (func, iterable, max_virtual_threads = None, max_platform_threads = None))]
pub fn virtual_thread_map(
    func: Bound<PyAny>,
    iterable: Bound<PyAny>,
    max_virtual_threads: Option<usize>,
    max_platform_threads: Option<usize>,
) -> PyResult<Py<PyList>> {
    let py = func.py();
    let executor = VirtualThreadExecutor::new(max_virtual_threads, max_platform_threads)?;
    executor.start()?;
    
    // Convert iterable to vector
    let items: Vec<Py<PyAny>> = iterable.try_iter()?
        .map(|item| Ok(item?.into()))
        .collect::<PyResult<Vec<_>>>()?;
    
    // Submit all tasks
    let mut thread_ids = Vec::with_capacity(items.len());
    for item in items {
        let args = PyTuple::new(py, [item])?;
        let thread_id = executor.submit_virtual_task(
            func.clone(),
            Some(args),
            false,
        )?;
        thread_ids.push(thread_id);
    }
    
    // Collect results
    let results = executor.join_all(thread_ids)?;
    executor.shutdown()?;
    
    Ok(PyList::new(py, results)?.into())
}
