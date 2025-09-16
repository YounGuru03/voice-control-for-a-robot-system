using System.Threading.Tasks;

namespace VoiceControlApp.Services
{
    /// <summary>
    /// Service for processing commands from transcribed text
    /// </summary>
    public interface ICommandProcessingService
    {
        /// <summary>
        /// Process transcribed text and extract robot commands
        /// </summary>
        Task<string> ProcessTextAsync(string transcribedText);

        /// <summary>
        /// Get list of supported commands
        /// </summary>
        string[] GetSupportedCommands();

        /// <summary>
        /// Check if command is an emergency command
        /// </summary>
        bool IsEmergencyCommand(string command);
    }
}