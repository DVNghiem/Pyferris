use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::net::SocketAddr;
use std::sync::{Arc, Mutex};

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
                gpu_count: detect_gpu_count(),
                specialized: detect_specialized_capabilities(),
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
        // Parse coordinator address
        let coordinator_addr: SocketAddr = coordinator_address.parse()
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid coordinator address: {}", e)))?;
        
        // Send join request with local node information
        match self.send_join_request(&coordinator_addr) {
            Ok(cluster_info) => {
                // Update local cluster state with received information
                self.update_cluster_state(cluster_info)?;
                self.coordinator = false;
                println!("Successfully joined cluster at {}", coordinator_address);
                Ok(())
            }
            Err(e) => {
                Err(pyo3::exceptions::PyConnectionError::new_err(
                    format!("Failed to join cluster: {}", e)
                ))
            }
        }
    }

    /// Start as cluster coordinator         
    pub fn start_coordinator(&mut self) -> PyResult<()> {
        self.coordinator = true;
        
        // Start listening for node connections in a background thread
        match self.start_coordinator_server() {
            Ok(_) => {
                println!("Cluster coordinator started on {}", self.local_node.address);
                Ok(())
            }
            Err(e) => {
                Err(pyo3::exceptions::PyRuntimeError::new_err(
                    format!("Failed to start coordinator: {}", e)
                ))
            }
        }
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

impl ClusterManager {
    /// Send join request to coordinator
    fn send_join_request(&self, coordinator_addr: &SocketAddr) -> Result<ClusterInfo, String> {
        use std::net::TcpStream;
        use std::io::{Read, Write};
        use std::time::Duration;
        
        // Create connection to coordinator
        let mut stream = TcpStream::connect_timeout(coordinator_addr, Duration::from_secs(10))
            .map_err(|e| format!("Connection failed: {}", e))?;
        
        // Prepare join request
        let join_request = JoinRequest {
            node: self.local_node.clone(),
            protocol_version: "1.0".to_string(),
        };
        
        // Serialize and send request
        let request_data = serde_json::to_string(&join_request)
            .map_err(|e| format!("Serialization failed: {}", e))?;
        
        stream.write_all(request_data.as_bytes())
            .map_err(|e| format!("Write failed: {}", e))?;
        
        // Read response
        let mut buffer = Vec::new();
        stream.read_to_end(&mut buffer)
            .map_err(|e| format!("Read failed: {}", e))?;
        
        let response = String::from_utf8(buffer)
            .map_err(|e| format!("Invalid UTF-8: {}", e))?;
        
        // Parse response
        let cluster_info: ClusterInfo = serde_json::from_str(&response)
            .map_err(|e| format!("Response parsing failed: {}", e))?;
        
        Ok(cluster_info)
    }
    
    /// Update cluster state with received information
    fn update_cluster_state(&self, cluster_info: ClusterInfo) -> PyResult<()> {
        let mut nodes = self.nodes.lock().unwrap();
        
        // Clear existing nodes and add new ones
        nodes.clear();
        for node in cluster_info.nodes {
            nodes.insert(node.id.clone(), node);
        }
        
        Ok(())
    }
    
    /// Start coordinator server to listen for joining nodes
    fn start_coordinator_server(&self) -> Result<(), String> {
        use std::net::TcpListener;
        use std::thread;
        use std::sync::Arc;
        
        let listener = TcpListener::bind(self.local_node.address)
            .map_err(|e| format!("Failed to bind to address: {}", e))?;
        
        let nodes = Arc::clone(&self.nodes);
        let local_node = self.local_node.clone();
        
        // Spawn background thread to handle connections
        thread::spawn(move || {
            for stream in listener.incoming() {
                match stream {
                    Ok(stream) => {
                        let nodes_clone = Arc::clone(&nodes);
                        let local_node_clone = local_node.clone();
                        
                        thread::spawn(move || {
                            if let Err(e) = Self::handle_join_request(stream, nodes_clone, local_node_clone) {
                                eprintln!("Failed to handle join request: {}", e);
                            }
                        });
                    }
                    Err(e) => {
                        eprintln!("Connection failed: {}", e);
                    }
                }
            }
        });
        
        Ok(())
    }
    
    /// Handle incoming join requests
    fn handle_join_request(
        mut stream: std::net::TcpStream,
        nodes: Arc<Mutex<HashMap<String, ClusterNode>>>,
        _local_node: ClusterNode,
    ) -> Result<(), String> {
        use std::io::{Read, Write};
        
        // Read request
        let mut buffer = Vec::new();
        stream.read_to_end(&mut buffer)
            .map_err(|e| format!("Read failed: {}", e))?;
        
        let request = String::from_utf8(buffer)
            .map_err(|e| format!("Invalid UTF-8: {}", e))?;
        
        // Parse join request
        let join_request: JoinRequest = serde_json::from_str(&request)
            .map_err(|e| format!("Request parsing failed: {}", e))?;
        
        // Add node to cluster
        {
            let mut nodes_guard = nodes.lock().unwrap();
            nodes_guard.insert(join_request.node.id.clone(), join_request.node);
        }
        
        // Prepare response with current cluster state
        let cluster_info = {
            let nodes_guard = nodes.lock().unwrap();
            ClusterInfo {
                nodes: nodes_guard.values().cloned().collect(),
                coordinator_id: "coordinator".to_string(),
            }
        };
        
        // Send response
        let response_data = serde_json::to_string(&cluster_info)
            .map_err(|e| format!("Serialization failed: {}", e))?;
        
        stream.write_all(response_data.as_bytes())
            .map_err(|e| format!("Write failed: {}", e))?;
        
        Ok(())
    }
    
    /// Get node health status
    pub fn get_node_health(&self, node_id: &str) -> PyResult<NodeHealth> {
        let nodes = self.nodes.lock().unwrap();
        if let Some(node) = nodes.get(node_id) {
            Ok(NodeHealth {
                node_id: node.id.clone(),
                status: node.status.clone(),
                load: node.load,
                last_heartbeat: std::time::SystemTime::now(),
                uptime: std::time::Duration::from_secs(3600), // Mock uptime
            })
        } else {
            Err(pyo3::exceptions::PyKeyError::new_err(format!("Node {} not found", node_id)))
        }
    }
    
    /// Send heartbeat to maintain cluster membership
    pub fn send_heartbeat(&self) -> PyResult<()> {
        // In a real implementation, this would send heartbeat to coordinator
        // For now, just update local node's timestamp
        println!("Heartbeat sent from node {}", self.local_node.id);
        Ok(())
    }
    
    /// Detect node failures and update cluster state
    pub fn detect_failed_nodes(&self) -> PyResult<Vec<String>> {
        let mut nodes = self.nodes.lock().unwrap();
        let mut failed_nodes = Vec::new();
        
        // In a real implementation, this would check heartbeat timestamps
        // For now, we'll simulate by checking load > 1.0 as "failed"
        for (node_id, node) in nodes.iter_mut() {
            if node.load > 1.0 {
                node.status = NodeStatus::Failed;
                failed_nodes.push(node_id.clone());
            }
        }
        
        Ok(failed_nodes)
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

/// Helper function to detect GPU count
fn detect_gpu_count() -> usize {
    // Try to detect NVIDIA GPUs first
    if let Ok(output) = std::process::Command::new("nvidia-smi")
        .arg("-L")
        .output()
    {
        if output.status.success() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            return stdout.lines().count();
        }
    }
    
    // Try to detect AMD GPUs
    if let Ok(output) = std::process::Command::new("rocm-smi")
        .arg("-i")
        .output()
    {
        if output.status.success() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            // Count lines that contain "GPU"
            return stdout.lines().filter(|line| line.contains("GPU")).count();
        }
    }
    
    // Check for OpenCL devices
    if std::path::Path::new("/dev/dri").exists() {
        if let Ok(entries) = std::fs::read_dir("/dev/dri") {
            let render_nodes = entries
                .filter_map(|entry| entry.ok())
                .filter(|entry| {
                    entry.file_name().to_string_lossy().starts_with("renderD")
                })
                .count();
            if render_nodes > 0 {
                return render_nodes;
            }
        }
    }
    
    // Default to 0 if no GPUs detected
    0
}

/// Helper function to detect specialized capabilities
fn detect_specialized_capabilities() -> Vec<String> {
    let mut capabilities = Vec::new();
    
    // Check for CUDA support
    if std::process::Command::new("nvidia-smi").output().is_ok() {
        capabilities.push("cuda".to_string());
    }
    
    // Check for ROCm support
    if std::process::Command::new("rocm-smi").output().is_ok() {
        capabilities.push("rocm".to_string());
    }
    
    // Check for OpenCL support
    if std::path::Path::new("/usr/lib/libOpenCL.so").exists() ||
       std::path::Path::new("/usr/lib/x86_64-linux-gnu/libOpenCL.so").exists() {
        capabilities.push("opencl".to_string());
    }
    
    // Check for CPU-specific features based on architecture
    #[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
    {
        if is_x86_feature_detected!("avx") {
            capabilities.push("avx".to_string());
        }
        
        if is_x86_feature_detected!("avx2") {
            capabilities.push("avx2".to_string());
        }
        
        if is_x86_feature_detected!("sse4.1") {
            capabilities.push("sse4.1".to_string());
        }
    }
    
    #[cfg(target_arch = "aarch64")]
    {
        // Check for ARM NEON support
        if std::arch::is_aarch64_feature_detected!("neon") {
            capabilities.push("neon".to_string());
        }
        
        // Check for ARM SVE support (if available)
        if std::arch::is_aarch64_feature_detected!("sve") {
            capabilities.push("sve".to_string());
        }
    }
    
    #[cfg(target_arch = "arm")]
    {
        // For ARMv7, we can check for NEON support
        if std::arch::is_arm_feature_detected!("neon") {
            capabilities.push("neon".to_string());
        }
    }
    
    // For other architectures, add generic capability detection
    #[cfg(not(any(target_arch = "x86", target_arch = "x86_64", target_arch = "aarch64", target_arch = "arm")))]
    {
        // Add generic capabilities for other architectures
        capabilities.push("generic".to_string());
    }
    
    // Check for high core count (> 16 cores)
    if num_cpus::get() > 16 {
        capabilities.push("high_core_count".to_string());
    }
    
    // Check for high memory (> 32GB)
    if get_total_memory_gb() > 32.0 {
        capabilities.push("high_memory".to_string());
    }
    
    capabilities
}

// Data structures for cluster communication
#[derive(Debug, Serialize, Deserialize)]
struct JoinRequest {
    node: ClusterNode,
    protocol_version: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct ClusterInfo {
    nodes: Vec<ClusterNode>,
    coordinator_id: String,
}

#[derive(Debug, Clone)]
pub struct NodeHealth {
    pub node_id: String,
    pub status: NodeStatus,
    pub load: f64,
    pub last_heartbeat: std::time::SystemTime,
    pub uptime: std::time::Duration,
}
