# ============================================================================
# command_hotword_manager.py
# ============================================================================

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import re

class CommandHotwordManager:
    """整合的命令与热词管理器"""
    
    def __init__(self, data_file="commands_hotwords.json"):
        """初始化管理器"""
        self.data_file = os.path.abspath(data_file)
        self.data = self._load()
        print(f"✅ CommandHotwordManager loaded: {len(self.data['commands'])} commands")
    
    def _load(self) -> Dict[str, Any]:
        """加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Load error: {e}")
        
        return {
            "commands": {},
            "global_settings": {
                "base_weight": 1.0,
                "max_weight": 3.0,
                "auto_boost": True,
                "boost_increment": 0.2
            }
        }
    
    def _save(self) -> bool:
        """保存数据"""
        try:
            temp_file = self.data_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
            os.rename(temp_file, self.data_file)
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False
    
    def add_command(self, text: str) -> bool:
        """添加命令"""
        text = text.strip()
        if not text or text in self.data["commands"]:
            return False
        
        self.data["commands"][text] = {
            "text": text,
            "weight": self.data["global_settings"]["base_weight"],
            "usage_count": 0,
            "success_count": 0,
            "training_count": 0,
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        
        return self._save()
    
    def remove_command(self, text: str) -> bool:
        """删除命令"""
        if text in self.data["commands"]:
            del self.data["commands"][text]
            return self._save()
        return False
    
    def get_all_commands(self) -> List[str]:
        """获取所有命令"""
        return list(self.data["commands"].keys())
    
    def record_usage(self, text: str, success: bool = True) -> None:
        """记录使用统计"""
        if text not in self.data["commands"]:
            return
        
        cmd_data = self.data["commands"][text]
        cmd_data["usage_count"] += 1
        cmd_data["last_used"] = datetime.now().isoformat()
        
        if success:
            cmd_data["success_count"] += 1
            
        # 自动权重提升
        if self.data["global_settings"]["auto_boost"]:
            max_weight = self.data["global_settings"]["max_weight"]
            increment = self.data["global_settings"]["boost_increment"]
            cmd_data["weight"] = min(cmd_data["weight"] + increment, max_weight)
        
        self._save()
    
    def train_command(self, text: str) -> float:
        """训练命令"""
        if text not in self.data["commands"]:
            return 0.0
        
        cmd_data = self.data["commands"][text]
        cmd_data["training_count"] += 1
        
        # 基于训练次数计算权重
        max_weight = self.data["global_settings"]["max_weight"]
        base_weight = self.data["global_settings"]["base_weight"]
        new_weight = min(base_weight + cmd_data["training_count"] * 0.3, max_weight)
        cmd_data["weight"] = new_weight
        
        self._save()
        return new_weight
    
    def get_boost_phrases(self, max_count: int = 15) -> List[str]:
        """获取权重排序的短语列表"""
        if not self.data["commands"]:
            return []
        
        # 按权重和使用频率排序
        sorted_commands = sorted(
            self.data["commands"].items(),
            key=lambda x: (x[1]["weight"], x[1]["usage_count"]),
            reverse=True
        )
        
        return [cmd[0] for cmd in sorted_commands[:max_count]]
    
    def get_command_info(self, text: str) -> Dict[str, Any]:
        """获取命令详细信息"""
        return self.data["commands"].get(text, {})
    
    def get_training_count(self, text: str) -> int:
        """获取训练次数"""
        return self.get_command_info(text).get("training_count", 0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.data["commands"]:
            return {"total": 0, "most_used": [], "highest_weight": []}
        
        by_usage = sorted(
            self.data["commands"].items(),
            key=lambda x: x[1]["usage_count"],
            reverse=True
        )
        
        by_weight = sorted(
            self.data["commands"].items(),
            key=lambda x: x[1]["weight"],
            reverse=True
        )
        
        return {
            "total": len(self.data["commands"]),
            "most_used": [(cmd, data["usage_count"]) for cmd, data in by_usage[:5]],
            "highest_weight": [(cmd, data["weight"]) for cmd, data in by_weight[:5]]
        }