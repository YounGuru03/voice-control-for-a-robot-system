//! Utility functions and helpers

use anyhow::Result;
use std::path::PathBuf;

/// Get the application directory
pub fn get_app_dir() -> PathBuf {
    std::env::current_exe()
        .unwrap_or_else(|_| PathBuf::from("."))
        .parent()
        .unwrap_or(&PathBuf::from("."))
        .to_path_buf()
}

/// Format duration in human-readable format
pub fn format_duration(seconds: f32) -> String {
    if seconds < 60.0 {
        format!("{:.1}s", seconds)
    } else if seconds < 3600.0 {
        let minutes = (seconds / 60.0) as u32;
        let remaining_seconds = seconds % 60.0;
        format!("{}m {:.1}s", minutes, remaining_seconds)
    } else {
        let hours = (seconds / 3600.0) as u32;
        let remaining_minutes = ((seconds % 3600.0) / 60.0) as u32;
        format!("{}h {}m", hours, remaining_minutes)
    }
}

/// Format memory size in human-readable format
pub fn format_memory_size(bytes: u64) -> String {
    const UNITS: &[&str] = &["B", "KB", "MB", "GB", "TB"];
    let mut size = bytes as f64;
    let mut unit_index = 0;
    
    while size >= 1024.0 && unit_index < UNITS.len() - 1 {
        size /= 1024.0;
        unit_index += 1;
    }
    
    if unit_index == 0 {
        format!("{} {}", bytes, UNITS[unit_index])
    } else {
        format!("{:.1} {}", size, UNITS[unit_index])
    }
}

/// Clamp a value between min and max
pub fn clamp<T: PartialOrd>(value: T, min: T, max: T) -> T {
    if value < min {
        min
    } else if value > max {
        max
    } else {
        value
    }
}

/// Check if a string contains any of the given patterns (case-insensitive)
pub fn contains_any_pattern(text: &str, patterns: &[&str]) -> bool {
    let text_lower = text.to_lowercase();
    patterns.iter().any(|pattern| text_lower.contains(&pattern.to_lowercase()))
}

/// Extract number from text (e.g., "camera 3" -> Some(3))
pub fn extract_number(text: &str) -> Option<i32> {
    use std::str::FromStr;
    
    let words = text.split_whitespace();
    for word in words {
        if let Ok(num) = i32::from_str(word) {
            return Some(num);
        }
        
        // Handle word numbers
        match word.to_lowercase().as_str() {
            "zero" => return Some(0),
            "one" => return Some(1),
            "two" => return Some(2),
            "three" => return Some(3),
            "four" => return Some(4),
            "five" => return Some(5),
            "six" => return Some(6),
            "seven" => return Some(7),
            "eight" => return Some(8),
            "nine" => return Some(9),
            "ten" => return Some(10),
            _ => continue,
        }
    }
    
    None
}

/// Get current timestamp as formatted string
pub fn current_timestamp() -> String {
    chrono::Local::now().format("%Y-%m-%d %H:%M:%S").to_string()
}

/// Validate file path and create directory if needed
pub fn ensure_file_path(path: &PathBuf) -> Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_duration() {
        assert_eq!(format_duration(30.5), "30.5s");
        assert_eq!(format_duration(90.0), "1m 30.0s");
        assert_eq!(format_duration(3665.0), "1h 1m");
    }

    #[test]
    fn test_format_memory_size() {
        assert_eq!(format_memory_size(512), "512 B");
        assert_eq!(format_memory_size(1024), "1.0 KB");
        assert_eq!(format_memory_size(1048576), "1.0 MB");
        assert_eq!(format_memory_size(2147483648), "2.0 GB");
    }

    #[test]
    fn test_clamp() {
        assert_eq!(clamp(5, 1, 10), 5);
        assert_eq!(clamp(-1, 1, 10), 1);
        assert_eq!(clamp(15, 1, 10), 10);
        assert_eq!(clamp(5.5, 1.0, 10.0), 5.5);
    }

    #[test]
    fn test_contains_any_pattern() {
        assert!(contains_any_pattern("open camera", &["camera", "mic"]));
        assert!(contains_any_pattern("Open Camera", &["camera", "mic"]));
        assert!(!contains_any_pattern("start recording", &["camera", "mic"]));
    }

    #[test]
    fn test_extract_number() {
        assert_eq!(extract_number("camera 3"), Some(3));
        assert_eq!(extract_number("open camera four"), Some(4));
        assert_eq!(extract_number("template seven"), Some(7));
        assert_eq!(extract_number("no number here"), None);
        assert_eq!(extract_number("multiple 1 2 numbers"), Some(1)); // Returns first
    }
}