# ============================================================================
# optimized_audio_processor.py
# ============================================================================

import warnings
warnings.filterwarnings("ignore")

import os
import sys
import re
import time
import threading
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pyaudio
from typing import Optional, List, Dict, Any

# 导入优化模块
from command_hotword_manager import CommandHotwordManager
from optimized_tts_manager import OptimizedTTSManager
from local_model_manager import LocalModelManager

# Whisper后端检测
BACKEND = None
try:
    from faster_whisper import WhisperModel
    BACKEND = "faster-whisper"
except ImportError:
    try:
        import whisper
        BACKEND = "openai-whisper"
    except ImportError:
        BACKEND = "none"
        print("❌ WARNING: No Whisper backend available")

class OptimizedAudioProcessor:
    """优化的音频处理器 - 修复时间间隔和TTS问题"""
    
    # 状态定义
    WAKE_STATE_INACTIVE = 0
    WAKE_STATE_ACTIVE = 1
    
    def __init__(self, model_size="base", language="en", device="cpu"):
        """初始化音频处理器"""
        
        # 基础配置
        self.language = language
        self.wake_state = self.WAKE_STATE_INACTIVE
        self.model_size = model_size
        self.device = device
        self.model = None
        
        # 状态管理
        self._lock = threading.Lock()
        self._processing = False
        self._last_command_time = 0
        self._command_cooldown = 3.0  # 增加到3秒冷却时间，防止识别过快
        
        # 初始化管理器
        print("🔄 Initializing optimized processors...")
        
        # 命令热词管理器
        self.cmd_hotword_mgr = CommandHotwordManager()
        
        # TTS管理器
        self.tts_mgr = OptimizedTTSManager()
        
        # 本地模型管理器
        self.model_mgr = LocalModelManager()
        
        # 初始化Whisper模型
        self._initialize_whisper_model()
        
        print(f"✅ OptimizedAudioProcessor initialized")
        print(f"   Model: {model_size}, Backend: {BACKEND}")
    
    def _initialize_whisper_model(self):
        """初始化Whisper模型"""
        try:
            if BACKEND == "faster-whisper":
                # 使用本地模型管理器加载模型
                print(f"🔄 Loading local model: {self.model_size}")
                self.model = self.model_mgr.load_model(self.model_size)
                
                if self.model:
                    print("✅ Using local faster-whisper model")
                else:
                    print("❌ Failed to load local model")
                    
            elif BACKEND == "openai-whisper":
                import whisper
                self.model = whisper.load_model(self.model_size, device=self.device)
                print("✅ Using openai-whisper model")
                
            else:
                print("❌ No Whisper backend available")
                self.model = None
                
        except Exception as e:
            print(f"❌ Model initialization error: {e}")
            self.model = None
    
    def set_wake_state(self, state):
        """设置唤醒状态（线程安全）"""
        if state not in [self.WAKE_STATE_INACTIVE, self.WAKE_STATE_ACTIVE]:
            return False
        
        with self._lock:
            self.wake_state = state
            
        state_name = "ACTIVE" if state == 1 else "INACTIVE"
        print(f"🔄 Wake state: {state_name}")
        return True
    
    def get_wake_state(self):
        """获取唤醒状态"""
        with self._lock:
            return self.wake_state
    
    def is_active(self):
        """检查是否活跃"""
        return self.get_wake_state() == self.WAKE_STATE_ACTIVE
    
    def is_processing(self):
        """检查是否正在处理"""
        with self._lock:
            return self._processing
    
    def record_audio(self, duration=5, sample_rate=16000):
        """录制音频（减少终端输出）"""
        chunk = 1024
        channels = 1
        
        try:
            p = pyaudio.PyAudio()
            
            # 查找默认输入设备（不输出设备信息）
            default_device = p.get_default_input_device_info()
            # print(f"🎤 Using microphone: {default_device['name']}")  # 移除终端输出
            
            stream = p.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk,
                input_device_index=default_device['index']
            )
            
            frames = []
            frames_to_read = int(sample_rate / chunk * duration)
            
            for i in range(frames_to_read):
                try:
                    data = stream.read(chunk, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    # print(f"⚠️ Audio read warning: {e}")  # 减少输出
                    continue
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            if not frames:
                print("❌ No audio data recorded")
                return None
            
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            audio_data = audio_data.astype(np.float32) / 32768.0
            
            # 检查音频质量（简化输出）
            rms = np.sqrt(np.mean(audio_data**2))
            if rms < 0.001:  # 太安静
                print("⚠️ Audio too quiet")
            
            # print(f"✅ Recorded {duration}s audio, RMS: {rms:.4f}")  # 减少输出
            return audio_data
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return None
    
    def detect_wake_word(self, audio_data, wake_word="susie"):
        """检测唤醒词（增强处理）"""
        if audio_data is None or self.model is None:
            return False
        
        with self._lock:
            if self._processing:
                print("⚠️ Already processing, skipping wake word detection")
                return False
            self._processing = True
        
        try:
            # 获取热词提升
            boost_phrases = [wake_word] + self.cmd_hotword_mgr.get_boost_phrases(5)
            
            # print(f"🔍 Detecting wake word '{wake_word}'...")  # 减少输出
            
            # 转写音频
            if BACKEND == "faster-whisper":
                initial_prompt = ", ".join(boost_phrases)
                segments, _ = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    beam_size=1,
                    vad_filter=True,
                    initial_prompt=initial_prompt
                )
                text = " ".join([seg.text for seg in segments])
                
            elif BACKEND == "openai-whisper":
                initial_prompt = ", ".join(boost_phrases)
                result = self.model.transcribe(
                    audio_data, 
                    language=self.language, 
                    fp16=False,
                    initial_prompt=initial_prompt
                )
                text = result["text"]
            else:
                return False
            
            text = text.strip().lower()
            detected = wake_word.lower() in text
            
            # print(f"🔍 Wake word detection result: '{text}' -> {detected}")  # 减少输出
            
            if detected:
                print(f"✅ Wake word '{wake_word}' detected")
                # TTS播报唤醒
                self.tts_mgr.speak_status("please speak")
            
            return detected
            
        except Exception as e:
            print(f"❌ Wake word detection error: {e}")
            return False
        finally:
            with self._lock:
                self._processing = False
    
    def transcribe(self, audio_data):
        """转写音频（增强状态检查和错误处理）"""
        # 状态检查
        current_state = self.get_wake_state()
        if current_state != self.WAKE_STATE_ACTIVE:
            print(f"❌ Not in active state (current: {current_state}), skipping transcription")
            return None
        
        if audio_data is None or self.model is None:
            print("❌ No audio data or model not available")
            return None
        
        with self._lock:
            if self._processing:
                print("⚠️ Already processing, skipping transcription")
                return None
            self._processing = True
        
        try:
            # 获取热词提升短语
            boost_phrases = self.cmd_hotword_mgr.get_boost_phrases(15)
            initial_prompt = ", ".join(boost_phrases) if boost_phrases else None
            
            print("🔄 Transcribing audio...")
            
            # 转写音频
            if BACKEND == "faster-whisper":
                segments, _ = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    beam_size=3,  # 减少beam_size提高速度
                    vad_filter=True,
                    initial_prompt=initial_prompt
                )
                text = " ".join([seg.text for seg in segments])
                
            elif BACKEND == "openai-whisper":
                result = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    fp16=False,
                    initial_prompt=initial_prompt
                )
                text = result["text"]
            else:
                return None
            
            text = text.strip()
            
            # 数字格式化处理
            text = self._format_numbers(text)
            
            print(f"✅ Transcription result: '{text}'")
            return text if text else None
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
        finally:
            with self._lock:
                self._processing = False
    
    def _format_numbers(self, text: str) -> str:
        """格式化数字输出"""
        if not text:
            return text
        
        # 英文数字词汇到阿拉伯数字的映射
        number_words = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
            'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
            'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
            'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'thirty': '30',
            'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
            'eighty': '80', 'ninety': '90', 'hundred': '100', 'thousand': '1000'
        }
        
        # 替换英文数字为阿拉伯数字
        words = text.split()
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?')
            if word_lower in number_words:
                words[i] = word.replace(word_lower, number_words[word_lower])
        
        return ' '.join(words)
    
    def match_command(self, text, commands):
        """匹配命令（增强冷却时间处理）"""
        if not text or not commands:
            return None
        
        # 检查冷却时间
        current_time = time.time()
        if current_time - self._last_command_time < self._command_cooldown:
            print(f"⚠️ Command cooldown active ({self._command_cooldown}s)")
            return None
        
        text_lower = text.lower().strip()
        matched_command = None
        
        # 精确匹配和包含匹配
        for cmd in commands:
            cmd_lower = cmd.lower().strip()
            if cmd_lower == text_lower or cmd_lower in text_lower:
                matched_command = cmd
                break
        
        # 记录使用情况
        if matched_command:
            self.cmd_hotword_mgr.record_usage(matched_command, success=True)
            self._last_command_time = current_time
            
            # TTS播报命令
            self.tts_mgr.speak_command(matched_command)
            
            print(f"✅ Command matched: '{text}' -> '{matched_command}'")
        else:
            # 检查是否有部分匹配
            for word in text_lower.split():
                if word in [cmd.lower() for cmd in commands]:
                    self.cmd_hotword_mgr.record_usage(word, success=False)
            
            # TTS播报未匹配
            self.tts_mgr.speak_status("not match")
            
            print(f"❌ No command match for: '{text}'")
        
        return matched_command
    
    def reset_wake_state(self):
        """重置唤醒状态"""
        with self._lock:
            self.wake_state = self.WAKE_STATE_INACTIVE
            self._processing = False
        
        print("🔄 Wake state reset to INACTIVE")
        # TTS播报状态重置
        self.tts_mgr.speak_status("stand by")
    
    def add_command(self, text: str) -> bool:
        """添加命令"""
        return self.cmd_hotword_mgr.add_command(text)
    
    def remove_command(self, text: str) -> bool:
        """删除命令"""
        return self.cmd_hotword_mgr.remove_command(text)
    
    def get_all_commands(self) -> List[str]:
        """获取所有命令"""
        return self.cmd_hotword_mgr.get_all_commands()
    
    def train_command(self, text: str) -> float:
        """训练命令"""
        return self.cmd_hotword_mgr.train_command(text)
    
    def get_training_count(self, text: str) -> int:
        """获取训练次数"""
        return self.cmd_hotword_mgr.get_training_count(text)
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        with self._lock:
            current_wake_state = self.wake_state
            current_processing = self._processing
        
        status = {
            "wake_state": current_wake_state,
            "processing": current_processing,
            "model_size": self.model_size,
            "backend": BACKEND,
            "model_loaded": self.model is not None,
            "features": {
                "tts_enabled": True,
                "hotwords_enabled": True,
                "embedded_models": True
            }
        }
        
        # 命令统计
        cmd_stats = self.cmd_hotword_mgr.get_statistics()
        status["commands"] = {
            "total": cmd_stats["total"],
            "most_used": cmd_stats["most_used"][:3]
        }
        
        # TTS状态
        tts_info = self.tts_mgr.get_engine_info()
        status["tts"] = {
            "engine_type": tts_info["engine_type"],
            "enabled": tts_info["enabled"],
            "running": tts_info["running"],
            "speaking": tts_info["speaking"]
        }
        
        # 模型状态
        model_info = self.model_mgr.get_system_info()
        status["local_models"] = {
            "offline_mode": model_info["offline_mode"],
            "available": model_info["available_models"],
            "total_size": model_info["total_size"]
        }
        
        return status
    
    def shutdown(self):
        """关闭处理器"""
        print("🔄 Shutting down audio processor...")
        
        # 重置状态
        with self._lock:
            self.wake_state = self.WAKE_STATE_INACTIVE
            self._processing = False
        
        # 停止TTS
        if self.tts_mgr:
            self.tts_mgr.stop()
        
        print("✅ Audio processor shutdown complete")