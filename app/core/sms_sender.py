"""
SMS notification module using TextBelt.
"""

import time
import requests
import datetime
from typing import List, Dict, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal
import logging

logger = logging.getLogger(__name__)


class SMSMessage:
    """
    Class to represent an SMS message with tracking information.
    """
    
    def __init__(self, recipient: str, message: str, text_id: Optional[str] = None):
        """Initialize the SMS message."""
        self.recipient = recipient
        self.message = message
        self.text_id = text_id
        self.timestamp = datetime.datetime.now()
        self.status = "pending"  # pending, sent, delivered, failed
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        return {
            "recipient": self.recipient,
            "message": self.message,
            "text_id": self.text_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SMSMessage':
        """Create a message from a dictionary."""
        message = cls(data["recipient"], data["message"], data["text_id"])
        message.timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        message.status = data["status"]
        message.error = data["error"]
        return message


class SMSSender(QObject):
    """
    Handles sending SMS messages via TextBelt.
    Uses QObject to allow for signal emission for UI updates.
    """
    
    # Define signals
    status_update = pyqtSignal(str)
    sms_sent = pyqtSignal(str, int)  # message, recipient count
    sms_status_updated = pyqtSignal(str, str)  # text_id, status
    
    # TextBelt API endpoint
    API_URL = "https://textbelt.com/text"
    STATUS_URL = "https://textbelt.com/status"
    
    def __init__(self, **kwargs):
        """Initialize the SMS sender with any required configuration."""
        super().__init__()
        self.config = kwargs
        self.api_key = "textbelt"  # Default key for free tier
        self.recipients = []
        self.is_configured = False
        self.is_free_tier = True
        self.message_history = []
        logger.info("SMS Sender initialized")
    
    def configure(self, 
                  api_key: str, 
                  recipients: List[str]) -> bool:
        """
        Configure the SMS sender with TextBelt API key and recipients.
        
        Args:
            api_key: TextBelt API key (use "textbelt" for free tier with attribution)
            recipients: List of phone numbers to send SMS to
            
        Returns:
            bool: True if configuration was successful, False otherwise
        """
        self.api_key = api_key
        self.recipients = recipients
        
        # Check if using free tier
        self.is_free_tier = (api_key.lower() == "textbelt")
        
        # Validate configuration
        if not self.api_key:
            self.is_configured = False
            self.status_update.emit("Error: API key not provided")
            return False
            
        if not self.recipients:
            self.is_configured = False
            self.status_update.emit("Error: No recipients configured")
            return False
        
        self.is_configured = True
        tier_type = "free" if self.is_free_tier else "paid"
        self.status_update.emit(f"SMS sender configured successfully (using {tier_type} tier)")
        return True
    
    def validate_phone_number(self, phone: str) -> tuple:
        """
        Validate and format a phone number according to TextBelt's requirements.
        
        Args:
            phone: The phone number to validate and format
            
        Returns:
            tuple: (is_valid, formatted_number, error_message)
                - is_valid: True if the number is valid
                - formatted_number: The formatted E.164 number if valid, None otherwise
                - error_message: Error message if invalid, None otherwise
        """
        # Remove all non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Handle empty or very short phone numbers
        if not digits_only or len(digits_only) < 8:
            return False, None, f"Invalid phone number: {phone} - too few digits"
        
        # Handle very long phone numbers (likely a mistake)
        if len(digits_only) > 15:
            return False, None, f"Invalid phone number: {phone} - too many digits"
        
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
                return False, None, f"Invalid phone number: {phone} - missing country code (use +XX format)"
        
        return True, formatted, None

    def send_message(self, message: str, force_production: bool = True) -> bool:
        """
        Send an SMS message to all configured recipients.
        
        Args:
            message: The message content to send
            force_production: If True, ensures messages are sent as real messages
            
        Returns:
            bool: True if messages were sent successfully, False otherwise
        """
        if not self.is_configured:
            self.status_update.emit("Error: SMS sender not configured")
            return False
        
        if not self.recipients:
            self.status_update.emit("Error: No recipients configured")
            return False
        
        success_count = 0
        invalid_numbers = []
        
        try:
            for recipient in self.recipients:
                # Validate and format the phone number
                is_valid, formatted_number, error_msg = self.validate_phone_number(recipient)
                
                if not is_valid:
                    self.status_update.emit(error_msg)
                    invalid_numbers.append((recipient, error_msg))
                    continue
                    
                # Create a message object to track this SMS
                sms_message = SMSMessage(recipient, message)
                
                self.status_update.emit(f"Sending SMS to formatted number: {formatted_number}")
                
                # Prepare the payload
                payload = {
                    'phone': formatted_number,
                    'message': message,
                    'key': self.api_key
                }
                
                # Log whether this is production or test mode
                if force_production:
                    self.status_update.emit("Sending in PRODUCTION mode - real message will be sent")
                
                self.status_update.emit(f"Sending request to: {self.API_URL}")
                self.status_update.emit(f"Payload: phone={formatted_number[:3]}...{formatted_number[-3:]}, message length={len(message)}, key={self.api_key[:4]}...")
                
                # Send the request
                response = requests.post(self.API_URL, data=payload)
                self.status_update.emit(f"Response status code: {response.status_code}")
                
                try:
                    response_data = response.json()
                    self.status_update.emit(f"Response data: {response_data}")
                except:
                    self.status_update.emit(f"Failed to parse response as JSON: {response.text}")
                    response_data = {"success": False, "error": "Failed to parse response"}
                
                if response_data.get('success'):
                    # Update message with text_id and status
                    text_id = response_data.get('textId')
                    sms_message.text_id = text_id
                    sms_message.status = "sent"
                    
                    success_count += 1
                    self.status_update.emit(f"SMS sent to {recipient}, Message ID: {text_id}")
                    
                    if 'quotaRemaining' in response_data:
                        self.status_update.emit(f"Remaining quota: {response_data.get('quotaRemaining', 'unknown')}")
                    
                    # Start checking delivery status in the future
                    self.status_update.emit(f"Message ID: {text_id} - Can check delivery status")
                else:
                    error_msg = response_data.get('error', 'Unknown error')
                    sms_message.status = "failed"
                    sms_message.error = error_msg
                    
                    # Provide more detailed error information
                    if "disabled for this country" in error_msg:
                        self.status_update.emit(f"Failed to send SMS to {recipient}: Free SMS are disabled for this country.")
                        self.status_update.emit("To send to this country, you need to purchase TextBelt credits.")
                    elif "quota" in error_msg.lower():
                        self.status_update.emit(f"Failed to send SMS to {recipient}: {error_msg}")
                        self.status_update.emit("You've exceeded your SMS quota. Purchase credits at textbelt.com")
                    else:
                        self.status_update.emit(f"Failed to send SMS to {recipient}: {error_msg}")
                
                # Add to message history
                self.message_history.append(sms_message)
                    
                # Add a small delay to avoid rate limiting
                time.sleep(0.1)
            
            # Show summary of invalid numbers if any
            if invalid_numbers:
                invalid_summary = "The following numbers were invalid and SMS were not sent:\n"
                for num, err in invalid_numbers:
                    invalid_summary += f"• {num}: {err}\n"
                self.status_update.emit(invalid_summary)
                
                # If all numbers were invalid, report failure
                if success_count == 0:
                    self.status_update.emit("No valid phone numbers found. Please check your recipient list.")
                    return False
            
            self.sms_sent.emit(message, success_count)
            return success_count > 0
            
        except Exception as e:
            self.status_update.emit(f"Error sending SMS: {str(e)}")
            import traceback
            self.status_update.emit(f"Traceback: {traceback.format_exc()}")
            return False
    
    def check_message_status(self, text_id: str) -> Optional[Dict[str, Any]]:
        """
        Check the delivery status of a message.
        
        Args:
            text_id: The text ID to check
            
        Returns:
            Dict containing the status information, or None if the check failed
        """
        if not self.api_key:
            self.status_update.emit("Error: API key not provided")
            return None
        
        try:
            # Log details for debugging
            self.status_update.emit(f"Checking status for message ID: {text_id}")
            
            # Prepare the payload
            payload = {
                'textId': text_id,
                'key': self.api_key
            }
            
            # Log request details
            self.status_update.emit(f"Sending request to: {self.STATUS_URL} with payload: {payload}")
            
            # Send the request
            response = requests.get(self.STATUS_URL, params=payload)
            
            # Log the complete response
            self.status_update.emit(f"Response status code: {response.status_code}")
            self.status_update.emit(f"Response content: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                
                # Update message in history
                for message in self.message_history:
                    if message.text_id == text_id:
                        message.status = data.get('status', message.status)
                        
                        # Emit signal for status update
                        self.sms_status_updated.emit(text_id, data.get('status', 'unknown'))
                        
                        if data.get('status') == 'DELIVERED':
                            self.status_update.emit(f"Message {text_id} delivered successfully")
                        elif data.get('status') == 'FAILED':
                            self.status_update.emit(f"Message {text_id} failed to deliver")
                        else:
                            self.status_update.emit(f"Message {text_id} status: {data.get('status')}")
                
                return data
            elif response.status_code == 404:
                # Special handling for 404 errors
                self.status_update.emit(f"Status check failed: HTTP 404 - Message ID '{text_id}' not found.")
                self.status_update.emit("Note: According to TextBelt documentation, status checks are only available for messages sent in the last 24-48 hours.")
                
                # Try a test request to see if the endpoint is working at all
                self.status_update.emit("Testing status endpoint availability...")
                test_response = requests.get("https://textbelt.com/status", params={'key': self.api_key})
                self.status_update.emit(f"Test response status: {test_response.status_code}")
                
                return None
            else:
                self.status_update.emit(f"Status check failed: HTTP {response.status_code}")
                self.status_update.emit(f"Response body: {response.text}")
                return None
                
        except Exception as e:
            self.status_update.emit(f"Error checking message status: {str(e)}")
            import traceback
            self.status_update.emit(f"Traceback: {traceback.format_exc()}")
            return None
    
    def check_all_pending_messages(self):
        """Check the status of all pending messages."""
        for message in self.message_history:
            if message.text_id and message.status not in ["DELIVERED", "FAILED"]:
                self.check_message_status(message.text_id)
                # Add a small delay to avoid rate limiting
                time.sleep(0.1)
    
    def get_message_history(self) -> List[Dict[str, Any]]:
        """
        Get the message history.
        
        Returns:
            List of message dictionaries
        """
        return [message.to_dict() for message in self.message_history]
    
    def test_connection(self) -> bool:
        """
        Test TextBelt connection by making a simple API call without sending a message.
        
        Returns:
            bool: True if test was successful, False otherwise
        """
        if not self.is_configured:
            self.status_update.emit("Error: SMS sender not configured")
            return False
        
        try:
            # Use a valid test phone number
            test_phone = '5555555555'
            
            # Explicitly add test flag to ensure no real message is sent
            self.status_update.emit("Running in TEST mode - no actual message will be sent")
            
            # Prepare test payload that won't actually send an SMS
            payload = {
                'phone': test_phone,
                'message': 'Test connection',
                'key': self.api_key,
                'test': '1'  # This tells TextBelt this is just a test
            }
            
            # Make the request
            self.status_update.emit(f"Sending test request to: {self.API_URL}")
            self.status_update.emit(f"Test payload includes 'test' flag to prevent actual message delivery")
            response = requests.post(self.API_URL, data=payload)
            
            if response.status_code == 200:
                data = response.json()
                # Check if response contains either success or error (both are valid responses)
                if 'success' in data or 'error' in data:
                    # Success could be false if out of quota, but connection still works
                    if data.get('error'):
                        self.status_update.emit(f"TextBelt connection test successful but returned: {data.get('error')}")
                    else:
                        tier_type = "free" if self.is_free_tier else "paid"
                        self.status_update.emit(f"TextBelt connection test successful! (using {tier_type} tier)")
                    
                    # Show quota if available
                    if 'quotaRemaining' in data:
                        self.status_update.emit(f"Remaining quota: {data.get('quotaRemaining', 'unknown')}")
                    
                    return True
                else:
                    self.status_update.emit("TextBelt connection test failed: Invalid response format")
                    return False
            else:
                self.status_update.emit(f"TextBelt connection test failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.status_update.emit(f"TextBelt connection test failed: {str(e)}")
            return False
    
    def is_using_free_tier(self) -> bool:
        """
        Check if the SMS sender is using the free tier.
        
        Returns:
            bool: True if using free tier, False otherwise
        """
        return self.is_free_tier

    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send an SMS message to a phone number.
        
        Args:
            phone_number: The recipient's phone number
            message: The message to send
            
        Returns:
            bool: True if the message was sent successfully, False otherwise
        """
        try:
            # Implement your SMS sending logic here
            # This would connect to your SMS service provider
            logger.info(f"Sending SMS to {phone_number}: {message}")
            
            # For now, just log the message rather than actually sending it
            # Replace with your actual SMS sending code
            logger.debug(f"SMS would be sent to {phone_number}: {message}")
            
            # Return True to indicate success (replace with actual success check)
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False 