# =====================================================================
# 说话人管理模块 - Speaker Manager Module
# =====================================================================
# 功能：管理说话人档案的创建、删除和持久化存储
# 作者：NTU EEE MSc Group 2025
# 说明：支持多说话人识别，每个说话人有唯一UUID标识
# =====================================================================

import json
import os
import uuid
from datetime import datetime


class SpeakerManager:
    """
    说话人管理器类
    
    职责：
    1. 加载和保存说话人档案（speakers.json）
    2. 添加、删除说话人
    3. 查询说话人信息
    4. 为说话人生成唯一ID
    
    数据结构：
    {
        "说话人ID(UUID)": {
            "name": "说话人名称",
            "created_at": "创建时间"
        }
    }
    
    设计模式：单例模式（每个应用实例一个管理器）
    """

    def __init__(self, speakers_file="speakers.json"):
        """
        初始化说话人管理器
        
        参数说明：
            speakers_file: JSON文件路径，存储所有说话人档案
        
        【关键】初始化流程：
        1. 使用绝对路径确保Windows兼容性
        2. 从JSON文件加载已有说话人
        3. 若文件不存在，创建空说话人字典
        """
        # 【文件路径】使用绝对路径
        self.speakers_file = os.path.abspath(speakers_file)
        self.speakers = self._load_speakers()

    def _load_speakers(self):
        """
        从JSON文件加载说话人档案
        
        返回值：
            说话人字典，格式见类文档说明
        
        【关键】加载策略：
        1. 文件存在：解析JSON并返回
        2. 文件不存在：返回空字典
        3. 解析失败：记录错误，返回空字典
        
        【数据流】磁盘文件 → JSON解析 → Python字典
        """
        if os.path.exists(self.speakers_file):
            try:
                # 【编码】强制UTF-8编码
                with open(self.speakers_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载说话人文件错误: {e}")
                return {}
        return {}

    def _save_speakers(self):
        """
        保存说话人档案到JSON文件
        
        【关键】保存策略：
        1. 格式化输出（indent=2）便于检查
        2. 支持中文字符（ensure_ascii=False）
        3. 强制UTF-8编码
        4. 即时写入磁盘
        
        【数据流】Python字典 → JSON序列化 → 磁盘文件
        """
        try:
            # 【编码】强制UTF-8
            with open(self.speakers_file, 'w', encoding='utf-8') as f:
                json.dump(self.speakers, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存说话人文件错误: {e}")

    def add_speaker(self, name):
        """
        添加新说话人档案
        
        参数说明：
            name: 说话人名称（用户定义，可重复）
        
        返回值：
            生成的说话人ID（UUID的前8位）
        
        【关键】创建流程：
        1. 生成UUID确保全局唯一性
        2. 截取前8位作为简化ID显示
        3. 记录创建时间戳（ISO 8601格式）
        4. 即时保存到磁盘
        
        【数据流】用户输入名称 → 生成UUID → 创建档案 → 保存JSON
        """
        # 【关键】生成唯一ID（UUID前8位）
        speaker_id = str(uuid.uuid4())[:8]

        # 创建说话人档案
        self.speakers[speaker_id] = {
            "name": name,
            "created_at": datetime.now().isoformat()
        }

        # 即时保存
        self._save_speakers()
        return speaker_id

    def remove_speaker(self, speaker_id):
        """
        删除说话人档案
        
        参数说明：
            speaker_id: 要删除的说话人ID
        
        【数据流】删除操作 → 保存JSON
        """
        if speaker_id in self.speakers:
            del self.speakers[speaker_id]
            self._save_speakers()

    def get_all_speakers(self):
        """
        获取所有说话人档案
        
        返回值：
            说话人字典，格式见类文档说明
        """
        return self.speakers

    def get_speaker_name(self, speaker_id):
        """
        根据ID获取说话人名称
        
        参数说明：
            speaker_id: 说话人ID
        
        返回值：
            说话人名称，不存在返回"Unknown"
        """
        return self.speakers.get(speaker_id, {}).get("name", "Unknown")