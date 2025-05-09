#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import logging
import configparser
from PyQt5.QtWidgets import QApplication

from app.core.message_service import MessageService
from app.gui.main_window import MainWindow

def main():
    """Main entry point for the application."""
    # Load configuration
    config = configparser.ConfigParser()
    config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
    
    # Create default config if it doesn't exist
    if not os.path.exists(config_file):
        config['General'] = {
            'LogLevel': 'INFO'
        }
        config['Messaging'] = {
            'SMSEnabled': 'True',
            'DiscordEnabled': 'False',
            'DiscordToken': ''
        }
        with open(config_file, 'w') as f:
            config.write(f)
    
    config.read(config_file)
    
    # Set up logging
    log_level = getattr(logging, config.get('General', 'LogLevel', fallback='INFO'))
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Initialize the message service
    messaging_config = {
        'sms_enabled': config.getboolean('Messaging', 'SMSEnabled', fallback=True),
        'discord_enabled': config.getboolean('Messaging', 'DiscordEnabled', fallback=False),
        'discord_token': config.get('Messaging', 'DiscordToken', fallback=''),
        'sms_config': {}  # Add any SMS-specific config here
    }
    message_service = MessageService(messaging_config)
    
    # Set application details
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern base style
    app.setApplicationName("Fast SMS")
    app.setApplicationDisplayName("Fast SMS Alert System")
    app.setOrganizationName("Fast SMS")
    
    # Create and show main window
    window = MainWindow(message_service)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 