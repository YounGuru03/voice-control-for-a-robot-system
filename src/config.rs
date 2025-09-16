//! Configuration module for the Voice Control application
//! 
//! Handles loading and saving of application settings with sensible defaults.

use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tracing::{info, warn};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Speech recognition confidence threshold (0.0 to 1.0)
    pub confidence_threshold: f32,
    
    /// Audio recording duration in seconds
    pub recording_duration: f32,
    
    /// Enable audio preprocessing
    pub enable_preprocessing: bool,
    
    /// Enable real-time transcription display
    pub show_transcription: bool,
    
    /// Enable memory usage monitoring
    pub monitor_memory: bool,
    
    /// Audio sample rate
    pub sample_rate: u32,
    
    /// Audio buffer size
    pub buffer_size: usize,
    
    /// Maximum number of log entries to keep
    pub max_log_entries: usize,
    
    /// Maximum number of transcriptions to keep in history
    pub max_transcription_history: usize,
    
    /// File output path for commands
    pub output_file: String,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            confidence_threshold: 0.7,
            recording_duration: 3.0,
            enable_preprocessing: true,
            show_transcription: true,
            monitor_memory: true,
            sample_rate: 16000,
            buffer_size: 1024,
            max_log_entries: 100,
            max_transcription_history: 50,
            output_file: "text.txt".to_string(),
        }
    }
}

impl Config {
    /// Get the default config file path
    pub fn config_file_path() -> PathBuf {
        std::env::current_exe()
            .unwrap_or_else(|_| PathBuf::from("."))
            .parent()
            .unwrap_or(&PathBuf::from("."))
            .join("config.json")
    }
    
    /// Load configuration from file, or create default if file doesn't exist
    pub fn load_or_default() -> Result<Self> {
        let config_path = Self::config_file_path();
        
        if config_path.exists() {
            match Self::load_from_file(&config_path) {
                Ok(config) => {
                    info!("Configuration loaded from: {}", config_path.display());
                    Ok(config)
                }
                Err(e) => {
                    warn!("Failed to load config file: {}. Using defaults.", e);
                    let default_config = Self::default();
                    // Try to save defaults for next time
                    if let Err(save_err) = default_config.save_to_file(&config_path) {
                        warn!("Failed to save default config: {}", save_err);
                    }
                    Ok(default_config)
                }
            }
        } else {
            info!("No config file found. Creating default configuration.");
            let default_config = Self::default();
            
            // Try to save defaults
            if let Err(e) = default_config.save_to_file(&config_path) {
                warn!("Failed to save default config: {}", e);
            } else {
                info!("Default config saved to: {}", config_path.display());
            }
            
            Ok(default_config)
        }
    }
    
    /// Load configuration from a specific file
    pub fn load_from_file(path: &PathBuf) -> Result<Self> {
        let content = std::fs::read_to_string(path)?;
        let config: Self = serde_json::from_str(&content)?;
        Ok(config)
    }
    
    /// Save configuration to a specific file
    pub fn save_to_file(&self, path: &PathBuf) -> Result<()> {
        let content = serde_json::to_string_pretty(self)?;
        std::fs::write(path, content)?;
        Ok(())
    }
    
    /// Save current configuration to the default location
    pub fn save(&self) -> Result<()> {
        let config_path = Self::config_file_path();
        self.save_to_file(&config_path)?;
        info!("Configuration saved to: {}", config_path.display());
        Ok(())
    }
    
    /// Validate configuration values and return a corrected version
    pub fn validate(mut self) -> Self {
        // Clamp confidence threshold
        self.confidence_threshold = self.confidence_threshold.clamp(0.0, 1.0);
        
        // Clamp recording duration
        self.recording_duration = self.recording_duration.clamp(0.5, 10.0);
        
        // Ensure reasonable sample rate
        if self.sample_rate < 8000 || self.sample_rate > 48000 {
            warn!("Invalid sample rate {}, using default 16000", self.sample_rate);
            self.sample_rate = 16000;
        }
        
        // Ensure reasonable buffer size
        if self.buffer_size < 256 || self.buffer_size > 8192 {
            warn!("Invalid buffer size {}, using default 1024", self.buffer_size);
            self.buffer_size = 1024;
        }
        
        // Ensure reasonable limits
        self.max_log_entries = self.max_log_entries.max(10).min(1000);
        self.max_transcription_history = self.max_transcription_history.max(10).min(500);
        
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn test_default_config() {
        let config = Config::default();
        assert_eq!(config.confidence_threshold, 0.7);
        assert_eq!(config.recording_duration, 3.0);
        assert!(config.enable_preprocessing);
        assert!(config.show_transcription);
        assert!(config.monitor_memory);
    }

    #[test]
    fn test_config_validation() {
        let mut config = Config::default();
        config.confidence_threshold = 1.5; // Invalid
        config.recording_duration = -1.0; // Invalid
        config.sample_rate = 100; // Invalid
        
        let validated = config.validate();
        assert_eq!(validated.confidence_threshold, 1.0);
        assert_eq!(validated.recording_duration, 0.5);
        assert_eq!(validated.sample_rate, 16000);
    }

    #[test]
    fn test_save_and_load() -> Result<()> {
        let temp_dir = tempdir()?;
        let config_path = temp_dir.path().join("test_config.json");
        
        let original_config = Config::default();
        original_config.save_to_file(&config_path)?;
        
        let loaded_config = Config::load_from_file(&config_path)?;
        assert_eq!(original_config.confidence_threshold, loaded_config.confidence_threshold);
        assert_eq!(original_config.recording_duration, loaded_config.recording_duration);
        
        Ok(())
    }
}