# ============================================================================
# local_model_manager.py
# ============================================================================

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

# Supported model configurations
SUPPORTED_MODELS = {
    "tiny": {"size": "~39MB", "memory": "~200MB", "speed": "fast"},
    "base": {"size": "~74MB", "memory": "~400MB", "speed": "balanced"},
    "small": {"size": "~244MB", "memory": "~1GB", "speed": "accurate"}
}

class LocalModelManager:
    """Smart local model manager with automatic download and offline capabilities"""
    
    def __init__(self, models_dir="local_models"):
        """Initialize model manager"""
        self.models_dir = self._get_models_directory(models_dir)
        self.models_info_file = os.path.join(self.models_dir, "models_info.json")
        self.models_info = self._load_models_info()
        
        # Ensure directory exists
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Setup cache environment
        self._setup_cache_environment()
        
        print(f"✅ LocalModelManager initialized: {self.models_dir}")
        
        # Verify models on startup
        self._verify_models_on_startup()

    def _setup_cache_environment(self):
        """Setup cache environment without forcing offline mode"""
        # Set local cache directory if not already set
        if not os.environ.get('HF_HOME'):
            cache_dir = os.path.join(self.models_dir, 'hf_cache')
            os.makedirs(cache_dir, exist_ok=True)
            os.environ['HF_HOME'] = cache_dir
        
        print(f"🔧 Cache environment setup: {os.environ.get('HF_HOME')}")

    def _get_models_directory(self, models_dir: str) -> str:
        """Get model directory path"""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller environment
            base_path = sys._MEIPASS
            models_path = os.path.join(base_path, models_dir)
            if not os.path.exists(models_path):
                # If embedded path doesn't exist, use app directory
                app_dir = os.path.dirname(sys.executable)
                models_path = os.path.join(app_dir, models_dir)
        else:
            # Development environment
            models_path = os.path.abspath(models_dir)
        
        return models_path

    def _load_models_info(self) -> Dict[str, Any]:
        """Load model information"""
        if os.path.exists(self.models_info_file):
            try:
                with open(self.models_info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Models info load error: {e}")
        
        return {
            "local_models": {},
            "default_model": "base",
            "auto_download": True
        }

    def _save_models_info(self):
        """Save model information"""
        try:
            with open(self.models_info_file, 'w', encoding='utf-8') as f:
                json.dump(self.models_info, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Models info save error: {e}")

    def _check_local_model_cache(self, model_name: str) -> bool:
        """Check if model exists in local cache"""
        try:
            from faster_whisper import WhisperModel
            # Try to create model instance with local_files_only=True
            model = WhisperModel(
                model_name,
                device="cpu",
                compute_type="int8",
                local_files_only=True
            )
            print(f"✅ Model '{model_name}' found in local cache")
            return True
        except Exception:
            return False

    def _download_model(self, model_name: str):
        """Download model to local cache"""
        try:
            from faster_whisper import WhisperModel
            print(f"📥 Downloading model '{model_name}' to local cache...")
            
            # Download model (this will cache it locally)
            model = WhisperModel(
                model_name,
                device="cpu",
                compute_type="int8",
                local_files_only=False  # Allow download
            )
            
            # Update model info
            self.models_info["local_models"][model_name] = {
                "status": "downloaded",
                "size": SUPPORTED_MODELS.get(model_name, {}).get("size", "unknown"),
                "downloaded_at": str(Path().absolute())
            }
            self._save_models_info()
            
            print(f"✅ Model '{model_name}' downloaded successfully")
            return model
            
        except Exception as e:
            print(f"❌ Failed to download model '{model_name}': {e}")
            return None

    def is_model_available(self, model_name: str) -> bool:
        """Check if model is available locally"""
        return self._check_local_model_cache(model_name)

    def load_model(self, model_name: str = None):
        """Load model with smart download/offline logic"""
        if model_name is None:
            model_name = self.models_info.get("default_model", "base")
        
        print(f"🔄 Loading model: {model_name}")
        
        # Step 1: Try to load from local cache first
        if self._check_local_model_cache(model_name):
            try:
                from faster_whisper import WhisperModel
                model = WhisperModel(
                    model_name,
                    device="cpu",
                    compute_type="int8",
                    local_files_only=True
                )
                
                # Update model info
                self.models_info["local_models"][model_name] = {
                    "status": "loaded",
                    "size": SUPPORTED_MODELS.get(model_name, {}).get("size", "unknown"),
                    "loaded_at": str(Path().absolute())
                }
                self._save_models_info()
                
                print(f"✅ Loaded model from local cache: {model_name}")
                return model
                
            except Exception as e:
                print(f"⚠️ Error loading from cache: {e}")
        
        # Step 2: If not in cache and auto_download is enabled, try to download
        if self.models_info.get("auto_download", True):
            print(f"🔄 Model '{model_name}' not found locally, attempting download...")
            model = self._download_model(model_name)
            if model:
                return model
        
        # Step 3: Final fallback - try loading without local_files_only
        try:
            print(f"🔄 Trying final fallback for model: {model_name}")
            from faster_whisper import WhisperModel
            model = WhisperModel(
                model_name,
                device="cpu",
                compute_type="int8"
            )
            
            self.models_info["local_models"][model_name] = {
                "status": "fallback_loaded",
                "size": SUPPORTED_MODELS.get(model_name, {}).get("size", "unknown"),
                "loaded_at": str(Path().absolute())
            }
            self._save_models_info()
            
            print(f"✅ Model '{model_name}' loaded via fallback method")
            return model
            
        except Exception as e:
            print(f"❌ Failed to load model '{model_name}': {e}")
            return None

    def preload_models(self, model_list: List[str] = None):
        """Preload specified models or default models"""
        if model_list is None:
            model_list = ["tiny", "base"]  # Default models to preload
        
        print(f"🚀 Preloading models: {model_list}")
        
        for model_name in model_list:
            if model_name in SUPPORTED_MODELS:
                if not self._check_local_model_cache(model_name):
                    print(f"📥 Preloading model: {model_name}")
                    self._download_model(model_name)
                else:
                    print(f"✅ Model '{model_name}' already cached")
            else:
                print(f"⚠️ Unknown model: {model_name}")

    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        available = []
        for model_name in SUPPORTED_MODELS.keys():
            if self.is_model_available(model_name):
                available.append(model_name)
        return available

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed model information"""
        if model_name in self.models_info["local_models"]:
            info = self.models_info["local_models"][model_name].copy()
            if model_name in SUPPORTED_MODELS:
                info.update(SUPPORTED_MODELS[model_name])
            return info
        return None

    def validate_models(self) -> Dict[str, bool]:
        """Validate model availability"""
        validation_results = {}
        for model_name in SUPPORTED_MODELS.keys():
            validation_results[model_name] = self.is_model_available(model_name)
        return validation_results

    def get_total_size(self) -> str:
        """Get estimated total size"""
        available_models = self.get_available_models()
        total_mb = 0
        
        for model_name in available_models:
            model_info = SUPPORTED_MODELS.get(model_name, {})
            size_str = model_info.get("size", "0MB")
            
            # Parse size string
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
        """Get system information"""
        return {
            "auto_download": self.models_info.get("auto_download", True),
            "models_directory": self.models_dir,
            "available_models": self.get_available_models(),
            "total_size": self.get_total_size(),
            "environment": {
                "HF_HOME": os.environ.get('HF_HOME', 'not_set'),
                "HF_HUB_OFFLINE": os.environ.get('HF_HUB_OFFLINE', 'not_set')
            }
        }

    def enable_auto_download(self, enabled: bool = True):
        """Enable or disable automatic model downloading"""
        self.models_info["auto_download"] = enabled
        self._save_models_info()
        status = "enabled" if enabled else "disabled"
        print(f"🔧 Auto-download {status}")

    def prepare_for_pyinstaller(self) -> List[str]:
        """Prepare PyInstaller data file parameters"""
        # Since we use system cache, no special data file parameters needed
        return []
    
    def _verify_models_on_startup(self):
        """Verify models exist on startup and download if missing"""
        print("\n" + "="*60)
        print("🔍 CHECKING LOCAL MODELS ON STARTUP")
        print("="*60)
        
        # Check if faster-whisper is available
        try:
            from faster_whisper import WhisperModel
            print("✅ faster-whisper library is installed")
        except ImportError:
            print("❌ faster-whisper library NOT found!")
            print("   Please install: pip install faster-whisper")
            return
        
        # Get default model
        default_model = self.models_info.get("default_model", "base")
        print(f"\n📦 Default model: {default_model}")
        
        # Check if default model exists
        if self._check_local_model_cache(default_model):
            print(f"✅ Model '{default_model}' found in local cache")
            print(f"   Location: {os.environ.get('HF_HOME', 'system cache')}")
        else:
            print(f"⚠️  Model '{default_model}' NOT found in local cache")
            
            # Auto-download if enabled
            if self.models_info.get("auto_download", True):
                print(f"📥 Auto-download enabled, downloading model '{default_model}'...")
                model = self._download_model(default_model)
                if model:
                    print(f"✅ Model '{default_model}' downloaded successfully")
                else:
                    print(f"❌ Failed to download model '{default_model}'")
                    print("   The system may not work in offline mode")
            else:
                print("❌ Auto-download is disabled")
                print("   Enable auto-download or manually download the model")
        
        # Check TTS engine
        print(f"\n🔊 CHECKING TTS ENGINE")
        print("-"*60)
        try:
            import pyttsx3
            print("✅ pyttsx3 TTS library is installed")
            
            # Try to initialize TTS engine
            try:
                test_engine = pyttsx3.init()
                voices = test_engine.getProperty('voices')
                print(f"✅ TTS engine initialized successfully")
                print(f"   Available voices: {len(voices)}")
                test_engine.stop()
                del test_engine
            except Exception as e:
                print(f"⚠️  TTS engine initialization issue: {e}")
                print("   TTS may not work properly")
        except ImportError:
            print("❌ pyttsx3 library NOT found!")
            print("   Please install: pip install pyttsx3")
        
        # Summary
        print("\n" + "="*60)
        print("🎯 SYSTEM VERIFICATION SUMMARY")
        print("="*60)
        available_models = self.get_available_models()
        print(f"✅ Available models: {len(available_models)}")
        if available_models:
            for model in available_models:
                info = SUPPORTED_MODELS.get(model, {})
                print(f"   • {model}: {info.get('size', 'unknown size')}")
        print(f"📁 Models directory: {self.models_dir}")
        print(f"💾 Total cache size: {self.get_total_size()}")
        print(f"🌐 Offline mode: {'✅ Ready' if available_models else '❌ Not ready'}")
        print("="*60 + "\n")