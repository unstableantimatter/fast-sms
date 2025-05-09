import logging
import os
from typing import Optional, Dict, Any, List

from app.core.sms_sender import SMSSender
from app.core.discord_sender import DiscordSender

logger = logging.getLogger(__name__)

class MessageService:
    """A service to send messages via different providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the message service.
        
        Args:
            config: Configuration dictionary with the following keys:
                - sms_enabled: Whether SMS is enabled
                - discord_enabled: Whether Discord is enabled
                - discord_token: Discord bot token (required if discord_enabled is True)
                - sms_config: Configuration for SMS sender (required if sms_enabled is True)
        """
        self.config = config
        self.providers = {}
        
        # Initialize SMS provider if enabled
        if config.get('sms_enabled', False):
            try:
                sms_config = config.get('sms_config', {})
                self.providers['sms'] = SMSSender(**sms_config)
                logger.info("SMS provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize SMS provider: {str(e)}")
        
        # Initialize Discord provider if enabled
        if config.get('discord_enabled', False):
            try:
                discord_token = config.get('discord_token')
                if not discord_token:
                    logger.error("Discord token not provided")
                else:
                    discord_sender = DiscordSender(discord_token)
                    
                    # Load any existing user mappings
                    discord_sender.load_user_mapping()
                    
                    # Start the bot in a separate thread
                    discord_sender.run_bot_async()
                    
                    self.providers['discord'] = discord_sender
                    logger.info("Discord provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Discord provider: {str(e)}")
    
    def send_message(self, user_id: str, message: str, 
                     providers: Optional[List[str]] = None) -> Dict[str, bool]:
        """Send a message to a user via one or more providers.
        
        Args:
            user_id: The user ID to send the message to
            message: The message to send
            providers: List of provider names to use, or None to use all available providers
            
        Returns:
            A dictionary mapping provider names to success status
        """
        results = {}
        
        # Determine which providers to use
        use_providers = providers or list(self.providers.keys())
        
        # Send via each provider
        for provider_name in use_providers:
            provider = self.providers.get(provider_name)
            if not provider:
                logger.warning(f"Provider {provider_name} not available")
                results[provider_name] = False
                continue
                
            try:
                if provider_name == 'sms':
                    # Assume user_id is the phone number for SMS
                    success = provider.send_sms(user_id, message)
                elif provider_name == 'discord':
                    # For Discord, we need to look up the Discord user ID
                    success = False
                    if hasattr(provider, 'send_message_sync'):
                        success = provider.send_message_sync(user_id, message)
                    else:
                        # Use the helper function from discord_sender
                        from app.core.discord_sender import send_message_sync
                        discord_token = self.config.get('discord_token', '')
                        success = send_message_sync(discord_token, user_id, message)
                else:
                    logger.warning(f"Unknown provider {provider_name}")
                    success = False
                    
                results[provider_name] = success
                logger.info(f"Message sent via {provider_name}: {success}")
            except Exception as e:
                logger.error(f"Error sending message via {provider_name}: {str(e)}")
                results[provider_name] = False
                
        return results 