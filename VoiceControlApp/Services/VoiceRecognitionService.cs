using Microsoft.Extensions.Logging;
using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace VoiceControlApp.Services
{
    /// <summary>
    /// Voice recognition service using OpenAI Whisper tiny model
    /// Implementation uses Python subprocess to call Whisper CLI
    /// </summary>
    public class VoiceRecognitionService : IVoiceRecognitionService, IDisposable
    {
        private readonly ILogger<VoiceRecognitionService> _logger;
        private readonly string _tempDirectory;
        private bool _isInitialized = false;

        public VoiceRecognitionService(ILogger<VoiceRecognitionService> logger)
        {
            _logger = logger;
            _tempDirectory = Path.Combine(Path.GetTempPath(), "VoiceControlApp");
            Directory.CreateDirectory(_tempDirectory);
        }

        public async Task InitializeAsync()
        {
            try
            {
                _logger.LogInformation("Initializing Whisper tiny model...");
                
                // Check if Python and Whisper are available
                var pythonCheck = await RunProcessAsync("python", "--version", TimeSpan.FromSeconds(10));
                if (pythonCheck.ExitCode != 0)
                {
                    throw new InvalidOperationException("Python not found. Please install Python 3.8+");
                }

                // Test Whisper installation
                var whisperCheck = await RunProcessAsync("python", "-c \"import whisper; print('Whisper available')\"", TimeSpan.FromSeconds(10));
                if (whisperCheck.ExitCode != 0)
                {
                    _logger.LogWarning("Whisper not found. Attempting to install...");
                    var installResult = await RunProcessAsync("pip", "install openai-whisper", TimeSpan.FromMinutes(5));
                    
                    if (installResult.ExitCode != 0)
                    {
                        throw new InvalidOperationException($"Failed to install Whisper: {installResult.StandardError}");
                    }
                }

                _isInitialized = true;
                _logger.LogInformation("Voice recognition service initialized successfully");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to initialize voice recognition service");
                throw;
            }
        }

        public async Task<string> TranscribeAsync(byte[] audioData, CancellationToken cancellationToken)
        {
            if (!_isInitialized)
            {
                await InitializeAsync();
            }

            if (audioData == null || audioData.Length == 0)
            {
                return string.Empty;
            }

            try
            {
                // Save audio data to temporary WAV file
                var tempAudioFile = Path.Combine(_tempDirectory, $"audio_{Guid.NewGuid()}.wav");
                await File.WriteAllBytesAsync(tempAudioFile, audioData, cancellationToken);

                try
                {
                    _logger.LogDebug("Transcribing audio file: {AudioFile} ({Size} bytes)", tempAudioFile, audioData.Length);

                    // Use Whisper tiny model for fast transcription
                    var whisperScript = CreateWhisperScript();
                    var scriptFile = Path.Combine(_tempDirectory, "whisper_transcribe.py");
                    await File.WriteAllTextAsync(scriptFile, whisperScript, cancellationToken);

                    // Run Whisper transcription
                    var transcriptionResult = await RunProcessAsync(
                        "python", 
                        $"\"{scriptFile}\" \"{tempAudioFile}\"",
                        TimeSpan.FromSeconds(30),
                        cancellationToken);

                    if (transcriptionResult.ExitCode == 0)
                    {
                        var transcribedText = transcriptionResult.StandardOutput.Trim();
                        _logger.LogDebug("Transcription result: '{Text}'", transcribedText);
                        return transcribedText;
                    }
                    else
                    {
                        _logger.LogError("Whisper transcription failed: {Error}", transcriptionResult.StandardError);
                        return string.Empty;
                    }
                }
                finally
                {
                    // Clean up temporary audio file
                    try
                    {
                        File.Delete(tempAudioFile);
                    }
                    catch (Exception ex)
                    {
                        _logger.LogWarning(ex, "Failed to delete temporary audio file: {File}", tempAudioFile);
                    }
                }
            }
            catch (OperationCanceledException)
            {
                _logger.LogDebug("Transcription cancelled");
                return string.Empty;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during transcription");
                return string.Empty;
            }
        }

        private string CreateWhisperScript()
        {
            return @"
import sys
import whisper
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

def transcribe_audio(audio_file):
    try:
        # Load the tiny model for fast performance
        model = whisper.load_model('tiny')
        
        # Transcribe the audio
        result = model.transcribe(audio_file, fp16=False, language='en')
        
        # Return the transcribed text
        return result['text'].strip()
    except Exception as e:
        print(f'Error: {str(e)}', file=sys.stderr)
        return ''

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python whisper_transcribe.py <audio_file>', file=sys.stderr)
        sys.exit(1)
    
    audio_file = sys.argv[1]
    transcribed_text = transcribe_audio(audio_file)
    print(transcribed_text)
";
        }

        private async Task<ProcessResult> RunProcessAsync(
            string fileName, 
            string arguments, 
            TimeSpan timeout, 
            CancellationToken cancellationToken = default)
        {
            try
            {
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = fileName,
                    Arguments = arguments,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    StandardOutputEncoding = Encoding.UTF8,
                    StandardErrorEncoding = Encoding.UTF8
                };

                using var process = new Process { StartInfo = processStartInfo };
                
                var outputBuilder = new StringBuilder();
                var errorBuilder = new StringBuilder();

                process.OutputDataReceived += (sender, args) =>
                {
                    if (args.Data != null)
                        outputBuilder.AppendLine(args.Data);
                };

                process.ErrorDataReceived += (sender, args) =>
                {
                    if (args.Data != null)
                        errorBuilder.AppendLine(args.Data);
                };

                process.Start();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();

                // Wait for process to complete with timeout
                var completed = await Task.Run(() => process.WaitForExit((int)timeout.TotalMilliseconds), cancellationToken);

                if (!completed)
                {
                    try
                    {
                        process.Kill();
                    }
                    catch (Exception ex)
                    {
                        _logger.LogWarning(ex, "Failed to kill process");
                    }
                    throw new TimeoutException($"Process {fileName} timed out after {timeout}");
                }

                return new ProcessResult
                {
                    ExitCode = process.ExitCode,
                    StandardOutput = outputBuilder.ToString(),
                    StandardError = errorBuilder.ToString()
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error running process {FileName} {Arguments}", fileName, arguments);
                return new ProcessResult
                {
                    ExitCode = -1,
                    StandardOutput = string.Empty,
                    StandardError = ex.Message
                };
            }
        }

        public void Dispose()
        {
            try
            {
                if (Directory.Exists(_tempDirectory))
                {
                    Directory.Delete(_tempDirectory, true);
                }
                _logger.LogInformation("Voice recognition service disposed");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error disposing voice recognition service");
            }
        }

        private class ProcessResult
        {
            public int ExitCode { get; set; }
            public string StandardOutput { get; set; } = string.Empty;
            public string StandardError { get; set; } = string.Empty;
        }
    }
}