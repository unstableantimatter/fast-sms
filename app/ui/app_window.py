"""
Main application window for the Fast SMS Alert System.
"""

import os
import sys
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget,
                           QLabel, QStatusBar, QAction, QMenu, QMenuBar, QMessageBox,
                           QSplashScreen, QApplication)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QCloseEvent, QFont

from app.core.file_monitor import FileMonitor
from app.core.sms_sender import SMSSender
from app.utils.config import Config
from app.ui.monitor_tab import MonitorTab
from app.ui.settings_tab import SettingsTab
from app.ui.history_tab import HistoryTab
from app.ui.styles import get_stylesheet


class MainWindow(QMainWindow):
    """Main application window for the Fast SMS Alert System."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Set up core components
        self.file_monitor = FileMonitor()
        self.sms_sender = SMSSender()
        self.config = Config()
        
        # Set window properties
        self.setWindowTitle("Fast SMS Alert System")
        self.setMinimumSize(900, 700)
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        
        # Create UI
        self.create_ui()
        
        # Apply custom styling
        self.apply_styles()
        
        # Load settings
        self.load_all_settings()
        
        # Connect signals
        self.connect_signals()
    
    def create_ui(self):
        """Create the user interface."""
        # Create central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(False)
        
        # Create tabs
        self.monitor_tab = MonitorTab()
        self.settings_tab = SettingsTab()
        self.history_tab = HistoryTab()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.monitor_tab, "Monitor")
        self.tab_widget.addTab(self.history_tab, "History")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_message = QLabel("Ready")
        self.status_bar.addWidget(self.status_message)
        
        # Create menu bar
        self.create_menu()
        
        # Set up core components in tabs
        self.monitor_tab.set_file_monitor(self.file_monitor)
        self.monitor_tab.set_sms_sender(self.sms_sender)
        self.settings_tab.set_sms_sender(self.sms_sender)
        self.history_tab.set_sms_sender(self.sms_sender)
    
    def create_menu(self):
        """Create the application menu."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # New menu item in File menu
        new_action = QAction("&New Monitoring", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_monitoring)
        file_menu.addAction(new_action)
        
        # Quit menu item in File menu
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # About menu item in Help menu
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_styles(self):
        """Apply custom styles to the application."""
        # Load the stylesheet
        ui_settings = self.config.load_ui_settings()
        theme = ui_settings.get("theme", "dark")
        
        # Apply the stylesheet
        self.setStyleSheet(get_stylesheet(theme))
    
    def load_all_settings(self):
        """Load all settings from the configuration."""
        # Load SMS settings
        sms_settings = self.config.load_sms_settings()
        if sms_settings["textbelt_api_key"]:
            # Configure SMS sender
            self.sms_sender.configure(
                sms_settings["textbelt_api_key"],
                sms_settings["sms_recipients"]
            )
        
        # Load and populate UI
        self.settings_tab.load_settings(sms_settings)
        
        # Load monitor settings
        monitor_settings = self.config.load_monitor_settings()
        self.monitor_tab.load_settings(monitor_settings)
        
        # Load UI settings
        ui_settings = self.config.load_ui_settings()
        
        # Restore window geometry if available
        if ui_settings["window_geometry"]:
            self.restoreGeometry(ui_settings["window_geometry"])
        
        # Restore window state if available
        if ui_settings["window_state"]:
            self.restoreState(ui_settings["window_state"])
        
        # Refresh the history tab
        self.history_tab.refresh_history()
    
    def connect_signals(self):
        """Connect signals to slots."""
        # Connect monitor tab signals
        self.monitor_tab.status_update.connect(self.update_status)
        self.monitor_tab.settings_saved.connect(self.save_monitor_settings)
        
        # Connect settings tab signals
        self.settings_tab.status_update.connect(self.update_status)
        self.settings_tab.settings_saved.connect(self.save_sms_settings)
        
        # Connect history tab signals
        self.history_tab.status_update.connect(self.update_status)
    
    def update_status(self, message: str):
        """
        Update the status bar with a message.
        
        Args:
            message: The status message to display
        """
        self.status_message.setText(message)
    
    def save_sms_settings(self, settings: Dict[str, Any]):
        """
        Save SMS settings to the configuration.
        
        Args:
            settings: Dictionary containing SMS settings
        """
        self.config.save_sms_settings(
            settings["textbelt_api_key"],
            settings["sms_recipients"]
        )
    
    def save_monitor_settings(self, settings: Dict[str, Any]):
        """
        Save monitor settings to the configuration.
        
        Args:
            settings: Dictionary containing monitor settings
        """
        self.config.save_monitor_settings(
            settings["last_file_path"],
            settings["patterns"],
            settings["custom_message"]
        )
    
    def save_ui_settings(self):
        """Save UI settings to the configuration."""
        # Get current theme (always dark in this version)
        theme = "dark"
        
        # Save window geometry and state
        self.config.save_ui_settings(
            theme,
            self.saveGeometry(),
            self.saveState()
        )
    
    def new_monitoring(self):
        """Set up a new monitoring configuration."""
        # Check if monitoring is currently active
        if self.file_monitor.running:
            response = QMessageBox.question(
                self,
                "Monitoring Active",
                "Monitoring is currently active. Do you want to stop it and start a new configuration?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if response == QMessageBox.No:
                return
            
            # Stop current monitoring
            self.monitor_tab.stop_monitoring()
        
        # Clear monitor settings
        self.monitor_tab.file_path_input.clear()
        self.monitor_tab.patterns_text.clear()
        self.monitor_tab.custom_message_input.clear()
        
        # Switch to monitor tab
        self.tab_widget.setCurrentIndex(0)
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Fast SMS Alert System",
            "<h2>Fast SMS Alert System</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A simple application for monitoring log files and sending SMS alerts.</p>"
            "<p>Uses TextBelt for SMS notifications (1 free SMS/day).</p>"
            "<p>Delivery status tracking and history features available.</p>"
            "<p>&copy; 2023</p>"
        )
    
    def closeEvent(self, event: QCloseEvent):
        """
        Handle the window close event.
        
        Args:
            event: The close event
        """
        # Stop monitoring if active
        if self.file_monitor.running:
            self.file_monitor.stop()
        
        # Save UI settings
        self.save_ui_settings()
        
        # Accept the event
        event.accept() 