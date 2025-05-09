import os
import sys
import configparser
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QHBoxLayout, QFileDialog, QComboBox,
                            QTabWidget, QLineEdit, QFormLayout, QCheckBox,
                            QMessageBox)
from PyQt5.QtCore import Qt

from app.core.message_service import MessageService

class MainWindow(QMainWindow):
    def __init__(self, message_service: MessageService):
        super().__init__()
        self.message_service = message_service
        self.setWindowTitle("Fast SMS")
        self.setMinimumSize(800, 600)
        
        # Setup central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Add tabs
        tabs.addTab(self.create_sms_tab(), "SMS")
        tabs.addTab(self.create_discord_tab(), "Discord")
        tabs.addTab(self.create_settings_tab(), "Settings")
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def create_sms_tab(self):
        """Create the SMS tab"""
        # ... existing SMS UI code ...
        # This would be the original UI of your application
        sms_widget = QWidget()
        layout = QVBoxLayout(sms_widget)
        
        # Add your existing SMS UI components here
        
        return sms_widget
        
    def create_discord_tab(self):
        """Create the Discord tab for configuration and testing"""
        discord_widget = QWidget()
        layout = QVBoxLayout(discord_widget)
        
        # Discord setup section
        layout.addWidget(QLabel("<h3>Discord Bot Setup</h3>"))
        
        # Token configuration
        token_layout = QHBoxLayout()
        self.discord_token_field = QLineEdit()
        self.discord_token_field.setEchoMode(QLineEdit.Password)
        self.discord_token_field.setPlaceholderText("Enter your Discord Bot Token here")
        
        # Load token from config if available
        config = configparser.ConfigParser()
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
        if os.path.exists(config_file):
            config.read(config_file)
            token = config.get('Messaging', 'DiscordToken', fallback='')
            self.discord_token_field.setText(token)
        
        token_layout.addWidget(QLabel("Bot Token:"))
        token_layout.addWidget(self.discord_token_field, 1)
        
        save_token_btn = QPushButton("Save Token")
        save_token_btn.clicked.connect(self.save_discord_token)
        token_layout.addWidget(save_token_btn)
        
        layout.addLayout(token_layout)
        
        # Enable Discord checkbox
        enable_layout = QHBoxLayout()
        self.enable_discord_checkbox = QCheckBox("Enable Discord messaging")
        if os.path.exists(config_file):
            config.read(config_file)
            is_enabled = config.getboolean('Messaging', 'DiscordEnabled', fallback=False)
            self.enable_discord_checkbox.setChecked(is_enabled)
        
        enable_layout.addWidget(self.enable_discord_checkbox)
        enable_save_btn = QPushButton("Save")
        enable_save_btn.clicked.connect(self.save_discord_enabled)
        enable_layout.addWidget(enable_save_btn)
        enable_layout.addStretch(1)
        
        layout.addLayout(enable_layout)
        
        # Invite URL section
        layout.addWidget(QLabel("<h3>Bot Invite Link</h3>"))
        layout.addWidget(QLabel("Share this link with users to add the bot to their Discord:"))
        
        invite_layout = QHBoxLayout()
        self.invite_url_field = QLineEdit()
        self.invite_url_field.setReadOnly(True)
        self.invite_url_field.setText("https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=274877958144&scope=bot")
        invite_layout.addWidget(self.invite_url_field, 1)
        
        copy_url_btn = QPushButton("Copy URL")
        copy_url_btn.clicked.connect(self.copy_invite_url)
        invite_layout.addWidget(copy_url_btn)
        
        layout.addLayout(invite_layout)
        
        # Registration instructions
        layout.addWidget(QLabel("<h3>User Registration</h3>"))
        layout.addWidget(QLabel("To register, users should:"))
        instructions = """
        1. Add the bot to their Discord using the invite link
        2. Start a direct message with the bot
        3. Send '!register USER_ID' where USER_ID is their app ID
        """
        layout.addWidget(QLabel(instructions))
        
        # Test message section
        layout.addWidget(QLabel("<h3>Test Discord Message</h3>"))
        test_layout = QFormLayout()
        
        self.test_user_id = QLineEdit()
        self.test_message = QLineEdit()
        self.test_message.setText("This is a test message from Fast SMS")
        
        test_layout.addRow("User ID:", self.test_user_id)
        test_layout.addRow("Message:", self.test_message)
        
        layout.addLayout(test_layout)
        
        test_btn = QPushButton("Send Test Message")
        test_btn.clicked.connect(self.send_test_discord_message)
        layout.addWidget(test_btn)
        
        layout.addStretch(1)
        return discord_widget
        
    def create_settings_tab(self):
        """Create the settings tab"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        # Log level selection
        log_layout = QHBoxLayout()
        log_layout.addWidget(QLabel("Log Level:"))
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        
        # Load current log level from config
        config = configparser.ConfigParser()
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
        if os.path.exists(config_file):
            config.read(config_file)
            current_level = config.get('General', 'LogLevel', fallback='INFO')
            index = self.log_level_combo.findText(current_level)
            if index >= 0:
                self.log_level_combo.setCurrentIndex(index)
        
        log_layout.addWidget(self.log_level_combo)
        
        save_log_btn = QPushButton("Save")
        save_log_btn.clicked.connect(self.save_log_level)
        log_layout.addWidget(save_log_btn)
        log_layout.addStretch(1)
        
        layout.addLayout(log_layout)
        layout.addStretch(1)
        
        return settings_widget
    
    def save_discord_token(self):
        """Save the Discord token to the config file"""
        token = self.discord_token_field.text().strip()
        
        config = configparser.ConfigParser()
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
        
        # Create or load config
        if os.path.exists(config_file):
            config.read(config_file)
        
        if 'Messaging' not in config:
            config['Messaging'] = {}
        
        config['Messaging']['DiscordToken'] = token
        
        with open(config_file, 'w') as f:
            config.write(f)
        
        self.statusBar().showMessage("Discord token saved. Restart the application to apply changes.")
    
    def save_discord_enabled(self):
        """Save the Discord enabled setting to the config file"""
        is_enabled = self.enable_discord_checkbox.isChecked()
        
        config = configparser.ConfigParser()
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
        
        # Create or load config
        if os.path.exists(config_file):
            config.read(config_file)
        
        if 'Messaging' not in config:
            config['Messaging'] = {}
        
        config['Messaging']['DiscordEnabled'] = str(is_enabled)
        
        with open(config_file, 'w') as f:
            config.write(f)
        
        self.statusBar().showMessage("Discord settings saved. Restart the application to apply changes.")
    
    def copy_invite_url(self):
        """Copy the invite URL to clipboard"""
        url = self.invite_url_field.text()
        clipboard = QApplication.clipboard()
        clipboard.setText(url)
        self.statusBar().showMessage("Invite URL copied to clipboard")
    
    def send_test_discord_message(self):
        """Send a test message via Discord"""
        user_id = self.test_user_id.text().strip()
        message = self.test_message.text().strip()
        
        if not user_id:
            QMessageBox.warning(self, "Missing Information", "Please enter a User ID")
            return
        
        if not message:
            QMessageBox.warning(self, "Missing Information", "Please enter a message")
            return
        
        # Check if Discord is enabled in the message service
        if 'discord' not in self.message_service.providers:
            QMessageBox.warning(
                self, 
                "Discord Not Enabled", 
                "Discord messaging is not enabled. Please enable it in the settings and restart the application."
            )
            return
        
        # Try to send the message
        results = self.message_service.send_message(user_id, message, providers=['discord'])
        
        if results.get('discord', False):
            QMessageBox.information(self, "Success", f"Test message sent to user ID: {user_id}")
        else:
            QMessageBox.warning(
                self, 
                "Failed", 
                f"Failed to send test message. Make sure the user has registered with the bot."
            )
    
    def save_log_level(self):
        """Save the log level to the config file"""
        log_level = self.log_level_combo.currentText()
        
        config = configparser.ConfigParser()
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
        
        # Create or load config
        if os.path.exists(config_file):
            config.read(config_file)
        
        if 'General' not in config:
            config['General'] = {}
        
        config['General']['LogLevel'] = log_level
        
        with open(config_file, 'w') as f:
            config.write(f)
        
        self.statusBar().showMessage("Log level saved. Restart the application to apply changes.") 