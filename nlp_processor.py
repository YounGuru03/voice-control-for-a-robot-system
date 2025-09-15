"""
NLP Processor Module
===================

Handles text processing, cleaning, and command mapping.
Removes fillers, normalizes text, and maps intents to short commands.
"""

import re
import string
from typing import Optional, Dict, List

class NLPProcessor:
    """Handles natural language processing for command extraction."""
    
    def __init__(self):
        """Initialize the NLP processor."""
        self.confidence_threshold = 0.5
        
        # Common filler words to remove
        self.filler_words = {
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'i mean', 'sort of',
            'kind of', 'well', 'so', 'actually', 'basically', 'literally',
            'right', 'okay', 'ok', 'yeah', 'yes', 'yep', 'sure', 'uhm', 'hmm'
        }
        
        # Command mapping patterns (intent -> command)
        self.command_patterns = {
            # Movement commands
            r'\b(move|go|walk|run|drive)\s+(forward|ahead|front)\b': 'move forward',
            r'\b(move|go|walk|run|drive)\s+(backward|back|backwards)\b': 'move back',
            r'\b(turn|rotate|spin)\s+(left|port)\b': 'turn left',
            r'\b(turn|rotate|spin)\s+(right|starboard)\b': 'turn right',
            r'\b(stop|halt|brake|pause)\b': 'stop',
            
            # Navigation commands
            r'\b(go|move|navigate)\s+to\s+(home|base|start)\b': 'go home',
            r'\b(return|go back)\s+(home|base)?\b': 'go home',
            
            # System commands
            r'\b(start|begin|initialize|power on)\b': 'start',
            r'\b(shutdown|power off|turn off|quit|exit)\b': 'shutdown',
            r'\b(restart|reboot|reset)\b': 'restart',
            
            # Application commands
            r'\b(open|launch|start)\s+(main|application|app|program)\b': 'open main',
            r'\b(close|exit|quit)\s+(main|application|app|program)\b': 'close main',
            r'\b(minimize|hide)\b': 'minimize',
            r'\b(maximize|show|expand)\b': 'maximize',
            
            # Robot-specific commands
            r'\b(pick up|grab|take|get)\b': 'pick up',
            r'\b(put down|drop|place|set down)\b': 'put down',
            r'\b(lift|raise|elevate)\b': 'lift',
            r'\b(lower|drop|descend)\b': 'lower',
            
            # Speed/mode commands
            r'\b(speed up|faster|accelerate)\b': 'speed up',
            r'\b(slow down|slower|decelerate)\b': 'slow down',
            r'\b(normal speed|regular speed)\b': 'normal speed',
            
            # Status commands
            r'\b(status|state|condition|how are you)\b': 'status',
            r'\b(help|assist|what can you do)\b': 'help',
            
            # Simple directional commands
            r'\b(forward|ahead|front)\b': 'forward',
            r'\b(backward|back|backwards)\b': 'back', 
            r'\b(left|port)\b': 'left',
            r'\b(right|starboard)\b': 'right',
            r'\b(up|upward)\b': 'up',
            r'\b(down|downward)\b': 'down',
        }
        
        # Emergency/priority commands (highest priority)
        self.emergency_patterns = {
            r'\b(emergency stop|e-?stop|abort|danger)\b': 'emergency stop',
            r'\b(help|emergency|urgent)\b': 'emergency',
        }
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize input text.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation except apostrophes (for contractions)
        text = re.sub(r"[^\w\s']", '', text)
        
        # Handle contractions
        contractions = {
            "can't": "cannot",
            "won't": "will not",
            "n't": " not",
            "'ll": " will",
            "'re": " are",
            "'ve": " have",
            "'d": " would",
            "'m": " am"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        # Remove filler words
        words = text.split()
        cleaned_words = []
        
        i = 0
        while i < len(words):
            word = words[i]
            
            # Check for multi-word filler phrases
            if i < len(words) - 1:
                two_word_phrase = f"{word} {words[i + 1]}"
                if two_word_phrase in self.filler_words:
                    i += 2  # Skip both words
                    continue
                    
            # Check single word fillers (but keep important directional words)
            important_words = {'right', 'left', 'forward', 'back', 'up', 'down', 'turn', 'move', 'go', 'stop'}
            if word not in self.filler_words or word in important_words:
                cleaned_words.append(word)
                
            i += 1
        
        return ' '.join(cleaned_words)
        
    def extract_command(self, text: str) -> Optional[str]:
        """
        Extract command from cleaned text using pattern matching.
        
        Args:
            text: Cleaned input text
            
        Returns:
            Extracted command or None if no match
        """
        if not text:
            return None
            
        # First check emergency patterns (highest priority)
        for pattern, command in self.emergency_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return command
                
        # Then check regular command patterns
        for pattern, command in self.command_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return command
                
        # If no pattern matches, try to extract key action words
        action_words = {
            'move', 'go', 'turn', 'stop', 'start', 'open', 'close', 
            'forward', 'back', 'left', 'right', 'up', 'down'
        }
        
        words = text.split()
        for word in words:
            if word in action_words:
                return word
                
        return None
        
    def process_text(self, text: str) -> Optional[str]:
        """
        Main processing function: clean text and extract command.
        
        Args:
            text: Raw input text
            
        Returns:
            Processed command or None if no command found
        """
        if not text or not text.strip():
            return None
            
        print(f"Processing text: '{text}'")
        
        # Clean the text
        cleaned_text = self.clean_text(text)
        print(f"Cleaned text: '{cleaned_text}'")
        
        if not cleaned_text:
            return None
            
        # Extract command
        command = self.extract_command(cleaned_text)
        print(f"Extracted command: '{command}'")
        
        return command
        
    def get_command_suggestions(self) -> List[str]:
        """
        Get a list of available commands for help/reference.
        
        Returns:
            List of available commands
        """
        commands = set()
        
        # Extract commands from patterns
        for command in self.command_patterns.values():
            commands.add(command)
            
        for command in self.emergency_patterns.values():
            commands.add(command)
            
        return sorted(list(commands))
        
    def set_confidence_threshold(self, threshold: float):
        """
        Set the confidence threshold for command extraction.
        
        Args:
            threshold: Confidence threshold (0.0 to 1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        
    def add_custom_command(self, pattern: str, command: str):
        """
        Add a custom command pattern.
        
        Args:
            pattern: Regular expression pattern
            command: Command to map to
        """
        self.command_patterns[pattern] = command