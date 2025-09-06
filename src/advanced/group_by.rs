use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use rayon::prelude::*;
use std::collections::HashMap;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::sync::{Arc, Mutex};

/// Parallel group_by implementation
#[pyfunction]
pub fn parallel_group_by(
    py: Python,
    iterable: Bound<PyAny>,
    key_func: Bound<PyAny>,
    chunk_size: Option<usize>,
) -> PyResult<Py<PyDict>> {
    let items: Vec<Py<PyAny>> = iterable
        .try_iter()?
        .map(|item| item.map(|i| i.into()))
        .collect::<PyResult<Vec<_>>>()?;

    if items.is_empty() {
        return Ok(PyDict::new(py).into());
    }

    let chunk_size = chunk_size.unwrap_or_else(|| {
        let len = items.len();
        if len < 1000 {
            (len / rayon::current_num_threads().max(1)).max(1)
        } else {
            1000
        }
    });

    let key_func: Arc<Py<PyAny>> = Arc::new(key_func.into());

    // Use a thread-safe HashMap to collect results
    let groups: Arc<Mutex<HashMap<u64, Vec<Py<PyAny>>>>> = Arc::new(Mutex::new(HashMap::new()));
    let key_objects: Arc<Mutex<HashMap<u64, Py<PyAny>>>> = Arc::new(Mutex::new(HashMap::new()));

    // Process in parallel chunks
    py.detach(|| {
        items.par_chunks(chunk_size).for_each(|chunk| {
            let mut local_groups: HashMap<u64, Vec<Py<PyAny>>> = HashMap::new();
            let mut local_keys: HashMap<u64, Py<PyAny>> = HashMap::new();

            for item in chunk {
                let key_result = Python::attach(|py| key_func.call1(py, (item,)));

                if let Ok(key) = key_result {
                    // Create a hash of the key for grouping
                    let key_hash = Python::attach(|py| {
                        let mut hasher = DefaultHasher::new();
                        if let Ok(hash_val) = key.bind(py).hash() {
                            hash_val.hash(&mut hasher);
                            hasher.finish()
                        } else {
                            // Fallback to string representation
                            if let Ok(str_repr) = key.bind(py).str() {
                                str_repr.to_string().hash(&mut hasher);
                                hasher.finish()
                            } else {
                                0
                            }
                        }
                    });

                    Python::attach(|py| {
                        local_groups
                            .entry(key_hash)
                            .or_insert_with(Vec::new)
                            .push(item.clone_ref(py));
                        local_keys.insert(key_hash, key);
                    });
                }
            }

            // Merge local results into global groups
            let mut global_groups = groups.lock().unwrap();
            let mut global_keys = key_objects.lock().unwrap();

            for (key_hash, items) in local_groups {
                global_groups
                    .entry(key_hash)
                    .or_insert_with(Vec::new)
                    .extend(items);
            }

            for (key_hash, key_obj) in local_keys {
                global_keys.entry(key_hash).or_insert(key_obj);
            }
        });
    });

    // Convert to Python dictionary
    let groups = groups.lock().unwrap();
    let key_objects = key_objects.lock().unwrap();

    let result_dict = PyDict::new(py);

    for (key_hash, items) in groups.iter() {
        if let Some(key_obj) = key_objects.get(key_hash) {
            let py_list = PyList::new(py, items)?;
            result_dict.set_item(key_obj, py_list)?;
        }
    }

    Ok(result_dict.into())
}
