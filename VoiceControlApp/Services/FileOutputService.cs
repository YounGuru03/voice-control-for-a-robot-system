using Microsoft.Extensions.Logging;
using System;
using System.IO;
using System.Threading.Tasks;

namespace VoiceControlApp.Services
{
    /// <summary>
    /// File output service for writing commands to text.txt
    /// </summary>
    public class FileOutputService : IFileOutputService
    {
        private readonly ILogger<FileOutputService> _logger;
        private readonly string _outputFilePath;
        private readonly object _fileLock = new object();

        public FileOutputService(ILogger<FileOutputService> logger)
        {
            _logger = logger;
            _outputFilePath = Path.Combine(AppContext.BaseDirectory, "text.txt");
        }

        public void ClearOutputFile()
        {
            try
            {
                lock (_fileLock)
                {
                    // Clear the file at startup as required by specifications
                    File.WriteAllText(_outputFilePath, string.Empty);
                    _logger.LogInformation("Output file cleared at startup: {FilePath}", _outputFilePath);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to clear output file: {FilePath}", _outputFilePath);
                throw;
            }
        }

        public async Task WriteCommandAsync(string command)
        {
            if (string.IsNullOrWhiteSpace(command) || command == "None")
            {
                return;
            }

            try
            {
                var timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
                var logEntry = $"[{timestamp}] {command}{Environment.NewLine}";

                await Task.Run(() =>
                {
                    lock (_fileLock)
                    {
                        File.AppendAllText(_outputFilePath, logEntry);
                    }
                });

                _logger.LogInformation("Command written to file: {Command}", command);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to write command to file: {Command}", command);
                throw;
            }
        }

        public string GetOutputFilePath()
        {
            return _outputFilePath;
        }
    }
}