"""
File Monitor Module
==================

Monitors text.txt file for changes using watchdog.
Provides callback functionality for file updates.
"""

import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, Optional

class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system events."""
    
    def __init__(self, target_file: str, callback: Callable[[str], None]):
        """
        Initialize the file change handler.
        
        Args:
            target_file: File to monitor
            callback: Function to call when file changes
        """
        self.target_file = os.path.abspath(target_file)
        self.callback = callback
        
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            event_path = os.path.abspath(event.src_path)
            if event_path == self.target_file:
                # Add small delay to ensure file write is complete
                time.sleep(0.1)
                self.callback(event_path)
                
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            event_path = os.path.abspath(event.src_path)
            if event_path == self.target_file:
                # Add small delay to ensure file write is complete
                time.sleep(0.1)
                self.callback(event_path)


class FileMonitor:
    """Monitors a file for changes and provides callbacks."""
    
    def __init__(self, filename: str):
        """
        Initialize the file monitor.
        
        Args:
            filename: Name of the file to monitor
        """
        self.filename = filename
        self.filepath = os.path.abspath(filename)
        self.directory = os.path.dirname(self.filepath)
        
        # Watchdog components
        self.observer = None
        self.event_handler = None
        
        # Callback function
        self.on_file_change = None
        
        # Ensure directory exists
        os.makedirs(self.directory, exist_ok=True)
        
        # Create empty file if it doesn't exist
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write('')
                
    def start_monitoring(self):
        """Start monitoring the file for changes."""
        if self.observer is not None:
            return  # Already monitoring
            
        try:
            # Create event handler
            self.event_handler = FileChangeHandler(
                self.filepath, 
                self._handle_file_change
            )
            
            # Create and start observer
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler, 
                self.directory, 
                recursive=False
            )
            self.observer.start()
            
            print(f"Started monitoring file: {self.filepath}")
            
        except Exception as e:
            print(f"Error starting file monitor: {str(e)}")
            self.observer = None
            
    def stop_monitoring(self):
        """Stop monitoring the file."""
        if self.observer is not None:
            try:
                self.observer.stop()
                self.observer.join(timeout=2.0)
                self.observer = None
                print(f"Stopped monitoring file: {self.filepath}")
            except Exception as e:
                print(f"Error stopping file monitor: {str(e)}")
                
    def _handle_file_change(self, filepath: str):
        """Handle file change events."""
        try:
            if self.on_file_change is not None:
                self.on_file_change(filepath)
        except Exception as e:
            print(f"Error in file change callback: {str(e)}")
            
    def read_file(self) -> Optional[str]:
        """
        Read the current content of the monitored file.
        
        Returns:
            File content or None if error
        """
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return None
            
    def write_file(self, content: str):
        """
        Write content to the monitored file.
        
        Args:
            content: Content to write
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing file: {str(e)}")
            
    def append_to_file(self, content: str):
        """
        Append content to the monitored file.
        
        Args:
            content: Content to append
        """
        try:
            with open(self.filepath, 'a', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Error appending to file: {str(e)}")
            
    def is_monitoring(self) -> bool:
        """
        Check if file monitoring is active.
        
        Returns:
            True if monitoring, False otherwise
        """
        return self.observer is not None and self.observer.is_alive()
        
    def get_file_info(self) -> dict:
        """
        Get information about the monitored file.
        
        Returns:
            Dictionary with file information
        """
        info = {
            'filename': self.filename,
            'filepath': self.filepath,
            'exists': os.path.exists(self.filepath),
            'monitoring': self.is_monitoring()
        }
        
        if info['exists']:
            try:
                stat = os.stat(self.filepath)
                info.update({
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'created': stat.st_ctime
                })
            except:
                pass
                
        return info
        
    def __del__(self):
        """Destructor to clean up resources."""
        self.stop_monitoring()