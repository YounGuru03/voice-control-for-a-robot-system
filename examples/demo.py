# Example Usage
# =============

# Simple script demonstrating voice control usage

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def demo_nlp_processing():
    """Demonstrate NLP command processing"""
    print("🧠 NLP Processing Demo")
    print("-" * 30)
    
    try:
        from simple_nlp_processor import create_nlp_processor
        nlp = create_nlp_processor()
        
        sample_commands = [
            "open main application",
            "start robot please", 
            "emergency stop now",
            "can you open camera 1",
            "launch lamp system",
            "close camera 2",
            "template alpha",
            "open user admin"
        ]
        
        for command in sample_commands:
            result = nlp.process_text(command)
            print(f"'{command}' → '{result}'")
            
    except ImportError:
        print("NLP processor not available")

def demo_voice_processor():
    """Demonstrate voice processor capabilities"""
    print("\n🎤 Voice Processor Demo") 
    print("-" * 30)
    
    try:
        from simple_voice_processor import create_voice_processor
        processor = create_voice_processor("tiny")  # Use tiny model for demo
        
        if processor.is_model_ready():
            print("✅ Voice processor ready")
            print("💡 In a real scenario, you would:")
            print("   1. Call processor.record_and_transcribe()")
            print("   2. Get transcribed text")
            print("   3. Process with NLP")
        else:
            print("⚠️  Voice processor in demo mode")
            
        processor.cleanup()
        
    except ImportError:
        print("Voice processor not available")

def demo_file_monitor():
    """Demonstrate file monitoring"""
    print("\n📁 File Monitor Demo")
    print("-" * 30)
    
    try:
        from simple_file_monitor import create_file_monitor
        
        # Monitor the output file
        monitor = create_file_monitor("text.txt")
        print("✅ File monitor created")
        print("💡 Monitor would watch 'text.txt' for changes")
        print("   and notify when new commands are written")
        
    except ImportError:
        print("File monitor not available")

if __name__ == "__main__":
    print("🎤 Voice Control System - Examples")
    print("=" * 40)
    
    demo_nlp_processing()
    demo_voice_processor()
    demo_file_monitor()
    
    print("\n🚀 To run the full application:")
    print("   python ../launcher.py")