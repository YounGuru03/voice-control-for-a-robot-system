"""Test TTS with multiple messages to verify sanitization works"""
from optimized_tts_manager import OptimizedTTSManager
import time

print("=" * 60)
print("TTS SEQUENTIAL TEST - Testing multiple messages")
print("=" * 60)

tts = OptimizedTTSManager()

print("\n1. Speaking 'ready' status...")
tts.speak_status('ready')
time.sleep(4)

print("\n2. Speaking 'listening' status...")
tts.speak_status('listening')
time.sleep(4)

print("\n3. Speaking 'processing' status...")
tts.speak_status('processing')
time.sleep(4)

print("\n4. Speaking command...")
tts.speak_command('open browser')
time.sleep(4)

print("\n5. Speaking 'not match' status...")
tts.speak_status('not match')
time.sleep(4)

print("\n6. Stopping TTS...")
tts.stop()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
