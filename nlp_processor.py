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
        
        # Command mapping patterns (intent -> command) - Updated per requirements
        self.command_patterns = {
            # Main application commands
            r'\b(open|launch|start)\s+(main)\b': 'open main',
            r'\b(open|launch|start)\s+(lamp)\b': 'open lamp',
            r'\b(open|launch|start)\s+(robot\s+cell)\b': 'open robot cell',
            r'\b(open|launch|start)\s+(robot)\b': 'open robot',
            
            # Numbered open commands
            r'\b(open|launch|start)\s+(1|one)\b': 'open 1',
            r'\b(open|launch|start)\s+(2|two)\b': 'open 2',
            
            # System commands
            r'\b(alarm|alert)\b': 'alarm',
            r'\b(open|launch|start)\s+(train)\b': 'open train',
            r'\b(open|launch|start)\s+(report)\b': 'open report',
            r'\b(open|launch|start)\s+(record)\b': 'open record',
            
            # User management commands
            r'\b(open|launch|start)\s+(user\s+admin)\b': 'open user admin',
            r'\b(open|launch|start)\s+(user\s+logging)\b': 'open user logging',
            r'\b(open|launch|start)\s+(user\s+log)\b': 'open user log',
            
            # Camera commands (open)
            r'\b(open|launch|start)\s+(camera\s+1|camera\s+one)\b': 'open camera 1',
            r'\b(open|launch|start)\s+(camera\s+2|camera\s+two)\b': 'open camera 2',
            r'\b(open|launch|start)\s+(camera\s+3|camera\s+three)\b': 'open camera 3',
            r'\b(open|launch|start)\s+(camera\s+4|camera\s+four)\b': 'open camera 4',
            
            # Camera commands (close)
            r'\b(close|shut|stop)\s+(camera\s+1|camera\s+one)\b': 'close camera 1',
            r'\b(close|shut|stop)\s+(camera\s+2|camera\s+two)\b': 'close camera 2',
            r'\b(close|shut|stop)\s+(camera\s+3|camera\s+three)\b': 'close camera 3',
            r'\b(close|shut|stop)\s+(camera\s+4|camera\s+four)\b': 'close camera 4',
            
            # Template commands (A-F)
            r'\b(template|temp)\s+(a|alpha)\b': 'template A',
            r'\b(template|temp)\s+(b|beta)\b': 'template B',
            r'\b(template|temp)\s+(c|charlie)\b': 'template C',
            r'\b(template|temp)\s+(d|delta)\b': 'template D',
            r'\b(template|temp)\s+(e|echo)\b': 'template E',
            r'\b(template|temp)\s+(f|foxtrot)\b': 'template F',
            
            # Template commands (7-10)
            r'\b(template|temp)\s+(7|seven)\b': 'template 7',
            r'\b(template|temp)\s+(8|eight)\b': 'template 8',
            r'\b(template|temp)\s+(9|nine)\b': 'template 9',
            r'\b(template|temp)\s+(10|ten)\b': 'template 10',
        }
        
        # Emergency/priority commands (highest priority)
        self.emergency_patterns = {
            r'\b(emergency stop|e-?stop|abort|danger)\b': 'emergency stop',
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