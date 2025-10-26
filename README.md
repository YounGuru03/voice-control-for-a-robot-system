# Voice Control For A Robot System - README

完全本地离线的语音识别指令控制系统。基于Whisper模型，支持多说话人识别与训练。

## 目录

1. [快速开始](#快速开始)
2. [环境配置](#环境配置)
3. [详细使用指南](#详细使用指南)
4. [打包为EXE](#打包为exe)
5. [代码文件详解](#代码文件详解)
6. [系统架构](#系统架构)

---

## 快速开始

### 最小化安装（5分钟）

```bash
# 1. 克隆或下载项目文件到本地目录
cd D:\NTU\EE6008  # 或你的项目目录

# 2. 创建Python虚拟环境
python -m venv venv

# 3. 激活虚拟环境
venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 放置Logo文件（可选）
# 将NTU.png文件放在项目根目录

# 6. 运行程序
python main_app.py
```

首次运行时会自动下载Whisper模型文件（base model, ~141MB），请保持网络连接。

---

## 环境配置

### 系统要求

- Windows 10 或更高版本
- Python 3.8+（推荐3.10或3.11）
- 至少4GB内存
- 麦克风设备
- 互联网连接（仅用于首次下载模型）

### 详细环境搭建步骤

#### 1. 安装Python

从 [python.org](https://www.python.org/downloads/) 下载Python 3.10或3.11

**关键**：安装时勾选"Add Python to PATH"

验证安装：
```bash
python --version
pip --version
```

#### 2. 创建项目目录结构

```
D:\NTU\EE6008\
├── venv/                    # 虚拟环境（自动生成）
├── audio_processor.py       # 音频处理模块
├── command_manager.py       # 指令管理模块
├── speaker_manager.py       # 说话人管理模块
├── main_app.py             # GUI主程序
├── NTU.png                 # Logo文件（建议）
├── commands.json           # 已注册指令（自动生成）
├── speakers.json           # 说话人档案（自动生成）
├── output.txt              # 识别结果输出（自动生成）
└── requirements.txt        # 依赖列表
```

#### 3. 创建虚拟环境

```bash
# 进入项目目录
cd D:\NTU\EE6008

# 创建虚拟环境
python -m venv venv

# Windows下激活
venv\Scripts\activate

# 验证激活（命令行前缀应显示(venv)）
```

#### 4. 安装依赖

创建 `requirements.txt` 文件：

```
faster-whisper>=0.11.0
pyaudio>=0.2.13
numpy>=1.21.0
Pillow>=9.0.0
```

安装依赖：

```bash
pip install -r requirements.txt
```

**可能的问题处理：**

- **PyAudio安装失败**：
  ```bash
  # Windows上使用预编译wheel
  pip install pipwin
  pipwin install pyaudio
  ```

- **Rust编译错误**：升级pip和setuptools
  ```bash
  pip install --upgrade pip setuptools
  ```

#### 5. 验证安装

```bash
python -c "from faster_whisper import WhisperModel; print('✅ Whisper OK')"
python -c "import pyaudio; print('✅ PyAudio OK')"
python -c "from PIL import Image; print('✅ Pillow OK')"
```

---

## 详细使用指南

### 第一次运行

```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行程序
python main_app.py
```

首次启动需要加载Whisper模型（约30-60秒，因人而异）。请等待状态从"Initializing..."变为"⚪ Idle"。

### 核心功能详解

#### 第1步：添加语音指令

1. 点击**Commands**标签页
2. 在"New:"输入框输入指令（如"open door"、"close window"）
3. 点击**Add**按钮或按Enter键
4. 在"Registered"列表中可看到已添加的指令

**建议**：
- 指令用英文表述，简短清晰
- 避免单字符或过长的指令
- 避免相似度高的指令（如"open"和"open door"）

#### 第2步：启动语音识别

1. 点击**Recognition**标签页
2. Speaker下拉列表选择"Auto"（系统自动识别说话人）
3. 点击绿色**▶ Start**按钮
4. 等待状态变为"🔴 Listening for 'susie'"

#### 第3步：说出唤醒词

清晰地说出："**susie**"

系统识别到唤醒词后，状态变为"🟢 Command Mode Ready"

#### 第4步：连续发送指令

无需重复唤醒词，直接说出已注册的指令：
- "open door"
- "close window"  
- "turn on light"

每次说话系统会自动：
- 识别和转写你的语音
- 在Results框显示转写结果
- 如果指令已注册，显示✅和"Saved to output.txt"
- 如果指令未注册，显示❌和"Not in command list"

#### 第5步：停止识别

点击红色**⏹ Stop**按钮立即退出识别模式。

状态恢复到"⚪ Idle"。

#### 第6步：查看识别结果

打开项目目录中的 **output.txt** 文件：

```
[2025-10-26 12:30:45] open door
[2025-10-26 12:30:52] close window
[2025-10-26 12:31:05] turn on light
```

每行代表一条成功识别的指令。**每次点击Start按钮时，output.txt会自动清空**。

### 高级功能：训练模式

用于提高识别准确度，特别是对特定发音。

#### 添加说话人档案

1. 点击**Speakers**标签页
2. 在"Name:"输入框输入说话人名称（如"John"、"Alice"）
3. 点击**Add**按钮
4. 在"Registered"表格中看到新的说话人ID和名称

#### 进行指令训练

1. 点击**Training**标签页
2. 在"Speaker:"下拉列表中选择说话人（或保持"None"进行全局训练）
3. 在指令表格中选择一条指令
4. 点击**Train**按钮
5. 弹出训练窗口显示倒计时（5秒）
6. 倒计时结束后开始录音，请在**5秒内重复说出该指令3-5次**
7. 录音完成后显示训练结果

**训练结果解读**：
- "Recognized 3 times"：系统在你的录音中识别到该指令3次
- "Count: 5"：该指令总共被训练5次
- "Weight: 1.5x"：该指令的识别权重提升到1.5倍（最高2.0倍）

#### 使用Auto Speaker Mode

训练多个说话人后，在Recognition标签页中：
1. Speaker选择"Auto"
2. 启动识别时，系统会自动识别当前说话人
3. 结果显示为"[说话人名称] ✅ 指令"

**准确度提示**：只有经过充分训练的说话人才能准确识别。训练次数越多，识别准确度越高。

### 系统维护

#### 查看使用指南

点击**Guide**标签页，包含：
- 7步详细使用说明
- MIT开源许可证
- 技术致谢

#### 清理缓存

点击**Maintenance**标签页，点击**🗑️ Clear Cache**按钮：
- 清除__pycache__目录
- 清除.cache目录
- **不会删除**commands.json、speakers.json、output.txt

建议定期清理以减少磁盘占用。

### 常见问题排查

**Q: 启动时卡在"Initializing..."**
- A: 系统正在下载并加载Whisper模型，首次需要30-60秒。请等待。

**Q: 说了指令但Results框没显示**
- A: 检查：
  1. 是否先说了"susie"激活系统？
  2. 麦克风是否正常工作？测试：`python -c "import pyaudio"`
  3. 指令是否已在Commands标签页注册？

**Q: 识别不准确**
- A: 尝试：
  1. 清晰地说，不要太快或太慢
  2. 在安静的环境中使用
  3. 使用Training功能训练该指令
  4. 提高权重（通过多次训练）

**Q: output.txt文件在哪**
- A: 在项目根目录（D:\NTU\EE6008\output.txt）。每次点击Start按钮时自动清空。

**Q: 如何导出识别结果**
- A: 直接复制output.txt文件内容或在识别过程中截图Results框。

---

## 打包为EXE

### 安装PyInstaller

```bash
# 激活虚拟环境
venv\Scripts\activate

# 安装PyInstaller
pip install pyinstaller
```

### 创建打包脚本

创建 `build.py` 文件在项目根目录：

```python
import os
import shutil
import subprocess
import sys

def build_exe():
    """打包成EXE文件"""
    
    print("开始打包...")
    
    # 清理之前的构建目录
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # PyInstaller命令
    cmd = [
        'pyinstaller',
        '--onefile',                    # 打包为单个EXE文件
        '--windowed',                   # 不显示控制台窗口
        '--name=VoiceControl',         # 应用名称
        '--icon=NTU.ico',              # 应用图标（如果有的话）
        '--add-data=NTU.png:.',        # 包含Logo文件
        '--hidden-import=faster_whisper',
        '--hidden-import=pyaudio',
        '--hidden-import=PIL',
        'main_app.py'
    ]
    
    # 执行打包
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print("✅ 打包成功！")
        print("EXE文件位置：dist\\VoiceControl.exe")
        print("请将以下文件夹复制到EXE同级目录：")
        print("  - commands.json（如果有的话）")
        print("  - speakers.json（如果有的话）")
    else:
        print("❌ 打包失败，请检查错误信息")
        sys.exit(1)

if __name__ == '__main__':
    build_exe()
```

### 执行打包

```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行打包脚本
python build.py
```

打包过程需要5-15分钟。完成后在 `dist` 目录中生成 `VoiceControl.exe`。

### 部署EXE

创建部署文件夹结构：

```
VoiceControl_App/
├── VoiceControl.exe          # 可执行文件
├── NTU.png                   # Logo文件（从dist复制）
├── commands.json             # 预设指令（可选）
├── speakers.json             # 预设说话人（可选）
└── README.txt               # 使用说明
```

**重要**：
- 首次运行仍需网络连接下载Whisper模型（~141MB）
- 模型文件会缓存在用户的 `%LOCALAPPDATA%` 目录
- 建议在虚拟环境中先运行一次，确保模型已下载，再打包

### 创建便携版本（推荐）

如需完全离线的EXE：

```bash
# 1. 手动下载模型文件到虚拟环境缓存
python -c "from faster_whisper import WhisperModel; m = WhisperModel('base')"

# 2. 找到模型缓存位置（通常在 ~/.cache/huggingface）
# 3. 将整个缓存目录打包到EXE同级目录
# 4. 修改main_app.py设置WHISPER_HOME环境变量指向本地缓存
```

---

## 代码文件详解

### 核心文件速览

```
项目结构分析：
├─ 数据处理层
│  ├─ audio_processor.py      (语音→文字的转换)
│  ├─ command_manager.py      (指令的增删查改+权重管理)
│  └─ speaker_manager.py      (说话人的档案管理)
│
├─ 表现层
│  └─ main_app.py             (GUI + 业务流程编排)
│
├─ 持久化
│  ├─ commands.json           (指令库)
│  ├─ speakers.json           (说话人库)
│  └─ output.txt              (识别结果日志)
```

### 文件1：audio_processor.py

**职责**：负责所有与音频和语音识别相关的操作

**核心类**：AudioProcessor

**关键方法**：

```python
class AudioProcessor:
    def __init__(self, model_size="base", language="en", device="cpu"):
        """
        初始化Whisper模型
        
        参数：
        - model_size: "tiny", "base", "small", "medium", "large"
                     越大识别准确度越高，但速度越慢
        - language: 语言代码，"en"表示英文
        - device: "cpu"或"cuda"，推荐使用cpu避免GPU依赖
        """
        self.model = WhisperModel(model_size, device=device, compute_type="int8")
    
    def record_audio(self, duration=5, sample_rate=16000):
        """
        从麦克风录制音频
        
        工作流程：
        1. 打开PyAudio流连接麦克风
        2. 按块采集音频数据（1024字节/块）
        3. 采集指定时长的数据
        4. 关闭PyAudio流
        5. 转换为numpy数组并归一化
        
        返回：numpy数组 shape=(sample_count,)，范围[-1.0, 1.0]
        """
        # 实现细节：分块采集、数据转换、流处理
    
    def detect_wake_word(self, audio_data, wake_word="susie"):
        """
        检测唤醒词
        
        流程：
        1. 调用Whisper转写音频
        2. 检查转写结果是否包含"susie"
        3. 不区分大小写
        
        返回：True/False
        """
        text = self._transcribe_internal(audio_data, beam_size=1)  # 快速模式
        return wake_word.lower() in text.lower()
    
    def transcribe(self, audio_data, boost_phrases=None):
        """
        转写音频为文本，支持短语增强
        
        短语增强（Phrase Boosting）工作原理：
        - 通过initial_prompt参数告诉Whisper"可能出现的短语"
        - Whisper在转写时会倾向于识别这些短语
        - 适合已知指令集的场景
        
        参数：
        - boost_phrases: 已注册指令列表，按权重排序
        
        返回：转写的文本字符串
        """
        if boost_phrases:
            initial_prompt = ", ".join(boost_phrases[:10])
        else:
            initial_prompt = None
        
        # 使用较高质量的beam_size=5
        result = self.model.transcribe(
            audio_data,
            language="en",
            beam_size=5,
            initial_prompt=initial_prompt
        )
        
        return result["text"].strip()
```

**使用示例**：

```python
from audio_processor import AudioProcessor

# 初始化（首次下载模型，需网络连接）
processor = AudioProcessor(model_size="base")

# 录制3秒音频检测唤醒词
wake_audio = processor.record_audio(duration=3)
if processor.detect_wake_word(wake_audio):
    print("✅ 唤醒词检测成功")
    
    # 录制5秒指令
    cmd_audio = processor.record_audio(duration=5)
    
    # 指令列表（模拟）
    commands = ["open door", "close window", "turn on light"]
    
    # 转写（带短语增强）
    text = processor.transcribe(cmd_audio, boost_phrases=commands)
    print(f"识别结果：{text}")
```

---

### 文件2：command_manager.py

**职责**：管理用户注册的语音指令，实现指令的持久化和权重管理

**核心类**：CommandManager

**关键方法**：

```python
class CommandManager:
    def __init__(self):
        """
        初始化时从commands.json加载已有指令
        若文件不存在，创建空指令库
        """
        self.commands = self._load_commands()
    
    def add_command(self, command_text):
        """
        添加新指令
        
        数据结构：
        {
            "open door": {
                "text": "open door",
                "training_count": 0,
                "weight": 1.0,
                "created_at": "2025-10-26T12:30:45",
                "speaker_training": {}  # {speaker_id: count}
            }
        }
        
        返回：True(成功) 或 False(已存在)
        """
        if command_text in self.commands:
            return False
        
        self.commands[command_text] = {
            "text": command_text,
            "training_count": 0,
            "weight": 1.0,
            "created_at": datetime.now().isoformat(),
            "speaker_training": {}
        }
        
        self._save_commands()
        return True
    
    def add_training(self, command_text, speaker_id=None):
        """
        记录一次训练
        
        功能：
        1. 增加training_count
        2. 更新weight（最高2.0倍）
        3. 如果指定了说话人，记录该说话人的训练
        4. 即时保存到JSON文件
        
        权重计算：weight = min(1.0 + training_count * 0.1, 2.0)
        """
        if command_text not in self.commands:
            return
        
        self.commands[command_text]["training_count"] += 1
        
        # 更新权重
        count = self.commands[command_text]["training_count"]
        self.commands[command_text]["weight"] = min(1.0 + count * 0.1, 2.0)
        
        # 如果指定了说话人，更新说话人训练记录
        if speaker_id:
            speaker_dict = self.commands[command_text]["speaker_training"]
            speaker_dict[speaker_id] = speaker_dict.get(speaker_id, 0) + 1
        
        self._save_commands()
    
    def get_boost_list(self):
        """
        获取用于Phrase Boosting的指令列表
        
        特点：
        - 按weight降序排序（权重高的优先）
        - 只返回指令文本
        - 用于传递给Whisper的initial_prompt
        
        返回：["指令1", "指令2", ...]
        """
        sorted_cmds = sorted(
            self.commands.values(),
            key=lambda x: x["weight"],
            reverse=True
        )
        return [cmd["text"] for cmd in sorted_cmds]
    
    def get_trained_speaker(self, command_text):
        """
        获取某个指令训练次数最多的说话人
        
        用于Auto Speaker Mode自动识别说话人
        
        返回：speaker_id 或 None
        """
        if command_text not in self.commands:
            return None
        
        speaker_training = self.commands[command_text]["speaker_training"]
        
        if not speaker_training:
            return None
        
        # 返回训练次数最多的说话人ID
        return max(speaker_training, key=speaker_training.get)
```

**数据流示意**：

```
用户操作               → CommandManager处理           → 数据持久化
添加"open door"       → add_command()               → commands.json写入
选择"open door"训练    → add_training(speaker_id)    → weight更新+speaker_training记录
获取识别用的指令列表   → get_boost_list()           → 返回按weight排序的列表
检测识别出的说话人     → get_trained_speaker()       → 返回最可能的说话人ID
```

---

### 文件3：speaker_manager.py

**职责**：管理说话人档案，支持多说话人识别

**核心类**：SpeakerManager

**关键方法**：

```python
class SpeakerManager:
    def __init__(self):
        """初始化，从speakers.json加载已有说话人"""
        self.speakers = self._load_speakers()
    
    def add_speaker(self, name):
        """
        添加新说话人
        
        说话人数据结构：
        {
            "A1B2C3D4-E5F6-G7H8": {
                "name": "John",
                "created_at": "2025-10-26T12:30:45"
            }
        }
        
        说话人ID使用UUID确保全局唯一性
        
        返回：生成的speaker_id
        """
        speaker_id = str(uuid.uuid4())[:8]  # 简化UUID显示
        
        self.speakers[speaker_id] = {
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_speakers()
        return speaker_id
    
    def get_all_speakers(self):
        """
        获取所有说话人
        
        返回：{speaker_id: {name, created_at}}字典
        """
        return self.speakers
```

**使用流程**：

```
创建说话人               训练指令              识别时匹配
"John" → ID:A1B2C3D4 → "open door"训练 → 识别到该指令
"Alice"→ ID:E5F6G7H8 → "open door"训练 → Auto mode识别训练次数最多的
```

---

### 文件4：main_app.py

**职责**：GUI应用主程序，编排所有业务流程

**核心类**：VoiceCommandApp

**关键架构**：

```
三状态机制：

STATE_IDLE
  ↓ (用户点击Start)
STATE_LISTENING_FOR_WAKE
  ↓ (检测到"susie")
STATE_COMMAND_MODE
  ↓ (用户点击Stop 或 5次失败)
STATE_IDLE

代码实现：
self.current_state = self.STATE_IDLE

def update_status_display(self):
    """根据当前状态更新UI显示"""
    status_map = {
        self.STATE_IDLE: ("⚪ Idle", THEME["gray"]),
        self.STATE_LISTENING_FOR_WAKE: ("🔴 Listening for 'susie'", "#FF6600"),
        self.STATE_COMMAND_MODE: ("🟢 Command Mode Ready", THEME["button_green"])
    }
```

**核心流程：start_listening()方法**

```python
def start_listening(self):
    """
    触发条件：用户点击Start按钮
    
    执行流程：
    1. 清空output.txt
    2. 启动listen_worker线程
    3. 线程内执行双阶段识别
    """
    
    self.clear_output_file()  # 清空output.txt
    
    self.is_listening = True
    self.current_state = self.STATE_LISTENING_FOR_WAKE
    
    def listen_worker():
        try:
            while self.is_listening:
                # ========== 第一阶段：唤醒词检测 ==========
                wake_audio = self.audio_processor.record_audio(duration=3)
                
                if self.audio_processor.detect_wake_word(wake_audio):
                    self.current_state = self.STATE_COMMAND_MODE
                    
                    # ========== 第二阶段：指令识别 ==========
                    while self.is_listening and self.current_state == self.STATE_COMMAND_MODE:
                        cmd_audio = self.audio_processor.record_audio(duration=5)
                        
                        # 获取boost列表（按权重排序）
                        boost_list = self.command_manager.get_boost_list()
                        
                        # 转写（带短语增强）
                        result = self.audio_processor.transcribe(cmd_audio, boost_list)
                        
                        # ===== 核心：匹配指令 =====
                        matched = self.audio_processor.check_phrase_match(
                            result,
                            self.command_manager.get_all_commands()
                        )
                        
                        if matched:
                            # 成功匹配
                            self.write_to_output(result)  # 写入output.txt
                            self.append_result(f"✅ {result}\n📝 Saved\n")
                            self.failed_match_count = 0
                        else:
                            # 未匹配
                            self.append_result(f"❌ {result}\n⚠️ Not matched\n")
                            self.failed_match_count += 1
                            
                            # 检查失败次数是否达到阈值
                            if self.failed_match_count >= 5:
                                self.current_state = self.STATE_LISTENING_FOR_WAKE
        
        finally:
            # 确保清理资源
            self.on_listening_stopped()
    
    # 在后台线程执行
    threading.Thread(target=listen_worker, daemon=True).start()
```

**GUI结构层级**：

```
VoiceCommandApp (主类)
├─ create_ui()                    → 创建所有UI
│  ├─ create_recognition_tab()   → Recognition标签页
│  ├─ create_commands_tab()      → Commands标签页
│  ├─ create_training_tab()      → Training标签页
│  ├─ create_speakers_tab()      → Speakers标签页
│  ├─ create_guide_tab()         → Guide标签页
│  └─ create_maintenance_tab()   → Maintenance标签页
│
├─ 事件处理
│  ├─ start_listening()          → Start按钮事件
│  ├─ stop_listening()           → Stop按钮事件
│  ├─ add_command()              → Add指令事件
│  ├─ train_command()            → Train训练事件
│  └─ add_speaker()              → Add说话人事件
│
└─ 数据管理
   ├─ self.command_manager       → 指令管理器
   ├─ self.speaker_manager       → 说话人管理器
   └─ self.audio_processor       → 音频处理器
```

**错误处理设计**：

```python
# 三层异常捕获结构
try:
    # 最外层：catch所有异常
    while self.is_listening:
        try:
            # 中层：wake-word循环
            wake_audio = ...
            
            if detected:
                while self.is_listening:
                    try:
                        # 内层：command循环
                        cmd_audio = ...
                        result = self.audio_processor.transcribe(cmd_audio)
                        
                        # ===== 关键：严格的数据验证 =====
                        if result is None:
                            continue
                        if not isinstance(result, str):
                            continue
                        result = result.strip()
                        if not result:
                            continue
                        # 现在result是有效的字符串
                        
                    except Exception as e:
                        print(f"Command error: {e}")
                        continue  # 继续下一轮，不崩溃
        
        except Exception as e:
            print(f"Wake-word error: {e}")
            continue  # 继续下一轮，不崩溃

except Exception as e:
    print(f"Critical error: {e}")

finally:
    # 无论如何都会执行清理
    self.on_listening_stopped()
```

---

### 文件5：commands.json（数据文件）

**结构示例**：

```json
{
  "open door": {
    "text": "open door",
    "training_count": 5,
    "weight": 1.5,
    "created_at": "2025-10-26T12:30:45.123456",
    "speaker_training": {
      "A1B2C3D4": 3,
      "E5F6G7H8": 2
    }
  },
  "close window": {
    "text": "close window",
    "training_count": 2,
    "weight": 1.2,
    "created_at": "2025-10-26T12:35:00.654321",
    "speaker_training": {
      "A1B2C3D4": 2
    }
  }
}
```

**字段说明**：
- `text`：指令文本
- `training_count`：总训练次数
- `weight`：识别权重倍数，用于phrase boosting
- `created_at`：创建时间戳，用于审计
- `speaker_training`：各说话人的训练次数记录

---

### 文件6：speakers.json（数据文件）

**结构示例**：

```json
{
  "A1B2C3D4": {
    "name": "John",
    "created_at": "2025-10-26T11:00:00.123456"
  },
  "E5F6G7H8": {
    "name": "Alice",
    "created_at": "2025-10-26T11:05:30.654321"
  }
}
```

---

### 文件7：output.txt（输出文件）

**内容示例**：

```
[2025-10-26 12:30:45] open door
[2025-10-26 12:30:52] close window
[2025-10-26 12:31:05] turn on light
```

**特性**：
- 每次点击Start按钮时自动清空
- 只记录成功匹配的指令
- 时间戳精确到秒
- 用于外部系统的指令接收

---

## 系统架构

### 数据流向图

```
麦克风
  ↓
record_audio()
  ↓ (numpy数组)
detect_wake_word() 或 transcribe()
  ↓ (字符串)
check_phrase_match()
  ↓ (匹配状态)
  ├─ 成功 → write_to_output() → output.txt
  │        → append_result() → GUI显示
  │        → update权重
  │
  └─ 失败 → append_result() → GUI显示
           → failed_match_count++
```

### 模块依赖关系

```
main_app.py (GUI层)
├─ imports audio_processor
├─ imports command_manager
└─ imports speaker_manager

audio_processor.py (音频层)
├─ uses PyAudio (麦克风)
├─ uses Whisper (模型)
└─ uses NumPy (数据处理)

command_manager.py (指令管理)
└─ uses JSON (持久化)

speaker_manager.py (说话人管理)
└─ uses JSON + UUID (持久化)
```

### 关键设计模式

**1. 状态机模式**
- 用于管理识别过程中的三个状态
- 清晰的状态转移条件
- 易于调试和扩展

**2. 模块化架构**
- 音频处理、业务逻辑、GUI表现分离
- 低耦合、高内聚
- 便于单元测试

**3. 多线程设计**
- GUI线程（主线程，Tkinter）
- 音频处理线程（后台线程，listen_worker）
- 通过root.after()安全跨线程更新GUI

**4. 异常处理分层**
- 第一层：操作异常（record_audio失败）
- 第二层：数据验证（transcribe返回值异常）
- 第三层：线程异常（listen_worker崩溃）
- 第四层：资源清理（finally块）

---

## 常见扩展方向

### 添加新的识别语言

修改 `audio_processor.py` 的 `__init__` 方法：

```python
def __init__(self, language="en"):  # 改为"zh"表示中文
    self.language = language
    # 后续transcribe()会使用此语言参数
```

### 添加命令执行功能

修改 `main_app.py` 的 `start_listening()` 方法：

```python
if matched:
    self.execute_command(result)  # 新增执行逻辑

def execute_command(self, command_text):
    """根据识别的指令执行对应操作"""
    if command_text == "open door":
        # 调用外部API或系统命令
        os.system("start C:\\path\\to\\door_app.exe")
    # ... 更多指令处理
```

### 添加网络上报

在 `write_to_output()` 后添加：

```python
def report_to_server(self, command_text):
    """将识别结果上报到服务器"""
    import requests
    requests.post(
        "http://your-server/api/command",
        json={"command": command_text, "timestamp": datetime.now()}
    )
```

---

## 贡献指南

### 代码规范

- 使用4个空格缩进
- 函数和类都需要docstring
- 遵循PEP 8风格

### 本地开发

```bash
# 创建开发分支
git checkout -b feature/your-feature

# 提交前确保本地测试通过
python main_app.py

# 提交代码
git commit -m "描述你的改动"
git push origin feature/your-feature
```

---

## 许可证

MIT License - 详见项目内LICENSE文件

---

## 技术支持

遇到问题？检查以下资源：

1. 本README的"常见问题排查"部分
2. Guide标签页的使用说明
3. Terminal的错误信息
4. 项目目录的commands.json和speakers.json确认数据格式

---

**版本**：1.0  
**最后更新**：2025-10-26  
**维护者**：NTU EEE MSc Group
