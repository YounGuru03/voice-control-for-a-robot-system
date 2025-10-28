# =====================================================================
# 音频处理模块 - Audio Processor Module
# =====================================================================
# 功能：负责所有音频录制和Whisper模型语音识别操作
# 作者：NTU EEE MSc Group 2025
# 说明：支持faster-whisper和openai-whisper两种后端，自动降级
# =====================================================================

import warnings
import os

# 【配置】抑制不必要的警告信息，保持终端输出清晰
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # TensorFlow日志级别设为ERROR

import numpy as np
import pyaudio

# 【关键】尝试导入faster-whisper（优先），失败则降级到openai-whisper
# faster-whisper使用CTranslate2引擎，支持int8量化，推理速度更快
try:
    from faster_whisper import WhisperModel
    BACKEND = "faster-whisper"
except ImportError:
    print("⚠️ faster-whisper不可用，降级到openai-whisper")
    import whisper
    BACKEND = "openai-whisper"


class AudioProcessor:
    """
    音频处理器类
    
    职责：
    1. 初始化和管理Whisper语音识别模型
    2. 从麦克风录制音频数据
    3. 执行唤醒词检测（快速模式）
    4. 执行语音转文字（标准模式，支持短语增强）
    5. 匹配转写结果与指令列表
    
    设计模式：策略模式（支持多种Whisper后端）
    """

    def __init__(self, model_size="base", language="en", device="cpu"):
        """
        初始化Whisper语音识别模型
        
        参数说明：
            model_size: 模型大小 - "tiny"(39M)，"base"(74M)，"small"(244M)，
                       "medium"(769M)，"large"(1550M)
                       越大越准确但推理越慢，推荐base平衡性能
            language: 语言代码 - "en"(英文)，"zh"(中文)，支持99种语言
            device: 计算设备 - "cpu"或"cuda"，离线系统推荐cpu避免GPU依赖
        
        【关键】模型加载流程：
        1. 首次运行会从HuggingFace下载模型文件（需联网）
        2. 后续运行从本地缓存加载（~/.cache/huggingface）
        3. faster-whisper使用int8量化，内存占用降低75%
        """
        print(f"🔄 正在初始化Whisper模型 (模型大小: {model_size})...")

        # 保存配置参数
        self.model_size = model_size
        self.language = language
        self.device = device

        # 【关键】根据后端类型加载模型
        if BACKEND == "faster-whisper":
            # faster-whisper: CTranslate2引擎 + int8量化
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type="int8"  # 量化计算，加速推理
            )
        else:
            # openai-whisper: 原始PyTorch实现
            self.model = whisper.load_model(model_size, device=device)

        print(f"✅ 模型加载成功 (后端: {BACKEND})")

    def record_audio(self, duration=5, sample_rate=16000):
        """
        从系统麦克风录制音频
        
        参数说明：
            duration: 录制时长（秒），唤醒词检测用3秒，指令识别用5秒
            sample_rate: 采样率（Hz），16000是语音识别标准采样率
        
        返回值：
            numpy数组，shape=(sample_count,)，数据范围[-1.0, 1.0]
            录制失败返回None
        
        【关键】录制流程：
        1. 打开PyAudio音频流连接麦克风
        2. 分块采集音频数据（chunk=1024字节，约64ms延迟）
        3. 采集指定时长的所有数据块
        4. 关闭音频流释放资源
        5. 将原始字节数据转换为float32数组并归一化
        
        数据流：麦克风 → PyAudio → bytes → numpy.int16 → numpy.float32
        """
        print(f"🎤 开始录制音频，时长 {duration} 秒...")

        # 【配置】PyAudio参数设置
        chunk = 1024                    # 缓冲区大小，1024字节 = 约64ms
        format_type = pyaudio.paInt16   # 16位PCM格式
        channels = 1                    # 单声道（语音识别推荐）

        try:
            # 【关键】初始化PyAudio并打开音频流
            p = pyaudio.PyAudio()
            stream = p.open(
                format=format_type,
                channels=channels,
                rate=sample_rate,
                input=True,                      # 输入模式（录音）
                frames_per_buffer=chunk
            )

            # 采集音频数据块
            frames = []
            num_chunks = int(sample_rate / chunk * duration)  # 计算需要的块数
            
            for _ in range(num_chunks):
                data = stream.read(chunk, exception_on_overflow=False)
                frames.append(data)

            # 【关键】清理资源
            stream.stop_stream()
            stream.close()
            p.terminate()

            print("✅ 录制完成")

            # 【数据转换】bytes → numpy.int16 → numpy.float32 (归一化)
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            audio_data = audio_data.astype(np.float32) / 32768.0  # 归一化到[-1, 1]

            return audio_data

        except Exception as e:
            print(f"❌ 录制错误: {e}")
            return None

    def detect_wake_word(self, audio_data, wake_word="susie"):
        """
        检测音频中是否包含唤醒词
        
        参数说明：
            audio_data: 录制的音频数据（numpy数组）
            wake_word: 唤醒词文本，默认"susie"
        
        返回值：
            True: 检测到唤醒词
            False: 未检测到或检测失败
        
        【关键】检测策略：
        1. 使用beam_size=1快速转写模式，降低延迟
        2. 启用VAD(Voice Activity Detection)过滤静音段
        3. 转写结果转小写进行子字符串匹配
        4. 适用于第一阶段快速唤醒检测
        
        性能优化：beam_size=1比beam_size=5快3-4倍
        """
        if audio_data is None:
            return False

        try:
            # 【关键】根据后端执行快速转写
            if BACKEND == "faster-whisper":
                segments, info = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    beam_size=1,        # 快速模式：单beam搜索
                    vad_filter=True     # VAD过滤：跳过静音段
                )
                # 拼接所有segment的文本
                text = " ".join([segment.text for segment in segments])
            else:
                # openai-whisper后端
                result = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    fp16=False          # CPU模式不使用半精度
                )
                text = result["text"]

            text = text.strip().lower()
            print(f"🔍 检测到文本: {text}")

            # 【关键】唤醒词匹配逻辑
            if wake_word.lower() in text:
                print(f"✅ 唤醒词 '{wake_word}' 已检测到！")
                return True

            return False

        except Exception as e:
            print(f"❌ 唤醒词检测错误: {e}")
            return False

    def transcribe(self, audio_data, boost_phrases=None):
        """
        将音频转写为文本，支持短语增强（Phrase Boosting）
        
        参数说明：
            audio_data: 录制的音频数据（numpy数组）
            boost_phrases: 短语列表，用于提高特定短语的识别准确度
        
        返回值：
            转写的文本字符串，失败返回None
        
        【关键】Phrase Boosting机制：
        1. 通过initial_prompt参数将已注册指令传递给Whisper
        2. Whisper在转写时倾向于识别prompt中的短语
        3. 显著提高已知指令的识别准确度（特别是短指令）
        4. 取前10个最高权重的指令作为prompt
        
        【关键】转写质量优化：
        - beam_size=5: 使用5个beam进行搜索，提高准确度
        - vad_filter=True: 过滤静音段，减少误识别
        - initial_prompt: 短语增强，针对已知指令优化
        
        数据流：音频 → Whisper模型 → segments → 拼接文本
        """
        if audio_data is None:
            return None

        try:
            # 【关键】准备短语增强prompt
            initial_prompt = None
            if boost_phrases and len(boost_phrases) > 0:
                # 取前10个短语，用逗号分隔
                initial_prompt = ", ".join(boost_phrases[:10])
                print(f"📋 使用短语增强: {initial_prompt}")

            # 【关键】根据后端执行高质量转写
            if BACKEND == "faster-whisper":
                segments, info = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    beam_size=5,              # 标准模式：5个beam搜索
                    vad_filter=True,          # VAD过滤
                    initial_prompt=initial_prompt  # 短语增强
                )
                # 拼接所有segment
                text = " ".join([segment.text for segment in segments])
            else:
                # openai-whisper后端
                result = self.model.transcribe(
                    audio_data,
                    language=self.language,
                    fp16=False,
                    initial_prompt=initial_prompt
                )
                text = result["text"]

            text = text.strip()
            print(f"📝 转写结果: {text}")

            return text

        except Exception as e:
            print(f"❌ 转写错误: {e}")
            return None

    def check_phrase_match(self, transcribed_text, command_list):
        """
        检查转写文本是否匹配指令列表中的任一指令
        
        参数说明：
            transcribed_text: Whisper转写的文本
            command_list: 已注册的指令列表
        
        返回值：
            匹配的指令文本，未匹配返回None
        
        【关键】匹配策略：
        1. 不区分大小写进行比较
        2. 支持精确匹配：转写文本 == 指令
        3. 支持子字符串匹配：指令 in 转写文本
        4. 适应用户可能说出完整句子的情况
        
        示例：
        - 转写："open door" → 匹配指令"open door"（精确）
        - 转写："please open door now" → 匹配指令"open door"（子串）
        
        数据流：转写文本 → 遍历指令列表 → 返回首个匹配项
        """
        if not transcribed_text or not command_list:
            return None

        transcribed_lower = transcribed_text.lower().strip()

        # 【关键】遍历所有已注册指令进行匹配
        for command in command_list:
            command_lower = command.lower().strip()

            # 精确匹配或子字符串匹配
            if command_lower == transcribed_lower or command_lower in transcribed_lower:
                print(f"✅ 匹配成功: '{command}'")
                return command

        print(f"❌ 未匹配: '{transcribed_text}'")
        return None