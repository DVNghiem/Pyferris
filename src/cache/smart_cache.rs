use pyo3::prelude::*;
use pyo3::types::PyType;
use std::collections::HashMap;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

/// Cache eviction policies
#[pyclass]
#[derive(Clone, Debug, PartialEq)]
pub enum EvictionPolicy {
    /// Least Recently Used - evicts the least recently accessed items
    LRU,
    /// Least Frequently Used - evicts the least frequently accessed items
    LFU,
    /// Time-based eviction - evicts items after a specified TTL
    TTL,
    /// Adaptive - dynamically switches between LRU and LFU based on hit rate
    Adaptive,
}

#[pymethods]
impl EvictionPolicy {
    /// Create LRU policy
    #[classmethod]
    pub fn lru(_cls: &Bound<'_, PyType>) -> Self {
        EvictionPolicy::LRU
    }

    /// Create LFU policy
    #[classmethod]
    pub fn lfu(_cls: &Bound<'_, PyType>) -> Self {
        EvictionPolicy::LFU
    }

    /// Create TTL policy
    #[classmethod]
    pub fn ttl(_cls: &Bound<'_, PyType>) -> Self {
        EvictionPolicy::TTL
    }

    /// Create Adaptive policy
    #[classmethod]
    pub fn adaptive(_cls: &Bound<'_, PyType>) -> Self {
        EvictionPolicy::Adaptive
    }

    fn __repr__(&self) -> String {
        match self {
            EvictionPolicy::LRU => "EvictionPolicy.LRU".to_string(),
            EvictionPolicy::LFU => "EvictionPolicy.LFU".to_string(),
            EvictionPolicy::TTL => "EvictionPolicy.TTL".to_string(),
            EvictionPolicy::Adaptive => "EvictionPolicy.Adaptive".to_string(),
        }
    }
}

/// Cache entry metadata
#[derive(Debug)]
struct CacheEntry {
    value: Py<PyAny>,
    access_count: u64,
    last_accessed: Instant,
    created_at: Instant,
}

/// Internal cache statistics
#[derive(Clone, Debug)]
struct CacheStats {
    hits: u64,
    misses: u64,
    evictions: u64,
    current_size: usize,
}

/// A high-performance thread-safe cache with multiple eviction policies
#[pyclass]
pub struct SmartCache {
    cache: Arc<Mutex<HashMap<u64, CacheEntry>>>,
    policy: EvictionPolicy,
    max_size: usize,
    ttl: Option<Duration>,
    stats: Arc<Mutex<CacheStats>>,
    adaptive_threshold: f64,
    #[allow(dead_code)]
    adaptive_window: u64,
}

impl SmartCache {
    /// Hash a Python object to use as cache key
    fn hash_key(&self, py: Python, key: &Py<PyAny>) -> PyResult<u64> {
        let key_str = key.bind(py).str()?.to_string();
        let mut hasher = DefaultHasher::new();
        key_str.hash(&mut hasher);
        Ok(hasher.finish())
    }

    /// Check if an entry has expired based on TTL
    fn is_expired(&self, entry: &CacheEntry) -> bool {
        if let Some(ttl) = self.ttl {
            entry.created_at.elapsed() > ttl
        } else {
            false
        }
    }

    /// Update entry access information
    fn update_access(&self, entry: &mut CacheEntry) {
        entry.access_count += 1;
        entry.last_accessed = Instant::now();
    }

    /// Find the key to evict based on the current policy
    fn find_eviction_key(&self, cache: &HashMap<u64, CacheEntry>) -> Option<u64> {
        match self.policy {
            EvictionPolicy::LRU => cache
                .iter()
                .min_by_key(|(_, entry)| entry.last_accessed)
                .map(|(key, _)| *key),
            EvictionPolicy::LFU => cache
                .iter()
                .min_by_key(|(_, entry)| entry.access_count)
                .map(|(key, _)| *key),
            EvictionPolicy::TTL => {
                // Find oldest entry for TTL policy
                cache
                    .iter()
                    .min_by_key(|(_, entry)| entry.created_at)
                    .map(|(key, _)| *key)
            }
            EvictionPolicy::Adaptive => {
                // Adaptive policy switches between LRU and LFU based on hit rate
                let stats = self.stats.lock().unwrap();
                let hit_rate = if stats.hits + stats.misses > 0 {
                    stats.hits as f64 / (stats.hits + stats.misses) as f64
                } else {
                    0.0
                };

                if hit_rate > self.adaptive_threshold {
                    // High hit rate, use LFU to keep frequently accessed items
                    cache
                        .iter()
                        .min_by_key(|(_, entry)| entry.access_count)
                        .map(|(key, _)| *key)
                } else {
                    // Low hit rate, use LRU to make room for new items
                    cache
                        .iter()
                        .min_by_key(|(_, entry)| entry.last_accessed)
                        .map(|(key, _)| *key)
                }
            }
        }
    }

    /// Evict expired entries
    fn evict_expired(&self, cache: &mut HashMap<u64, CacheEntry>) -> usize {
        if self.ttl.is_none() {
            return 0;
        }

        let expired_keys: Vec<u64> = cache
            .iter()
            .filter(|(_, entry)| self.is_expired(entry))
            .map(|(key, _)| *key)
            .collect();

        let count = expired_keys.len();
        for key in expired_keys {
            cache.remove(&key);
        }

        count
    }

    /// Evict entries to make room for new ones
    fn evict_if_needed(&self, cache: &mut HashMap<u64, CacheEntry>) -> usize {
        let mut evicted = 0;

        // First, evict expired entries
        evicted += self.evict_expired(cache);

        // Then, evict based on policy if still over capacity
        while cache.len() >= self.max_size {
            if let Some(key) = self.find_eviction_key(cache) {
                cache.remove(&key);
                evicted += 1;
            } else {
                break;
            }
        }

        evicted
    }
}

#[pymethods]
impl SmartCache {
    /// Create a new SmartCache instance
    #[new]
    #[pyo3(signature = (max_size = 1000, policy = EvictionPolicy::LRU, ttl_seconds = None, adaptive_threshold = 0.7))]
    pub fn new(
        max_size: usize,
        policy: EvictionPolicy,
        ttl_seconds: Option<f64>,
        adaptive_threshold: f64,
    ) -> Self {
        let ttl = ttl_seconds.map(Duration::from_secs_f64);

        Self {
            cache: Arc::new(Mutex::new(HashMap::new())),
            policy,
            max_size,
            ttl,
            stats: Arc::new(Mutex::new(CacheStats {
                hits: 0,
                misses: 0,
                evictions: 0,
                current_size: 0,
            })),
            adaptive_threshold,
            adaptive_window: 1000,
        }
    }

    /// Get a value from the cache
    pub fn get(&self, py: Python, key: Py<PyAny>) -> PyResult<Option<Py<PyAny>>> {
        let hash_key = self.hash_key(py, &key)?;
        let mut cache = self.cache.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Cache lock poisoned")
        })?;

        if let Some(entry) = cache.get_mut(&hash_key) {
            if !self.is_expired(entry) {
                self.update_access(entry);

                // Update hit statistics
                let mut stats = self.stats.lock().map_err(|_| {
                    PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Stats lock poisoned")
                })?;
                stats.hits += 1;

                return Ok(Some(entry.value.clone_ref(py)));
            } else {
                // Entry expired, remove it
                cache.remove(&hash_key);
            }
        }

        // Cache miss
        let mut stats = self.stats.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Stats lock poisoned")
        })?;
        stats.misses += 1;

        Ok(None)
    }

    /// Put a value into the cache
    pub fn put(&self, py: Python, key: Py<PyAny>, value: Py<PyAny>) -> PyResult<()> {
        let hash_key = self.hash_key(py, &key)?;
        let mut cache = self.cache.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Cache lock poisoned")
        })?;

        let now = Instant::now();
        let entry = CacheEntry {
            value,
            access_count: 1,
            last_accessed: now,
            created_at: now,
        };

        // Check if we need to evict entries
        let evicted = self.evict_if_needed(&mut cache);

        cache.insert(hash_key, entry);

        // Update statistics
        let mut stats = self.stats.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Stats lock poisoned")
        })?;
        stats.current_size = cache.len();
        stats.evictions += evicted as u64;

        Ok(())
    }

    /// Check if a key exists in the cache
    pub fn contains(&self, py: Python, key: Py<PyAny>) -> PyResult<bool> {
        let hash_key = self.hash_key(py, &key)?;
        let cache = self.cache.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Cache lock poisoned")
        })?;

        if let Some(entry) = cache.get(&hash_key) {
            Ok(!self.is_expired(entry))
        } else {
            Ok(false)
        }
    }

    /// Remove a key from the cache
    pub fn remove(&self, py: Python, key: Py<PyAny>) -> PyResult<Option<Py<PyAny>>> {
        let hash_key = self.hash_key(py, &key)?;
        let mut cache = self.cache.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Cache lock poisoned")
        })?;

        if let Some(entry) = cache.remove(&hash_key) {
            // Update statistics
            let mut stats = self.stats.lock().map_err(|_| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Stats lock poisoned")
            })?;
            stats.current_size = cache.len();

            Ok(Some(entry.value))
        } else {
            Ok(None)
        }
    }

    /// Clear all entries from the cache
    pub fn clear(&self) -> PyResult<()> {
        let mut cache = self.cache.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Cache lock poisoned")
        })?;
        cache.clear();

        // Reset statistics
        let mut stats = self.stats.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Stats lock poisoned")
        })?;
        stats.current_size = 0;

        Ok(())
    }

    /// Get the current size of the cache
    pub fn size(&self) -> PyResult<usize> {
        let cache = self.cache.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Cache lock poisoned")
        })?;
        Ok(cache.len())
    }

    /// Get cache statistics
    pub fn stats(&self, py: Python) -> PyResult<Py<PyAny>> {
        let stats = self.stats.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Stats lock poisoned")
        })?;

        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("hits", stats.hits)?;
        dict.set_item("misses", stats.misses)?;
        dict.set_item("evictions", stats.evictions)?;
        dict.set_item("current_size", stats.current_size)?;
        dict.set_item("max_size", self.max_size)?;

        let hit_rate = if stats.hits + stats.misses > 0 {
            stats.hits as f64 / (stats.hits + stats.misses) as f64
        } else {
            0.0
        };
        dict.set_item("hit_rate", hit_rate)?;

        Ok(dict.into())
    }

    /// Manually trigger cleanup of expired entries
    pub fn cleanup(&self) -> PyResult<usize> {
        let mut cache = self.cache.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Cache lock poisoned")
        })?;

        let evicted = self.evict_expired(&mut cache);

        // Update statistics
        let mut stats = self.stats.lock().map_err(|_| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Stats lock poisoned")
        })?;
        stats.current_size = cache.len();
        stats.evictions += evicted as u64;

        Ok(evicted)
    }

    /// Get/set the eviction policy
    pub fn get_policy(&self) -> EvictionPolicy {
        self.policy.clone()
    }

    pub fn set_policy(&mut self, policy: EvictionPolicy) {
        self.policy = policy;
    }

    /// Get/set the maximum size
    pub fn get_max_size(&self) -> usize {
        self.max_size
    }

    pub fn set_max_size(&mut self, max_size: usize) {
        self.max_size = max_size;
    }

    /// Get/set the TTL in seconds
    pub fn get_ttl(&self) -> Option<f64> {
        self.ttl.map(|d| d.as_secs_f64())
    }

    pub fn set_ttl(&mut self, ttl_seconds: Option<f64>) {
        self.ttl = ttl_seconds.map(Duration::from_secs_f64);
    }

    /// String representation
    fn __repr__(&self) -> String {
        format!(
            "SmartCache(max_size={}, policy={:?}, ttl={:?})",
            self.max_size,
            self.policy,
            self.ttl.map(|d| d.as_secs_f64())
        )
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }
}
