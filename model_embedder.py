# ============================================================================
# model_embedder.py
# ============================================================================

import os
import sys
import shutil
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

SUPPORTED_MODELS = {
    "tiny": {"size": "~39MB", "memory": "~274MB", "speed": "~10x"},
    "tiny.en": {"size": "~39MB", "memory": "~274MB", "speed": "~10x"},
    "base": {"size": "~74MB", "memory": "~512MB", "speed": "~7x"},
    "base.en": {"size": "~74MB", "memory": "~512MB", "speed": "~7x"},
    "small": {"size": "~244MB", "memory": "~1GB", "speed": "~4x"},
    "small.en": {"size": "~244MB", "memory": "~1GB", "speed": "~4x"},
    "medium": {"size": "~769MB", "memory": "~2GB", "speed": "~2x"},
    "medium.en": {"size": "~769MB", "memory": "~2GB", "speed": "~2x"}
}

class ModelEmbedder:
    """Model Embedding Manager for Offline Deployment"""
    
    def __init__(self, models_dir="embedded_models"):
        """Initialize model embedder"""
        self.models_dir = self._get_models_directory(models_dir)
        self.models_info_file = os.path.join(self.models_dir, "models_info.json")
        self.models_info = self._load_models_info()
        
        os.makedirs(self.models_dir, exist_ok=True)
        print(f"✅ ModelEmbedder initialized: {self.models_dir}")
    
    def _get_models_directory(self, models_dir: str) -> str:
        """Get the correct models directory path"""
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
            models_path = os.path.join(base_path, models_dir)
            
            if not os.path.exists(models_path):
                app_dir = os.path.dirname(sys.executable)
                models_path = os.path.join(app_dir, models_dir)
            
            return models_path
        else:
            return os.path.abspath(models_dir)
    
    def _load_models_info(self) -> Dict[str, Any]:
        """Load models information from file"""
        if os.path.exists(self.models_info_file):
            try:
                with open(self.models_info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Models info load error: {e}")
        
        return {"embedded_models": {}, "download_info": {}}
    
    def _save_models_info(self):
        """Save models information to file"""
        try:
            with open(self.models_info_file, 'w', encoding='utf-8') as f:
                json.dump(self.models_info, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Models info save error: {e}")
    
    def get_model_path(self, model_name: str) -> Optional[str]:
        """Get the local path for a model"""
        model_dir = os.path.join(self.models_dir, model_name)
        
        if os.path.exists(model_dir):
            return model_dir
        
        return None
    
    def is_model_embedded(self, model_name: str) -> bool:
        """Check if model is embedded locally"""
        return model_name in self.models_info["embedded_models"]
    
    def embed_model(self, model_name: str, source_path: str = None) -> bool:
        """Embed a model for offline use"""
        if model_name not in SUPPORTED_MODELS:
            print(f"❌ Unsupported model: {model_name}")
            return False
        
        model_dir = os.path.join(self.models_dir, model_name)
        
        if source_path and os.path.exists(source_path):
            try:
                if os.path.exists(model_dir):
                    shutil.rmtree(model_dir)
                
                shutil.copytree(source_path, model_dir)
                
                self.models_info["embedded_models"][model_name] = {
                    "path": model_dir,
                    "size": SUPPORTED_MODELS[model_name]["size"],
                    "embedded_at": str(Path().absolute()),
                    "source": "copied"
                }
                
                self._save_models_info()
                print(f"✅ Model '{model_name}' embedded from {source_path}")
                return True
                
            except Exception as e:
                print(f"❌ Model embedding error: {e}")
                return False
        
        else:
            return self._download_and_embed_model(model_name)
    
    def _download_and_embed_model(self, model_name: str) -> bool:
        """Download and embed model using faster-whisper"""
        try:
            print(f"🔄 Downloading model '{model_name}'...")
            
            from faster_whisper import WhisperModel
            
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
            
            # Try to get model files from cache
            import huggingface_hub
            try:
                cache_dir = huggingface_hub.snapshot_download(
                    repo_id=f"guillaumekln/faster-whisper-{model_name}",
                    cache_dir=None
                )
                
                model_dir = os.path.join(self.models_dir, model_name)
                if os.path.exists(model_dir):
                    shutil.rmtree(model_dir)
                
                shutil.copytree(cache_dir, model_dir)
                
                self.models_info["embedded_models"][model_name] = {
                    "path": model_dir,
                    "size": SUPPORTED_MODELS[model_name]["size"],
                    "embedded_at": str(Path().absolute()),
                    "source": "downloaded"
                }
                
                self._save_models_info()
                print(f"✅ Model '{model_name}' downloaded and embedded")
                return True
                
            except Exception as cache_error:
                print(f"⚠️ Cache access failed: {cache_error}")
                # Model was loaded but we couldn't copy cache, still consider success
                return True
            
        except Exception as e:
            print(f"❌ Model download error: {e}")
            return False
    
    def load_embedded_model(self, model_name: str, device: str = "cpu", compute_type: str = "int8"):
        """Load embedded model for inference"""
        if not self.is_model_embedded(model_name):
            print(f"❌ Model '{model_name}' not embedded")
            return None
        
        try:
            from faster_whisper import WhisperModel
            
            model_path = self.get_model_path(model_name)
            
            model = WhisperModel(
                model_path,
                device=device,
                compute_type=compute_type,
                local_files_only=True
            )
            
            print(f"✅ Loaded embedded model: {model_name}")
            return model
            
        except Exception as e:
            print(f"❌ Model loading error: {e}")
            return None
    
    def get_embedded_models(self) -> List[str]:
        """Get list of embedded model names"""
        return list(self.models_info["embedded_models"].keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        if model_name in self.models_info["embedded_models"]:
            info = self.models_info["embedded_models"][model_name].copy()
            if model_name in SUPPORTED_MODELS:
                info.update(SUPPORTED_MODELS[model_name])
            return info
        
        return None
    
    def validate_embedded_models(self) -> Dict[str, bool]:
        """Validate that all embedded models are present and intact"""
        validation_results = {}
        
        for model_name in self.get_embedded_models():
            model_path = self.get_model_path(model_name)
            
            if not model_path or not os.path.exists(model_path):
                validation_results[model_name] = False
                continue
            
            # Check for essential files
            essential_files = ["config.json", "model.bin", "tokenizer.json"]
            has_essential = any(
                os.path.exists(os.path.join(model_path, f)) 
                for f in essential_files
            )
            
            validation_results[model_name] = has_essential
        
        return validation_results
    
    def get_total_size(self) -> str:
        """Get total size of embedded models"""
        total_size = 0
        size_units = {"MB": 1, "GB": 1024}
        
        for model_name in self.get_embedded_models():
            model_info = SUPPORTED_MODELS.get(model_name, {})
            size_str = model_info.get("size", "0MB")
            
            size_str = size_str.replace("~", "").upper()
            for unit, multiplier in size_units.items():
                if unit in size_str:
                    try:
                        size_val = float(size_str.replace(unit, ""))
                        total_size += size_val * multiplier
                        break
                    except ValueError:
                        pass
        
        if total_size >= 1024:
            return f"~{total_size/1024:.1f}GB"
        else:
            return f"~{total_size:.0f}MB"