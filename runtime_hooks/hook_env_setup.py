# ============================================================================
# Runtime Hook: Environment Setup for Voice Control
# ============================================================================
"""
Sets up environment variables and paths for the packaged application.
"""

import sys
import os
from pathlib import Path

def _setup_environment():
    """Setup runtime environment"""
    try:
        # Determine if running from packaged exe
        if getattr(sys, 'frozen', False):
            # Running from PyInstaller bundle
            application_path = Path(sys._MEIPASS)
            print(f"[HOOK] Running from bundle: {application_path}")
            
            # Set environment variables for offline mode
            os.environ['HF_HUB_OFFLINE'] = '1'
            os.environ['TRANSFORMERS_OFFLINE'] = '1'
            
            # Add local models path
            local_models = application_path / "local_models"
            if local_models.exists():
                print(f"[HOOK] Local models found: {local_models}")
            
            # Set cache directories to temp location
            temp_cache = Path(os.environ.get('TEMP', '/tmp')) / 'voice_control_cache'
            temp_cache.mkdir(exist_ok=True)
            os.environ['HF_HOME'] = str(temp_cache)
            
            print("[HOOK] Environment configured for packaged execution")
        else:
            print("[HOOK] Running in development mode")
            
    except Exception as e:
        print(f"[HOOK] WARNING: Environment setup failed: {e}")

# Execute setup
_setup_environment()
