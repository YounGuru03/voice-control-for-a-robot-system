//! Speech processing module using native Windows APIs
//! 
//! Handles audio capture and speech-to-text conversion with optimized performance.

use anyhow::{Result, anyhow};
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use cpal::{Device, Stream, StreamConfig, SampleRate};
use std::sync::{Arc, Mutex, mpsc};
use std::thread;
use std::time::Duration;
use tracing::{info, error, debug};
use crate::{AppState, LogLevel};

pub struct SpeechProcessor {
    audio_device: Option<Device>,
    audio_config: Option<StreamConfig>,
    recording_stream: Option<Stream>,
    is_listening: Arc<Mutex<bool>>,
    audio_sender: Option<mpsc::Sender<Vec<f32>>>,
}

impl SpeechProcessor {
    pub fn new() -> Result<Self> {
        info!("Initializing speech processor");
        
        // Get default audio host
        let host = cpal::default_host();
        info!("Using audio host: {}", host.id().name());
        
        // Get default input device
        let device = host
            .default_input_device()
            .ok_or_else(|| anyhow!("No input audio device available"))?;
        
        info!("Using audio device: {}", device.name().unwrap_or_else(|_| "Unknown".to_string()));
        
        // Get supported config
        let mut supported_configs = device.supported_input_configs()?;
        let supported_config = supported_configs
            .next()
            .ok_or_else(|| anyhow!("No supported audio configuration"))?;
        
        info!("Supported sample rate range: {} - {}", 
              supported_config.min_sample_rate().0, 
              supported_config.max_sample_rate().0);
        
        // Create config with preferred settings for speech recognition
        let sample_rate = if supported_config.max_sample_rate().0 >= 16000 {
            16000 // Preferred for speech recognition
        } else {
            supported_config.max_sample_rate().0
        };
        
        let config = StreamConfig {
            channels: 1, // Mono for speech recognition
            sample_rate: SampleRate(sample_rate),
            buffer_size: cpal::BufferSize::Fixed(1024),
        };
        
        info!("Audio configuration: {} Hz, {} channels, {} buffer size", 
              config.sample_rate.0, config.channels, "1024");
        
        Ok(Self {
            audio_device: Some(device),
            audio_config: Some(config),
            recording_stream: None,
            is_listening: Arc::new(Mutex::new(false)),
            audio_sender: None,
        })
    }
    
    pub fn start_listening(&mut self, app_state: Arc<Mutex<AppState>>) -> Result<()> {
        if *self.is_listening.lock().unwrap() {
            return Ok(()); // Already listening
        }
        
        let device = self.audio_device.as_ref()
            .ok_or_else(|| anyhow!("No audio device available"))?;
        
        let config = self.audio_config.as_ref()
            .ok_or_else(|| anyhow!("No audio configuration available"))?;
        
        info!("Starting audio stream");
        
        // Create channel for audio data
        let (audio_tx, audio_rx) = mpsc::channel::<Vec<f32>>();
        self.audio_sender = Some(audio_tx.clone());
        
        // Create audio processing thread
        let app_state_clone = app_state.clone();
        let is_listening = self.is_listening.clone();
        
        thread::spawn(move || {
            if let Err(e) = Self::audio_processing_thread(audio_rx, app_state_clone, is_listening) {
                error!("Audio processing thread failed: {}", e);
            }
        });
        
        // Create error callback
        let err_fn = |err| {
            error!("Audio stream error: {}", err);
        };
        
        // Create audio data callback
        let audio_tx_clone = audio_tx.clone();
        let data_fn = move |data: &[f32], _: &cpal::InputCallbackInfo| {
            // Send audio data for processing
            if audio_tx_clone.send(data.to_vec()).is_err() {
                // Channel closed, stop sending
                return;
            }
        };
        
        // Build and start the audio stream
        let stream = device.build_input_stream(config, data_fn, err_fn, None)?;
        stream.play()?;
        
        self.recording_stream = Some(stream);
        *self.is_listening.lock().unwrap() = true;
        
        info!("Audio stream started successfully");
        Ok(())
    }
    
    pub fn stop_listening(&mut self) -> Result<()> {
        if !*self.is_listening.lock().unwrap() {
            return Ok(()); // Not listening
        }
        
        info!("Stopping audio stream");
        
        // Stop the stream
        if let Some(stream) = self.recording_stream.take() {
            drop(stream); // This will stop the stream
        }
        
        *self.is_listening.lock().unwrap() = false;
        self.audio_sender = None;
        
        info!("Audio stream stopped");
        Ok(())
    }
    
    fn audio_processing_thread(
        audio_rx: mpsc::Receiver<Vec<f32>>,
        app_state: Arc<Mutex<AppState>>,
        is_listening: Arc<Mutex<bool>>,
    ) -> Result<()> {
        info!("Audio processing thread started");
        
        let mut audio_buffer = Vec::new();
        let mut last_process_time = std::time::Instant::now();
        
        // Get recording duration from config
        let recording_duration = {
            let state = app_state.lock().unwrap();
            state.config.recording_duration
        };
        
        let samples_per_chunk = (16000.0 * recording_duration) as usize; // Assuming 16kHz
        
        while *is_listening.lock().unwrap() {
            match audio_rx.recv_timeout(Duration::from_millis(100)) {
                Ok(audio_data) => {
                    audio_buffer.extend(audio_data);
                    
                    // Process when we have enough samples
                    if audio_buffer.len() >= samples_per_chunk {
                        debug!("Processing audio chunk of {} samples", audio_buffer.len());
                        
                        // Take the required samples for processing
                        let chunk: Vec<f32> = audio_buffer.drain(..samples_per_chunk).collect();
                        
                        // Process the audio chunk
                        if let Err(e) = Self::process_audio_chunk(&chunk, &app_state) {
                            error!("Failed to process audio chunk: {}", e);
                        }
                        
                        last_process_time = std::time::Instant::now();
                    }
                }
                Err(mpsc::RecvTimeoutError::Timeout) => {
                    // Check if we should process remaining buffer
                    if !audio_buffer.is_empty() && 
                       last_process_time.elapsed() > Duration::from_secs(1) {
                        debug!("Processing remaining audio buffer of {} samples", audio_buffer.len());
                        
                        if let Err(e) = Self::process_audio_chunk(&audio_buffer, &app_state) {
                            error!("Failed to process audio chunk: {}", e);
                        }
                        
                        audio_buffer.clear();
                        last_process_time = std::time::Instant::now();
                    }
                    continue;
                }
                Err(mpsc::RecvTimeoutError::Disconnected) => {
                    info!("Audio processing thread stopping - channel disconnected");
                    break;
                }
            }
        }
        
        info!("Audio processing thread stopped");
        Ok(())
    }
    
    fn process_audio_chunk(audio_data: &[f32], app_state: &Arc<Mutex<AppState>>) -> Result<()> {
        // Preprocess audio
        let processed_audio = Self::preprocess_audio(audio_data)?;
        
        // Check if preprocessing is enabled
        let enable_preprocessing = {
            let state = app_state.lock().unwrap();
            state.config.enable_preprocessing
        };
        
        let final_audio = if enable_preprocessing {
            processed_audio
        } else {
            audio_data.to_vec()
        };
        
        // Perform speech recognition
        let transcript = Self::speech_to_text(&final_audio)?;
        
        if !transcript.trim().is_empty() {
            info!("Transcribed: {}", transcript);
            
            // Update app state with transcript
            {
                let mut state = app_state.lock().unwrap();
                state.last_transcript = transcript.clone();
                state.add_transcription(transcript.clone());
                state.add_log_entry(
                    format!("Transcript: {}", transcript),
                    LogLevel::Info,
                );
            }
            
            // Process with NLP to extract command
            let command = Self::extract_command(&transcript)?;
            
            if !command.trim().is_empty() {
                info!("Command extracted: {}", command);
                
                // Update app state with command
                {
                    let mut state = app_state.lock().unwrap();
                    state.last_command = command.clone();
                    state.add_log_entry(
                        format!("Command: {}", command),
                        LogLevel::Command,
                    );
                }
                
                // Write to output file
                Self::write_command_to_file(&command)?;
                
                // Log success
                {
                    let mut state = app_state.lock().unwrap();
                    state.add_log_entry(
                        "Command saved to text.txt".to_string(),
                        LogLevel::Success,
                    );
                }
            }
        }
        
        Ok(())
    }
    
    fn preprocess_audio(audio_data: &[f32]) -> Result<Vec<f32>> {
        // Simple audio preprocessing:
        // 1. DC offset removal
        // 2. Normalization
        // 3. Basic noise gate
        
        let mut processed = audio_data.to_vec();
        
        // Remove DC offset
        let mean: f32 = processed.iter().sum::<f32>() / processed.len() as f32;
        for sample in processed.iter_mut() {
            *sample -= mean;
        }
        
        // Find peak for normalization
        let peak = processed.iter()
            .map(|x| x.abs())
            .fold(0.0, f32::max);
        
        // Normalize to prevent clipping
        if peak > 0.0 {
            let gain = 0.9 / peak;
            for sample in processed.iter_mut() {
                *sample *= gain;
            }
        }
        
        // Simple noise gate
        let noise_threshold = 0.01;
        for sample in processed.iter_mut() {
            if sample.abs() < noise_threshold {
                *sample = 0.0;
            }
        }
        
        Ok(processed)
    }
    
    fn speech_to_text(audio_data: &[f32]) -> Result<String> {
        // For the initial implementation, we'll use a mock speech recognition
        // In a full implementation, this would integrate with Windows Speech Platform
        // or a lightweight embedded model
        
        debug!("Processing audio for speech recognition ({} samples)", audio_data.len());
        
        // Calculate audio energy to determine if there's speech
        let energy: f32 = audio_data.iter().map(|x| x * x).sum::<f32>() / audio_data.len() as f32;
        let rms = energy.sqrt();
        
        debug!("Audio RMS level: {:.4}", rms);
        
        // Simple energy-based speech detection
        if rms > 0.005 { // Threshold for speech detection
            // Mock transcriptions for different energy levels
            // In a real implementation, this would be actual speech recognition
            let mock_transcripts = [
                "open main",
                "open lamp", 
                "open robot",
                "start camera 1",
                "close camera 2",
                "template A",
                "alarm",
                "open report",
                "emergency stop",
                "open user admin",
            ];
            
            // Use audio characteristics to select a mock transcript
            let index = ((rms * 1000.0) as usize) % mock_transcripts.len();
            let transcript = mock_transcripts[index].to_string();
            
            debug!("Mock transcript generated: {}", transcript);
            Ok(transcript)
        } else {
            debug!("No speech detected (low energy)");
            Ok(String::new())
        }
    }
    
    fn extract_command(transcript: &str) -> Result<String> {
        // Simple NLP processing to extract commands
        let text = transcript.to_lowercase().trim().to_string();
        
        debug!("Processing text for command extraction: {}", text);
        
        // Command mapping patterns (similar to Python version)
        let commands = [
            // Main application commands
            ("open main", &["open main", "launch main", "start main"][..]),
            ("open lamp", &["open lamp", "start lamp", "launch lamp"]),
            ("open robot", &["open robot", "launch robot", "start robot"]),
            ("open robot cell", &["open robot cell", "start robot cell", "launch robot cell"]),
            
            // Numbered commands
            ("open 1", &["open 1", "open one", "launch 1", "start 1"]),
            ("open 2", &["open 2", "open two", "launch 2", "start 2"]),
            
            // System commands
            ("alarm", &["alarm", "alert"]),
            ("open train", &["open train", "launch train", "start train"]),
            ("open report", &["open report", "launch report", "start report"]),
            ("open record", &["open record", "launch record", "start record"]),
            
            // User management
            ("open user admin", &["open user admin", "launch user admin", "user admin"]),
            ("open user logging", &["open user logging", "user logging"]),
            ("open user log", &["open user log", "user log"]),
            
            // Camera controls
            ("open camera 1", &["open camera 1", "open camera one", "start camera 1"]),
            ("close camera 1", &["close camera 1", "close camera one", "stop camera 1"]),
            ("open camera 2", &["open camera 2", "open camera two", "start camera 2"]),
            ("close camera 2", &["close camera 2", "close camera two", "stop camera 2"]),
            ("open camera 3", &["open camera 3", "open camera three", "start camera 3"]),
            ("close camera 3", &["close camera 3", "close camera three", "stop camera 3"]),
            ("open camera 4", &["open camera 4", "open camera four", "start camera 4"]),
            ("close camera 4", &["close camera 4", "close camera four", "stop camera 4"]),
            
            // Template commands
            ("template A", &["template a", "template alpha"]),
            ("template B", &["template b", "template beta"]),
            ("template C", &["template c", "template charlie"]),
            ("template D", &["template d", "template delta"]),
            ("template E", &["template e", "template echo"]),
            ("template F", &["template f", "template foxtrot"]),
            ("template 7", &["template 7", "template seven"]),
            ("template 8", &["template 8", "template eight"]),
            ("template 9", &["template 9", "template nine"]),
            ("template 10", &["template 10", "template ten"]),
            
            // Emergency
            ("emergency stop", &["emergency stop", "e-stop", "abort", "stop"]),
        ];
        
        // Find matching command
        for (command, patterns) in commands.iter() {
            for pattern in patterns.iter() {
                if text.contains(pattern) {
                    debug!("Command matched: {} -> {}", pattern, command);
                    return Ok(command.to_string());
                }
            }
        }
        
        debug!("No command pattern matched");
        Ok(String::new())
    }
    
    fn write_command_to_file(command: &str) -> Result<()> {
        use std::fs;
        use std::path::Path;
        
        let file_path = Path::new("text.txt");
        
        debug!("Writing command to file: {}", command);
        
        fs::write(file_path, command)?;
        
        info!("Command written to {}: {}", file_path.display(), command);
        Ok(())
    }
    
    pub fn is_listening(&self) -> bool {
        *self.is_listening.lock().unwrap()
    }
}

impl Drop for SpeechProcessor {
    fn drop(&mut self) {
        let _ = self.stop_listening();
        info!("Speech processor dropped and cleaned up");
    }
}