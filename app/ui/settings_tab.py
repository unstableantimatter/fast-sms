"""
Settings tab for the application.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QTextEdit, QPushButton, 
    QGroupBox, QComboBox, QMessageBox, QCheckBox,
    QToolButton, QDialog, QDialogButtonBox, QListWidget,
    QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QTextCharFormat, QTextCursor

from app.core.sms_sender import SMSSender


class PhoneNumberValidator:
    """Helper class to validate phone numbers."""
    
    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, str, str]:
        """
        Validate a phone number according to TextBelt's E.164 format.
        
        Args:
            phone: The phone number to validate
            
        Returns:
            Tuple[bool, str, str]: (is_valid, formatted_number, error_message)
        """
        # Remove all non-digit characters except leading '+'
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Handle empty or very short phone numbers
        if not digits_only or len(digits_only) < 8:
            return False, phone, "Too few digits (min 8)"
        
        # Handle very long phone numbers (likely a mistake)
        if len(digits_only) > 15:
            return False, phone, "Too many digits (max 15)"
        
        # Format the number according to E.164 format
        if phone.startswith('+'):
            # Already has a plus, just remove any non-digit characters except the leading +
            formatted = '+' + digits_only
        else:
            # No plus sign, need to add proper country code
            if digits_only.startswith('1') and len(digits_only) >= 10:
                # Looks like a US/Canada number with country code
                formatted = '+' + digits_only
            elif len(digits_only) == 10:
                # 10-digit number without country code, assume US/Canada
                formatted = '+1' + digits_only
            else:
                # Not clearly a US number and no country code specified
                return False, phone, "Missing country code (use +XX format)"
        
        return True, formatted, "Valid number"


class PhoneEntryDialog(QDialog):
    """Dialog for entering and validating a phone number."""
    
    def __init__(self, parent=None, initial_number=""):
        """Initialize the dialog."""
        super().__init__(parent)
        self.setWindowTitle("Add Phone Number")
        self.setMinimumWidth(400)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Form layout for inputs
        form_layout = QFormLayout()
        
        # Phone number input
        self.phone_input = QLineEdit(initial_number)
        self.phone_input.setPlaceholderText("e.g., +12345678900")
        self.phone_input.textChanged.connect(self.validate_input)
        form_layout.addRow("Phone Number:", self.phone_input)
        
        # Validation status
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        form_layout.addRow("", self.status_label)
        
        # Add form to main layout
        layout.addLayout(form_layout)
        
        # Format tips
        tips_label = QLabel(
            "<b>Phone Number Format Tips:</b><br>"
            "• Use international format with country code (E.164 format)<br>"
            "• Start with + followed by country code (e.g., +1 for US/Canada)<br>"
            "• US/Canada numbers: +1 followed by 10 digits<br>"
            "• Include only digits and + symbol"
        )
        tips_label.setStyleSheet("font-size: 11px; color: #6c757d;")
        tips_label.setWordWrap(True)
        layout.addWidget(tips_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initial validation
        self.validate_input()
        
        # Store the validated number
        self.validated_number = ""
    
    def validate_input(self):
        """Validate the phone number input."""
        phone = self.phone_input.text().strip()
        is_valid, formatted, message = PhoneNumberValidator.validate_phone_number(phone)
        
        if is_valid:
            self.status_label.setText(f"✓ {message}: {formatted}")
            self.status_label.setStyleSheet("color: green;")
            self.validated_number = formatted
        else:
            self.status_label.setText(f"❌ {message}")
            self.status_label.setStyleSheet("color: red;")
            self.validated_number = ""
    
    def accept(self):
        """Handle dialog acceptance."""
        if not self.validated_number:
            QMessageBox.warning(
                self,
                "Invalid Phone Number",
                "Please enter a valid phone number in international format."
            )
            return
        
        super().accept()
    
    def get_validated_number(self) -> str:
        """Get the validated phone number."""
        return self.validated_number


class EnhancedRecipientsList(QWidget):
    """Custom widget for managing a list of phone number recipients."""
    
    numbers_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        """Initialize the widget."""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Recipients list
        self.recipients_list = QListWidget()
        self.recipients_list.setAlternatingRowColors(True)
        layout.addWidget(self.recipients_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Number")
        self.add_button.clicked.connect(self.add_number)
        buttons_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_number)
        buttons_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_number)
        buttons_layout.addWidget(self.remove_button)
        
        layout.addLayout(buttons_layout)
    
    def add_number(self):
        """Add a new phone number."""
        dialog = PhoneEntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            number = dialog.get_validated_number()
            if number:
                item = QListWidgetItem(number)
                item.setData(Qt.UserRole, number)  # Store raw number
                self.recipients_list.addItem(item)
                self.emit_numbers_changed()
    
    def edit_number(self):
        """Edit the selected phone number."""
        selected_items = self.recipients_list.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a phone number to edit."
            )
            return
        
        selected_item = selected_items[0]
        current_number = selected_item.text()
        
        dialog = PhoneEntryDialog(self, current_number)
        if dialog.exec_() == QDialog.Accepted:
            number = dialog.get_validated_number()
            if number:
                selected_item.setText(number)
                selected_item.setData(Qt.UserRole, number)
                self.emit_numbers_changed()
    
    def remove_number(self):
        """Remove the selected phone number."""
        selected_items = self.recipients_list.selectedItems()
        if not selected_items:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a phone number to remove."
            )
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            "Are you sure you want to remove this phone number?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for item in selected_items:
                self.recipients_list.takeItem(self.recipients_list.row(item))
            self.emit_numbers_changed()
    
    def set_numbers(self, numbers: List[str]):
        """Set the list of phone numbers."""
        self.recipients_list.clear()
        valid_count = 0
        
        for number in numbers:
            is_valid, formatted, _ = PhoneNumberValidator.validate_phone_number(number)
            if is_valid:
                item = QListWidgetItem(formatted)
                item.setData(Qt.UserRole, formatted)
                self.recipients_list.addItem(item)
                valid_count += 1
            else:
                # Add invalid numbers with warning
                item = QListWidgetItem(f"⚠️ {number} (invalid)")
                item.setData(Qt.UserRole, number)
                item.setForeground(QBrush(QColor("red")))
                self.recipients_list.addItem(item)
        
        if numbers and valid_count < len(numbers):
            QMessageBox.warning(
                self,
                "Invalid Phone Numbers",
                f"Some phone numbers are invalid or not properly formatted ({valid_count}/{len(numbers)} valid).\n"
                "Please edit them to ensure they're in E.164 format (+[country code][number])."
            )
    
    def get_numbers(self) -> List[str]:
        """Get the list of phone numbers."""
        numbers = []
        for i in range(self.recipients_list.count()):
            item = self.recipients_list.item(i)
            number = item.data(Qt.UserRole)
            # Only include items that don't have the warning icon
            if not item.text().startswith("⚠️"):
                numbers.append(number)
        return numbers
    
    def emit_numbers_changed(self):
        """Emit the numbers_changed signal."""
        self.numbers_changed.emit(self.get_numbers())


class SettingsTab(QWidget):
    """Settings tab for configuring SMS notifications."""
    
    # Define signals
    settings_saved = pyqtSignal(dict)
    status_update = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize the settings tab."""
        super().__init__(parent)
        self.sms_sender = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("SMS Notification Settings")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #007BFF;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # TextBelt Settings group
        textbelt_group = QGroupBox("TextBelt Configuration")
        textbelt_layout = QFormLayout()
        textbelt_layout.setSpacing(10)
        textbelt_layout.setContentsMargins(15, 20, 15, 15)
        
        # TextBelt API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your TextBelt API Key")
        self.api_key_input.textChanged.connect(self.update_api_key_info)
        textbelt_layout.addRow(QLabel("TextBelt API Key:"), self.api_key_input)
        
        # Free tier info
        self.api_key_info = QLabel("")
        self.api_key_info.setWordWrap(True)
        self.api_key_info.setStyleSheet("font-size: 11px; color: #6c757d;")
        textbelt_layout.addRow("", self.api_key_info)
        
        textbelt_group.setLayout(textbelt_layout)
        main_layout.addWidget(textbelt_group)
        
        # Recipients group
        recipients_group = QGroupBox("SMS Recipients")
        recipients_layout = QVBoxLayout()
        recipients_layout.setSpacing(10)
        recipients_layout.setContentsMargins(15, 20, 15, 15)
        
        # Instructions
        instructions = QLabel(
            "Add phone numbers in E.164 format with country code. Example: +12125551234"
        )
        instructions.setWordWrap(True)
        recipients_layout.addWidget(instructions)
        
        # Enhanced recipients list
        self.recipients_widget = EnhancedRecipientsList()
        recipients_layout.addWidget(self.recipients_widget)
        
        recipients_group.setLayout(recipients_layout)
        main_layout.addWidget(recipients_group)

        # API Information group
        info_group = QGroupBox("TextBelt Information")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(15, 20, 15, 15)
        
        # TextBelt info
        info_label = QLabel(
            "<b>TextBelt Pricing Information:</b><br>"
            "• Free tier: 1 message/day with 'textbelt' API key (includes attribution)<br>"
            "• Note: Free SMS is not available in some countries (including US) due to abuse<br>"
            "• Paid tier: Starting at $0.01-$0.05 per message<br>"
            "• For more information or to purchase credits, visit <a href='https://textbelt.com'>https://textbelt.com</a>"
        )
        info_label.setOpenExternalLinks(True)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 11px;")
        info_layout.addWidget(info_label)
        
        # Phone number format info
        format_label = QLabel(
            "<b>Phone Number Format Requirements:</b><br>"
            "• All numbers must be in E.164 format (international format)<br>"
            "• Format: +[country code][phone number]<br>"
            "• Examples: +12125551234 (US), +447700900123 (UK), +33612345678 (France)<br>"
            "• The + symbol is required before the country code"
        )
        format_label.setWordWrap(True)
        format_label.setStyleSheet("font-size: 11px;")
        info_layout.addWidget(format_label)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Test connection button
        self.test_button = QPushButton("Test Connection")
        self.test_button.setIcon(self.style().standardIcon(self.style().SP_DialogApplyButton))
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)
        
        # Save settings button
        self.save_button = QPushButton("Save Settings")
        self.save_button.setIcon(self.style().standardIcon(self.style().SP_DialogSaveButton))
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
        # Spacer
        main_layout.addStretch()

        # Set default value and update info
        self.api_key_input.setText("textbelt")
        self.update_api_key_info("textbelt")
    
    def update_api_key_info(self, text=None):
        """
        Update API key information based on current input.
        
        Args:
            text: Optional text from textChanged signal
        """
        if text is None:
            text = self.api_key_input.text().strip()
        
        is_free_tier = (text.lower() == "textbelt")
        
        if is_free_tier:
            self.api_key_info.setText(
                "Using free tier with 'textbelt' API key provides 1 free SMS per day with TextBelt attribution. "
                "Note that free SMS are disabled for US numbers due to abuse prevention."
            )
        else:
            self.api_key_info.setText(
                "Using a paid TextBelt API key. Your account will be charged according to TextBelt's current rates."
            )
    
    def set_sms_sender(self, sms_sender: SMSSender):
        """
        Set the SMS sender instance.
        
        Args:
            sms_sender: The SMS sender instance to use
        """
        self.sms_sender = sms_sender
    
    def load_settings(self, settings: Dict[str, Any]):
        """
        Load settings into the UI.
        
        Args:
            settings: Dictionary containing settings
        """
        self.api_key_input.setText(settings.get("textbelt_api_key", "textbelt"))
        self.update_api_key_info()
        
        # Set recipients in enhanced widget
        recipients = settings.get("sms_recipients", [])
        if recipients:
            self.recipients_widget.set_numbers(recipients)
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get the current settings from the UI.
        
        Returns:
            Dict containing the current settings
        """
        # Get recipients from enhanced widget
        recipients = self.recipients_widget.get_numbers()
        
        return {
            "textbelt_api_key": self.api_key_input.text().strip(),
            "sms_recipients": recipients
        }
    
    def validate_settings(self) -> bool:
        """
        Validate the current settings.
        
        Returns:
            bool: True if settings are valid, False otherwise
        """
        # Check API Key
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(
                self, 
                "Invalid Settings", 
                "Please enter a TextBelt API Key. Use 'textbelt' for free tier (1 SMS/day)."
            )
            return False
        
        # Check if recipients are defined
        recipients = self.recipients_widget.get_numbers()
        
        if not recipients:
            QMessageBox.warning(
                self, 
                "Invalid Settings", 
                "Please add at least one valid phone number to receive SMS notifications."
            )
            return False
        
        # All validation handled by the EnhancedRecipientsList widget
        return True
    
    def test_connection(self):
        """Test the TextBelt connection with the current settings."""
        if not self.validate_settings():
            return
        
        settings = self.get_settings()
        
        # Check if we're using a paid key
        is_paid_key = settings["textbelt_api_key"].lower() != "textbelt"
        is_free_tier = not is_paid_key
        
        # Create a temporary SMS sender for testing
        temp_sender = SMSSender()
        
        # Connect the status update signal
        temp_sender.status_update.connect(self.status_update.emit)
        
        # Configure the sender
        success = temp_sender.configure(
            settings["textbelt_api_key"],
            settings["sms_recipients"]
        )
        
        if success:
            # Test the connection
            if temp_sender.test_connection():
                message = "TextBelt connection test successful!\n\n"
                if is_free_tier:
                    message += (
                        "You are using the free tier ('textbelt' API key).\n"
                        "• Limited to 1 SMS per day\n"
                        "• Messages include TextBelt branding\n"
                        "• Free SMS are not available for US numbers due to abuse prevention"
                    )
                else:
                    message += (
                        "You are using a paid TextBelt API key.\n"
                        "• Your account will be charged per TextBelt's current rates\n"
                        "• No attribution required in messages\n"
                        "• Higher sending limits and better deliverability\n\n"
                        "Note: When testing with your paid key, we added a special 'test' flag to avoid using your credits."
                    )
                
                if is_paid_key and temp_sender.is_free_tier:
                    message += "\n\nWarning: Your key looks like a paid key but was detected as free tier. Please double-check your API key."
                
                QMessageBox.information(
                    self, 
                    "Connection Test", 
                    message
                )
            else:
                if is_free_tier and any("+1" in num for num in settings["sms_recipients"]):
                    message = (
                        "TextBelt connection test failed.\n\n"
                        "It appears you're using the free tier with US phone numbers. "
                        "TextBelt has disabled free SMS for US numbers due to abuse.\n\n"
                        "Solution: Purchase a TextBelt API key at textbelt.com to send SMS to US numbers."
                    )
                else:
                    message = (
                        "TextBelt connection test failed.\n\n"
                        "This could be due to:\n"
                        "• Internet connectivity issues\n"
                        "• Firewall blocking the connection\n"
                        "• TextBelt service being temporarily unavailable\n"
                        "• Free SMS being disabled for your country (if using free tier)\n\n"
                        "Please check your network connection and try again."
                    )
                
                QMessageBox.warning(
                    self, 
                    "Connection Test", 
                    message
                )
        else:
            QMessageBox.critical(
                self, 
                "Configuration Error", 
                "Failed to configure SMS sender. Please check your settings and try again."
            )
    
    def save_settings(self):
        """Save the current settings."""
        if not self.validate_settings():
            return
        
        settings = self.get_settings()
        
        # Configure the SMS sender if it exists
        if self.sms_sender:
            success = self.sms_sender.configure(
                settings["textbelt_api_key"],
                settings["sms_recipients"]
            )
            
            if not success:
                QMessageBox.warning(
                    self, 
                    "Configuration Error", 
                    "Failed to configure SMS sender. Please check your settings and try again."
                )
                return
        
        # Emit settings saved signal
        self.settings_saved.emit(settings)
        
        # Show success message
        QMessageBox.information(
            self, 
            "Settings Saved", 
            "SMS notification settings have been saved successfully."
        )
        
        self.status_update.emit("SMS settings saved successfully") 