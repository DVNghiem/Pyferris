use pyo3::prelude::*;
use pyo3::types::PyList;

/// Converts string to camel case.
#[pyfunction]
pub fn camel_case(string: &str) -> String {
    let mut result = String::new();
    let mut next_upper = false;
    let mut first = true;

    for c in string.chars() {
        if c.is_alphanumeric() {
            if first {
                result.push(c.to_ascii_lowercase());
                first = false;
            } else if next_upper {
                result.push(c.to_ascii_uppercase());
                next_upper = false;
            } else {
                result.push(c.to_ascii_lowercase());
            }
        } else {
            next_upper = true;
        }
    }
    result
}

/// Converts string to kebab case.
#[pyfunction]
pub fn kebab_case(string: &str) -> String {
    let mut result = String::new();
    let mut first = true;

    for (i, c) in string.chars().enumerate() {
        if c.is_uppercase() {
            if !first && i > 0 {
                result.push('-');
            }
            result.push(c.to_ascii_lowercase());
            first = false;
        } else if c.is_alphanumeric() {
            result.push(c);
            first = false;
        } else {
            if !first {
                result.push('-');
                first = true; // Treat next char as start of new word (but we handle hyphen logic above)
            }
        }
    }
    // Clean up multiple hyphens
    let cleaned = result.replace("--", "-");
    let trimmed = cleaned.trim_matches('-');
    trimmed.to_string()
}

/// Converts string to snake case.
#[pyfunction]
pub fn snake_case(string: &str) -> String {
    kebab_case(string).replace("-", "_")
}

/// Converts the first character of string to upper case and the remaining to lower case.
#[pyfunction]
pub fn capitalize(string: &str) -> String {
    let mut chars = string.chars();
    match chars.next() {
        None => String::new(),
        Some(f) => f.to_uppercase().collect::<String>() + &chars.as_str().to_lowercase(),
    }
}

/// Splits string into an array of its words.
#[pyfunction]
pub fn words(py: Python, string: &str) -> PyResult<Py<PyList>> {
    let words: Vec<&str> = string.split_whitespace().collect();
    Ok(PyList::new(py, words)?.into())
}

/// Truncates string if it's longer than the given maximum string length.
#[pyfunction]
#[pyo3(signature = (string, length=30, omission="..."))]
pub fn truncate(string: &str, length: usize, omission: &str) -> String {
    if string.len() <= length {
        return string.to_string();
    }
    
    let target_len = length.saturating_sub(omission.len());
    let truncated: String = string.chars().take(target_len).collect();
    truncated + omission
}

#[pymodule]
pub fn string(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(camel_case, m)?)?;
    m.add_function(wrap_pyfunction!(kebab_case, m)?)?;
    m.add_function(wrap_pyfunction!(snake_case, m)?)?;
    m.add_function(wrap_pyfunction!(capitalize, m)?)?;
    m.add_function(wrap_pyfunction!(words, m)?)?;
    m.add_function(wrap_pyfunction!(truncate, m)?)?;
    Ok(())
}
