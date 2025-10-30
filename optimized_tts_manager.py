# ============================================================================
# optimized_tts_manager.py
# ============================================================================

import os
import threading
import time
import queue
from typing import Optional, List, Dict, Any
from datetime import datetime

TTS_ENGINE = None
TTS_TYPE = None

try:
    import pyttsx3

    TTS_ENGINE = pyttsx3
    TTS_TYPE = "pyttsx3"
except ImportError:
    print("❌ pyttsx3 not available")


class OptimizedTTSManager:
    """优化的TTS管理器 - 增强容错性和稳定性"""

    def __init__(self, config_file="tts_config.json"):
        """初始化TTS管理器"""
        self.config_file = os.path.abspath(config_file)
        self.config = self._load_config()

        # TTS队列和线程控制
        self.tts_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        self.engine = None
        self._lock = threading.Lock()
        self._current_speaking = False

        # 增强容错性的控制变量
        self._engine_error_count = 0
        self._max_error_count = 3
        self._last_engine_init_time = 0
        self._engine_init_cooldown = 5.0

        # 初始化引擎
        self._initialize_engine()

        print(f"✅ OptimizedTTSManager initialized with {TTS_TYPE}")

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "enabled": True,
            "rate": 160,
            "volume": 0.9,
            "voice_index": 0
        }

        if os.path.exists(self.config_file):
            try:
                import json
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except Exception as e:
                print(f"⚠️ Config load error: {e}")

        return default_config

    def _initialize_engine(self):
        """初始化TTS引擎"""
        if not self.config["enabled"] or TTS_TYPE != "pyttsx3":
            return

        try:
            # 启动工作线程
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
        except Exception as e:
            print(f"❌ TTS initialization error: {e}")

    def _init_pyttsx3_engine(self):
        """初始化pyttsx3引擎（带容错）"""
        current_time = time.time()

        # 检查冷却时间
        if current_time - self._last_engine_init_time < self._engine_init_cooldown:
            return False

        try:
            if self.engine:
                try:
                    self.engine.stop()
                except:
                    pass
                self.engine = None

            # 重新初始化引擎
            self.engine = pyttsx3.init()

            # 配置引擎
            self.engine.setProperty('rate', self.config["rate"])
            self.engine.setProperty('volume', self.config["volume"])

            # 设置语音
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > self.config["voice_index"]:
                voice_id = voices[self.config["voice_index"]].id
                self.engine.setProperty('voice', voice_id)

            self._engine_error_count = 0
            self._last_engine_init_time = current_time
            print("✅ TTS engine reinitialized successfully")
            return True

        except Exception as e:
            print(f"❌ Engine initialization error: {e}")
            self._engine_error_count += 1
            self._last_engine_init_time = current_time
            return False

    def _worker_loop(self):
        """TTS工作线程循环 - 增强容错性"""
        # 初始化引擎
        if not self._init_pyttsx3_engine():
            print("❌ Failed to initialize TTS engine")
            return

        # 处理TTS队列 - 增强容错性
        consecutive_errors = 0
        max_consecutive_errors = 5

        while self.is_running:
            try:
                # 获取TTS任务 - 增加容错性，不会因为队列空而break
                try:
                    task = self.tts_queue.get(timeout=2.0)  # 增加timeout时间
                except queue.Empty:
                    # 队列为空时继续等待，不退出
                    consecutive_errors = 0  # 重置连续错误计数
                    continue

                # 处理停止信号
                if task is None:
                    print("🔄 TTS received stop signal")
                    break

                text = task.get("text", "")
                if not text:
                    consecutive_errors = 0
                    continue

                # 检查引擎状态
                if not self.engine:
                    print("⚠️ Engine not available, attempting to reinitialize...")
                    if self._init_pyttsx3_engine():
                        print("✅ Engine reinitialized successfully")
                    else:
                        print("❌ Engine reinitialization failed, skipping task")
                        consecutive_errors += 1
                        if consecutive_errors >= max_consecutive_errors:
                            print("❌ Too many consecutive errors, attempting full reset...")
                            time.sleep(3.0)
                            consecutive_errors = 0
                        continue

                # 执行TTS播报
                try:
                    with self._lock:
                        self._current_speaking = True

                    print(f"🔊 Speaking: {text[:30]}...")
                    self.engine.say(text)
                    self.engine.runAndWait()

                    # 播报成功，重置错误计数
                    consecutive_errors = 0

                    # 完成后稍作停顿
                    time.sleep(0.5)

                except Exception as e:
                    print(f"❌ TTS speaking error: {e}")
                    consecutive_errors += 1

                    # 尝试重新初始化引擎
                    if consecutive_errors >= 2:
                        print("⚠️ Multiple TTS errors, reinitializing engine...")
                        if self._init_pyttsx3_engine():
                            consecutive_errors = 0
                        else:
                            print("❌ Engine reinitialization failed")

                    # 如果连续错误过多，暂停一段时间
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"❌ Too many consecutive TTS errors ({consecutive_errors}), pausing...")
                        time.sleep(5.0)
                        consecutive_errors = 0

                finally:
                    with self._lock:
                        self._current_speaking = False

                # 标记任务完成
                try:
                    self.tts_queue.task_done()
                except:
                    pass

            except Exception as e:
                print(f"❌ TTS worker loop error: {e}")
                consecutive_errors += 1

                # 如果是严重错误，暂停并尝试恢复
                if consecutive_errors >= max_consecutive_errors:
                    print("❌ Critical TTS error, attempting recovery...")
                    time.sleep(3.0)

                    # 尝试重新初始化引擎
                    if self._init_pyttsx3_engine():
                        consecutive_errors = 0
                        print("✅ TTS recovery successful")
                    else:
                        print("❌ TTS recovery failed")

                continue

        # 清理资源
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass

        with self._lock:
            self._current_speaking = False

        print("✅ TTS worker loop ended")

    def speak_text(self, text: str) -> bool:
        """说话（异步，增强容错性）"""
        if not self.config["enabled"] or not text.strip():
            return False

        if not self.is_running:
            print("❌ TTS not running")
            return False

        if not self.worker_thread or not self.worker_thread.is_alive():
            print("❌ TTS worker thread not active")
            return False

        try:
            # 添加到队列（增强容错性）
            text = text.strip()
            if len(text) > 500:  # 限制文本长度
                text = text[:500] + "..."

            self.tts_queue.put({"text": text}, timeout=1.0)
            return True

        except queue.Full:
            print("⚠️ TTS queue is full, clearing old tasks...")
            # 清空队列中的旧任务
            while not self.tts_queue.empty():
                try:
                    self.tts_queue.get_nowait()
                except queue.Empty:
                    break

            # 重新尝试添加
            try:
                self.tts_queue.put({"text": text}, timeout=0.5)
                return True
            except:
                return False

        except Exception as e:
            print(f"❌ TTS queue error: {e}")
            return False

    def speak_command(self, command: str) -> bool:
        """播报识别到的命令"""
        if not command:
            return False

        speak_text = f"{command}"
        return self.speak_text(speak_text)

    def speak_status(self, status: str) -> bool:
        """播报状态信息"""
        if not status:
            return False

        return self.speak_text(status)

    def is_speaking(self) -> bool:
        """检查是否正在播报"""
        with self._lock:
            return self._current_speaking

    def get_queue_size(self) -> int:
        """获取队列大小"""
        return self.tts_queue.qsize()

    def clear_queue(self):
        """清空TTS队列"""
        while not self.tts_queue.empty():
            try:
                self.tts_queue.get_nowait()
            except queue.Empty:
                break
        print("✅ TTS queue cleared")

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """获取可用语音"""
        voices = []

        if TTS_TYPE == "pyttsx3":
            try:
                temp_engine = pyttsx3.init()
                pyttsx3_voices = temp_engine.getProperty('voices')

                for i, voice in enumerate(pyttsx3_voices):
                    voices.append({
                        "index": i,
                        "id": voice.id,
                        "name": voice.name,
                        "languages": getattr(voice, 'languages', [])
                    })

                temp_engine.stop()
            except Exception as e:
                print(f"⚠️ Voice enumeration error: {e}")

        return voices

    def set_rate(self, rate: int) -> bool:
        """设置语速"""
        if rate < 50 or rate > 400:
            return False

        self.config["rate"] = rate
        self._save_config()

        # 更新引擎设置
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
            except:
                pass

        return True

    def set_volume(self, volume: float) -> bool:
        """设置音量"""
        if volume < 0.0 or volume > 1.0:
            return False

        self.config["volume"] = volume
        self._save_config()

        # 更新引擎设置
        if self.engine:
            try:
                self.engine.setProperty('volume', volume)
            except:
                pass

        return True

    def _save_config(self):
        """保存配置"""
        try:
            import json
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Config save error: {e}")

    def stop(self):
        """停止TTS"""
        print("🔄 Stopping TTS...")
        self.is_running = False

        # 清空队列
        self.clear_queue()

        # 发送停止信号
        try:
            self.tts_queue.put(None, timeout=1.0)
        except:
            pass

        # 等待工作线程结束
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
            if self.worker_thread.is_alive():
                print("⚠️ TTS worker thread did not stop gracefully")

        with self._lock:
            self._current_speaking = False

        print("✅ TTS stopped")

    def get_engine_info(self) -> Dict[str, Any]:
        """获取引擎信息"""
        return {
            "engine_type": TTS_TYPE,
            "enabled": self.config["enabled"],
            "running": self.is_running,
            "speaking": self._current_speaking,
            "queue_size": self.tts_queue.qsize(),
            "error_count": self._engine_error_count,
            "worker_alive": self.worker_thread.is_alive() if self.worker_thread else False,
            "settings": {
                "rate": self.config["rate"],
                "volume": self.config["volume"],
                "voice_index": self.config["voice_index"]
            }
        }