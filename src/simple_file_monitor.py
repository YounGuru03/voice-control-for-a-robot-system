"""
Simple File Monitor
==================

Lightweight file monitoring for output file changes.
Provides basic file watching capabilities with minimal dependencies.
"""

import os
import time
import threading
from datetime import datetime
from typing import Optional, Callable

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("File monitoring disabled - missing watchdog")

class SimpleFileHandler(FileSystemEventHandler):
    """Handle file system events for the target file"""
    
    def __init__(self, filename: str, callback: Callable = None):
        self.filename = os.path.basename(filename)
        self.callback = callback
        
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory and os.path.basename(event.src_path) == self.filename:
            if self.callback:
                self.callback(event.src_path)

class SimpleFileMonitor:
    """Simple file monitoring for command output files"""
    
    def __init__(self, filename: str, callback: Callable = None):
        """
        Initialize file monitor
        
        Args:
            filename: Path to file to monitor
            callback: Function to call when file changes
        """
        self.filename = filename
        self.callback = callback
        self.observer = None
        self.is_monitoring = False
        self.last_modified = 0
        self.poll_thread = None
        
        # Ensure file exists
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        """Create file if it doesn't exist"""
        try:
            if not os.path.exists(self.filename):
                with open(self.filename, 'w') as f:
                    f.write("# Voice Command Output\n")
                    f.write(f"# Started: {datetime.now().isoformat()}\n\n")
        except Exception as e:
            print(f"Warning: Could not create output file: {e}")
    
    def start_monitoring(self):
        """Start monitoring the file for changes"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        
        if WATCHDOG_AVAILABLE:
            self._start_watchdog_monitoring()
        else:
            self._start_polling_monitoring()
    
    def _start_watchdog_monitoring(self):
        """Start monitoring using watchdog library"""
        try:
            self.observer = Observer()
            handler = SimpleFileHandler(self.filename, self._on_file_changed)
            
            watch_dir = os.path.dirname(os.path.abspath(self.filename)) or '.'
            self.observer.schedule(handler, watch_dir, recursive=False)
            
            self.observer.start()
            print(f"📂 Started file monitoring: {self.filename}")
            
        except Exception as e:
            print(f"❌ Watchdog monitoring failed: {e}")
            self._start_polling_monitoring()
    
    def _start_polling_monitoring(self):
        """Start monitoring using simple polling"""
        print(f"📂 Started polling file monitoring: {self.filename}")
        self.poll_thread = threading.Thread(target=self._poll_file, daemon=True)
        self.poll_thread.start()
    
    def _poll_file(self):
        """Poll file for changes"""
        try:
            self.last_modified = os.path.getmtime(self.filename) if os.path.exists(self.filename) else 0
        except:
            self.last_modified = 0
            
        while self.is_monitoring:
            try:
                if os.path.exists(self.filename):
                    current_mtime = os.path.getmtime(self.filename)
                    if current_mtime > self.last_modified:
                        self.last_modified = current_mtime
                        self._on_file_changed(self.filename)
                        
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"❌ Polling error: {e}")
                time.sleep(2)  # Wait longer on error
    
    def _on_file_changed(self, filepath):
        """Handle file change events"""
        if self.callback:
            try:
                self.callback(filepath)
            except Exception as e:
                print(f"❌ File change callback error: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring the file"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            
        print("📂 Stopped file monitoring")
    
    def get_recent_content(self, lines: int = 10) -> str:
        """
        Get recent content from the monitored file
        
        Args:
            lines: Number of recent lines to return
            
        Returns:
            Recent file content
        """
        try:
            if not os.path.exists(self.filename):
                return "File not found"
                
            with open(self.filename, 'r') as f:
                file_lines = f.readlines()
                
            if not file_lines:
                return "File is empty"
                
            recent_lines = file_lines[-lines:] if len(file_lines) > lines else file_lines
            return ''.join(recent_lines).strip()
            
        except Exception as e:
            return f"Error reading file: {e}"

# Factory function to create file monitor
def create_file_monitor(filename: str, callback: Optional[Callable] = None):
    """
    Create file monitor instance
    
    Args:
        filename: Path to file to monitor
        callback: Optional callback for file changes
        
    Returns:
        SimpleFileMonitor instance
    """
    return SimpleFileMonitor(filename, callback)