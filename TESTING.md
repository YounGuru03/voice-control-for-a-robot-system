# Testing Guide - Voice Control System v2.0.0

## Quick Test Checklist

### ✅ Pre-Test Setup
- [ ] Python 3.8+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Microphone connected and working
- [ ] Speakers/headphones connected

---

## 🧪 Test Scenarios

### 1. Application Startup
```bash
python main_voice_app.py
```

**Expected Results:**
- ✅ GUI window opens (800x700)
- ✅ Console shows: "Loading system components..."
- ✅ Console shows: "ModelManager initialized"
- ✅ System status shows model loading
- ✅ "Start Voice Control" button becomes enabled
- ✅ TTS says: "System ready"

**Time:** ~10-15 seconds

---

### 2. Wake Word Detection
1. Click "Start Voice Control"
2. Wait for TTS: "Listening for wake word"
3. Say clearly: **"Susie"**

**Expected Results:**
- ✅ TTS responds: "Wake word detected. Please speak your command"
- ✅ Status changes to "Command Mode"
- ✅ Recognition result shows wake word detected

**Time:** 2-3 seconds response

---

### 3. Command Recognition
After wake word activation:
1. Say: **"open browser"** (or any command from your database)

**Expected Results:**
- ✅ TTS says: "Command recognized: open browser"
- ✅ Command appears in output.txt with timestamp
- ✅ Recognition result shows matched command
- ✅ System returns to listening for wake word

**Time:** 1-2 seconds recognition + TTS

---

### 4. Command Management

#### Add Command
1. Switch to "Commands" tab
2. Enter command: "turn on lights"
3. Click "Add"

**Expected Results:**
- ✅ Command appears in command list
- ✅ Weight initialized (default ~1.0)
- ✅ commands_hotwords.json updated

#### Delete Command
1. Select a command from list
2. Click "Delete"

**Expected Results:**
- ✅ Command removed from list
- ✅ JSON file updated

---

### 5. Training System
1. Switch to "Train" tab
2. Select a command
3. Click "Train"
4. Repeat the command 3-5 times

**Expected Results:**
- ✅ Training count increases
- ✅ Weight value increases
- ✅ Command priority improves

---

### 6. System Status
1. Switch to "System" tab
2. Check displayed information

**Expected Results:**
- ✅ Whisper model status (loaded/loading)
- ✅ TTS engine status (running/stopped)
- ✅ Error tracking (if any errors occurred)
- ✅ Model path shown
- ✅ Last success timestamp

---

### 7. Auto-Return to Standby
1. Start voice control
2. Say wake word "susie"
3. Say 5 unrecognized phrases

**Expected Results:**
- ✅ After 5 failures, TTS says: "Returning to standby mode"
- ✅ System returns to wake word detection
- ✅ Fail counter resets

---

### 8. Stop and Restart
1. Click "Stop Voice Control"
2. Wait 2 seconds
3. Click "Start Voice Control" again

**Expected Results:**
- ✅ Clean stop (no errors)
- ✅ TTS stops speaking
- ✅ Restart successful
- ✅ All functionality works after restart

---

## 🏗️ Build System Test

### Test Executable Creation
```bash
python build.py
```

**Expected Results:**
- ✅ Models pre-downloaded
- ✅ PyInstaller runs without errors
- ✅ `dist/VoiceControl.exe` created
- ✅ File size: ~150-200MB (with base model)

### Test Executable
```bash
.\dist\VoiceControl.exe
```

**Expected Results:**
- ✅ Runs without Python installation
- ✅ All features work as in development
- ✅ Models load from bundled directory
- ✅ No console window (windowed mode)

---

## 🐛 Known Issues & Workarounds

### Issue: TTS Engine Not Available
**Symptom:** Console shows "pyttsx3 not available"
**Fix:** `pip install pyttsx3 --upgrade`

### Issue: Microphone Not Detected
**Symptom:** "No default audio device found"
**Fix:** 
1. Check Windows Sound settings
2. Set default recording device
3. Restart application

### Issue: Model Download Fails
**Symptom:** "Model download error" or timeout
**Fix:**
1. Check internet connection
2. Manually download from HuggingFace
3. Place in `local_models/hf_cache/`

### Issue: Import Errors
**Symptom:** "ModuleNotFoundError"
**Fix:** `pip install -r requirements.txt --force-reinstall`

---

## ⚡ Performance Benchmarks

### Expected Response Times
| Operation | Time | Notes |
|-----------|------|-------|
| Application startup | 10-15s | Includes model loading |
| Wake word detection | 2-3s | After speech ends |
| Command recognition | 1-2s | After speech ends |
| TTS playback | 1-3s | Depends on message length |
| Command add/delete | <1s | Database update |
| Training iteration | 2-3s | Per training sample |

### Resource Usage (Base Model)
- **RAM:** ~400-600MB during operation
- **CPU:** 10-30% during recognition, <5% idle
- **Disk:** ~200MB for application + models

---

## 📊 Test Results Template

```
Voice Control System - Test Results
Date: [DATE]
Tester: [NAME]
Version: 2.0.0

[ ] Application Startup - PASS/FAIL
[ ] Wake Word Detection - PASS/FAIL  
[ ] Command Recognition - PASS/FAIL
[ ] Command Management - PASS/FAIL
[ ] Training System - PASS/FAIL
[ ] System Status - PASS/FAIL
[ ] Auto-Return Standby - PASS/FAIL
[ ] Stop/Restart - PASS/FAIL
[ ] Build System - PASS/FAIL
[ ] Executable Test - PASS/FAIL

Issues Found:
1. [Description]
2. [Description]

Additional Notes:
[Your notes here]
```

---

## 🔍 Debug Mode

To enable verbose logging:

1. Open `audio_engine.py`
2. Find: `DEBUG = False`
3. Change to: `DEBUG = True`
4. Restart application

**Output:** Detailed console logs for all operations

---

## 📝 Test Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| audio_engine.py | Core STT | ✅ Tested |
| tts_engine.py | TTS playback | ✅ Tested |
| command_manager.py | Command CRUD | ✅ Tested |
| model_manager.py | Model loading | ✅ Tested |
| main_voice_app.py | GUI interactions | ✅ Tested |
| build.py | Packaging | ✅ Tested |

---

## ✅ Sign-Off

**Tested By:** _________________  
**Date:** _________________  
**Build:** _________________  
**Result:** PASS / FAIL  

**Reviewer Comments:**
___________________________________
___________________________________
___________________________________

---

**Last Updated:** October 30, 2025  
**Version:** 2.0.0  
**Status:** Ready for Testing
