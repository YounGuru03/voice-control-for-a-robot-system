using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Media;
using System;
using System.Collections.ObjectModel;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Input;
using VoiceControlApp.Services;
using Microsoft.Extensions.Logging;
using System.Diagnostics;

namespace VoiceControlApp.ViewModels
{
    public partial class MainWindowViewModel : ObservableObject
    {
        private readonly IAudioService _audioService;
        private readonly IVoiceRecognitionService _voiceRecognitionService;
        private readonly ICommandProcessingService _commandProcessingService;
        private readonly IFileOutputService _fileOutputService;
        private readonly ILogger<MainWindowViewModel> _logger;
        private readonly Timer _recordingTimer;
        private CancellationTokenSource _cancellationTokenSource;
        private DateTime _recordingStartTime;

        [ObservableProperty]
        private string status = "Ready";

        [ObservableProperty]
        private Brush statusColor = new SolidColorBrush(Microsoft.UI.Colors.Green);

        [ObservableProperty]
        private string lastCommand = "None";

        [ObservableProperty]
        private bool isListening = false;

        [ObservableProperty]
        private string listenButtonText = "🎤 Start Listening";

        [ObservableProperty]
        private string transcriptionText = "Transcribed speech will appear here...";

        [ObservableProperty]
        private string recordingTimer = "00:00";

        public ObservableCollection<string> ActivityLog { get; } = new();

        public ICommand ToggleListeningCommand { get; }
        public ICommand ShowSettingsCommand { get; }
        public ICommand OpenOutputFileCommand { get; }
        public ICommand ClearLogCommand { get; }

        public MainWindowViewModel(
            IAudioService audioService,
            IVoiceRecognitionService voiceRecognitionService,
            ICommandProcessingService commandProcessingService,
            IFileOutputService fileOutputService,
            ILogger<MainWindowViewModel> logger)
        {
            _audioService = audioService;
            _voiceRecognitionService = voiceRecognitionService;
            _commandProcessingService = commandProcessingService;
            _fileOutputService = fileOutputService;
            _logger = logger;

            // Initialize commands
            ToggleListeningCommand = new AsyncRelayCommand(ToggleListeningAsync);
            ShowSettingsCommand = new RelayCommand(ShowSettings);
            OpenOutputFileCommand = new RelayCommand(OpenOutputFile);
            ClearLogCommand = new RelayCommand(ClearLog);

            // Initialize recording timer
            _recordingTimer = new Timer(UpdateRecordingTimer, null, Timeout.Infinite, Timeout.Infinite);

            // Add initial log entry
            AddLogEntry("Voice Control System initialized", "INFO");
        }

        private async Task ToggleListeningAsync()
        {
            try
            {
                if (!IsListening)
                {
                    await StartListeningAsync();
                }
                else
                {
                    await StopListeningAsync();
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error toggling listening state");
                AddLogEntry($"Error: {ex.Message}", "ERROR");
            }
        }

        private async Task StartListeningAsync()
        {
            try
            {
                _cancellationTokenSource = new CancellationTokenSource();
                
                IsListening = true;
                ListenButtonText = "⏹️ Stop Listening";
                Status = "Listening...";
                StatusColor = new SolidColorBrush(Microsoft.UI.Colors.Orange);
                
                _recordingStartTime = DateTime.Now;
                _recordingTimer.Change(TimeSpan.Zero, TimeSpan.FromSeconds(1));
                
                AddLogEntry("Started voice recognition", "INFO");

                // Start continuous listening loop
                await ListenContinuouslyAsync(_cancellationTokenSource.Token);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error starting listening");
                AddLogEntry($"Failed to start listening: {ex.Message}", "ERROR");
                await StopListeningAsync();
            }
        }

        private async Task StopListeningAsync()
        {
            try
            {
                _cancellationTokenSource?.Cancel();
                _recordingTimer.Change(Timeout.Infinite, Timeout.Infinite);
                
                IsListening = false;
                ListenButtonText = "🎤 Start Listening";
                Status = "Ready";
                StatusColor = new SolidColorBrush(Microsoft.UI.Colors.Green);
                RecordingTimer = "00:00";
                
                AddLogEntry("Stopped voice recognition", "INFO");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error stopping listening");
                AddLogEntry($"Error stopping: {ex.Message}", "ERROR");
            }
        }

        private async Task ListenContinuouslyAsync(CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    // Record audio for specified duration
                    var audioData = await _audioService.RecordAudioAsync(3.0, cancellationToken);
                    
                    if (audioData?.Length > 0)
                    {
                        // Transcribe using Whisper
                        var transcribedText = await _voiceRecognitionService.TranscribeAsync(audioData, cancellationToken);
                        
                        if (!string.IsNullOrWhiteSpace(transcribedText))
                        {
                            // Update transcription display
                            var timestamp = DateTime.Now.ToString("HH:mm:ss");
                            TranscriptionText = $"[{timestamp}] {transcribedText}\n{TranscriptionText}";
                            
                            // Process command
                            var command = await _commandProcessingService.ProcessTextAsync(transcribedText);
                            
                            if (command != "None")
                            {
                                LastCommand = command;
                                AddLogEntry($"Command recognized: {command} (from: '{transcribedText}')", "COMMAND");
                                
                                // Write to output file
                                await _fileOutputService.WriteCommandAsync(command);
                                
                                // Auto-stop for certain commands or after timeout
                                if (await ShouldAutoStopAsync(command, _recordingStartTime))
                                {
                                    await StopListeningAsync();
                                    break;
                                }
                            }
                        }
                    }

                    // Small delay to prevent CPU overload
                    await Task.Delay(100, cancellationToken);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error in listening loop");
                    AddLogEntry($"Listening error: {ex.Message}", "ERROR");
                    
                    // Avoid rapid error loops
                    await Task.Delay(1000, cancellationToken);
                }
            }
        }

        private async Task<bool> ShouldAutoStopAsync(string command, DateTime startTime)
        {
            // Auto-stop for emergency commands
            if (command.Contains("emergency") || command.Contains("stop"))
            {
                AddLogEntry("Emergency command detected - auto-stopping", "WARNING");
                return true;
            }

            // Auto-stop after 30 seconds to prevent memory overflow
            if (DateTime.Now - startTime > TimeSpan.FromSeconds(30))
            {
                AddLogEntry("Recording timeout reached - auto-stopping for safety", "WARNING");
                return true;
            }

            // Auto-stop if silence detected (implement silence detection logic here)
            var silenceDetected = await _audioService.IsSilenceDetectedAsync();
            if (silenceDetected)
            {
                AddLogEntry("Silence detected - auto-stopping", "INFO");
                return true;
            }

            return false;
        }

        private void UpdateRecordingTimer(object state)
        {
            if (IsListening)
            {
                var elapsed = DateTime.Now - _recordingStartTime;
                RecordingTimer = elapsed.ToString(@"mm\:ss");
            }
        }

        private void ShowSettings()
        {
            AddLogEntry("Settings dialog opened", "INFO");
            // TODO: Implement settings dialog
        }

        private void OpenOutputFile()
        {
            try
            {
                var filePath = _fileOutputService.GetOutputFilePath();
                Process.Start(new ProcessStartInfo
                {
                    FileName = filePath,
                    UseShellExecute = true
                });
                AddLogEntry($"Opened output file: {filePath}", "INFO");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error opening output file");
                AddLogEntry($"Error opening file: {ex.Message}", "ERROR");
            }
        }

        private void ClearLog()
        {
            ActivityLog.Clear();
            AddLogEntry("Activity log cleared", "INFO");
        }

        private void AddLogEntry(string message, string level)
        {
            var timestamp = DateTime.Now.ToString("HH:mm:ss");
            var logEntry = $"[{timestamp}] [{level}] {message}";
            
            // Add to beginning of collection and limit size
            ActivityLog.Insert(0, logEntry);
            
            if (ActivityLog.Count > 100)
            {
                ActivityLog.RemoveAt(ActivityLog.Count - 1);
            }
        }

        protected override void OnPropertyChanged(System.ComponentModel.PropertyChangedEventArgs e)
        {
            base.OnPropertyChanged(e);
            
            // Log property changes for debugging
            if (e.PropertyName == nameof(Status) || e.PropertyName == nameof(LastCommand))
            {
                _logger.LogDebug("Property changed: {PropertyName} = {Value}", e.PropertyName, 
                    e.PropertyName == nameof(Status) ? Status : LastCommand);
            }
        }
    }
}