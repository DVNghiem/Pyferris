use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple};
use std::sync::{Arc, Mutex};

/// Creates a function that memoizes the result of func.
#[pyfunction]
pub fn memoize(py: Python, func: Bound<PyAny>, resolver: Option<Bound<PyAny>>) -> PyResult<Py<PyAny>> {
    // This is a simplified version. A real implementation needs to store the cache.
    // Since we are returning a Python function, we can use a Python closure or class.
    // But here we want to use Rust.
    // However, creating a stateful Rust closure callable from Python is tricky without a class.
    // So we will define a helper class in Python or use a Python-side wrapper in the final module.
    // For now, let's implement a simple wrapper that uses a dict attached to the function if possible,
    // or return a Python lambda that calls a Rust class.
    
    // Actually, best way is to return a Python object that is callable (a class instance).
    
    let memoize_cls = py.import("pyferris.lodash")?.getattr("Memoize")?;
    memoize_cls.call1((func, resolver)).map(|v| v.into())
}

// We will implement the Memoize class in Python side for simplicity of state management with GC,
// or we can implement a Rust class `MemoizedFunction`. Let's do the Rust class.

#[pyclass]
struct MemoizedFunction {
    func: Py<PyAny>,
    resolver: Option<Py<PyAny>>,
    cache: Py<PyDict>,
}

#[pymethods]
impl MemoizedFunction {
    #[new]
    fn new(func: Py<PyAny>, resolver: Option<Py<PyAny>>) -> Self {
        Python::with_gil(|py| {
            Self {
                func,
                resolver,
                cache: PyDict::new(py).into(),
            }
        })
    }

    fn __call__(&self, py: Python, args: &Bound<PyTuple>, kwargs: Option<&Bound<PyDict>>) -> PyResult<Py<PyAny>> {
        let key = if let Some(resolver) = &self.resolver {
            resolver.bind(py).call(args, kwargs)?
        } else {
            // Default key is the first argument, or string representation of args
            if let Ok(first) = args.get_item(0) {
                first.into()
            } else {
                args.clone().into_any().into()
            }
        };

        let cache = self.cache.bind(py);
        if let Some(val) = cache.get_item(&key)? {
            return Ok(val.into());
        }

        let result = self.func.bind(py).call(args, kwargs)?;
        cache.set_item(key, &result)?;
        Ok(result.into())
    }
    
    #[getter]
    fn cache(&self, py: Python) -> PyResult<Py<PyDict>> {
        Ok(self.cache.clone_ref(py))
    }
}

/// Creates a function that is restricted to invoking func once. Repeat calls to the function return the value of the first invocation.
#[pyfunction]
pub fn once(py: Python, func: Bound<PyAny>) -> PyResult<Py<PyAny>> {
    let once_wrapper = Py::new(py, OnceWrapper::new(func.into()))?;
    Ok(once_wrapper.into_any())
}

#[pyclass]
struct OnceWrapper {
    func: Option<Py<PyAny>>,
    result: Option<Py<PyAny>>,
}

#[pymethods]
impl OnceWrapper {
    #[new]
    fn new(func: Py<PyAny>) -> Self {
        Self {
            func: Some(func),
            result: None,
        }
    }

    fn __call__(&mut self, py: Python, args: &Bound<PyTuple>, kwargs: Option<&Bound<PyDict>>) -> PyResult<Py<PyAny>> {
        if let Some(func) = &self.func {
            let res = func.bind(py).call(args, kwargs)?;
            self.result = Some(res.clone().into());
            self.func = None; // Drop function to release references if needed
            Ok(res.into())
        } else {
            Ok(self.result.as_ref().unwrap().clone_ref(py))
        }
    }
}

/// The opposite of `before`; this method creates a function that invokes func once it's called n or more times.
#[pyfunction]
pub fn after(py: Python, n: usize, func: Bound<PyAny>) -> PyResult<Py<PyAny>> {
    let wrapper = Py::new(py, AfterWrapper::new(n, func.into()))?;
    Ok(wrapper.into_any())
}

#[pyclass]
struct AfterWrapper {
    n: usize,
    count: usize,
    func: Py<PyAny>,
}

#[pymethods]
impl AfterWrapper {
    #[new]
    fn new(n: usize, func: Py<PyAny>) -> Self {
        Self { n, count: 0, func }
    }

    fn __call__(&mut self, py: Python, args: &Bound<PyTuple>, kwargs: Option<&Bound<PyDict>>) -> PyResult<Py<PyAny>> {
        self.count += 1;
        if self.count >= self.n {
            self.func.bind(py).call(args, kwargs).map(|v| v.into())
        } else {
            Ok(py.None())
        }
    }
}

/// Creates a function that invokes func while it's called less than n times.
#[pyfunction]
pub fn before(py: Python, n: usize, func: Bound<PyAny>) -> PyResult<Py<PyAny>> {
    let wrapper = Py::new(py, BeforeWrapper::new(n, func.into()))?;
    Ok(wrapper.into_any())
}

#[pyclass]
struct BeforeWrapper {
    n: usize,
    count: usize,
    func: Py<PyAny>,
    result: Option<Py<PyAny>>,
}

#[pymethods]
impl BeforeWrapper {
    #[new]
    fn new(n: usize, func: Py<PyAny>) -> Self {
        Self { n, count: 0, func, result: None }
    }

    fn __call__(&mut self, py: Python, args: &Bound<PyTuple>, kwargs: Option<&Bound<PyDict>>) -> PyResult<Py<PyAny>> {
        self.count += 1;
        if self.count < self.n {
            let res = self.func.bind(py).call(args, kwargs)?;
            self.result = Some(res.clone().into());
            Ok(res.into())
        } else {
            Ok(self.result.as_ref().unwrap().clone_ref(py))
        }
    }
}

#[pymodule]
pub fn function(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<MemoizedFunction>()?;
    m.add_class::<OnceWrapper>()?;
    m.add_class::<AfterWrapper>()?;
    m.add_class::<BeforeWrapper>()?;
    
    // We don't export the classes directly as public API, but use helper functions
    // Actually, exporting classes is fine too.
    
    // m.add_function(wrap_pyfunction!(memoize, m)?)?; // We need to fix memoize implementation first
    // For now, let's just expose the classes or use a simple wrapper
    
    // Re-implement memoize to return the class instance directly
    #[pyfunction]
    fn memoize_fn(py: Python, func: Bound<PyAny>, resolver: Option<Bound<PyAny>>) -> PyResult<Py<PyAny>> {
        let wrapper = Py::new(py, MemoizedFunction::new(func.into(), resolver.map(|r| r.into())))?;
        Ok(wrapper.into_any())
    }
    m.add_function(wrap_pyfunction!(memoize_fn, m)?)?;
    
    m.add_function(wrap_pyfunction!(once, m)?)?;
    m.add_function(wrap_pyfunction!(after, m)?)?;
    m.add_function(wrap_pyfunction!(before, m)?)?;
    Ok(())
}
