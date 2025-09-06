use pyo3::prelude::*;
use pyo3::types::{PyFunction, PyTuple};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

#[derive(Debug, Clone)]
pub enum RetryStrategy {
    FixedDelay(Duration),
    ExponentialBackoff {
        initial: Duration,
        max: Duration,
        multiplier: f64,
    },
    LinearBackoff {
        initial: Duration,
        increment: Duration,
    },
}

/// Retry executor for handling transient failures
#[pyclass]
pub struct RetryExecutor {
    strategy: RetryStrategy,
    max_attempts: usize,
    exceptions_to_retry: Vec<String>,
    on_retry_callback: Option<Py<PyFunction>>,
}

impl Clone for RetryExecutor {
    fn clone(&self) -> Self {
        Self {
            strategy: self.strategy.clone(),
            max_attempts: self.max_attempts,
            exceptions_to_retry: self.exceptions_to_retry.clone(),
            on_retry_callback: None, // Cannot clone Py<PyFunction>, so reset to None
        }
    }
}

#[pymethods]
impl RetryExecutor {
    #[new]
    #[pyo3(signature = (max_attempts=3, strategy="fixed", initial_delay=1.0, max_delay=None, multiplier=None, increment=None))]
    pub fn new(
        max_attempts: usize,
        strategy: &str,
        initial_delay: f64,
        max_delay: Option<f64>,
        multiplier: Option<f64>,
        increment: Option<f64>,
    ) -> Self {
        let strategy = match strategy {
            "exponential" => RetryStrategy::ExponentialBackoff {
                initial: Duration::from_secs_f64(initial_delay),
                max: Duration::from_secs_f64(max_delay.unwrap_or(60.0)),
                multiplier: multiplier.unwrap_or(2.0),
            },
            "linear" => RetryStrategy::LinearBackoff {
                initial: Duration::from_secs_f64(initial_delay),
                increment: Duration::from_secs_f64(increment.unwrap_or(1.0)),
            },
            _ => RetryStrategy::FixedDelay(Duration::from_secs_f64(initial_delay)),
        };

        Self {
            strategy,
            max_attempts,
            exceptions_to_retry: vec![
                "Exception".to_string(),
                "RuntimeError".to_string(),
                "Error".to_string(),
            ],
            on_retry_callback: None,
        }
    }

    /// Set retry callback function
    pub fn set_retry_callback(&mut self, callback: Py<PyFunction>) {
        self.on_retry_callback = Some(callback);
    }

    /// Add exception types that should trigger retries
    pub fn add_retryable_exception(&mut self, exception_name: String) {
        self.exceptions_to_retry.push(exception_name);
    }

    /// Execute function with retry logic
    pub fn execute(
        &self,
        function: Bound<'_, PyFunction>,
        args: Bound<'_, PyTuple>,
    ) -> PyResult<Py<PyAny>> {
        let mut last_error: Option<PyErr> = None;

        for attempt in 0..self.max_attempts {
            match function.call1(&args) {
                Ok(result) => return Ok(result.unbind()),
                Err(err) => {
                    // Check if this exception should trigger a retry
                    let should_retry = self.should_retry_error(&err);

                    if !should_retry || attempt == self.max_attempts - 1 {
                        return Err(err);
                    }

                    last_error = Some(err);

                    // Calculate delay for this attempt
                    let delay = self.calculate_delay(attempt);

                    // Call retry callback if set (simplified - just sleep for now)
                    thread::sleep(delay);
                }
            }
        }

        // If we get here, all attempts failed
        Err(last_error.unwrap_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("All retry attempts failed")
        }))
    }

    /// Get retry statistics
    pub fn get_stats<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, pyo3::types::PyDict>> {
        let stats = pyo3::types::PyDict::new(py);
        stats.set_item("max_attempts", self.max_attempts)?;
        stats.set_item("strategy", format!("{:?}", self.strategy))?;
        stats.set_item("retryable_exceptions", &self.exceptions_to_retry)?;
        Ok(stats)
    }
}

impl RetryExecutor {
    fn should_retry_error(&self, error: &PyErr) -> bool {
        // Simple implementation - always retry for demo
        Python::attach(|py| {
            let error_type = error.get_type(py);
            let error_name = error_type
                .name()
                .map(|s| s.to_string())
                .unwrap_or_else(|_| "Unknown".to_string());
            self.exceptions_to_retry
                .iter()
                .any(|exc| error_name.contains(exc))
        })
    }

    fn calculate_delay(&self, attempt: usize) -> Duration {
        match &self.strategy {
            RetryStrategy::FixedDelay(delay) => *delay,
            RetryStrategy::ExponentialBackoff {
                initial,
                max,
                multiplier,
            } => {
                let delay = initial.as_secs_f64() * multiplier.powi(attempt as i32);
                Duration::from_secs_f64(delay.min(max.as_secs_f64()))
            }
            RetryStrategy::LinearBackoff { initial, increment } => {
                *initial + *increment * attempt as u32
            }
        }
    }
}

/// Circuit breaker implementation
#[pyclass]
#[derive(Clone)]
pub struct CircuitBreaker {
    failure_threshold: usize,
    recovery_timeout: Duration,
    failure_count: Arc<Mutex<usize>>,
    last_failure: Arc<Mutex<Option<Instant>>>,
    state: Arc<Mutex<CircuitState>>,
}

#[derive(Debug, Clone)]
enum CircuitState {
    Closed,   // Normal operation
    Open,     // Failing fast
    HalfOpen, // Testing if service recovered
}

#[pymethods]
impl CircuitBreaker {
    #[new]
    pub fn new(failure_threshold: Option<usize>, recovery_timeout: Option<f64>) -> Self {
        Self {
            failure_threshold: failure_threshold.unwrap_or(5),
            recovery_timeout: Duration::from_secs_f64(recovery_timeout.unwrap_or(60.0)),
            failure_count: Arc::new(Mutex::new(0)),
            last_failure: Arc::new(Mutex::new(None)),
            state: Arc::new(Mutex::new(CircuitState::Closed)),
        }
    }

    /// Execute function with circuit breaker protection
    pub fn execute(
        &self,
        _py: Python<'_>,
        function: Bound<'_, PyFunction>,
        args: Bound<'_, PyTuple>,
    ) -> PyResult<Py<PyAny>> {
        // Check current state
        {
            let mut state = self.state.lock().unwrap();
            let last_failure = *self.last_failure.lock().unwrap();

            match *state {
                CircuitState::Open => {
                    // Check if we should transition to half-open
                    if let Some(last_fail) = last_failure {
                        if last_fail.elapsed() >= self.recovery_timeout {
                            *state = CircuitState::HalfOpen;
                        } else {
                            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                                "Circuit breaker is open - failing fast",
                            ));
                        }
                    }
                }
                CircuitState::HalfOpen => {
                    // Allow limited testing
                }
                CircuitState::Closed => {
                    // Normal operation
                }
            }
        }

        // Execute the function
        match function.call1(&args) {
            Ok(result) => {
                // Success - reset failure count and close circuit
                *self.failure_count.lock().unwrap() = 0;
                *self.state.lock().unwrap() = CircuitState::Closed;
                Ok(result.unbind())
            }
            Err(err) => {
                // Failure - increment count and potentially open circuit
                let mut failure_count = self.failure_count.lock().unwrap();
                *failure_count += 1;
                *self.last_failure.lock().unwrap() = Some(Instant::now());

                if *failure_count >= self.failure_threshold {
                    *self.state.lock().unwrap() = CircuitState::Open;
                }

                Err(err)
            }
        }
    }

    /// Get circuit breaker status
    pub fn get_status<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, pyo3::types::PyDict>> {
        let stats = pyo3::types::PyDict::new(py);
        let state = self.state.lock().unwrap();
        let failure_count = *self.failure_count.lock().unwrap();

        let state_str = match *state {
            CircuitState::Closed => "closed",
            CircuitState::Open => "open",
            CircuitState::HalfOpen => "half_open",
        };

        stats.set_item("state", state_str)?;
        stats.set_item("failure_count", failure_count)?;
        stats.set_item("failure_threshold", self.failure_threshold)?;
        Ok(stats)
    }

    /// Reset circuit breaker to closed state
    pub fn reset(&self) -> PyResult<()> {
        *self.failure_count.lock().unwrap() = 0;
        *self.last_failure.lock().unwrap() = None;
        *self.state.lock().unwrap() = CircuitState::Closed;
        Ok(())
    }
}
