using System;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceControlApp.Services
{
    /// <summary>
    /// Service for speech-to-text conversion using OpenAI Whisper
    /// </summary>
    public interface IVoiceRecognitionService
    {
        /// <summary>
        /// Transcribe audio data to text using Whisper tiny model
        /// </summary>
        Task<string> TranscribeAsync(byte[] audioData, CancellationToken cancellationToken);

        /// <summary>
        /// Initialize the Whisper model
        /// </summary>
        Task InitializeAsync();

        /// <summary>
        /// Clean up resources
        /// </summary>
        void Dispose();
    }
}