"""
File monitoring module for watching log files and detecting patterns.
"""

import os
import threading
import time
from typing import Callable, List, Dict, Optional
from PyQt5.QtCore import QObject, pyqtSignal


class FileMonitor(QObject):
    """
    Class to monitor a file for changes and detect patterns.
    Uses QObject to allow for signal emission for UI updates.
    """
    
    # Define signals
    file_updated = pyqtSignal(str)
    pattern_found = pyqtSignal(str, str)
    status_update = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the file monitor."""
        super().__init__()
        self.file_path = ""
        self.patterns = []
        self.running = False
        self.monitor_thread = None
        self.last_position = 0
    
    def configure(self, file_path: str, patterns: List[str]):
        """
        Configure the file monitor with a file path and patterns to detect.
        
        Args:
            file_path: Path to the file to monitor
            patterns: List of string patterns to look for
        """
        self.file_path = file_path
        self.patterns = patterns
        self.last_position = 0
        
        # Reset position if file exists
        if os.path.exists(self.file_path):
            self.last_position = os.path.getsize(self.file_path)
            self.status_update.emit(f"Monitor configured to watch {self.file_path}")
        else:
            self.status_update.emit(f"Warning: File {self.file_path} does not exist yet")
    
    def start(self):
        """Start monitoring the file in a separate thread."""
        if not self.file_path:
            self.status_update.emit("Error: No file path specified")
            return
        
        if self.running:
            self.status_update.emit("Monitor is already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True  # Thread will exit when main program exits
        self.monitor_thread.start()
        
        self.status_update.emit(f"Started monitoring {self.file_path}")
    
    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(1.0)  # Wait up to 1 second for thread to finish
        
        self.status_update.emit("Monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread."""
        while self.running:
            try:
                if not os.path.exists(self.file_path):
                    time.sleep(0.5)
                    continue
                
                current_size = os.path.getsize(self.file_path)
                
                if current_size > self.last_position:
                    # File has grown, read the new data
                    with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        f.seek(self.last_position)
                        new_data = f.read()
                    
                    self.last_position = current_size
                    self.file_updated.emit(f"Read {len(new_data)} new characters")
                    
                    # Process the new data line by line
                    for line in new_data.splitlines():
                        for pattern in self.patterns:
                            if pattern.lower() in line.lower():
                                self.pattern_found.emit(pattern, line)
            
            except Exception as e:
                self.status_update.emit(f"Error: {str(e)}")
                
            # Sleep to avoid high CPU usage
            time.sleep(0.5) 