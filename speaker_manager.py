# Speaker Manager - Complete Final Version
# Manages speaker profiles

import json
import os
import uuid
from datetime import datetime


class SpeakerManager:
    """Manages speaker profiles for multi-speaker recognition"""

    def __init__(self, speakers_file="speakers.json"):
        """Initialize speaker manager"""
        self.speakers_file = speakers_file
        self.speakers = self._load_speakers()

    def _load_speakers(self):
        """Load speakers from JSON file"""
        if os.path.exists(self.speakers_file):
            try:
                with open(self.speakers_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading speakers: {e}")
                return {}
        return {}

    def _save_speakers(self):
        """Save speakers to JSON file"""
        try:
            with open(self.speakers_file, 'w', encoding='utf-8') as f:
                json.dump(self.speakers, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving speakers: {e}")

    def add_speaker(self, name):
        """
        Add new speaker

        Args:
            name: Speaker name

        Returns:
            Generated speaker ID
        """
        speaker_id = str(uuid.uuid4())[:8]

        self.speakers[speaker_id] = {
            "name": name,
            "created_at": datetime.now().isoformat()
        }

        self._save_speakers()
        return speaker_id

    def remove_speaker(self, speaker_id):
        """Remove speaker"""
        if speaker_id in self.speakers:
            del self.speakers[speaker_id]
            self._save_speakers()

    def get_all_speakers(self):
        """Get all speakers"""
        return self.speakers

    def get_speaker_name(self, speaker_id):
        """Get speaker name by ID"""
        return self.speakers.get(speaker_id, {}).get("name", "Unknown")