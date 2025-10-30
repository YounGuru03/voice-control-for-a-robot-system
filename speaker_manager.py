# ============================================================================
# speaker_manager.py
# ============================================================================

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class SpeakerManager:
    """说话人管理器"""
    
    def __init__(self, speakers_file="speakers.json"):
        """初始化说话人管理器"""
        self.speakers_file = os.path.abspath(speakers_file)
        self.speakers = self._load()
        print(f"✅ SpeakerManager loaded: {len(self.speakers)} speakers")
    
    def _load(self) -> Dict[str, Any]:
        """加载说话人数据"""
        if os.path.exists(self.speakers_file):
            try:
                with open(self.speakers_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Load error: {e}")
        return {}
    
    def _save(self) -> bool:
        """保存说话人数据"""
        try:
            temp_file = self.speakers_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.speakers, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(self.speakers_file):
                os.remove(self.speakers_file)
            os.rename(temp_file, self.speakers_file)
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def add(self, name: str) -> Optional[str]:
        """添加说话人"""
        name = name.strip()
        if not name:
            return None
        
        speaker_id = str(uuid.uuid4())[:8]
        self.speakers[speaker_id] = {
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        
        self._save()
        return speaker_id
    
    def remove(self, speaker_id: str) -> bool:
        """删除说话人"""
        if speaker_id in self.speakers:
            del self.speakers[speaker_id]
            return self._save()
        return False
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有说话人"""
        return self.speakers
    
    def get_name(self, speaker_id: str) -> str:
        """获取说话人名称"""
        return self.speakers.get(speaker_id, {}).get("name", "Unknown")