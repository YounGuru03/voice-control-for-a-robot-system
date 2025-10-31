# Voice Control System v2 - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Windows 10/11
- Python 3.8+
- Microphone
- Internet connection (for initial setup)

---

## 📥 Installation

### Step 1: Install Dependencies (2 minutes)

```bash
# Install Python packages
pip install faster-whisper numpy pyaudio pywin32

# IMPORTANT: Run pywin32 post-install (as Administrator)
python Scripts/pywin32_postinstall.py -install
```

### Step 2: Verify Installation (1 minute)

```bash
# Test TTS engine
python tts_engine_v2.py

# Expected output:
# ✓ COM initialized
# ✓ SAPI available - X voices detected
# ✓ TTS worker started
```

### Step 3: Run Application (1 minute)

```bash
# Start the application
python main_voice_app.py
```

### Step 4: First Use (1 minute)

1. **Wait for initialization** (3-5 seconds)
2. **Check System tab** - Verify model loaded
3. **Click "Start Listening"**
4. **Say "susie"** (wake word)
5. **Say a command** (e.g., "open browser")

---

## 🎯 Basic Usage

### Wake Word + Command Flow:

```
1. Say "susie" → System beeps → "Command mode active"
2. Say command → System confirms → Executes command
3. Repeat or wait for timeout
```

### Default Commands:

| Command | Action |
|---------|--------|
| "open browser" | Writes to output.txt |
| "close window" | Writes to output.txt |
| "play music" | Writes to output.txt |
| "minimize window" | Writes to output.txt |
| "maximize window" | Writes to output.txt |

---

## 📝 Adding Custom Commands

### Via GUI:
1. Go to **Commands** tab
2. Enter command name
3. Click **Add Command**
4. Done!

### Via File:
1. Edit `commands_hotwords.json`
2. Add new command:
```json
"your command": {
    "weight": 1.0,
    "usage_count": 0,
    "last_used": null
}
```
3. Click **Reload JSON** button

---

## 🔧 Configuration

### TTS Settings (`tts_config.json`):

```json
{
  "voice_index": 0,      // Voice selection (0 = default)
  "rate": 0,             // Speech rate (-10 to 10)
  "volume": 100,         // Volume (0 to 100)
  "enabled": true        // Enable/disable TTS
}
```

### Command Settings (`commands_hotwords.json`):

```json
{
  "commands": {
    "command name": {
      "weight": 1.5,     // Recognition priority
      "usage_count": 0,  // Times used
      "last_used": null  // Last usage timestamp
    }
  }
}
```

---

## 🏗️ Building Executable

### One-Command Build:

```bash
python build_v2.py
```

### Output:
```
dist/VoiceControlSystem.exe  (Ready to distribute!)
```

### Distribution:
- Just copy `VoiceControlSystem.exe`
- No dependencies needed
- Config files created automatically

---

## ❓ Troubleshooting

### Issue: "pywin32 not found"
```bash
# Solution:
pip install pywin32
python Scripts/pywin32_postinstall.py -install
```

### Issue: "No microphone detected"
1. Check microphone is plugged in
2. Set as default in Windows Settings
3. Allow microphone access

### Issue: "Model loading failed"
1. Check internet connection (first time)
2. Models download to `local_models/`
3. Wait for download to complete

### Issue: Application hangs on close
- **Fixed in v2!** Update to latest version
- Use modified `main_voice_app.py`

---

## 🎓 Tips & Tricks

### Tip 1: Improve Recognition
- Speak clearly and at normal speed
- Reduce background noise
- Train frequently-used commands

### Tip 2: Faster Startup
- Models are cached after first run
- Use smaller model (tiny/base) for speed
- Use larger model (medium/large) for accuracy

### Tip 3: Customize TTS
- System tab → Select voice
- Adjust rate and volume
- Test with "Test Voice" button

### Tip 4: Command Training
- Training tab → Select command → Train
- Increases recognition priority
- Use for frequently-used commands

---

## 📊 Model Selection Guide

| Model | Size | Speed | Accuracy | Recommended For |
|-------|------|-------|----------|-----------------|
| tiny | 39MB | Fastest | Basic | Testing |
| base | 74MB | Fast | Good | **Daily use** ⭐ |
| small | 244MB | Medium | High | Quiet environment |
| medium | 769MB | Slow | Very High | Accuracy critical |
| large | 1.5GB | Slowest | Best | Production |

**Recommendation:** Start with `base`, upgrade if needed.

---

## 🔄 Update Guide

### Updating Application:

```bash
# 1. Backup configs
copy commands_hotwords.json commands_hotwords.json.bak
copy tts_config.json tts_config.json.bak

# 2. Update files
# Replace with new versions

# 3. Rebuild
python build_v2.py
```

### Updating Dependencies:

```bash
pip install --upgrade faster-whisper pywin32 numpy pyaudio
```

---

## 📱 GUI Overview

### Listen Tab
- Start/Stop listening
- View recognition results
- Real-time status updates

### Commands Tab
- Add/remove commands
- View command list
- Reload from JSON

### Training Tab
- View usage statistics
- Train commands
- Boost recognition

### System Tab
- Model selection
- Voice configuration
- System status
- Health check

---

## 🎯 Best Practices

### For Users:
1. ✅ Use default wake word "susie"
2. ✅ Speak clearly and naturally
3. ✅ Wait for confirmation beep
4. ✅ Train frequently-used commands
5. ✅ Keep background noise low

### For Developers:
1. ✅ Always use enhanced v2 modules
2. ✅ Test before building exe
3. ✅ Check runtime hooks are included
4. ✅ Verify COM initialization
5. ✅ Test shutdown thoroughly

---

## 📞 Support

### Quick Fixes:
1. **Restart application** - Solves 80% of issues
2. **Check console** - Look for error messages
3. **Rebuild exe** - If TTS not working
4. **Update dependencies** - Keep packages current

### Getting Help:
1. Check error messages in console
2. Review build log files
3. Check system status in System tab
4. Run health check

---

## 🎉 Success Checklist

Ready to use when:
- [x] Application starts without errors
- [x] TTS announces "System ready"
- [x] Wake word "susie" works
- [x] Commands are recognized
- [x] Application closes cleanly
- [x] No console errors

---

## 📚 Next Steps

1. **Learn the system** (30 minutes)
   - Try all default commands
   - Explore all tabs
   - Test TTS voices

2. **Customize** (1 hour)
   - Add your commands
   - Train frequently-used ones
   - Adjust TTS settings

3. **Build executable** (5 minutes)
   - Run `build_v2.py`
   - Test the executable
   - Share with others!

---

## 🏆 You're Ready!

You now have a fully functional voice control system with:
- ✅ Windows TTS integration
- ✅ Offline speech recognition
- ✅ Custom command support
- ✅ GUI for easy management
- ✅ Executable for distribution

**Enjoy your voice-controlled system!** 🎤🤖

---

**Version:** 2.2.0  
**Last Updated:** 2025-10-31  
**Status:** Production Ready ✅
