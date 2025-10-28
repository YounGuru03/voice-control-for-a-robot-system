# =====================================================================
# 指令管理模块 - Command Manager Module
# =====================================================================
# 功能：管理语音指令的注册、训练、权重计算和持久化存储
# 作者：NTU EEE MSc Group 2025
# 说明：使用JSON文件存储指令数据，支持多说话人训练记录
# =====================================================================

import json
import os
from datetime import datetime


class CommandManager:
    """
    指令管理器类
    
    职责：
    1. 加载和保存指令数据（commands.json）
    2. 添加、删除指令
    3. 记录指令训练次数和计算权重
    4. 管理说话人与指令的训练关联
    5. 生成用于Phrase Boosting的指令列表
    
    数据结构：
    {
        "指令文本": {
            "text": "指令文本",
            "training_count": 训练次数,
            "weight": 权重倍数(1.0-2.0),
            "created_at": "创建时间",
            "speaker_training": {
                "说话人ID": 该说话人的训练次数
            }
        }
    }
    
    设计模式：单例模式（每个应用实例一个管理器）
    """

    def __init__(self, commands_file="commands.json"):
        """
        初始化指令管理器
        
        参数说明：
            commands_file: JSON文件路径，存储所有指令数据
        
        【关键】初始化流程：
        1. 使用绝对路径确保Windows兼容性
        2. 从JSON文件加载已有指令
        3. 若文件不存在，创建空指令字典
        """
        # 【文件路径】使用绝对路径，确保Windows兼容
        self.commands_file = os.path.abspath(commands_file)
        self.commands = self._load_commands()

    def _load_commands(self):
        """
        从JSON文件加载指令数据
        
        返回值：
            指令字典，格式见类文档说明
        
        【关键】加载策略：
        1. 文件存在：解析JSON并返回
        2. 文件不存在：返回空字典
        3. 解析失败：记录错误，返回空字典
        
        【数据流】磁盘文件 → JSON解析 → Python字典
        """
        if os.path.exists(self.commands_file):
            try:
                # 【编码】强制使用UTF-8编码，确保中文支持
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载指令文件错误: {e}")
                return {}
        return {}

    def _save_commands(self):
        """
        保存指令数据到JSON文件
        
        【关键】保存策略：
        1. 使用indent=2格式化输出，便于人工检查
        2. ensure_ascii=False支持中文字符直接存储
        3. 强制UTF-8编码
        4. 即时写入，确保数据持久化
        
        【数据流】Python字典 → JSON序列化 → 磁盘文件
        """
        try:
            # 【编码】强制UTF-8，支持中文
            with open(self.commands_file, 'w', encoding='utf-8') as f:
                json.dump(self.commands, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存指令文件错误: {e}")

    def add_command(self, command_text):
        """
        添加新指令到指令库
        
        参数说明：
            command_text: 指令文本，如"open door"
        
        返回值：
            True: 添加成功
            False: 指令已存在
        
        【关键】新指令初始化：
        1. text: 指令文本（冗余存储，便于容灾）
        2. training_count: 训练次数初始为0
        3. weight: 权重初始为1.0（标准权重）
        4. created_at: 记录创建时间戳（ISO 8601格式）
        5. speaker_training: 空字典，后续记录各说话人训练
        
        【数据流】用户输入 → 创建指令对象 → 保存到JSON
        """
        command_text = command_text.strip()

        # 检查指令是否已存在
        if command_text in self.commands:
            return False

        # 【关键】创建新指令数据结构
        self.commands[command_text] = {
            "text": command_text,
            "training_count": 0,
            "weight": 1.0,
            "created_at": datetime.now().isoformat(),
            "speaker_training": {}  # 说话人训练记录
        }

        # 【关键】即时保存到磁盘
        self._save_commands()
        return True

    def remove_command(self, command_text):
        """
        从指令库删除指令
        
        参数说明：
            command_text: 要删除的指令文本
        
        【数据流】删除操作 → 保存到JSON
        """
        if command_text in self.commands:
            del self.commands[command_text]
            self._save_commands()

    def get_all_commands(self):
        """
        获取所有已注册指令的文本列表
        
        返回值：
            指令文本列表，如["open door", "close window"]
        
        【数据流】指令字典 → 提取keys → 列表
        """
        return list(self.commands.keys())

    def get_command_info(self, command_text):
        """
        获取指定指令的完整信息
        
        参数说明：
            command_text: 指令文本
        
        返回值：
            指令信息字典，不存在返回空字典
        """
        return self.commands.get(command_text, {})

    def add_training(self, command_text, speaker_id=None):
        """
        记录一次指令训练
        
        参数说明：
            command_text: 被训练的指令文本
            speaker_id: 可选，说话人ID（用于多说话人识别）
        
        【关键】训练记录流程：
        1. 增加指令的总训练次数
        2. 根据训练次数更新权重（最高2.0倍）
        3. 如果指定了说话人，记录该说话人的训练次数
        4. 即时保存到磁盘
        
        【关键】权重计算公式：
        weight = min(1.0 + training_count * 0.1, 2.0)
        - 每训练1次，权重增加0.1
        - 训练10次达到最大权重2.0
        - 高权重指令在Phrase Boosting中优先级更高
        
        【数据流】训练操作 → 更新count和weight → 保存JSON
        """
        if command_text not in self.commands:
            return

        # 【关键】增加训练次数
        self.commands[command_text]["training_count"] += 1

        # 【关键】更新权重（上限2.0倍）
        count = self.commands[command_text]["training_count"]
        self.commands[command_text]["weight"] = min(1.0 + count * 0.1, 2.0)

        # 【关键】记录说话人特定的训练次数
        if speaker_id:
            speaker_dict = self.commands[command_text]["speaker_training"]
            speaker_dict[speaker_id] = speaker_dict.get(speaker_id, 0) + 1

        # 即时保存
        self._save_commands()

    def get_boost_list(self):
        """
        获取用于Phrase Boosting的指令列表（按权重排序）
        
        返回值：
            指令文本列表，按权重从高到低排序
        
        【关键】排序策略：
        1. 按weight字段降序排序
        2. 高权重指令排在前面
        3. Whisper优先识别前面的短语
        4. 提高已训练指令的识别准确度
        
        示例：
        ["open door"(2.0x), "close window"(1.5x), "turn on light"(1.0x)]
        
        【数据流】指令字典 → 按weight排序 → 提取text → 列表
        """
        # 【关键】按权重降序排序
        sorted_commands = sorted(
            self.commands.values(),
            key=lambda x: x["weight"],
            reverse=True
        )

        # 返回指令文本列表
        return [cmd["text"] for cmd in sorted_commands]

    def get_trained_speaker(self, command_text):
        """
        获取某指令训练次数最多的说话人（用于自动识别）
        
        参数说明：
            command_text: 指令文本
        
        返回值：
            说话人ID，无训练记录返回None
        
        【关键】识别策略：
        1. 查询该指令的speaker_training字典
        2. 找出训练次数最多的说话人
        3. 用于Auto Speaker Mode自动识别
        
        示例：
        指令"open door"的speaker_training:
        {"speaker1": 5, "speaker2": 2}
        → 返回"speaker1"（训练5次最多）
        
        【数据流】指令 → speaker_training → max训练次数 → 说话人ID
        """
        if command_text not in self.commands:
            return None

        speaker_training = self.commands[command_text]["speaker_training"]

        if not speaker_training:
            return None

        # 【关键】返回训练次数最多的说话人
        return max(speaker_training, key=speaker_training.get)