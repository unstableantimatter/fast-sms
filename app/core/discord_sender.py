import os
import asyncio
import logging
from typing import Dict, Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

logger = logging.getLogger(__name__)

class DiscordSender:
    def __init__(self, token: str):
        """Initialize the Discord sender with a bot token.
        
        Args:
            token: The Discord bot token
        """
        self.token = token
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
        self._setup_commands()
        self.user_mapping: Dict[str, int] = {}  # Maps application user_id to Discord user_id
        
    def _setup_commands(self):
        """Set up the Discord bot commands and events."""
        
        @self.bot.event
        async def on_ready():
            logger.info(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
            logger.info('Bot is ready to send messages')
            
        @self.bot.event
        async def on_message(message):
            # Ignore messages from the bot itself
            if message.author == self.bot.user:
                return
                
            # Process DMs to register users
            if isinstance(message.channel, discord.DMChannel):
                if message.content.startswith('!register'):
                    try:
                        # Format should be: !register USER_ID
                        parts = message.content.split()
                        if len(parts) != 2:
                            await message.channel.send("Please use format: !register YOUR_USER_ID")
                            return
                            
                        user_id = parts[1]
                        self.user_mapping[user_id] = message.author.id
                        await message.channel.send(f"Successfully registered! You will now receive notifications for user ID: {user_id}")
                        logger.info(f"Registered Discord user {message.author.id} with app user {user_id}")
                    except Exception as e:
                        logger.error(f"Registration error: {str(e)}")
                        await message.channel.send("Registration failed. Please try again.")
            
            await self.bot.process_commands(message)
            
        # Add a slash command for registration
        @self.bot.tree.command(name="register", description="Register to receive notifications")
        async def register(interaction, user_id: str):
            """Register your Discord account to receive notifications for a specific user ID"""
            try:
                self.user_mapping[user_id] = interaction.user.id
                await interaction.response.send_message(
                    f"Successfully registered! You will now receive notifications for user ID: {user_id}",
                    ephemeral=True
                )
                logger.info(f"Registered Discord user {interaction.user.id} with app user {user_id}")
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                await interaction.response.send_message("Registration failed. Please try again.", ephemeral=True)
    
    async def start_bot(self):
        """Start the Discord bot."""
        try:
            await self.bot.start(self.token)
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {str(e)}")
            
    def run_bot(self):
        """Run the Discord bot in the current thread."""
        try:
            self.bot.run(self.token)
        except Exception as e:
            logger.error(f"Failed to run Discord bot: {str(e)}")
            
    def run_bot_async(self):
        """Run the Discord bot in a separate thread."""
        import threading
        thread = threading.Thread(target=self.run_bot, daemon=True)
        thread.start()
        return thread
            
    async def send_message(self, user_id: str, message: str) -> bool:
        """Send a direct message to a Discord user.
        
        Args:
            user_id: The application user ID (mapped to Discord user ID)
            message: The message to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            # Get the Discord user ID from our mapping
            discord_user_id = self.user_mapping.get(user_id)
            if not discord_user_id:
                logger.error(f"No Discord user mapping found for user_id: {user_id}")
                return False
                
            # Get the Discord user
            user = self.bot.get_user(discord_user_id)
            if not user:
                try:
                    user = await self.bot.fetch_user(discord_user_id)
                except discord.NotFound:
                    logger.error(f"Discord user with ID {discord_user_id} not found")
                    return False
                except Exception as e:
                    logger.error(f"Error fetching Discord user: {str(e)}")
                    return False
                    
            # Send the message
            await user.send(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send Discord message: {str(e)}")
            return False
            
    def save_user_mapping(self, filepath: str = "discord_user_mapping.json"):
        """Save the user mapping to a file."""
        import json
        try:
            with open(filepath, 'w') as f:
                json.dump(self.user_mapping, f)
            logger.info(f"User mapping saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save user mapping: {str(e)}")
            return False
            
    def load_user_mapping(self, filepath: str = "discord_user_mapping.json"):
        """Load the user mapping from a file."""
        import json
        try:
            with open(filepath, 'r') as f:
                self.user_mapping = json.load(f)
            logger.info(f"User mapping loaded from {filepath}")
            return True
        except FileNotFoundError:
            logger.warning(f"User mapping file not found: {filepath}")
            return False
        except Exception as e:
            logger.error(f"Failed to load user mapping: {str(e)}")
            return False


# Helper function to send a message (can be called from synchronous code)
def send_message_sync(token: str, user_id: str, message: str) -> bool:
    """Send a Discord message from synchronous code."""
    import asyncio
    
    async def _send():
        sender = DiscordSender(token)
        # Start the bot just long enough to send a message
        await sender.send_message(user_id, message)
        
    asyncio.run(_send())
    return True 