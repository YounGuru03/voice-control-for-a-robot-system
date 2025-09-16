using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace VoiceControlApp.Services
{
    /// <summary>
    /// Command processing service that matches transcribed text to the exact command set specified in requirements
    /// </summary>
    public class CommandProcessingService : ICommandProcessingService
    {
        private readonly ILogger<CommandProcessingService> _logger;
        private readonly Dictionary<string, List<string>> _commandPatterns;

        // Exact command set from requirements
        private readonly string[] _supportedCommands = {
            "open main",
            "open lamp", 
            "open robot",
            "open robot cell",
            "open 1",
            "open 2", 
            "alarm",
            "open train",
            "open report",
            "open record",
            "open user admin",
            "open user logging",
            "open user log",
            "open camera 1",
            "open camera 2", 
            "open camera 3",
            "open camera 4",
            "close camera 1",
            "close camera 2",
            "close camera 3", 
            "close camera 4",
            "template A",
            "template B",
            "template C",
            "template D",
            "template E",
            "template F",
            "template 7",
            "template 8",
            "template 9", 
            "template 10"
        };

        public CommandProcessingService(ILogger<CommandProcessingService> logger)
        {
            _logger = logger;
            _commandPatterns = InitializeCommandPatterns();
            
            _logger.LogInformation("Command processing service initialized with {Count} commands", _supportedCommands.Length);
        }

        public async Task<string> ProcessTextAsync(string transcribedText)
        {
            if (string.IsNullOrWhiteSpace(transcribedText))
            {
                return "None";
            }

            try
            {
                // Clean and normalize the input text
                var cleanText = CleanText(transcribedText);
                _logger.LogDebug("Processing text: '{Original}' -> '{Clean}'", transcribedText, cleanText);

                // Try to match against command patterns
                foreach (var kvp in _commandPatterns)
                {
                    var command = kvp.Key;
                    var patterns = kvp.Value;

                    foreach (var pattern in patterns)
                    {
                        try
                        {
                            if (Regex.IsMatch(cleanText, pattern, RegexOptions.IgnoreCase))
                            {
                                _logger.LogDebug("Command matched: '{Command}' using pattern '{Pattern}'", command, pattern);
                                return command;
                            }
                        }
                        catch (RegexException ex)
                        {
                            _logger.LogError(ex, "Invalid regex pattern: {Pattern}", pattern);
                        }
                    }
                }

                _logger.LogDebug("No command matched for text: '{Text}'", cleanText);
                return "None";
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing text: {Text}", transcribedText);
                return "None";
            }
        }

        public string[] GetSupportedCommands()
        {
            return _supportedCommands.ToArray();
        }

        public bool IsEmergencyCommand(string command)
        {
            return command.Equals("alarm", StringComparison.OrdinalIgnoreCase);
        }

        private Dictionary<string, List<string>> InitializeCommandPatterns()
        {
            var patterns = new Dictionary<string, List<string>>();

            // System Controls
            patterns["open main"] = new List<string>
            {
                @"\b(open|launch|start)\s+(main)\b",
                @"\bmain\b"
            };

            patterns["open lamp"] = new List<string>
            {
                @"\b(open|launch|start)\s+(lamp|light)\b",
                @"\blamp\b",
                @"\blight\b"
            };

            patterns["open robot"] = new List<string>
            {
                @"\b(open|launch|start)\s+(robot)\b",
                @"\brobot\b"
            };

            patterns["open robot cell"] = new List<string>
            {
                @"\b(open|launch|start)\s+(robot\s+cell)\b",
                @"\brobot\s+cell\b"
            };

            patterns["open 1"] = new List<string>
            {
                @"\b(open|launch|start)\s+(1|one)\b",
                @"\b(1|one)\b"
            };

            patterns["open 2"] = new List<string>
            {
                @"\b(open|launch|start)\s+(2|two)\b", 
                @"\b(2|two)\b"
            };

            patterns["alarm"] = new List<string>
            {
                @"\b(alarm|alert|warning|emergency)\b"
            };

            // Application Controls
            patterns["open train"] = new List<string>
            {
                @"\b(open|launch|start)\s+(train|training)\b",
                @"\btrain\b",
                @"\btraining\b"
            };

            patterns["open report"] = new List<string>
            {
                @"\b(open|launch|start)\s+(report|reports)\b",
                @"\breport\b",
                @"\breports\b"
            };

            patterns["open record"] = new List<string>
            {
                @"\b(open|launch|start)\s+(record|recording)\b",
                @"\brecord\b",
                @"\brecording\b"
            };

            patterns["open user admin"] = new List<string>
            {
                @"\b(open|launch|start)\s+(user\s+admin|user\s+administration)\b",
                @"\buser\s+admin\b",
                @"\buser\s+administration\b"
            };

            patterns["open user logging"] = new List<string>
            {
                @"\b(open|launch|start)\s+(user\s+logging)\b",
                @"\buser\s+logging\b"
            };

            patterns["open user log"] = new List<string>
            {
                @"\b(open|launch|start)\s+(user\s+log)\b",
                @"\buser\s+log\b"
            };

            // Camera Controls
            patterns["open camera 1"] = new List<string>
            {
                @"\b(open|launch|start)\s+(camera\s+(1|one))\b",
                @"\bcamera\s+(1|one)\b"
            };

            patterns["open camera 2"] = new List<string>
            {
                @"\b(open|launch|start)\s+(camera\s+(2|two))\b",
                @"\bcamera\s+(2|two)\b"
            };

            patterns["open camera 3"] = new List<string>
            {
                @"\b(open|launch|start)\s+(camera\s+(3|three))\b",
                @"\bcamera\s+(3|three)\b"
            };

            patterns["open camera 4"] = new List<string>
            {
                @"\b(open|launch|start)\s+(camera\s+(4|four))\b",
                @"\bcamera\s+(4|four)\b"
            };

            patterns["close camera 1"] = new List<string>
            {
                @"\b(close|stop|shut)\s+(camera\s+(1|one))\b",
                @"\bclose\s+camera\s+(1|one)\b"
            };

            patterns["close camera 2"] = new List<string>
            {
                @"\b(close|stop|shut)\s+(camera\s+(2|two))\b",
                @"\bclose\s+camera\s+(2|two)\b"
            };

            patterns["close camera 3"] = new List<string>
            {
                @"\b(close|stop|shut)\s+(camera\s+(3|three))\b", 
                @"\bclose\s+camera\s+(3|three)\b"
            };

            patterns["close camera 4"] = new List<string>
            {
                @"\b(close|stop|shut)\s+(camera\s+(4|four))\b",
                @"\bclose\s+camera\s+(4|four)\b"
            };

            // Template Commands
            patterns["template A"] = new List<string>
            {
                @"\btemplate\s+(a|alpha)\b",
                @"\btemplate\s+a\b"
            };

            patterns["template B"] = new List<string>
            {
                @"\btemplate\s+(b|beta|bravo)\b",
                @"\btemplate\s+b\b"
            };

            patterns["template C"] = new List<string>
            {
                @"\btemplate\s+(c|charlie)\b",
                @"\btemplate\s+c\b"
            };

            patterns["template D"] = new List<string>
            {
                @"\btemplate\s+(d|delta)\b",
                @"\btemplate\s+d\b"
            };

            patterns["template E"] = new List<string>
            {
                @"\btemplate\s+(e|echo)\b",
                @"\btemplate\s+e\b"
            };

            patterns["template F"] = new List<string>
            {
                @"\btemplate\s+(f|foxtrot)\b",
                @"\btemplate\s+f\b"
            };

            patterns["template 7"] = new List<string>
            {
                @"\btemplate\s+(7|seven)\b"
            };

            patterns["template 8"] = new List<string>
            {
                @"\btemplate\s+(8|eight)\b"
            };

            patterns["template 9"] = new List<string>
            {
                @"\btemplate\s+(9|nine)\b"
            };

            patterns["template 10"] = new List<string>
            {
                @"\btemplate\s+(10|ten)\b"
            };

            return patterns;
        }

        private string CleanText(string text)
        {
            if (string.IsNullOrWhiteSpace(text))
            {
                return string.Empty;
            }

            // Convert to lowercase
            text = text.ToLowerInvariant().Trim();

            // Remove common filler words and phrases
            var fillerWords = new[]
            {
                "um", "uh", "er", "ah", "like", "you know", "well", "so",
                "okay", "ok", "please", "can you", "could you", "would you",
                "hey", "hi", "hello", "excuse me"
            };

            foreach (var filler in fillerWords)
            {
                text = Regex.Replace(text, $@"\b{filler}\b", " ", RegexOptions.IgnoreCase);
            }

            // Remove punctuation
            text = Regex.Replace(text, @"[^\w\s]", " ");

            // Normalize whitespace
            text = Regex.Replace(text, @"\s+", " ").Trim();

            return text;
        }
    }
}