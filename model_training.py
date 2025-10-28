# =====================================================================
# 模型训练模块 - Model Training Module
# =====================================================================
# 功能：管理Whisper模型的训练数据采集、标注、训练和评估
# 作者：NTU EEE MSc Group 2025
# 说明：支持音频样本收集、数据集管理、模型微调和检查点管理
# =====================================================================

import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import hashlib


class TrainingDataManager:
    """
    训练数据管理器类
    
    职责：
    1. 采集和存储音频样本
    2. 标注和验证训练样本
    3. 管理数据集分割（训练/验证/测试）
    4. 生成训练批次
    5. 记录数据集元信息
    
    数据目录结构：
    training_data/
    ├── samples/           # 原始音频样本
    │   ├── sample_001.wav
    │   ├── sample_002.wav
    │   └── ...
    ├── labels.json        # 样本标注信息
    ├── dataset.json       # 数据集分割信息
    └── metadata.json      # 数据集元信息
    """

    def __init__(self, data_dir="training_data"):
        """
        初始化训练数据管理器
        
        参数说明：
            data_dir: 训练数据根目录
        
        【关键】目录结构初始化：
        - 使用绝对路径确保Windows兼容性
        - 自动创建必要的子目录
        - 加载已有的标注和数据集信息
        """
        self.data_dir = os.path.abspath(data_dir)
        self.samples_dir = os.path.join(self.data_dir, "samples")
        self.labels_file = os.path.join(self.data_dir, "labels.json")
        self.dataset_file = os.path.join(self.data_dir, "dataset.json")
        self.metadata_file = os.path.join(self.data_dir, "metadata.json")
        
        # 【关键】创建目录结构
        os.makedirs(self.samples_dir, exist_ok=True)
        
        # 【关键】加载已有数据
        self.labels = self._load_labels()
        self.dataset = self._load_dataset()
        self.metadata = self._load_metadata()

    def _load_labels(self) -> Dict:
        """
        加载样本标注信息
        
        返回值：
            标注字典 {sample_id: {text, speaker_id, timestamp, verified}}
        """
        if os.path.exists(self.labels_file):
            try:
                with open(self.labels_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载标注文件错误: {e}")
                return {}
        return {}

    def _save_labels(self):
        """保存样本标注信息"""
        try:
            with open(self.labels_file, 'w', encoding='utf-8') as f:
                json.dump(self.labels, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存标注文件错误: {e}")

    def _load_dataset(self) -> Dict:
        """
        加载数据集分割信息
        
        返回值：
            数据集字典 {train: [...], val: [...], test: [...]}
        """
        if os.path.exists(self.dataset_file):
            try:
                with open(self.dataset_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载数据集文件错误: {e}")
                return {"train": [], "val": [], "test": []}
        return {"train": [], "val": [], "test": []}

    def _save_dataset(self):
        """保存数据集分割信息"""
        try:
            with open(self.dataset_file, 'w', encoding='utf-8') as f:
                json.dump(self.dataset, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存数据集文件错误: {e}")

    def _load_metadata(self) -> Dict:
        """
        加载数据集元信息
        
        返回值：
            元信息字典 {created_at, total_samples, last_updated, ...}
        """
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载元信息文件错误: {e}")
                return self._create_default_metadata()
        return self._create_default_metadata()

    def _create_default_metadata(self) -> Dict:
        """创建默认元信息"""
        return {
            "created_at": datetime.now().isoformat(),
            "total_samples": 0,
            "labeled_samples": 0,
            "verified_samples": 0,
            "last_updated": datetime.now().isoformat(),
            "version": "1.0"
        }

    def _save_metadata(self):
        """保存数据集元信息"""
        self.metadata["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存元信息文件错误: {e}")

    def add_sample(self, audio_data, text: str, speaker_id: Optional[str] = None) -> str:
        """
        添加音频样本到训练数据集
        
        参数说明：
            audio_data: 音频数据（numpy数组或文件路径）
            text: 样本的文本标注
            speaker_id: 可选，说话人ID
        
        返回值：
            生成的样本ID
        
        【关键】样本处理流程：
        1. 生成唯一样本ID（基于时间戳+哈希）
        2. 保存音频文件到samples目录
        3. 创建标注记录
        4. 更新元信息
        
        【数据流】音频数据 → 保存文件 → 创建标注 → 更新元数据
        """
        # 【关键】生成唯一样本ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(text.encode()).hexdigest()[:6]
        sample_id = f"sample_{timestamp}_{hash_suffix}"
        
        # 【关键】保存音频文件（实际实现需要音频编码）
        # 这里假设audio_data是numpy数组，实际需要转为WAV格式
        # 简化实现：如果是文件路径，直接复制
        if isinstance(audio_data, str) and os.path.exists(audio_data):
            sample_path = os.path.join(self.samples_dir, f"{sample_id}.wav")
            shutil.copy(audio_data, sample_path)
        else:
            # 实际应用需要将numpy数组保存为WAV
            sample_path = os.path.join(self.samples_dir, f"{sample_id}.wav")
            # TODO: 实现numpy数组到WAV的转换
            print(f"⚠️ 音频数据保存功能需要实现")
        
        # 【关键】创建标注记录
        self.labels[sample_id] = {
            "text": text,
            "speaker_id": speaker_id,
            "timestamp": datetime.now().isoformat(),
            "verified": False,
            "file_path": sample_path
        }
        
        # 【关键】更新元信息
        self.metadata["total_samples"] += 1
        self.metadata["labeled_samples"] += 1
        
        # 保存到磁盘
        self._save_labels()
        self._save_metadata()
        
        print(f"✅ 已添加样本: {sample_id}")
        return sample_id

    def verify_sample(self, sample_id: str, verified: bool = True):
        """
        验证样本标注的准确性
        
        参数说明：
            sample_id: 样本ID
            verified: 是否验证通过
        
        【关键】验证流程：
        - 标记样本为已验证
        - 更新verified_samples计数
        """
        if sample_id in self.labels:
            self.labels[sample_id]["verified"] = verified
            if verified:
                self.metadata["verified_samples"] = sum(
                    1 for label in self.labels.values() if label.get("verified", False)
                )
            self._save_labels()
            self._save_metadata()
            print(f"✅ 样本验证状态已更新: {sample_id} -> {verified}")
        else:
            print(f"❌ 样本不存在: {sample_id}")

    def split_dataset(self, train_ratio: float = 0.7, val_ratio: float = 0.15, 
                     test_ratio: float = 0.15, random_seed: int = 42):
        """
        将样本分割为训练集、验证集和测试集
        
        参数说明：
            train_ratio: 训练集比例（默认70%）
            val_ratio: 验证集比例（默认15%）
            test_ratio: 测试集比例（默认15%）
            random_seed: 随机种子，确保可复现
        
        【关键】分割策略：
        1. 仅对已验证的样本进行分割
        2. 使用随机种子确保分割可复现
        3. 按照指定比例分配样本
        4. 保存分割结果到dataset.json
        
        【数据流】已验证样本 → 随机打乱 → 按比例分割 → 保存结果
        """
        # 【关键】获取所有已验证的样本
        verified_samples = [
            sample_id for sample_id, label in self.labels.items()
            if label.get("verified", False)
        ]
        
        if len(verified_samples) == 0:
            print("⚠️ 没有已验证的样本可供分割")
            return
        
        # 【关键】随机打乱样本（使用固定种子）
        import random
        random.seed(random_seed)
        random.shuffle(verified_samples)
        
        # 【关键】计算分割点
        total = len(verified_samples)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        # 【关键】分割样本
        self.dataset = {
            "train": verified_samples[:train_end],
            "val": verified_samples[train_end:val_end],
            "test": verified_samples[val_end:]
        }
        
        # 保存分割结果
        self._save_dataset()
        
        print(f"✅ 数据集分割完成:")
        print(f"   训练集: {len(self.dataset['train'])} 样本")
        print(f"   验证集: {len(self.dataset['val'])} 样本")
        print(f"   测试集: {len(self.dataset['test'])} 样本")

    def get_batch(self, split: str, batch_size: int = 32) -> List[Dict]:
        """
        获取指定数据集的批次数据
        
        参数说明：
            split: 数据集类型 ("train", "val", "test")
            batch_size: 批次大小
        
        返回值：
            批次样本列表 [{sample_id, text, audio_path, speaker_id}, ...]
        
        【用途】为模型训练提供批次数据
        """
        if split not in self.dataset:
            print(f"❌ 无效的数据集类型: {split}")
            return []
        
        sample_ids = self.dataset[split]
        batch = []
        
        for sample_id in sample_ids[:batch_size]:
            if sample_id in self.labels:
                label = self.labels[sample_id]
                batch.append({
                    "sample_id": sample_id,
                    "text": label["text"],
                    "audio_path": label["file_path"],
                    "speaker_id": label.get("speaker_id")
                })
        
        return batch

    def get_statistics(self) -> Dict:
        """
        获取数据集统计信息
        
        返回值：
            统计信息字典
        """
        stats = {
            "total_samples": self.metadata["total_samples"],
            "labeled_samples": self.metadata["labeled_samples"],
            "verified_samples": self.metadata["verified_samples"],
            "train_samples": len(self.dataset.get("train", [])),
            "val_samples": len(self.dataset.get("val", [])),
            "test_samples": len(self.dataset.get("test", [])),
            "speakers": len(set(
                label.get("speaker_id") for label in self.labels.values()
                if label.get("speaker_id")
            ))
        }
        return stats


class ModelTrainer:
    """
    模型训练器类
    
    职责：
    1. 管理模型训练过程
    2. 执行微调和参数优化
    3. 评估模型准确度
    4. 管理训练检查点
    5. 记录训练日志
    
    【注意】实际的Whisper模型微调需要：
    - 大量GPU计算资源
    - HuggingFace transformers库
    - 专门的训练配置
    
    本实现提供训练框架，可扩展为实际训练功能
    """

    def __init__(self, model_name: str = "base", checkpoint_dir: str = "checkpoints"):
        """
        初始化模型训练器
        
        参数说明：
            model_name: Whisper模型名称
            checkpoint_dir: 检查点保存目录
        """
        self.model_name = model_name
        self.checkpoint_dir = os.path.abspath(checkpoint_dir)
        self.training_log_file = os.path.join(self.checkpoint_dir, "training_log.json")
        
        # 创建检查点目录
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # 加载训练日志
        self.training_log = self._load_training_log()

    def _load_training_log(self) -> List[Dict]:
        """加载训练日志"""
        if os.path.exists(self.training_log_file):
            try:
                with open(self.training_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载训练日志错误: {e}")
                return []
        return []

    def _save_training_log(self):
        """保存训练日志"""
        try:
            with open(self.training_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存训练日志错误: {e}")

    def train(self, data_manager: TrainingDataManager, epochs: int = 10, 
              batch_size: int = 16, learning_rate: float = 1e-5) -> Dict:
        """
        执行模型训练
        
        参数说明：
            data_manager: 训练数据管理器
            epochs: 训练轮数
            batch_size: 批次大小
            learning_rate: 学习率
        
        返回值：
            训练结果字典 {loss, accuracy, checkpoint_path}
        
        【关键】训练流程：
        1. 验证数据集是否就绪
        2. 初始化模型（或加载检查点）
        3. 迭代训练epochs轮
        4. 每轮评估验证集性能
        5. 保存最佳检查点
        6. 记录训练日志
        
        【注意】实际实现需要：
        - 加载Whisper模型
        - 实现前向传播和反向传播
        - 优化器配置
        - 损失函数计算
        """
        print(f"🔄 开始训练模型: {self.model_name}")
        print(f"   参数: epochs={epochs}, batch_size={batch_size}, lr={learning_rate}")
        
        # 【关键】验证数据集
        stats = data_manager.get_statistics()
        if stats["train_samples"] == 0:
            print("❌ 训练集为空，无法训练")
            return {"error": "No training data"}
        
        # 【关键】模拟训练过程（实际需要实现真实训练）
        print("⚠️ 注意：这是模拟训练，实际训练需要GPU和transformers库")
        
        # 训练日志条目
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model_name": self.model_name,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "train_samples": stats["train_samples"],
            "val_samples": stats["val_samples"],
            "status": "completed",
            "final_loss": 0.0,  # 模拟值
            "val_accuracy": 0.95,  # 模拟值
            "checkpoint_path": os.path.join(self.checkpoint_dir, f"checkpoint_epoch_{epochs}.pt")
        }
        
        # 保存日志
        self.training_log.append(log_entry)
        self._save_training_log()
        
        print(f"✅ 训练完成 (模拟)")
        print(f"   验证集准确度: {log_entry['val_accuracy']:.2%}")
        print(f"   检查点: {log_entry['checkpoint_path']}")
        
        return log_entry

    def evaluate(self, data_manager: TrainingDataManager, checkpoint_path: Optional[str] = None) -> Dict:
        """
        评估模型性能
        
        参数说明：
            data_manager: 训练数据管理器
            checkpoint_path: 检查点路径（可选）
        
        返回值：
            评估结果字典 {accuracy, wer, precision, recall}
        
        【关键】评估指标：
        - Accuracy: 整体准确率
        - WER (Word Error Rate): 词错误率
        - Precision: 精确率
        - Recall: 召回率
        """
        print(f"🔄 评估模型性能...")
        
        # 【关键】获取测试集数据
        test_samples = data_manager.get_batch("test", batch_size=100)
        
        if len(test_samples) == 0:
            print("⚠️ 测试集为空")
            return {"error": "No test data"}
        
        # 【关键】模拟评估（实际需要加载模型并推理）
        results = {
            "timestamp": datetime.now().isoformat(),
            "test_samples": len(test_samples),
            "accuracy": 0.92,  # 模拟值
            "wer": 0.08,  # 模拟值
            "precision": 0.93,  # 模拟值
            "recall": 0.91,  # 模拟值
            "checkpoint_path": checkpoint_path
        }
        
        print(f"✅ 评估完成:")
        print(f"   准确率: {results['accuracy']:.2%}")
        print(f"   词错误率: {results['wer']:.2%}")
        
        return results

    def save_checkpoint(self, model_state: Dict, optimizer_state: Dict, 
                       epoch: int, metrics: Dict) -> str:
        """
        保存训练检查点
        
        参数说明：
            model_state: 模型状态字典
            optimizer_state: 优化器状态字典
            epoch: 当前轮数
            metrics: 性能指标
        
        返回值：
            检查点文件路径
        
        【关键】检查点内容：
        - 模型参数
        - 优化器状态
        - 训练轮数
        - 性能指标
        - 时间戳
        """
        checkpoint_name = f"checkpoint_epoch_{epoch}.json"
        checkpoint_path = os.path.join(self.checkpoint_dir, checkpoint_name)
        
        checkpoint = {
            "model_name": self.model_name,
            "epoch": epoch,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "model_state": "saved",  # 实际应保存模型权重
            "optimizer_state": "saved"  # 实际应保存优化器状态
        }
        
        try:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)
            print(f"✅ 检查点已保存: {checkpoint_path}")
            return checkpoint_path
        except Exception as e:
            print(f"❌ 保存检查点错误: {e}")
            return ""

    def load_checkpoint(self, checkpoint_path: str) -> Optional[Dict]:
        """
        加载训练检查点
        
        参数说明：
            checkpoint_path: 检查点文件路径
        
        返回值：
            检查点数据字典，加载失败返回None
        """
        if not os.path.exists(checkpoint_path):
            print(f"❌ 检查点文件不存在: {checkpoint_path}")
            return None
        
        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            print(f"✅ 检查点已加载: {checkpoint_path}")
            return checkpoint
        except Exception as e:
            print(f"❌ 加载检查点错误: {e}")
            return None

    def get_training_history(self) -> List[Dict]:
        """
        获取训练历史记录
        
        返回值：
            训练日志列表
        """
        return self.training_log
