use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::net::SocketAddr;
use std::sync::{Arc, Mutex};
use tokio::net::{TcpListener, TcpStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};

/// Node information in a distributed cluster
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClusterNode {
    pub id: String,
    pub address: SocketAddr,
    pub status: NodeStatus,
    pub capabilities: NodeCapabilities,
    pub load: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum NodeStatus {
    Active,
    Busy,
    Offline,
    Failed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NodeCapabilities {
    pub cpu_cores: usize,
    pub memory_gb: f64,
    pub gpu_count: usize,
    pub specialized: Vec<String>,
}

/// Cluster manager for distributed operations
#[pyclass]
#[derive(Clone)]
pub struct ClusterManager {
    nodes: Arc<Mutex<HashMap<String, ClusterNode>>>,
    local_node: ClusterNode,
    coordinator: bool,
}

#[pymethods]
impl ClusterManager {
    #[new]
    pub fn new(node_id: String, address: String) -> PyResult<Self> {
        let addr: SocketAddr = address.parse()
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid address: {}", e)))?;
        
        let local_node = ClusterNode {
            id: node_id,
            address: addr,
            status: NodeStatus::Active,
            capabilities: NodeCapabilities {
                cpu_cores: num_cpus::get(),
                memory_gb: get_total_memory_gb(),
                gpu_count: 0, // TODO: Detect GPU count
                specialized: vec![],
            },
            load: 0.0,
        };

        Ok(Self {
            nodes: Arc::new(Mutex::new(HashMap::new())),
            local_node,
            coordinator: false,
        })
    }

    /// Join an existing cluster
    pub fn join_cluster(&mut self, coordinator_address: String) -> PyResult<()> {
        // TODO: Implement cluster joining protocol
        Ok(())
    }

    /// Start as cluster coordinator
    pub fn start_coordinator(&mut self) -> PyResult<()> {
        self.coordinator = true;
        // TODO: Start listening for node connections
        Ok(())
    }

    /// Add a node to the cluster
    pub fn add_node(&self, node_id: String, address: String, cpu_cores: usize, memory_gb: f64) -> PyResult<()> {
        let addr: std::net::SocketAddr = address.parse()
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid address: {}", e)))?;
        
        let node = ClusterNode {
            id: node_id.clone(),
            address: addr,
            status: NodeStatus::Active,
            capabilities: NodeCapabilities {
                cpu_cores,
                memory_gb,
                gpu_count: 0,
                specialized: vec![],
            },
            load: 0.0,
        };
        
        let mut nodes = self.nodes.lock().unwrap();
        nodes.insert(node_id, node);
        Ok(())
    }

    /// Remove a node from the cluster
    pub fn remove_node(&self, node_id: String) -> PyResult<()> {
        let mut nodes = self.nodes.lock().unwrap();
        nodes.remove(&node_id);
        Ok(())
    }

    /// Get all active nodes
    pub fn get_active_nodes(&self) -> PyResult<Vec<String>> {
        let nodes = self.nodes.lock().unwrap();
        let active_nodes: Vec<String> = nodes
            .values()
            .filter(|node| matches!(node.status, NodeStatus::Active))
            .map(|node| node.id.clone())
            .collect();
        Ok(active_nodes)
    }

    /// Get cluster statistics
    pub fn get_cluster_stats(&self) -> PyResult<HashMap<String, f64>> {
        let nodes = self.nodes.lock().unwrap();
        let mut stats = HashMap::new();
        
        let total_nodes = nodes.len() as f64;
        let active_nodes = nodes.values()
            .filter(|node| matches!(node.status, NodeStatus::Active))
            .count() as f64;
        
        let total_cores: usize = nodes.values()
            .map(|node| node.capabilities.cpu_cores)
            .sum();
        
        let total_memory: f64 = nodes.values()
            .map(|node| node.capabilities.memory_gb)
            .sum();
        
        let avg_load: f64 = nodes.values()
            .map(|node| node.load)
            .sum::<f64>() / total_nodes.max(1.0);

        stats.insert("total_nodes".to_string(), total_nodes);
        stats.insert("active_nodes".to_string(), active_nodes);
        stats.insert("total_cores".to_string(), total_cores as f64);
        stats.insert("total_memory_gb".to_string(), total_memory);
        stats.insert("average_load".to_string(), avg_load);
        stats.insert("availability".to_string(), active_nodes / total_nodes.max(1.0));

        Ok(stats)
    }

    /// Update node load
    pub fn update_node_load(&self, node_id: String, load: f64) -> PyResult<()> {
        let mut nodes = self.nodes.lock().unwrap();
        if let Some(node) = nodes.get_mut(&node_id) {
            node.load = load;
        }
        Ok(())
    }
}

/// Load balancer for distributing tasks across nodes
#[pyclass]
#[derive(Clone)]
pub struct LoadBalancer {
    strategy: LoadBalancingStrategy,
}

#[derive(Debug, Clone)]
pub enum LoadBalancingStrategy {
    RoundRobin,
    LeastLoaded,
    WeightedRoundRobin,
    Capability,
}

#[pymethods]
impl LoadBalancer {
    #[new]
    pub fn new(strategy: Option<String>) -> Self {
        let strategy = match strategy.as_deref() {
            Some("round_robin") => LoadBalancingStrategy::RoundRobin,
            Some("least_loaded") => LoadBalancingStrategy::LeastLoaded,
            Some("weighted") => LoadBalancingStrategy::WeightedRoundRobin,
            Some("capability") => LoadBalancingStrategy::Capability,
            _ => LoadBalancingStrategy::LeastLoaded,
        };

        Self { strategy }
    }

    /// Select the best node for a task
    pub fn select_node(&self, cluster: &ClusterManager, task_requirements: Option<HashMap<String, f64>>) -> PyResult<Option<String>> {
        let nodes = cluster.nodes.lock().unwrap();
        let active_nodes: Vec<&ClusterNode> = nodes
            .values()
            .filter(|node| matches!(node.status, NodeStatus::Active))
            .collect();

        if active_nodes.is_empty() {
            return Ok(None);
        }

        let selected = match self.strategy {
            LoadBalancingStrategy::RoundRobin => {
                // Simple round robin - would need state to track current index
                active_nodes.first()
            },
            LoadBalancingStrategy::LeastLoaded => {
                active_nodes.iter().min_by(|a, b| a.load.partial_cmp(&b.load).unwrap())
            },
            LoadBalancingStrategy::WeightedRoundRobin => {
                // Weight by inverse load and capabilities
                active_nodes.iter().min_by(|a, b| {
                    let weight_a = 1.0 / (a.load + 0.1) * a.capabilities.cpu_cores as f64;
                    let weight_b = 1.0 / (b.load + 0.1) * b.capabilities.cpu_cores as f64;
                    weight_b.partial_cmp(&weight_a).unwrap()
                })
            },
            LoadBalancingStrategy::Capability => {
                // Select based on capabilities and requirements
                if let Some(requirements) = task_requirements {
                    let cpu_req = requirements.get("cpu_cores").unwrap_or(&1.0);
                    let memory_req = requirements.get("memory_gb").unwrap_or(&1.0);
                    
                    active_nodes.iter().find(|node| {
                        node.capabilities.cpu_cores as f64 >= *cpu_req &&
                        node.capabilities.memory_gb >= *memory_req &&
                        node.load < 0.8
                    }).or_else(|| active_nodes.first())
                } else {
                    active_nodes.first()
                }
            }
        };

        Ok(selected.map(|node| node.id.clone()))
    }
}

/// Helper function to get total system memory in GB
fn get_total_memory_gb() -> f64 {
    // Simplified implementation - in a real system you'd use system APIs
    #[cfg(target_os = "linux")]
    {
        if let Ok(meminfo) = std::fs::read_to_string("/proc/meminfo") {
            for line in meminfo.lines() {
                if line.starts_with("MemTotal:") {
                    if let Some(kb_str) = line.split_whitespace().nth(1) {
                        if let Ok(kb) = kb_str.parse::<u64>() {
                            return (kb as f64) / 1024.0 / 1024.0; // Convert KB to GB
                        }
                    }
                }
            }
        }
    }
    
    // Default fallback
    8.0
}
