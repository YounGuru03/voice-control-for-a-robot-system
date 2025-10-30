# ============================================================================
# hotword_manager.py
# ============================================================================

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re

class HotwordManager:
    """Advanced Hotword Manager for enhanced speech recognition accuracy"""
    
    def __init__(self, hotwords_file="hotwords.json"):
        """Initialize hotword manager"""
        self.hotwords_file = os.path.abspath(hotwords_file)
        self.hotwords = self._load()
        self.context_history = []
        self.max_history = 10
        print(f"✅ HotwordManager loaded: {len(self.hotwords.get('hotwords', {}))} hotwords")
    
    def _load(self) -> Dict:
        """Load hotwords from JSON file"""
        if os.path.exists(self.hotwords_file):
            try:
                with open(self.hotwords_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Load error: {e}")
        
        return {
            "global_settings": {
                "base_weight": 1.0,
                "max_weight": 5.0,
                "context_boost": 0.5,
                "decay_factor": 0.95
            },
            "hotwords": {},
            "categories": {},
            "context_rules": {}
        }
    
    def _save(self) -> bool:
        """Save hotwords to JSON file"""
        try:
            temp_file = self.hotwords_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.hotwords, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(self.hotwords_file):
                os.remove(self.hotwords_file)
            os.rename(temp_file, self.hotwords_file)
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def add_hotword(self, word: str, category: str = "general", 
                   initial_weight: float = 2.0, aliases: List[str] = None) -> bool:
        """Add new hotword with specified parameters"""
        word = word.strip().lower()
        if not word:
            return False
        
        if word in self.hotwords["hotwords"]:
            print(f"⚠️ Hotword '{word}' already exists")
            return False
        
        self.hotwords["hotwords"][word] = {
            "text": word,
            "category": category,
            "weight": min(initial_weight, self.hotwords["global_settings"]["max_weight"]),
            "base_weight": initial_weight,
            "aliases": aliases or [],
            "usage_count": 0,
            "success_count": 0,
            "last_used": None,
            "created_at": datetime.now().isoformat(),
            "context_boost_active": False
        }
        
        if category not in self.hotwords["categories"]:
            self.hotwords["categories"][category] = []
        self.hotwords["categories"][category].append(word)
        
        self._save()
        print(f"✅ Added hotword: '{word}' (category: {category}, weight: {initial_weight})")
        return True
    
    def remove_hotword(self, word: str) -> bool:
        """Remove hotword"""
        word = word.strip().lower()
        if word not in self.hotwords["hotwords"]:
            return False
        
        category = self.hotwords["hotwords"][word]["category"]
        if category in self.hotwords["categories"]:
            if word in self.hotwords["categories"][category]:
                self.hotwords["categories"][category].remove(word)
        
        del self.hotwords["hotwords"][word]
        self._save()
        print(f"✅ Removed hotword: '{word}'")
        return True
    
    def boost_hotword(self, word: str, boost_amount: float = 0.5) -> bool:
        """Temporarily boost hotword weight"""
        word = word.strip().lower()
        if word not in self.hotwords["hotwords"]:
            return False
        
        hotword_data = self.hotwords["hotwords"][word]
        current_weight = hotword_data["weight"]
        max_weight = self.hotwords["global_settings"]["max_weight"]
        
        new_weight = min(current_weight + boost_amount, max_weight)
        hotword_data["weight"] = new_weight
        hotword_data["context_boost_active"] = True
        
        self._save()
        print(f"🚀 Boosted '{word}': {current_weight} → {new_weight}")
        return True
    
    def record_usage(self, word: str, success: bool = True) -> None:
        """Record hotword usage statistics"""
        word = word.strip().lower()
        if word not in self.hotwords["hotwords"]:
            return
        
        hotword_data = self.hotwords["hotwords"][word]
        hotword_data["usage_count"] += 1
        hotword_data["last_used"] = datetime.now().isoformat()
        
        if success:
            hotword_data["success_count"] += 1
            current_weight = hotword_data["weight"]
            max_weight = self.hotwords["global_settings"]["max_weight"]
            hotword_data["weight"] = min(current_weight + 0.05, max_weight)
        else:
            current_weight = hotword_data["weight"]
            max_weight = self.hotwords["global_settings"]["max_weight"]
            hotword_data["weight"] = min(current_weight + 0.1, max_weight)
        
        self._save()
    
    def get_boost_phrases(self, max_count: int = 20) -> List[str]:
        """Get prioritized list of hotwords for Whisper's initial_prompt"""
        if not self.hotwords["hotwords"]:
            return []
        
        sorted_hotwords = sorted(
            self.hotwords["hotwords"].items(),
            key=lambda x: (
                x[1]["weight"],
                x[1]["usage_count"],
                x[1]["last_used"] or "1900-01-01"
            ),
            reverse=True
        )
        
        boost_phrases = []
        for word, data in sorted_hotwords[:max_count]:
            boost_phrases.append(data["text"])
            for alias in data["aliases"]:
                boost_phrases.append(alias)
                if len(boost_phrases) >= max_count:
                    break
            if len(boost_phrases) >= max_count:
                break
        
        return boost_phrases[:max_count]
    
    def apply_context_boost(self, recognized_text: str) -> None:
        """Apply context-aware boosting based on recognized text"""
        self.context_history.append(recognized_text.lower())
        if len(self.context_history) > self.max_history:
            self.context_history.pop(0)
        
        context_text = " ".join(self.context_history)
        
        for word, hotword_data in self.hotwords["hotwords"].items():
            category = hotword_data["category"]
            
            if category in context_text or word in context_text:
                self.boost_hotword(word, 0.3)
    
    def decay_weights(self) -> None:
        """Gradually decay hotword weights to prevent inflation"""
        decay_factor = self.hotwords["global_settings"]["decay_factor"]
        
        for word, hotword_data in self.hotwords["hotwords"].items():
            if hotword_data["context_boost_active"]:
                hotword_data["weight"] = hotword_data["base_weight"]
                hotword_data["context_boost_active"] = False
            else:
                base_weight = hotword_data["base_weight"]
                current_weight = hotword_data["weight"]
                
                if current_weight > base_weight:
                    new_weight = max(current_weight * decay_factor, base_weight)
                    hotword_data["weight"] = new_weight
        
        self._save()
    
    def get_statistics(self) -> Dict:
        """Get hotword usage statistics"""
        stats = {
            "total_hotwords": len(self.hotwords["hotwords"]),
            "categories": list(self.hotwords["categories"].keys()),
            "most_used": [],
            "highest_weight": [],
            "recent_additions": []
        }
        
        if not self.hotwords["hotwords"]:
            return stats
        
        by_usage = sorted(
            self.hotwords["hotwords"].items(),
            key=lambda x: x[1]["usage_count"],
            reverse=True
        )
        stats["most_used"] = [(word, data["usage_count"]) for word, data in by_usage[:5]]
        
        by_weight = sorted(
            self.hotwords["hotwords"].items(),
            key=lambda x: x[1]["weight"],
            reverse=True
        )
        stats["highest_weight"] = [(word, data["weight"]) for word, data in by_weight[:5]]
        
        by_creation = sorted(
            self.hotwords["hotwords"].items(),
            key=lambda x: x[1]["created_at"],
            reverse=True
        )
        stats["recent_additions"] = [word for word, _ in by_creation[:5]]
        
        return stats
    
    def get_all_hotwords(self) -> Dict:
        """Get all hotwords data"""
        return self.hotwords["hotwords"]