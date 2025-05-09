"""
Monitor tab UI component.
"""

import os
import datetime
from typing import List, Dict, Any, Optional, Callable
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QTextEdit, QPushButton, QGroupBox, 
                            QListWidget, QListWidgetItem, QSplitter, QFileDialog,
                            QFormLayout, QSpacerItem, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QBrush, QFont

from app.core.file_monitor import FileMonitor
from app.core.sms_sender import SMSSender


class MonitorTab(QWidget):
    """Monitor tab for configuring file monitoring and pattern detection."""
    
    # Define signals
    settings_saved = pyqtSignal(dict)
    status_update = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize the monitor tab."""
        super().__init__(parent)
        self.file_monitor = None
        self.sms_sender = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Log File Monitor")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #007BFF;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # File Monitor Settings group
        file_group = QGroupBox("Log File Configuration")
        file_layout = QVBoxLayout()
        file_layout.setSpacing(10)
        file_layout.setContentsMargins(15, 20, 15, 15)
        
        # File path selection
        file_path_layout = QHBoxLayout()
        file_path_layout.setSpacing(10)
        
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Enter the path to the log file to monitor")
        file_path_layout.addWidget(self.file_path_input)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        file_path_layout.addWidget(self.browse_button)
        
        file_layout.addLayout(file_path_layout)
        
        # Pattern detection
        pattern_label = QLabel("Enter keywords or patterns to trigger alerts (one per line):")
        file_layout.addWidget(pattern_label)
        
        self.patterns_text = QTextEdit()
        self.patterns_text.setPlaceholderText("Enter patterns here...\nExample:\nerror\nfailure\ncritical")
        self.patterns_text.setMaximumHeight(100)
        file_layout.addWidget(self.patterns_text)
        
        # Custom message field
        custom_message_label = QLabel("Custom message to include in SMS alerts:")
        file_layout.addWidget(custom_message_label)
        
        self.custom_message_input = QLineEdit()
        self.custom_message_input.setPlaceholderText("Optional: Add additional context to SMS alerts")
        file_layout.addWidget(self.custom_message_input)
        
        # Custom message help text
        help_text = QLabel("The pattern and matched text will be included automatically. This adds extra context.")
        help_text.setStyleSheet("font-size: 11px; color: #6c757d;")
        help_text.setWordWrap(True)
        file_layout.addWidget(help_text)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # Monitoring output
        output_group = QGroupBox("Monitoring Output")
        output_layout = QVBoxLayout()
        output_layout.setSpacing(10)
        output_layout.setContentsMargins(15, 20, 15, 15)
        
        # Activity log
        self.log_list = QListWidget()
        self.log_list.setAlternatingRowColors(True)
        output_layout.addWidget(self.log_list)
        
        # Pattern matches
        match_label = QLabel("Pattern Matches:")
        output_layout.addWidget(match_label)
        
        self.matches_list = QListWidget()
        self.matches_list.setAlternatingRowColors(True)
        output_layout.addWidget(self.matches_list)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_button = QPushButton("Start Monitoring")
        self.start_button.setObjectName("start_button")
        self.start_button.clicked.connect(self.start_monitoring)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.setObjectName("stop_button")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.test_button = QPushButton("Send Test SMS")
        self.test_button.setObjectName("test_button")
        self.test_button.clicked.connect(self.send_test_sms)
        button_layout.addWidget(self.test_button)
        
        main_layout.addLayout(button_layout)
    
    def set_file_monitor(self, file_monitor: FileMonitor):
        """
        Set the file monitor instance.
        
        Args:
            file_monitor: The file monitor instance to use
        """
        self.file_monitor = file_monitor
        
        # Connect signals
        self.file_monitor.file_updated.connect(self.handle_file_update)
        self.file_monitor.pattern_found.connect(self.handle_pattern_found)
        self.file_monitor.status_update.connect(self.handle_status_update)
    
    def set_sms_sender(self, sms_sender: SMSSender):
        """
        Set the SMS sender instance.
        
        Args:
            sms_sender: The SMS sender instance to use
        """
        self.sms_sender = sms_sender
        
        # Connect signals
        self.sms_sender.status_update.connect(self.handle_status_update)
        self.sms_sender.sms_sent.connect(self.handle_sms_sent)
    
    def load_settings(self, settings: Dict[str, Any]):
        """
        Load settings into the UI.
        
        Args:
            settings: Dictionary containing settings
        """
        self.file_path_input.setText(settings.get("last_file_path", ""))
        
        patterns = settings.get("patterns", [])
        if patterns:
            self.patterns_text.setText("\n".join(patterns))
            
        self.custom_message_input.setText(settings.get("custom_message", ""))
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get the current settings from the UI.
        
        Returns:
            Dict containing the current settings
        """
        # Parse patterns (one per line)
        patterns_text = self.patterns_text.toPlainText().strip()
        patterns = [line.strip() for line in patterns_text.split("\n") if line.strip()]
        
        return {
            "last_file_path": self.file_path_input.text().strip(),
            "patterns": patterns,
            "custom_message": self.custom_message_input.text().strip()
        }
    
    def browse_file(self):
        """Open a file dialog to select a log file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Log File",
            "",
            "All Files (*);;Text Files (*.txt);;Log Files (*.log)"
        )
        
        if file_path:
            self.file_path_input.setText(file_path)
    
    def validate_settings(self) -> bool:
        """
        Validate the current settings.
        
        Returns:
            bool: True if settings are valid, False otherwise
        """
        settings = self.get_settings()
        
        # Check for required fields
        if not settings["last_file_path"]:
            QMessageBox.warning(self, "Missing Information", "Please select a log file to monitor.")
            return False
        
        if not settings["patterns"]:
            QMessageBox.warning(self, "Missing Information", "Please enter at least one pattern to detect.")
            return False
        
        # Check if SMS sender is configured
        if not self.sms_sender or not self.sms_sender.is_configured:
            response = QMessageBox.question(
                self,
                "SMS Not Configured",
                "SMS notifications are not configured. Monitoring will work but no SMS alerts will be sent.\n\n"
                "Do you want to continue anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if response == QMessageBox.No:
                return False
        
        return True
    
    def start_monitoring(self):
        """Start monitoring the selected file."""
        if not self.validate_settings():
            return
        
        settings = self.get_settings()
        
        # Configure the file monitor
        if self.file_monitor:
            self.file_monitor.configure(settings["last_file_path"], settings["patterns"])
            self.file_monitor.start()
            
            # Save monitor settings
            self.settings_saved.emit(settings)
            
            # Update UI
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.file_path_input.setEnabled(False)
            self.patterns_text.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.custom_message_input.setEnabled(False)
            
            # Add entry to log
            self.add_log_entry(f"Started monitoring {settings['last_file_path']}")
            
            # Update status
            self.status_update.emit(f"Monitoring started for {settings['last_file_path']}")
    
    def stop_monitoring(self):
        """Stop monitoring the file."""
        if self.file_monitor:
            self.file_monitor.stop()
            
            # Update UI
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.file_path_input.setEnabled(True)
            self.patterns_text.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.custom_message_input.setEnabled(True)
            
            # Add entry to log
            self.add_log_entry("Monitoring stopped")
            
            # Update status
            self.status_update.emit("Monitoring stopped")
    
    def send_test_sms(self):
        """Send a test SMS message."""
        if not self.sms_sender or not self.sms_sender.is_configured:
            QMessageBox.warning(
                self,
                "SMS Not Configured",
                "SMS notifications are not configured. Please configure SMS settings first."
            )
            return
        
        # Use custom message if available
        custom_message = self.custom_message_input.text().strip()
        if custom_message:
            test_message = f"This is a test message from Fast SMS Alert System.\n{custom_message}"
        else:
            test_message = "This is a test message from Fast SMS Alert System."
        
        # Ask user if they want to send as a real message
        response = QMessageBox.question(
            self,
            "Send Real SMS?",
            "Do you want to send a REAL SMS that will be charged to your TextBelt account?\n\n"
            "Yes: Send a real SMS (will count against your quota)\n"
            "No: Just test the connection without sending a real message",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        # Send message based on user's choice
        if response == QMessageBox.Yes:
            # Send a real message
            success = self.sms_sender.send_message(test_message, force_production=True)
            
            if success:
                QMessageBox.information(
                    self,
                    "Test Message Sent",
                    "The test message was sent successfully as a REAL SMS!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Test Message Failed",
                    "Failed to send the real test message. Please check the SMS settings and try again."
                )
        else:
            # Just test the connection
            success = self.sms_sender.test_connection()
            
            if success:
                QMessageBox.information(
                    self,
                    "Connection Test Successful",
                    "The TextBelt connection test was successful.\n\n"
                    "No actual SMS was sent and no quota was used."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Connection Test Failed",
                    "Failed to connect to TextBelt. Please check your internet connection and SMS settings."
                )
    
    def handle_file_update(self, message: str):
        """
        Handle file update event.
        
        Args:
            message: Update message
        """
        self.add_log_entry(message)
    
    def handle_pattern_found(self, pattern: str, line: str):
        """
        Handle pattern found event.
        
        Args:
            pattern: Pattern that was found
            line: Line of text containing the pattern
        """
        self.add_match_entry(pattern, line)
        
        # Get custom message if available
        custom_message = self.custom_message_input.text().strip()
        
        # Create alert message
        if custom_message:
            alert_message = f"{custom_message}\n\nPattern Detected: '{pattern}'\nIn: {line}"
        else:
            alert_message = f"Alert! Pattern Detected: '{pattern}'\nIn: {line}"
        
        # Send SMS alert if configured
        if self.sms_sender and self.sms_sender.is_configured:
            # Always send as a real message in monitoring mode
            self.sms_sender.send_message(alert_message, force_production=True)
        else:
            self.add_log_entry("Pattern found but SMS notifications are not configured.")
    
    def handle_status_update(self, message: str):
        """
        Handle status update event.
        
        Args:
            message: Status message
        """
        self.add_log_entry(message)
        self.status_update.emit(message)
    
    def handle_sms_sent(self, message: str, recipient_count: int):
        """
        Handle SMS sent event.
        
        Args:
            message: The message that was sent
            recipient_count: The number of recipients the message was sent to
        """
        self.add_log_entry(f"SMS alert sent to {recipient_count} recipient(s)")
    
    def add_log_entry(self, message: str):
        """
        Add an entry to the log list.
        
        Args:
            message: The log message
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = QListWidgetItem(f"[{timestamp}] {message}")
        self.log_list.addItem(item)
        self.log_list.scrollToBottom()
    
    def add_match_entry(self, pattern: str, line: str):
        """
        Add a match entry to the matches list.
        
        Args:
            pattern: The pattern that was found
            line: The line of text containing the pattern
        """
        # Format the text nicely with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        display_text = f"[{timestamp}] Pattern: '{pattern}'\nText: {line}"
        
        item = QListWidgetItem(display_text)
        item.setForeground(QBrush(QColor("#DC3545")))  # Red color for alerts
        
        # Make the font bold
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        
        # Add to the list
        self.matches_list.addItem(item)
        self.matches_list.scrollToBottom() 