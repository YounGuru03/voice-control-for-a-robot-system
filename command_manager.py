# ============================================================================
# command_manager.py
# ============================================================================

import json
import os
from datetime import datetime

class CommandManager:
    """Command Manager - Persistent storage and weight calculation"""
    
    def __init__(self, commands_file="commands.json"):
        """Initialize command manager"""
        self.commands_file = os.path.abspath(commands_file)
        self.commands = self._load()
        print(f"✅ CommandManager loaded: {len(self.commands)} commands")
    
    def _load(self):
        """Load from JSON file"""
        if os.path.exists(self.commands_file):
            try:
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Load error: {e}")
        return {}
    
    def _save(self):
        """Save to JSON file"""
        try:
            temp_file = self.commands_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.commands, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(self.commands_file):
                os.remove(self.commands_file)
            os.rename(temp_file, self.commands_file)
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def add(self, cmd_text):
        """Add new command"""
        cmd_text = cmd_text.strip()
        if not cmd_text or cmd_text in self.commands:
            return False
        
        self.commands[cmd_text] = {
            "text": cmd_text,
            "training_count": 0,
            "weight": 1.0,
            "created_at": datetime.now().isoformat()
        }
        
        return self._save()
    
    def remove(self, cmd_text):
        """Remove command"""
        if cmd_text in self.commands:
            del self.commands[cmd_text]
            return self._save()
        return False
    
    def get_all(self):
        """Get all command texts"""
        return list(self.commands.keys())
    
    def get_info(self, cmd_text):
        """Get command details"""
        return self.commands.get(cmd_text, {})
    
    def train(self, cmd_text):
        """
        Record training session
        Weight calculation: min(1.0 + training_count * 0.1, 2.0)
        Higher weight = higher priority in Phrase Boosting
        """
        if cmd_text not in self.commands:
            return None
        
        cmd = self.commands[cmd_text]
        cmd["training_count"] += 1
        cmd["weight"] = min(1.0 + cmd["training_count"] * 0.1, 2.0)
        
        self._save()
        return cmd["weight"]
    
    def increment_training(self, cmd_text):
        """Increment training count (alias for train method)"""
        return self.train(cmd_text)
    
    def get_training_count(self, cmd_text):
        """Get training count for a command"""
        cmd_info = self.get_info(cmd_text)
        return cmd_info.get("training_count", 0)
    
    def get_boost_list(self):
        """Get weight-sorted command list for Phrase Boosting"""
        sorted_cmds = sorted(
            self.commands.values(),
            key=lambda x: x["weight"],
            reverse=True
        )
        
        return [cmd["text"] for cmd in sorted_cmds[:10]]