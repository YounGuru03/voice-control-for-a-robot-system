using Microsoft.Extensions.Logging;
using NAudio.Wave;
using System;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceControlApp.Services
{
    /// <summary>
    /// Audio service implementation using NAudio for Windows
    /// </summary>
    public class AudioService : IAudioService, IDisposable
    {
        private readonly ILogger<AudioService> _logger;
        private WaveInEvent _waveIn;
        private MemoryStream _recordingStream;
        private WaveFileWriter _waveWriter;
        private bool _isRecording;
        private readonly object _lock = new object();
        private float[] _lastAudioSpectrum = new float[64]; // For visualization
        private DateTime _lastAudioActivity = DateTime.Now;

        // Audio settings optimized for speech recognition
        private const int SampleRate = 16000; // Whisper prefers 16kHz
        private const int BitsPerSample = 16;
        private const int Channels = 1; // Mono

        public AudioService(ILogger<AudioService> logger)
        {
            _logger = logger;
        }

        public async Task InitializeAsync()
        {
            try
            {
                _waveIn = new WaveInEvent
                {
                    WaveFormat = new WaveFormat(SampleRate, BitsPerSample, Channels),
                    BufferMilliseconds = 100
                };

                _waveIn.DataAvailable += OnDataAvailable;
                _logger.LogInformation("Audio service initialized successfully");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to initialize audio service");
                throw;
            }
        }

        public async Task<byte[]> RecordAudioAsync(double durationSeconds, CancellationToken cancellationToken)
        {
            if (_waveIn == null)
            {
                await InitializeAsync();
            }

            try
            {
                lock (_lock)
                {
                    if (_isRecording)
                    {
                        return Array.Empty<byte>();
                    }

                    _isRecording = true;
                    _recordingStream = new MemoryStream();
                    
                    // Create wave writer for proper WAV format
                    _waveWriter = new WaveFileWriter(_recordingStream, _waveIn.WaveFormat);
                }

                // Start recording
                _waveIn.StartRecording();
                _logger.LogDebug("Started audio recording for {Duration}s", durationSeconds);

                // Wait for specified duration or cancellation
                var recordingTask = Task.Delay(TimeSpan.FromSeconds(durationSeconds), cancellationToken);
                await recordingTask;

                // Stop recording
                _waveIn.StopRecording();
                
                lock (_lock)
                {
                    _isRecording = false;
                    _waveWriter?.Dispose();
                    var audioData = _recordingStream.ToArray();
                    _recordingStream?.Dispose();
                    
                    _logger.LogDebug("Completed audio recording: {Size} bytes", audioData.Length);
                    return audioData;
                }
            }
            catch (OperationCanceledException)
            {
                _logger.LogDebug("Audio recording cancelled");
                return Array.Empty<byte>();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during audio recording");
                throw;
            }
            finally
            {
                try
                {
                    _waveIn?.StopRecording();
                    lock (_lock)
                    {
                        _isRecording = false;
                        _waveWriter?.Dispose();
                        _recordingStream?.Dispose();
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error cleaning up audio recording");
                }
            }
        }

        public async Task<bool> IsSilenceDetectedAsync()
        {
            // Simple silence detection based on time since last audio activity
            var silenceThreshold = TimeSpan.FromSeconds(2);
            var isSilent = DateTime.Now - _lastAudioActivity > silenceThreshold;
            
            if (isSilent)
            {
                _logger.LogDebug("Silence detected");
            }
            
            return isSilent;
        }

        public async Task<float[]> GetAudioSpectrumAsync()
        {
            // Return the last computed audio spectrum for visualization
            lock (_lock)
            {
                return _lastAudioSpectrum.ToArray();
            }
        }

        private void OnDataAvailable(object sender, WaveInEventArgs e)
        {
            try
            {
                lock (_lock)
                {
                    if (_isRecording && _waveWriter != null)
                    {
                        // Write audio data to stream
                        _waveWriter.Write(e.Buffer, 0, e.BytesRecorded);

                        // Update audio activity timestamp
                        if (HasAudioActivity(e.Buffer, e.BytesRecorded))
                        {
                            _lastAudioActivity = DateTime.Now;
                        }

                        // Compute simple spectrum for visualization
                        UpdateAudioSpectrum(e.Buffer, e.BytesRecorded);
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing audio data");
            }
        }

        private bool HasAudioActivity(byte[] buffer, int bytesRecorded)
        {
            // Simple activity detection based on audio level
            const int threshold = 500; // Adjust based on testing
            
            for (int i = 0; i < bytesRecorded - 1; i += 2)
            {
                var sample = BitConverter.ToInt16(buffer, i);
                if (Math.Abs(sample) > threshold)
                {
                    return true;
                }
            }
            return false;
        }

        private void UpdateAudioSpectrum(byte[] buffer, int bytesRecorded)
        {
            try
            {
                // Simple spectrum analysis for visualization
                // Convert bytes to samples and compute basic frequency bins
                var samples = new short[bytesRecorded / 2];
                Buffer.BlockCopy(buffer, 0, samples, 0, bytesRecorded);

                // Group samples into spectrum bins (simplified)
                var binSize = samples.Length / _lastAudioSpectrum.Length;
                
                for (int bin = 0; bin < _lastAudioSpectrum.Length; bin++)
                {
                    float sum = 0;
                    var startIndex = bin * binSize;
                    var endIndex = Math.Min(startIndex + binSize, samples.Length);
                    
                    for (int i = startIndex; i < endIndex; i++)
                    {
                        sum += Math.Abs(samples[i]);
                    }
                    
                    _lastAudioSpectrum[bin] = sum / binSize / 32768.0f; // Normalize to 0-1
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error updating audio spectrum");
            }
        }

        public void Dispose()
        {
            try
            {
                _waveIn?.StopRecording();
                _waveIn?.Dispose();
                _waveWriter?.Dispose();
                _recordingStream?.Dispose();
                _logger.LogInformation("Audio service disposed");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error disposing audio service");
            }
        }
    }
}