"""
History tab for viewing SMS message history and delivery status.
"""

import datetime
from typing import Dict, List, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox,
    QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QBrush, QFont

from app.core.sms_sender import SMSSender


class HistoryTab(QWidget):
    """History tab for viewing SMS message history and delivery status."""
    
    # Define signals
    status_update = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize the history tab."""
        super().__init__(parent)
        self.sms_sender = None
        self.auto_refresh = False
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.check_pending_messages)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("SMS Message History")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #007BFF;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # History table
        history_group = QGroupBox("Message History")
        history_layout = QVBoxLayout()
        history_layout.setSpacing(10)
        history_layout.setContentsMargins(15, 20, 15, 15)
        
        # Table for message history
        self.history_table = QTableWidget(0, 5)  # rows, columns
        self.history_table.setHorizontalHeaderLabels([
            "Time", "Recipient", "Message", "Status", "Message ID"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history_table.setAlternatingRowColors(True)
        history_layout.addWidget(self.history_table)
        
        # Buttons for history actions
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.check_status_button = QPushButton("Check Selected Status")
        self.check_status_button.clicked.connect(self.check_selected_status)
        button_layout.addWidget(self.check_status_button)
        
        self.check_all_button = QPushButton("Check All Pending")
        self.check_all_button.clicked.connect(self.check_pending_messages)
        button_layout.addWidget(self.check_all_button)
        
        self.auto_refresh_button = QPushButton("Auto Refresh: Off")
        self.auto_refresh_button.setCheckable(True)
        self.auto_refresh_button.clicked.connect(self.toggle_auto_refresh)
        button_layout.addWidget(self.auto_refresh_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_history)
        button_layout.addWidget(self.refresh_button)
        
        history_layout.addLayout(button_layout)
        
        # Status information
        status_label = QLabel(
            "Note: According to TextBelt documentation, message delivery status updates " 
            "may be delayed by carrier networks. Please allow time for statuses to update."
        )
        status_label.setWordWrap(True)
        status_label.setStyleSheet("font-size: 11px; color: #6c757d;")
        history_layout.addWidget(status_label)
        
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)
    
    def set_sms_sender(self, sms_sender: SMSSender):
        """
        Set the SMS sender instance.
        
        Args:
            sms_sender: The SMS sender instance to use
        """
        self.sms_sender = sms_sender
        
        # Connect signals
        if self.sms_sender:
            self.sms_sender.sms_status_updated.connect(self.update_message_status)
    
    def refresh_history(self):
        """Refresh the message history display."""
        if not self.sms_sender:
            return
        
        # Get message history
        messages = self.sms_sender.get_message_history()
        
        # Clear the table
        self.history_table.clearContents()
        self.history_table.setRowCount(len(messages))
        
        # Fill the table with message history
        for i, message in enumerate(messages):
            # Time
            time_item = QTableWidgetItem(
                datetime.datetime.fromisoformat(message["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            )
            self.history_table.setItem(i, 0, time_item)
            
            # Recipient
            recipient_item = QTableWidgetItem(message["recipient"])
            self.history_table.setItem(i, 1, recipient_item)
            
            # Message content (truncated if too long)
            message_text = message["message"]
            if len(message_text) > 50:
                message_text = message_text[:47] + "..."
            message_item = QTableWidgetItem(message_text)
            self.history_table.setItem(i, 2, message_item)
            
            # Status
            status_item = QTableWidgetItem(message["status"].upper())
            
            # Color code status
            if message["status"].upper() == "DELIVERED":
                status_item.setForeground(QBrush(QColor("#28a745")))  # Green
            elif message["status"].upper() == "FAILED":
                status_item.setForeground(QBrush(QColor("#dc3545")))  # Red
            elif message["status"].upper() == "SENT":
                status_item.setForeground(QBrush(QColor("#ffc107")))  # Yellow/amber
            
            self.history_table.setItem(i, 3, status_item)
            
            # Message ID
            text_id_item = QTableWidgetItem(message["text_id"] if message["text_id"] else "N/A")
            self.history_table.setItem(i, 4, text_id_item)
        
        # Sort by time (newest first)
        self.history_table.sortItems(0, Qt.DescendingOrder)
    
    def check_selected_status(self):
        """Check the delivery status of the selected message."""
        if not self.sms_sender:
            return
        
        # Get the selected row
        selected_rows = self.history_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a message to check its status."
            )
            return
        
        # Get the message ID from the selected row
        row = selected_rows[0].row()
        text_id_item = self.history_table.item(row, 4)
        text_id = text_id_item.text()
        
        if text_id == "N/A":
            QMessageBox.warning(
                self,
                "Status Check Failed",
                "This message doesn't have a valid Message ID. It may have failed to send."
            )
            return
        
        # Check the status
        self.status_update.emit(f"Checking status of message {text_id}...")
        self.sms_sender.check_message_status(text_id)
    
    def check_pending_messages(self):
        """Check the status of all pending messages."""
        if not self.sms_sender:
            return
        
        self.status_update.emit("Checking status of all pending messages...")
        self.sms_sender.check_all_pending_messages()
        self.refresh_history()
    
    def update_message_status(self, text_id: str, status: str):
        """
        Update the status of a message in the table.
        
        Args:
            text_id: The text ID of the message
            status: The new status
        """
        # Find the row with this text_id
        for row in range(self.history_table.rowCount()):
            if self.history_table.item(row, 4).text() == text_id:
                # Update status
                status_item = QTableWidgetItem(status.upper())
                
                # Color code status
                if status.upper() == "DELIVERED":
                    status_item.setForeground(QBrush(QColor("#28a745")))  # Green
                elif status.upper() == "FAILED":
                    status_item.setForeground(QBrush(QColor("#dc3545")))  # Red
                elif status.upper() == "SENT":
                    status_item.setForeground(QBrush(QColor("#ffc107")))  # Yellow/amber
                
                self.history_table.setItem(row, 3, status_item)
                break
    
    def toggle_auto_refresh(self, checked: bool):
        """
        Toggle automatic refreshing of message statuses.
        
        Args:
            checked: Whether the auto-refresh button is checked
        """
        self.auto_refresh = checked
        
        if checked:
            self.auto_refresh_button.setText("Auto Refresh: On")
            # Check every 30 seconds
            self.refresh_timer.start(30000)  # 30 seconds
        else:
            self.auto_refresh_button.setText("Auto Refresh: Off")
            self.refresh_timer.stop()
    
    def showEvent(self, event):
        """Event triggered when the tab is shown."""
        super().showEvent(event)
        # Refresh the history when the tab is shown
        self.refresh_history() 