use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};
use uuid;

/// Checkpoint data structure
#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Checkpoint {
    #[pyo3(get)]
    pub id: String,
    #[pyo3(get)]
    pub operation: String,
    #[pyo3(get)]
    pub state: HashMap<String, String>,
    #[pyo3(get)]
    pub progress: f64,
    #[pyo3(get)]
    pub timestamp: u64,
    #[pyo3(get)]
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl Checkpoint {
    #[new]
    pub fn new(
        id: String,
        operation: String,
        state: HashMap<String, String>,
        progress: f64,
        metadata: Option<HashMap<String, String>>
    ) -> Self {
        Self {
            id,
            operation,
            state,
            progress,
            timestamp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_micros() as u64,
            metadata: metadata.unwrap_or_default(),
        }
    }
}

/// Checkpoint manager for saving and restoring operation state
#[pyclass]
#[derive(Clone)]
pub struct CheckpointManager {
    checkpoint_dir: PathBuf,
    auto_save_interval: Option<u64>,
    max_checkpoints: usize,
}

#[pymethods]
impl CheckpointManager {
    #[new]
    #[pyo3(signature = (checkpoint_dir, auto_save_interval=None, max_checkpoints=10))]
    pub fn new(
        checkpoint_dir: String,
        auto_save_interval: Option<u64>,
        max_checkpoints: usize
    ) -> PyResult<Self> {
        let checkpoint_dir = PathBuf::from(checkpoint_dir);
        
        // Create directory if it doesn't exist
        if !checkpoint_dir.exists() {
            fs::create_dir_all(&checkpoint_dir)
                .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to create checkpoint directory: {}", e)))?;
        }

        Ok(Self {
            checkpoint_dir,
            auto_save_interval,
            max_checkpoints,
        })
    }

    /// Save a checkpoint
    #[pyo3(signature = (operation_id, state_data, progress, metadata=None))]
    pub fn save_checkpoint(
        &self,
        operation_id: String,
        state_data: HashMap<String, String>,
        progress: f64,
        metadata: Option<HashMap<String, String>>
    ) -> PyResult<String> {
        let checkpoint_id = format!("{}_{}_{}", operation_id, 
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_millis(),
            uuid::Uuid::new_v4().to_string()[..8].to_string());

        let checkpoint = Checkpoint::new(
            checkpoint_id.clone(),
            operation_id.clone(),
            state_data,
            progress,
            metadata
        );

        let checkpoint_file = self.checkpoint_dir.join(format!("{}.json", checkpoint_id));
        let checkpoint_json = serde_json::to_string_pretty(&checkpoint)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Failed to serialize checkpoint: {}", e)))?;

        fs::write(&checkpoint_file, checkpoint_json)
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to write checkpoint: {}", e)))?;

        // Clean up old checkpoints
        self.cleanup_old_checkpoints(&operation_id)?;

        Ok(checkpoint_id)
    }

    /// Restore a checkpoint by ID
    pub fn restore_checkpoint(&self, checkpoint_id: String) -> PyResult<Checkpoint> {
        let checkpoint_file = self.checkpoint_dir.join(format!("{}.json", checkpoint_id));
        
        if !checkpoint_file.exists() {
            return Err(pyo3::exceptions::PyFileNotFoundError::new_err(
                format!("Checkpoint {} not found", checkpoint_id)
            ));
        }

        let checkpoint_data = fs::read_to_string(&checkpoint_file)
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to read checkpoint: {}", e)))?;

        let checkpoint: Checkpoint = serde_json::from_str(&checkpoint_data)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Failed to deserialize checkpoint: {}", e)))?;

        Ok(checkpoint)
    }

    /// Get the latest checkpoint for an operation
    pub fn get_latest_checkpoint(&self, operation_id: String) -> PyResult<Option<Checkpoint>> {
        let checkpoints = self.list_checkpoints(Some(operation_id))?;
        Ok(checkpoints.into_iter().next())
    }

    /// List checkpoints for an operation (or all if None)
    #[pyo3(signature = (operation_id=None))]
    pub fn list_checkpoints(&self, operation_id: Option<String>) -> PyResult<Vec<Checkpoint>> {
        let mut checkpoints = Vec::new();

        let entries = fs::read_dir(&self.checkpoint_dir)
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to read checkpoint directory: {}", e)))?;

        for entry in entries {
            let entry = entry.map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
            let path = entry.path();
            
            if path.extension().and_then(|s| s.to_str()) == Some("json") {
                let checkpoint_data = fs::read_to_string(&path)
                    .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to read checkpoint: {}", e)))?;

                if let Ok(checkpoint) = serde_json::from_str::<Checkpoint>(&checkpoint_data) {
                    if operation_id.is_none() || operation_id.as_ref() == Some(&checkpoint.operation) {
                        checkpoints.push(checkpoint);
                    }
                }
            }
        }

        // Sort by timestamp (newest first)
        checkpoints.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));
        Ok(checkpoints)
    }

    /// Delete a checkpoint
    pub fn delete_checkpoint(&self, checkpoint_id: String) -> PyResult<bool> {
        let checkpoint_file = self.checkpoint_dir.join(format!("{}.json", checkpoint_id));
        
        if checkpoint_file.exists() {
            fs::remove_file(&checkpoint_file)
                .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to delete checkpoint: {}", e)))?;
            Ok(true)
        } else {
            Ok(false)
        }
    }

    /// Get statistics about checkpoints
    pub fn get_stats(&self) -> PyResult<HashMap<String, u64>> {
        let checkpoints = self.list_checkpoints(None)?;
        let mut stats = HashMap::new();
        
        stats.insert("total_checkpoints".to_string(), checkpoints.len() as u64);
        
        let mut operations = std::collections::HashSet::new();
        for checkpoint in &checkpoints {
            operations.insert(&checkpoint.operation);
        }
        stats.insert("unique_operations".to_string(), operations.len() as u64);
        
        Ok(stats)
    }

    /// Clean up old checkpoints beyond max_checkpoints limit
    fn cleanup_old_checkpoints(&self, operation_id: &str) -> PyResult<()> {
        let mut checkpoints = self.list_checkpoints(Some(operation_id.to_string()))?;
        
        if checkpoints.len() > self.max_checkpoints {
            // Sort by timestamp (oldest first for removal)
            checkpoints.sort_by(|a, b| a.timestamp.cmp(&b.timestamp));
            
            let to_remove = checkpoints.len() - self.max_checkpoints;
            for checkpoint in checkpoints.iter().take(to_remove) {
                self.delete_checkpoint(checkpoint.id.clone())?;
            }
        }
        
        Ok(())
    }
}

/// Auto-checkpoint functionality
#[pyclass]
pub struct AutoCheckpoint {
    operation_id: String,
    checkpoint_manager: CheckpointManager,
    interval_seconds: u64,
    last_checkpoint: std::sync::Mutex<Option<SystemTime>>,
}

#[pymethods]
impl AutoCheckpoint {
    #[new]
    pub fn new(
        operation_id: String,
        checkpoint_manager: CheckpointManager,
        interval_seconds: u64
    ) -> Self {
        Self {
            operation_id,
            checkpoint_manager,
            interval_seconds,
            last_checkpoint: std::sync::Mutex::new(None),
        }
    }

    /// Maybe create a checkpoint if enough time has passed
    pub fn maybe_checkpoint(
        &self,
        state_data: HashMap<String, String>,
        progress: f64
    ) -> PyResult<Option<String>> {
        let now = SystemTime::now();
        let mut last_checkpoint = self.last_checkpoint.lock().unwrap();
        
        let should_checkpoint = match *last_checkpoint {
            None => true,
            Some(last) => {
                now.duration_since(last)
                    .unwrap_or_default()
                    .as_secs() >= self.interval_seconds
            }
        };

        if should_checkpoint {
            let checkpoint_id = self.checkpoint_manager.save_checkpoint(
                self.operation_id.clone(),
                state_data,
                progress,
                None
            )?;
            *last_checkpoint = Some(now);
            Ok(Some(checkpoint_id))
        } else {
            Ok(None)
        }
    }

    /// Force create a checkpoint regardless of timing
    pub fn force_checkpoint(
        &self,
        state_data: HashMap<String, String>,
        progress: f64
    ) -> PyResult<String> {
        let checkpoint_id = self.checkpoint_manager.save_checkpoint(
            self.operation_id.clone(),
            state_data,
            progress,
            None
        )?;
        
        let mut last_checkpoint = self.last_checkpoint.lock().unwrap();
        *last_checkpoint = Some(SystemTime::now());
        
        Ok(checkpoint_id)
    }
}