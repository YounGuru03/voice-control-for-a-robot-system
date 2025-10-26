# Command Manager - Complete Final Version
# Manages command registration, training, and weights

import json
import os
from datetime import datetime


class CommandManager:
    """Manages voice commands and their training data"""

    def __init__(self, commands_file="commands.json"):
        """Initialize command manager"""
        self.commands_file = commands_file
        self.commands = self._load_commands()

    def _load_commands(self):
        """Load commands from JSON file"""
        if os.path.exists(self.commands_file):
            try:
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading commands: {e}")
                return {}
        return {}

    def _save_commands(self):
        """Save commands to JSON file"""
        try:
            with open(self.commands_file, 'w', encoding='utf-8') as f:
                json.dump(self.commands, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving commands: {e}")

    def add_command(self, command_text):
        """
        Add new command

        Args:
            command_text: Command text

        Returns:
            True if added, False if already exists
        """
        command_text = command_text.strip()

        if command_text in self.commands:
            return False

        self.commands[command_text] = {
            "text": command_text,
            "training_count": 0,
            "weight": 1.0,
            "created_at": datetime.now().isoformat(),
            "speaker_training": {}
        }

        self._save_commands()
        return True

    def remove_command(self, command_text):
        """Remove command"""
        if command_text in self.commands:
            del self.commands[command_text]
            self._save_commands()

    def get_all_commands(self):
        """Get list of all command texts"""
        return list(self.commands.keys())

    def get_command_info(self, command_text):
        """Get command information"""
        return self.commands.get(command_text, {})

    def add_training(self, command_text, speaker_id=None):
        """
        Record a training session

        Args:
            command_text: Command being trained
            speaker_id: Optional speaker ID
        """
        if command_text not in self.commands:
            return

        # Increment training count
        self.commands[command_text]["training_count"] += 1

        # Update weight (max 2.0x)
        count = self.commands[command_text]["training_count"]
        self.commands[command_text]["weight"] = min(1.0 + count * 0.1, 2.0)

        # Record speaker-specific training
        if speaker_id:
            speaker_dict = self.commands[command_text]["speaker_training"]
            speaker_dict[speaker_id] = speaker_dict.get(speaker_id, 0) + 1

        self._save_commands()

    def get_boost_list(self):
        """
        Get phrase list for boosting, sorted by weight

        Returns:
            List of command texts sorted by weight (descending)
        """
        sorted_commands = sorted(
            self.commands.values(),
            key=lambda x: x["weight"],
            reverse=True
        )

        return [cmd["text"] for cmd in sorted_commands]

    def get_trained_speaker(self, command_text):
        """
        Get speaker with most training for this command

        Args:
            command_text: Command text

        Returns:
            Speaker ID or None
        """
        if command_text not in self.commands:
            return None

        speaker_training = self.commands[command_text]["speaker_training"]

        if not speaker_training:
            return None

        # Return speaker with most training
        return max(speaker_training, key=speaker_training.get)