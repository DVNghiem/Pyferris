use pyo3::prelude::*;
use pyo3::types::PyList;
use std::fs;
use std::path::Path;
use rayon::prelude::*;
use crate::error::ParallelExecutionError;

/// Parallel file operations for batch processing
#[pyclass]
pub struct ParallelFileProcessor {
    max_workers: usize,
    chunk_size: usize,
}

#[pymethods]
impl ParallelFileProcessor {
    #[new]
    #[pyo3(signature = (max_workers = 0, chunk_size = 1000))]
    pub fn new(max_workers: usize, chunk_size: usize) -> Self {
        let workers = if max_workers == 0 {
            rayon::current_num_threads()
        } else {
            max_workers
        };
        
        Self {
            max_workers: workers,
            chunk_size,
        }
    }

    /// Process multiple files in parallel with a custom function
    pub fn process_files(&self, py: Python, file_paths: Vec<String>, processor_func: Py<PyAny>) -> PyResult<Py<PyList>> {
        // Set up thread pool if custom worker count is specified
        if self.max_workers != rayon::current_num_threads() {
            rayon::ThreadPoolBuilder::new()
                .num_threads(self.max_workers)
                .build_global()
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to set thread pool: {}", e)))?;
        }

        // First, read all files in parallel (no GIL needed for file I/O)
        let file_contents: Result<Vec<_>, _> = file_paths
            .par_iter()
            .map(|file_path| {
                std::fs::read_to_string(file_path)
                    .map_err(|e| format!("Failed to read {}: {}", file_path, e))
                    .map(|content| (file_path.clone(), content))
            })
            .collect();

        let file_contents = file_contents
            .map_err(|e| ParallelExecutionError::new_err(e))?;

        // Then process with Python function sequentially to avoid GIL deadlock
        let results: Result<Vec<_>, _> = py.detach(|| {
            file_contents.into_iter().map(|(file_path, content)| {
                Python::attach(|py| {
                    let args = (file_path.as_str(), content.as_str());
                    processor_func.call1(py, args)
                        .map_err(|e| ParallelExecutionError::new_err(format!("Processor function failed for {}: {}", file_path, e)))
                })
            }).collect::<Result<Vec<_>, _>>()
        });

        let results = results?;

        let py_results = PyList::empty(py);
        for result in results {
            py_results.append(result)?;
        }
        
        Ok(py_results.into())
    }

    /// Read multiple files in parallel
    pub fn read_files_parallel(&self, py: Python, file_paths: Vec<String>) -> PyResult<Py<PyList>> {
        let results: Result<Vec<_>, _> = file_paths
            .par_iter()
            .map(|path| {
                std::fs::read_to_string(path)
                    .map_err(|e| format!("Failed to read {}: {}", path, e))
            })
            .collect();

        let results = results
            .map_err(|e| ParallelExecutionError::new_err(e))?;

        let py_results = PyList::empty(py);
        for (path, content) in file_paths.iter().zip(results.iter()) {
            let tuple = (path.as_str(), content.as_str());
            py_results.append(tuple)?;
        }
        
        Ok(py_results.into())
    }

    /// Write multiple files in parallel
    pub fn write_files_parallel(&self, file_data: Vec<(String, String)>) -> PyResult<()> {
        let results: Result<Vec<_>, _> = file_data
            .par_iter()
            .map(|(path, content)| {
                std::fs::write(path, content)
                    .map_err(|e| format!("Failed to write {}: {}", path, e))
            })
            .collect();

        results.map_err(|e| ParallelExecutionError::new_err(e))?;
        Ok(())
    }

    /// Copy multiple files in parallel
    pub fn copy_files_parallel(&self, file_pairs: Vec<(String, String)>) -> PyResult<()> {
        let results: Result<Vec<_>, _> = file_pairs
            .par_iter()
            .map(|(src, dst)| {
                // Create destination directory if it doesn't exist
                if let Some(parent) = Path::new(dst).parent() {
                    if !parent.exists() {
                        fs::create_dir_all(parent)
                            .map_err(|e| format!("Failed to create directory {}: {}", parent.display(), e))?;
                    }
                }
                
                std::fs::copy(src, dst)
                    .map_err(|e| format!("Failed to copy {} to {}: {}", src, dst, e))
            })
            .collect();

        results.map_err(|e| ParallelExecutionError::new_err(e))?;
        Ok(())
    }

    /// Process directory recursively in parallel
    pub fn process_directory(&self, py: Python, dir_path: &str, file_filter: Option<Py<PyAny>>, processor_func: Py<PyAny>) -> PyResult<Py<PyList>> {
        let paths = collect_files_recursive(dir_path)?;
        
        // Filter files if filter function is provided
        let filtered_paths = if let Some(filter_func) = file_filter {
            // Apply filter sequentially to avoid GIL issues
            let mut filtered = Vec::new();
            for path in paths {
                let should_include = filter_func.call1(py, (path.as_str(),))?
                    .extract::<bool>(py)
                    .map_err(|e| ParallelExecutionError::new_err(format!("Filter function error for {}: {}", path, e)))?;
                
                if should_include {
                    filtered.push(path);
                }
            }
            filtered
        } else {
            paths
        };

        self.process_files(py, filtered_paths, processor_func)
    }

    /// Get file statistics in parallel
    pub fn get_file_stats_parallel(&self, py: Python, file_paths: Vec<String>) -> PyResult<Py<PyList>> {
        let results: Result<Vec<_>, String> = file_paths
            .par_iter()
            .map(|path| {
                let metadata = std::fs::metadata(path)
                    .map_err(|e| format!("Failed to get metadata for {}: {}", path, e))?;
                
                Ok((
                    path.clone(),
                    metadata.len(),
                    metadata.is_file(),
                    metadata.is_dir(),
                    metadata.modified()
                        .map(|t| t.duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs())
                        .unwrap_or(0),
                ))
            })
            .collect();

        let results = results
            .map_err(|e| ParallelExecutionError::new_err(e))?;

        let py_results = PyList::empty(py);
        for (path, size, is_file, is_dir, modified) in results {
            let stats_dict = pyo3::types::PyDict::new(py);
            stats_dict.set_item("path", path)?;
            stats_dict.set_item("size", size)?;
            stats_dict.set_item("is_file", is_file)?;
            stats_dict.set_item("is_dir", is_dir)?;
            stats_dict.set_item("modified", modified)?;
            py_results.append(stats_dict)?;
        }
        
        Ok(py_results.into())
    }
}

/// Collect all files in directory recursively
fn collect_files_recursive(dir_path: &str) -> PyResult<Vec<String>> {
    let mut files = Vec::new();
    collect_files_recursive_helper(Path::new(dir_path), &mut files)?;
    Ok(files)
}

fn collect_files_recursive_helper(dir: &Path, files: &mut Vec<String>) -> PyResult<()> {
    if dir.is_dir() {
        let entries = fs::read_dir(dir)
            .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read directory {}: {}", dir.display(), e)))?;

        for entry in entries {
            let entry = entry
                .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read directory entry: {}", e)))?;
            
            let path = entry.path();
            if path.is_dir() {
                collect_files_recursive_helper(&path, files)?;
            } else if path.is_file() {
                if let Some(path_str) = path.to_str() {
                    files.push(path_str.to_string());
                }
            }
        }
    } else if dir.is_file() {
        if let Some(path_str) = dir.to_str() {
            files.push(path_str.to_string());
        }
    }
    Ok(())
}

/// Process files in chunks with parallel execution
#[pyfunction]
pub fn parallel_process_file_chunks(py: Python, file_path: &str, chunk_size: usize, processor_func: Py<PyAny>) -> PyResult<Py<PyList>> {
    let content = std::fs::read_to_string(file_path)
        .map_err(|e| ParallelExecutionError::new_err(format!("Failed to read file: {}", e)))?;
    
    let lines: Vec<&str> = content.lines().collect();
    let chunks: Vec<Vec<&str>> = lines
        .chunks(chunk_size)
        .map(|chunk| chunk.to_vec())
        .collect();

    // Process chunks sequentially to avoid GIL deadlock
    let results: Result<Vec<_>, _> = chunks
        .into_iter()
        .enumerate()
        .map(|(chunk_idx, chunk)| -> PyResult<Py<PyAny>> {
            let chunk_lines = PyList::empty(py);
            for line in chunk {
                chunk_lines.append(line)?;
            }
            
            let args = (chunk_idx, &chunk_lines);
            processor_func.call1(py, args)
                .map_err(|e| ParallelExecutionError::new_err(format!("Processor function failed for chunk {}: {}", chunk_idx, e)))
        })
        .collect();

    let results = results?;

    let py_results = PyList::empty(py);
    for result in results {
        py_results.append(result)?;
    }
    
    Ok(py_results.into())
}

/// Find files matching pattern in parallel
#[pyfunction]
pub fn parallel_find_files(py: Python, root_dir: &str, pattern: &str) -> PyResult<Py<PyList>> {
    let all_files = collect_files_recursive(root_dir)?;
    
    let matching_files: Vec<String> = all_files
        .par_iter()
        .filter(|path| {
            let file_name = Path::new(path)
                .file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("");
            
            // Simple pattern matching (can be extended for regex)
            if pattern.contains('*') {
                let pattern_parts: Vec<&str> = pattern.split('*').collect();
                if pattern_parts.len() == 2 {
                    file_name.starts_with(pattern_parts[0]) && file_name.ends_with(pattern_parts[1])
                } else {
                    false
                }
            } else {
                file_name.contains(pattern)
            }
        })
        .cloned()
        .collect();

    let py_results = PyList::empty(py);
    for file_path in matching_files {
        py_results.append(file_path)?;
    }
    
    Ok(py_results.into())
}

/// Get directory size in parallel
#[pyfunction]
pub fn parallel_directory_size(dir_path: &str) -> PyResult<u64> {
    let files = collect_files_recursive(dir_path)?;
    
    let total_size: u64 = files
        .par_iter()
        .map(|path| {
            std::fs::metadata(path)
                .map(|metadata| metadata.len())
                .unwrap_or(0)
        })
        .sum();

    Ok(total_size)
}

/// Count lines in multiple files in parallel
#[pyfunction]
pub fn parallel_count_lines(file_paths: Vec<String>) -> PyResult<u64> {
    let total_lines: Result<u64, _> = file_paths
        .par_iter()
        .map(|path| {
            std::fs::read_to_string(path)
                .map(|content| content.lines().count() as u64)
                .map_err(|e| format!("Failed to read {}: {}", path, e))
        })
        .sum();

    total_lines.map_err(|e| ParallelExecutionError::new_err(e))
}
