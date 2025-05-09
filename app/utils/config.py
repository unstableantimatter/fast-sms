"""
Configuration utility for the Fast SMS Alert System.
"""

import os
import json
from typing import Dict, List, Any, Optional
from PyQt5.QtCore import QSettings


class Config:
    """
    Handles application configuration storage and retrieval.
    Uses QSettings for platform-specific storage.
    """
    
    def __init__(self):
        """Initialize the config utility with default values."""
        self.settings = QSettings("FastSMS", "AlertSystem")
        self.default_values = {
            # TextBelt settings
            "textbelt_api_key": "textbelt",  # Default is free tier
            "sms_recipients": [],
            
            # File monitor settings
            "last_file_path": "",
            "patterns": [],
            "custom_message": "",
            
            # UI settings
            "theme": "dark",
            "window_geometry": None,
            "window_state": None,
        }
    
    def save_sms_settings(self, 
                          textbelt_api_key: str,
                          sms_recipients: List[str]) -> None:
        """
        Save SMS notification settings.
        
        Args:
            textbelt_api_key: TextBelt API key
            sms_recipients: List of phone numbers
        """
        self.settings.setValue("textbelt_api_key", textbelt_api_key)
        self.settings.setValue("sms_recipients", json.dumps(sms_recipients))
    
    def load_sms_settings(self) -> Dict[str, Any]:
        """
        Load SMS notification settings.
        
        Returns:
            Dict containing SMS settings
        """
        return {
            "textbelt_api_key": self.settings.value("textbelt_api_key", self.default_values["textbelt_api_key"]),
            "sms_recipients": json.loads(self.settings.value("sms_recipients", "[]")) if self.settings.value("sms_recipients") else []
        }
    
    def save_monitor_settings(self, file_path: str, patterns: List[str], custom_message: str = "") -> None:
        """
        Save file monitor settings.
        
        Args:
            file_path: Path to the file to monitor
            patterns: List of patterns to look for
            custom_message: Custom message to include in SMS alerts
        """
        self.settings.setValue("last_file_path", file_path)
        self.settings.setValue("patterns", json.dumps(patterns))
        self.settings.setValue("custom_message", custom_message)
    
    def load_monitor_settings(self) -> Dict[str, Any]:
        """
        Load file monitor settings.
        
        Returns:
            Dict containing monitor settings
        """
        return {
            "last_file_path": self.settings.value("last_file_path", self.default_values["last_file_path"]),
            "patterns": json.loads(self.settings.value("patterns", "[]")) if self.settings.value("patterns") else [],
            "custom_message": self.settings.value("custom_message", self.default_values["custom_message"])
        }
    
    def save_ui_settings(self, theme: str, geometry: bytes, state: bytes) -> None:
        """
        Save UI settings.
        
        Args:
            theme: UI theme name
            geometry: Window geometry
            state: Window state
        """
        self.settings.setValue("theme", theme)
        self.settings.setValue("window_geometry", geometry)
        self.settings.setValue("window_state", state)
    
    def load_ui_settings(self) -> Dict[str, Any]:
        """
        Load UI settings.
        
        Returns:
            Dict containing UI settings
        """
        return {
            "theme": self.settings.value("theme", self.default_values["theme"]),
            "window_geometry": self.settings.value("window_geometry", self.default_values["window_geometry"]),
            "window_state": self.settings.value("window_state", self.default_values["window_state"])
        }
    
    def clear_all_settings(self) -> None:
        """Clear all saved settings and reset to defaults."""
        self.settings.clear()
    
    def clear_section(self, section: str) -> None:
        """
        Clear settings for a specific section.
        
        Args:
            section: Name of the section to clear (sms, monitor, ui)
        """
        if section == "sms":
            self.settings.remove("textbelt_api_key")
            self.settings.remove("sms_recipients")
        elif section == "monitor":
            self.settings.remove("last_file_path")
            self.settings.remove("patterns")
            self.settings.remove("custom_message")
        elif section == "ui":
            self.settings.remove("theme")
            self.settings.remove("window_geometry")
            self.settings.remove("window_state") 