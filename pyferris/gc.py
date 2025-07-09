"""
Auto Garbage Collection System for Pyferris

This module provides advanced automatic garbage collection capabilities specifically designed
for high-performance Python applications. It includes intelligent memory management,
resource cleanup, and optimization strategies.
"""

import gc
import weakref
import threading
import time
import os
from typing import Any, Dict, List, Optional, Callable, Set
from collections import defaultdict, deque
from contextlib import contextmanager
from functools import wraps
import logging

from .memory import MemoryPool, memory_mapped_array, memory_mapped_info
from .profiling import Profiler
from .concurrent import AtomicCounter

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class AutoGCConfig:
    """Configuration for automatic garbage collection system."""
    
    def __init__(self):
        self.enabled = True
        self.aggressive_mode = False
        self.memory_threshold_mb = 512  # Trigger GC when memory usage exceeds this
        self.memory_threshold_percent = 80  # Trigger GC when memory usage exceeds this percentage
        self.cleanup_interval = 5.0  # Seconds between cleanup cycles
        self.generation_thresholds = (700, 10, 10)  # GC generation thresholds
        self.track_allocations = True
        self.profile_gc = True
        self.auto_optimize = True
        self.weak_ref_cleanup = True
        self.memory_pool_management = True
        self.mmap_file_cleanup = True
        self.thread_safe = True
        self.emergency_threshold_mb = 1024  # Emergency cleanup threshold
        self.max_cleanup_time = 10.0  # Maximum time to spend in one cleanup cycle

class MemoryTracker:
    """Advanced memory tracking and analysis."""
    
    def __init__(self):
        self.allocations = defaultdict(int)
        self.deallocations = defaultdict(int)
        self.peak_memory = 0
        self.total_allocations = AtomicCounter()
        self.total_deallocations = AtomicCounter()
        self.memory_timeline = deque(maxlen=100)  # Keep last 100 memory samples
        self.lock = threading.RLock()
        self.profiler = Profiler()
        
    def track_allocation(self, obj_type: str, size: int):
        """Track memory allocation."""
        with self.lock:
            self.allocations[obj_type] += size
            self.total_allocations.increment()
            self._update_peak_memory()
            
    def track_deallocation(self, obj_type: str, size: int):
        """Track memory deallocation."""
        with self.lock:
            self.deallocations[obj_type] += size
            self.total_deallocations.increment()
            
    def _update_peak_memory(self):
        """Update peak memory usage."""
        current_memory = self.get_current_memory_mb()
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory
            
    def get_current_memory_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            if HAS_PSUTIL:
                process = psutil.Process(os.getpid())
                return process.memory_info().rss / 1024 / 1024
            else:
                # Fallback to basic memory estimation
                return 0.0
        except Exception:
            return 0.0
            
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        with self.lock:
            current_memory = self.get_current_memory_mb()
            self.memory_timeline.append((time.time(), current_memory))
            
            return {
                'current_memory_mb': current_memory,
                'peak_memory_mb': self.peak_memory,
                'total_allocations': self.total_allocations.get(),
                'total_deallocations': self.total_deallocations.get(),
                'net_allocations': self.total_allocations.get() - self.total_deallocations.get(),
                'allocations_by_type': dict(self.allocations),
                'deallocations_by_type': dict(self.deallocations),
                'memory_timeline': list(self.memory_timeline)[-10:],  # Last 10 samples
                'gc_stats': gc.get_stats(),
                'gc_counts': gc.get_count()
            }

class ResourceManager:
    """Manages cleanup of various resource types."""
    
    def __init__(self):
        self.memory_pools: Set[MemoryPool] = set()
        self.mmap_files: Set[str] = set()
        self.weak_refs: Set[weakref.ref] = set()
        self.cleanup_callbacks: List[Callable] = []
        self.lock = threading.RLock()
        
    def register_memory_pool(self, pool: MemoryPool):
        """Register a memory pool for automatic cleanup."""
        with self.lock:
            self.memory_pools.add(pool)
            
    def unregister_memory_pool(self, pool: MemoryPool):
        """Unregister a memory pool."""
        with self.lock:
            self.memory_pools.discard(pool)
            
    def register_mmap_file(self, filepath: str):
        """Register a memory-mapped file for cleanup."""
        with self.lock:
            self.mmap_files.add(filepath)
            
    def unregister_mmap_file(self, filepath: str):
        """Unregister a memory-mapped file."""
        with self.lock:
            self.mmap_files.discard(filepath)
            
    def register_weak_ref(self, ref: weakref.ref):
        """Register a weak reference for cleanup."""
        with self.lock:
            self.weak_refs.add(ref)
            
    def register_cleanup_callback(self, callback: Callable):
        """Register a cleanup callback."""
        with self.lock:
            self.cleanup_callbacks.append(callback)
            
    def cleanup_memory_pools(self) -> int:
        """Clean up memory pools and return number of blocks freed."""
        freed_blocks = 0
        with self.lock:
            for pool in list(self.memory_pools):
                try:
                    stats = pool.stats()
                    if stats.get('available_blocks', 0) > 0:
                        # Only clear if there are available blocks
                        pool.clear()
                        freed_blocks += stats.get('available_blocks', 0)
                except Exception:
                    logger.warning(f"Failed to cleanup memory pool: {pool}")
                    
        return freed_blocks
        
    def cleanup_mmap_files(self) -> int:
        """Clean up orphaned memory-mapped files."""
        cleaned_files = 0
        with self.lock:
            for filepath in list(self.mmap_files):
                try:
                    if os.path.exists(filepath):
                        info = memory_mapped_info(filepath)
                        # Check if file is still in use (basic heuristic)
                        if info.get('size_mb', 0) > 0:
                            # File exists and has content, check if it's truly orphaned
                            # This is a simplified check - in production, you'd want more sophisticated tracking
                            pass
                except Exception:
                    logger.warning(f"Failed to cleanup mmap file: {filepath}")
                    
        return cleaned_files
        
    def cleanup_weak_refs(self) -> int:
        """Clean up dead weak references."""
        cleaned_refs = 0
        with self.lock:
            dead_refs = [ref for ref in self.weak_refs if ref() is None]
            for ref in dead_refs:
                self.weak_refs.discard(ref)
                cleaned_refs += 1
                
        return cleaned_refs
        
    def run_cleanup_callbacks(self):
        """Run all registered cleanup callbacks."""
        with self.lock:
            for callback in self.cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.warning(f"Cleanup callback failed: {e}")

class AutoGarbageCollector:
    """Advanced automatic garbage collection system."""
    
    def __init__(self, config: Optional[AutoGCConfig] = None):
        self.config = config or AutoGCConfig()
        self.memory_tracker = MemoryTracker()
        self.resource_manager = ResourceManager()
        self.profiler = Profiler()
        
        self._running = False
        self._cleanup_thread = None
        self._lock = threading.RLock()
        self._last_cleanup = time.time()
        self._cleanup_stats = defaultdict(int)
        self._emergency_cleanups = 0
        
        # Set up GC thresholds
        if self.config.enabled:
            gc.set_threshold(*self.config.generation_thresholds)
            
        # Track original objects for restoration if needed
        self._original_gc_callbacks = gc.callbacks.copy()
        
    def start(self):
        """Start the automatic garbage collection system."""
        with self._lock:
            if self._running:
                return
                
            self._running = True
            logger.info("Starting Auto Garbage Collection System")
            
            # Register GC callbacks
            if self.config.profile_gc:
                gc.callbacks.append(self._gc_callback)
                
            # Start cleanup thread
            self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self._cleanup_thread.start()
            
    def stop(self):
        """Stop the automatic garbage collection system."""
        with self._lock:
            if not self._running:
                return
                
            self._running = False
            logger.info("Stopping Auto Garbage Collection System")
            
            # Clean up callbacks
            gc.callbacks.clear()
            gc.callbacks.extend(self._original_gc_callbacks)
            
            # Wait for cleanup thread to finish
            if self._cleanup_thread:
                self._cleanup_thread.join(timeout=5.0)
                
    def _gc_callback(self, phase: str, info: Dict[str, Any]):
        """Callback for garbage collection events."""
        if self.config.profile_gc:
            self.profiler.increment_counter(f"gc_{phase}")
            
            if phase == 'start':
                self.profiler.start_timer("gc_collection")
            elif phase == 'stop':
                self.profiler.stop_timer("gc_collection")
                
    def _cleanup_loop(self):
        """Main cleanup loop running in background thread."""
        while self._running:
            try:
                time.sleep(self.config.cleanup_interval)
                
                if not self._running:
                    break
                    
                # Check if cleanup is needed
                if self._should_cleanup():
                    self._perform_cleanup()
                    
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                
    def _should_cleanup(self) -> bool:
        """Determine if cleanup should be performed."""
        current_memory = self.memory_tracker.get_current_memory_mb()
        
        # Check memory thresholds
        if current_memory > self.config.memory_threshold_mb:
            return True
            
        # Check memory percentage
        try:
            if HAS_PSUTIL:
                memory_percent = psutil.virtual_memory().percent
                if memory_percent > self.config.memory_threshold_percent:
                    return True
        except Exception:
            pass
            
        # Check time since last cleanup
        if time.time() - self._last_cleanup > self.config.cleanup_interval * 2:
            return True
            
        return False
        
    def _perform_cleanup(self):
        """Perform comprehensive cleanup."""
        cleanup_start = time.time()
        
        try:
            with self._lock:
                self.profiler.start_timer("auto_cleanup")
                
                # Check for emergency cleanup
                current_memory = self.memory_tracker.get_current_memory_mb()
                emergency_mode = current_memory > self.config.emergency_threshold_mb
                
                if emergency_mode:
                    self._emergency_cleanups += 1
                    logger.warning(f"Emergency cleanup triggered at {current_memory:.1f}MB")
                    
                # 1. Clean up weak references
                cleaned_refs = self.resource_manager.cleanup_weak_refs()
                self._cleanup_stats['weak_refs'] += cleaned_refs
                
                # 2. Clean up memory pools
                if self.config.memory_pool_management:
                    freed_blocks = self.resource_manager.cleanup_memory_pools()
                    self._cleanup_stats['memory_pool_blocks'] += freed_blocks
                    
                # 3. Clean up memory-mapped files
                if self.config.mmap_file_cleanup:
                    cleaned_files = self.resource_manager.cleanup_mmap_files()
                    self._cleanup_stats['mmap_files'] += cleaned_files
                    
                # 4. Run custom cleanup callbacks
                self.resource_manager.run_cleanup_callbacks()
                
                # 5. Force garbage collection
                if emergency_mode or self.config.aggressive_mode:
                    # Aggressive cleanup
                    for generation in range(3):
                        collected = gc.collect(generation)
                        self._cleanup_stats[f'gc_gen_{generation}'] += collected
                else:
                    # Normal cleanup
                    collected = gc.collect()
                    self._cleanup_stats['gc_normal'] += collected
                    
                # 6. Optimize if enabled
                if self.config.auto_optimize:
                    self._optimize_gc_settings()
                    
                self._last_cleanup = time.time()
                self.profiler.stop_timer("auto_cleanup")
                
                # Log cleanup results
                cleanup_time = time.time() - cleanup_start
                logger.info(f"Cleanup completed in {cleanup_time:.2f}s, freed {cleaned_refs} refs, "
                           f"{freed_blocks} pool blocks, collected {collected} objects")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            
    def _optimize_gc_settings(self):
        """Automatically optimize GC settings based on usage patterns."""
        stats = self.memory_tracker.get_memory_stats()
        
        # Adaptive threshold adjustment
        if stats['net_allocations'] > 1000:
            # High allocation rate - reduce thresholds for more frequent GC
            new_thresholds = (max(100, self.config.generation_thresholds[0] - 100),
                            max(5, self.config.generation_thresholds[1] - 2),
                            max(5, self.config.generation_thresholds[2] - 2))
            gc.set_threshold(*new_thresholds)
        elif stats['net_allocations'] < 100:
            # Low allocation rate - increase thresholds for less frequent GC
            new_thresholds = (min(1000, self.config.generation_thresholds[0] + 100),
                            min(20, self.config.generation_thresholds[1] + 2),
                            min(20, self.config.generation_thresholds[2] + 2))
            gc.set_threshold(*new_thresholds)
            
    def force_cleanup(self):
        """Force immediate cleanup."""
        logger.info("Forcing immediate cleanup")
        self._perform_cleanup()
        
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive garbage collection statistics."""
        with self._lock:
            return {
                'enabled': self.config.enabled,
                'running': self._running,
                'emergency_cleanups': self._emergency_cleanups,
                'cleanup_stats': dict(self._cleanup_stats),
                'memory_stats': self.memory_tracker.get_memory_stats(),
                'gc_thresholds': gc.get_threshold(),
                'gc_counts': gc.get_count(),
                'gc_stats': gc.get_stats(),
                'resource_counts': {
                    'memory_pools': len(self.resource_manager.memory_pools),
                    'mmap_files': len(self.resource_manager.mmap_files),
                    'weak_refs': len(self.resource_manager.weak_refs),
                    'cleanup_callbacks': len(self.resource_manager.cleanup_callbacks)
                }
            }
            
    def configure(self, **kwargs):
        """Dynamically configure the garbage collector."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    logger.info(f"Updated config: {key} = {value}")
                    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

# Global instance
_auto_gc = None
_auto_gc_lock = threading.Lock()

def get_auto_gc() -> AutoGarbageCollector:
    """Get the global AutoGarbageCollector instance."""
    global _auto_gc
    with _auto_gc_lock:
        if _auto_gc is None:
            _auto_gc = AutoGarbageCollector()
        return _auto_gc

def enable_auto_gc(config: Optional[AutoGCConfig] = None):
    """Enable automatic garbage collection."""
    global _auto_gc
    with _auto_gc_lock:
        if _auto_gc is None:
            _auto_gc = AutoGarbageCollector(config)
        _auto_gc.start()

def disable_auto_gc():
    """Disable automatic garbage collection."""
    global _auto_gc
    with _auto_gc_lock:
        if _auto_gc is not None:
            _auto_gc.stop()

def force_gc():
    """Force immediate garbage collection."""
    auto_gc = get_auto_gc()
    auto_gc.force_cleanup()

def gc_stats() -> Dict[str, Any]:
    """Get garbage collection statistics."""
    auto_gc = get_auto_gc()
    return auto_gc.get_stats()

def track_allocation(obj_type: str, size: int):
    """Track memory allocation for an object type."""
    auto_gc = get_auto_gc()
    auto_gc.memory_tracker.track_allocation(obj_type, size)

def track_deallocation(obj_type: str, size: int):
    """Track memory deallocation for an object type."""
    auto_gc = get_auto_gc()
    auto_gc.memory_tracker.track_deallocation(obj_type, size)

def register_memory_pool(pool: MemoryPool):
    """Register a memory pool for automatic cleanup."""
    auto_gc = get_auto_gc()
    auto_gc.resource_manager.register_memory_pool(pool)

def register_mmap_file(filepath: str):
    """Register a memory-mapped file for cleanup."""
    auto_gc = get_auto_gc()
    auto_gc.resource_manager.register_mmap_file(filepath)

def register_cleanup_callback(callback: Callable):
    """Register a cleanup callback."""
    auto_gc = get_auto_gc()
    auto_gc.resource_manager.register_cleanup_callback(callback)

@contextmanager
def managed_memory():
    """Context manager for automatic memory management."""
    auto_gc = get_auto_gc()
    auto_gc.start()
    try:
        yield auto_gc
    finally:
        auto_gc.force_cleanup()

def auto_gc_decorator(func):
    """Decorator to automatically manage garbage collection for a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with managed_memory():
            return func(*args, **kwargs)
    return wrapper

class ManagedMemoryPool(MemoryPool):
    """Memory pool with automatic garbage collection integration."""
    
    def __init__(self, block_size: int, max_blocks: Optional[int] = None):
        super().__init__(block_size, max_blocks)
        register_memory_pool(self)
        
    def __del__(self):
        """Cleanup when pool is destroyed."""
        auto_gc = get_auto_gc()
        auto_gc.resource_manager.unregister_memory_pool(self)

def create_managed_mmap(filepath: str, size: int, dtype: str = "float64", mode: str = "r+"):
    """Create a memory-mapped array with automatic cleanup."""
    register_mmap_file(filepath)
    return memory_mapped_array(filepath, size, dtype, mode)

# Initialize auto GC on module import
def _initialize_auto_gc():
    """Initialize the auto GC system."""
    try:
        # Check if we should auto-enable
        if os.environ.get('PYFERRIS_AUTO_GC', '1').lower() in ('1', 'true', 'yes'):
            enable_auto_gc()
            logger.info("Auto GC enabled by default")
    except Exception as e:
        logger.warning(f"Failed to initialize auto GC: {e}")

# Initialize on import
_initialize_auto_gc()

__all__ = [
    'AutoGCConfig',
    'AutoGarbageCollector',
    'MemoryTracker',
    'ResourceManager',
    'ManagedMemoryPool',
    'get_auto_gc',
    'enable_auto_gc',
    'disable_auto_gc',
    'force_gc',
    'gc_stats',
    'track_allocation',
    'track_deallocation',
    'register_memory_pool',
    'register_mmap_file',
    'register_cleanup_callback',
    'managed_memory',
    'auto_gc_decorator',
    'create_managed_mmap'
]
