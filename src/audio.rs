//! Audio processing utilities and helpers

use anyhow::Result;

/// Audio processing utilities
pub struct AudioUtils;

impl AudioUtils {
    /// Apply a simple bandpass filter for speech frequencies (300-3400 Hz)
    pub fn bandpass_filter(audio_data: &[f32], sample_rate: f32) -> Result<Vec<f32>> {
        // Simple implementation of a bandpass filter
        // In a full implementation, this would use more sophisticated DSP
        
        let low_cutoff = 300.0;
        let high_cutoff = 3400.0;
        
        let nyquist = sample_rate / 2.0;
        let low_ratio = low_cutoff / nyquist;
        let high_ratio = high_cutoff / nyquist;
        
        // Simple frequency domain filtering (conceptual)
        // In practice, you'd use FFT and proper filter design
        
        let mut filtered = audio_data.to_vec();
        
        // Apply a simple high-pass filter (remove low frequencies)
        let alpha = 1.0 - low_ratio;
        let mut prev = 0.0;
        for sample in filtered.iter_mut() {
            let current = *sample;
            *sample = alpha * (*sample - prev);
            prev = current;
        }
        
        // Apply a simple low-pass filter (remove high frequencies)
        let beta = high_ratio;
        let mut prev = 0.0;
        for sample in filtered.iter_mut() {
            *sample = beta * (*sample) + (1.0 - beta) * prev;
            prev = *sample;
        }
        
        Ok(filtered)
    }
    
    /// Normalize audio to prevent clipping
    pub fn normalize_audio(audio_data: &[f32]) -> Vec<f32> {
        let max_amplitude = audio_data.iter()
            .map(|x| x.abs())
            .fold(0.0, f32::max);
        
        if max_amplitude == 0.0 {
            return audio_data.to_vec();
        }
        
        let gain = 0.9 / max_amplitude;
        audio_data.iter().map(|x| x * gain).collect()
    }
    
    /// Remove DC offset from audio
    pub fn remove_dc_offset(audio_data: &[f32]) -> Vec<f32> {
        let mean: f32 = audio_data.iter().sum::<f32>() / audio_data.len() as f32;
        audio_data.iter().map(|x| x - mean).collect()
    }
    
    /// Apply noise gate to reduce background noise
    pub fn apply_noise_gate(audio_data: &[f32], threshold: f32) -> Vec<f32> {
        audio_data.iter().map(|&x| {
            if x.abs() < threshold {
                0.0
            } else {
                x
            }
        }).collect()
    }
    
    /// Calculate RMS level of audio signal
    pub fn calculate_rms(audio_data: &[f32]) -> f32 {
        let sum_squares: f32 = audio_data.iter().map(|x| x * x).sum();
        (sum_squares / audio_data.len() as f32).sqrt()
    }
    
    /// Detect if speech is present in audio based on energy
    pub fn detect_speech(audio_data: &[f32], threshold: f32) -> bool {
        let rms = Self::calculate_rms(audio_data);
        rms > threshold
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_normalize_audio() {
        let audio = vec![0.1, -0.5, 0.8, -0.3];
        let normalized = AudioUtils::normalize_audio(&audio);
        
        // Check that the maximum absolute value is close to 0.9
        let max_val = normalized.iter().map(|x| x.abs()).fold(0.0, f32::max);
        assert!((max_val - 0.9).abs() < 0.01);
    }

    #[test]
    fn test_remove_dc_offset() {
        let audio = vec![1.1, 0.6, 1.8, 0.7]; // Has DC offset of 1.05
        let corrected = AudioUtils::remove_dc_offset(&audio);
        
        // Check that mean is close to zero
        let mean: f32 = corrected.iter().sum::<f32>() / corrected.len() as f32;
        assert!(mean.abs() < 1e-6);
    }

    #[test]
    fn test_noise_gate() {
        let audio = vec![0.001, 0.5, 0.002, -0.3, 0.0001];
        let gated = AudioUtils::apply_noise_gate(&audio, 0.01);
        
        // Small values should be zeroed
        assert_eq!(gated[0], 0.0);
        assert_eq!(gated[2], 0.0);
        assert_eq!(gated[4], 0.0);
        
        // Large values should remain
        assert_eq!(gated[1], 0.5);
        assert_eq!(gated[3], -0.3);
    }

    #[test]
    fn test_calculate_rms() {
        let audio = vec![1.0, -1.0, 1.0, -1.0];
        let rms = AudioUtils::calculate_rms(&audio);
        assert!((rms - 1.0).abs() < 1e-6);
    }

    #[test]
    fn test_detect_speech() {
        let quiet_audio = vec![0.001, 0.002, -0.001];
        let loud_audio = vec![0.1, -0.2, 0.15];
        
        assert!(!AudioUtils::detect_speech(&quiet_audio, 0.01));
        assert!(AudioUtils::detect_speech(&loud_audio, 0.01));
    }
}