using System;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceControlApp.Services
{
    /// <summary>
    /// Service for audio recording and processing
    /// </summary>
    public interface IAudioService
    {
        /// <summary>
        /// Record audio for the specified duration
        /// </summary>
        Task<byte[]> RecordAudioAsync(double durationSeconds, CancellationToken cancellationToken);

        /// <summary>
        /// Check if silence is detected (for auto-stop functionality)
        /// </summary>
        Task<bool> IsSilenceDetectedAsync();

        /// <summary>
        /// Get audio spectrum data for visualization
        /// </summary>
        Task<float[]> GetAudioSpectrumAsync();

        /// <summary>
        /// Initialize audio recording device
        /// </summary>
        Task InitializeAsync();

        /// <summary>
        /// Clean up audio resources
        /// </summary>
        void Dispose();
    }
}