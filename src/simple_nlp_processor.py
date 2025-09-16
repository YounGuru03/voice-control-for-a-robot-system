"""
Simple NLP Processor
===================

Streamlined natural language processing for robot voice commands.
Focuses on essential command recognition with minimal memory usage.
"""

import re
from typing import Dict, List, Optional

class SimpleNLPProcessor:
    """Lightweight NLP processor for command extraction"""
    
    def __init__(self):
        """Initialize the NLP processor with command patterns"""
        
        # Define robot control commands in order of priority
        self.command_patterns = {
            # Emergency commands (highest priority)
            'emergency stop': [r'\b(emergency\s+stop|e-?stop|abort|stop\s+everything)\b'],
            'alarm': [r'\b(alarm|alert|warning)\b'],
            
            # Main application commands  
            'open main': [r'\b(open|launch|start)\s+(main)\b'],
            'open robot': [r'\b(open|launch|start)\s+(robot)\b'],
            'open robot cell': [r'\b(open|launch|start)\s+(robot\s+cell)\b'],
            'open lamp': [r'\b(open|launch|start)\s+(lamp)\b'],
            
            # Numbered commands
            'open 1': [r'\b(open|launch|start)\s+(1|one)\b'],
            'open 2': [r'\b(open|launch|start)\s+(2|two)\b'],
            
            # System commands
            'open train': [r'\b(open|launch|start)\s+(train)\b'],
            'open report': [r'\b(open|launch|start)\s+(report)\b'],  
            'open record': [r'\b(open|launch|start)\s+(record)\b'],
            
            # User management
            'open user admin': [r'\b(open|launch|start)\s+(user\s+admin)\b'],
            'open user logging': [r'\b(open|launch|start)\s+(user\s+logging)\b'],
            'open user log': [r'\b(open|launch|start)\s+(user\s+log)\b'],
            
            # Camera controls
            'open camera 1': [r'\b(open)\s+(camera\s+(1|one))\b'],
            'open camera 2': [r'\b(open)\s+(camera\s+(2|two))\b'], 
            'open camera 3': [r'\b(open)\s+(camera\s+(3|three))\b'],
            'open camera 4': [r'\b(open)\s+(camera\s+(4|four))\b'],
            
            'close camera 1': [r'\b(close)\s+(camera\s+(1|one))\b'],
            'close camera 2': [r'\b(close)\s+(camera\s+(2|two))\b'],
            'close camera 3': [r'\b(close)\s+(camera\s+(3|three))\b'], 
            'close camera 4': [r'\b(close)\s+(camera\s+(4|four))\b'],
            
            # Template commands
            'template A': [r'\b(template\s+(a|alpha))\b'],
            'template B': [r'\b(template\s+(b|beta|bravo))\b'],
            'template C': [r'\b(template\s+(c|charlie))\b'],
            'template D': [r'\b(template\s+(d|delta))\b'],
            'template E': [r'\b(template\s+(e|echo))\b'],
            'template F': [r'\b(template\s+(f|foxtrot))\b'],
            'template 7': [r'\b(template\s+(7|seven))\b'],
            'template 8': [r'\b(template\s+(8|eight))\b'],
            'template 9': [r'\b(template\s+(9|nine))\b'],
            'template 10': [r'\b(template\s+(10|ten))\b'],
        }
        
        # Words to remove for cleaner processing
        self.filler_words = {
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'well', 'so',
            'okay', 'ok', 'please', 'can you', 'could you', 'would you'
        }
    
    def clean_text(self, text: str) -> str:
        """
        Clean input text by removing noise and normalizing
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text
        """
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove punctuation at start/end
        text = text.strip('.,!?;:')
        
        # Remove common filler phrases
        for filler in ['um ', 'uh ', 'er ', 'ah ']:
            text = text.replace(filler, ' ')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_command(self, text: str) -> str:
        """
        Extract robot command from text
        
        Args:
            text: Input text to process
            
        Returns:
            Recognized command or "None" if no match
        """
        if not text or not isinstance(text, str):
            return "None"
        
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        if not cleaned_text:
            return "None"
        
        # Try to match command patterns (in order of priority)
        for command, patterns in self.command_patterns.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, cleaned_text, re.IGNORECASE):
                        return command
                except re.error:
                    continue  # Skip invalid regex patterns
        
        return "None"
    
    def process_text(self, text: str) -> str:
        """
        Process text and extract command (main entry point)
        
        Args:
            text: Input text to process
            
        Returns:
            Extracted command
        """
        return self.extract_command(text)
    
    def get_supported_commands(self) -> List[str]:
        """
        Get list of all supported commands
        
        Returns:
            List of supported command strings
        """
        return list(self.command_patterns.keys())
    
    def is_emergency_command(self, command: str) -> bool:
        """
        Check if a command is an emergency command
        
        Args:
            command: Command to check
            
        Returns:
            True if emergency command
        """
        emergency_commands = {'emergency stop', 'alarm'}
        return command in emergency_commands

# Create processor instance
def create_nlp_processor():
    """Create and return NLP processor instance"""
    return SimpleNLPProcessor()