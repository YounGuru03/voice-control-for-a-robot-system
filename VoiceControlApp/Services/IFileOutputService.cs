using System.Threading.Tasks;

namespace VoiceControlApp.Services
{
    /// <summary>
    /// Service for writing commands to text.txt output file
    /// </summary>
    public interface IFileOutputService
    {
        /// <summary>
        /// Write a command to the output file
        /// </summary>
        Task WriteCommandAsync(string command);

        /// <summary>
        /// Clear the output file (called at startup)
        /// </summary>
        void ClearOutputFile();

        /// <summary>
        /// Get the full path to the output file
        /// </summary>
        string GetOutputFilePath();
    }
}