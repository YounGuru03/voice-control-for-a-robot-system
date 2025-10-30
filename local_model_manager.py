# ============================================================================
# local_model_manager.py
# ============================================================================

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

# 支持的模型配置
SUPPORTED_MODELS = {
    "tiny": {"size": "~39MB", "memory": "~200MB", "speed": "fast"},
    "base": {"size": "~74MB", "memory": "~400MB", "speed": "balanced"},
    "small": {"size": "~244MB", "memory": "~1GB", "speed": "accurate"}
}

class LocalModelManager:
    """完全离线本地模型管理器 - 修复网络依赖问题"""
    
    def __init__(self, models_dir="local_models"):
        """初始化模型管理器"""
        self.models_dir = self._get_models_directory(models_dir)
        self.models_info_file = os.path.join(self.models_dir, "models_info.json")
        self.models_info = self._load_models_info()
        
        # 确保目录存在
        os.makedirs(self.models_dir, exist_ok=True)
        
        # 设置离线模式
        self._set_offline_mode()
        
        print(f"✅ LocalModelManager initialized: {self.models_dir}")
    
    def _set_offline_mode(self):
        """设置完全离线模式"""
        # 设置Hugging Face离线模式
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        
        # 设置本地缓存目录
        if not os.environ.get('HF_HOME'):
            cache_dir = os.path.join(self.models_dir, 'hf_cache')
            os.makedirs(cache_dir, exist_ok=True)
            os.environ['HF_HOME'] = cache_dir
        
        print("🔒 Offline mode enabled - no network requests will be made")
    
    def _get_models_directory(self, models_dir: str) -> str:
        """获取模型目录路径"""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller环境
            base_path = sys._MEIPASS
            models_path = os.path.join(base_path, models_dir)
            
            if not os.path.exists(models_path):
                # 如果嵌入路径不存在，使用应用目录
                app_dir = os.path.dirname(sys.executable)
                models_path = os.path.join(app_dir, models_dir)
        else:
            # 开发环境
            models_path = os.path.abspath(models_dir)
        
        return models_path
    
    def _load_models_info(self) -> Dict[str, Any]:
        """加载模型信息"""
        if os.path.exists(self.models_info_file):
            try:
                with open(self.models_info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Models info load error: {e}")
        
        return {
            "local_models": {},
            "default_model": "base",
            "offline_mode": True
        }
    
    def _save_models_info(self):
        """保存模型信息"""
        try:
            with open(self.models_info_file, 'w', encoding='utf-8') as f:
                json.dump(self.models_info, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Models info save error: {e}")
    
    def is_model_available(self, model_name: str) -> bool:
        """检查模型是否可用"""
        # 检查系统缓存中的模型
        try:
            from faster_whisper import WhisperModel
            # 尝试创建模型实例（不下载）
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
            print(f"✅ Model '{model_name}' found in system cache")
            return True
        except Exception as e:
            print(f"⚠️ Model '{model_name}' not available: {e}")
            return False
    
    def load_model(self, model_name: str = None):
        """加载本地模型（纯离线）"""
        if model_name is None:
            model_name = self.models_info.get("default_model", "base")
        
        try:
            from faster_whisper import WhisperModel
            
            print(f"🔄 Loading offline model: {model_name}")
            
            # 尝试加载模型（完全离线模式）
            model = WhisperModel(
                model_name,
                device="cpu",
                compute_type="int8",
                local_files_only=True  # 强制本地文件模式
            )
            
            # 更新模型信息
            self.models_info["local_models"][model_name] = {
                "status": "loaded",
                "size": SUPPORTED_MODELS.get(model_name, {}).get("size", "unknown"),
                "loaded_at": str(Path().absolute())
            }
            self._save_models_info()
            
            print(f"✅ Loaded offline model: {model_name}")
            return model
            
        except Exception as e:
            print(f"❌ Model loading error: {e}")
            print("💡 Please ensure the model is pre-installed in your system")
            
            # 尝试不使用local_files_only（但在离线模式下）
            try:
                print("🔄 Trying alternative loading method...")
                model = WhisperModel(
                    model_name,
                    device="cpu",
                    compute_type="int8"
                )
                
                self.models_info["local_models"][model_name] = {
                    "status": "cached",
                    "size": SUPPORTED_MODELS.get(model_name, {}).get("size", "unknown"),
                    "loaded_at": str(Path().absolute())
                }
                self._save_models_info()
                
                print(f"✅ Model '{model_name}' loaded from system cache")
                return model
                
            except Exception as e2:
                print(f"❌ Alternative loading failed: {e2}")
                return None
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        available = []
        
        for model_name in SUPPORTED_MODELS.keys():
            if self.is_model_available(model_name):
                available.append(model_name)
        
        return available
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """获取模型详细信息"""
        if model_name in self.models_info["local_models"]:
            info = self.models_info["local_models"][model_name].copy()
            if model_name in SUPPORTED_MODELS:
                info.update(SUPPORTED_MODELS[model_name])
            return info
        return None
    
    def validate_models(self) -> Dict[str, bool]:
        """验证模型可用性"""
        validation_results = {}
        
        for model_name in SUPPORTED_MODELS.keys():
            validation_results[model_name] = self.is_model_available(model_name)
        
        return validation_results
    
    def get_total_size(self) -> str:
        """获取总大小估算"""
        available_models = self.get_available_models()
        total_mb = 0
        
        for model_name in available_models:
            model_info = SUPPORTED_MODELS.get(model_name, {})
            size_str = model_info.get("size", "0MB")
            
            # 解析大小字符串
            size_str = size_str.replace("~", "").upper()
            if "MB" in size_str:
                try:
                    size_val = float(size_str.replace("MB", ""))
                    total_mb += size_val
                except:
                    pass
        
        if total_mb >= 1024:
            return f"~{total_mb/1024:.1f}GB"
        else:
            return f"~{total_mb:.0f}MB"
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "offline_mode": True,
            "models_directory": self.models_dir,
            "available_models": self.get_available_models(),
            "total_size": self.get_total_size(),
            "environment": {
                "HF_HUB_OFFLINE": os.environ.get('HF_HUB_OFFLINE', 'not_set'),
                "HF_HOME": os.environ.get('HF_HOME', 'not_set')
            }
        }
    
    def prepare_for_pyinstaller(self) -> List[str]:
        """准备PyInstaller数据文件参数"""
        # 由于使用系统缓存，不需要特殊的数据文件参数
        return []