from .base import SuccubusHandler
from datetime import datetime, timedelta
import asyncio
import random
import discord

class MimiHandler(SuccubusHandler):
    """
    Handler for the Mimi succubus
    
    Ability: You automatically receive the daily reward
    Burden: You have a 20% chance of not receiving the daily reward
    """
    
    def __init__(self, bot):
        super().__init__(bot)
        self.succubus_id = "mimi"  # Unique identifier for Mimi
        self.failure_chance = 0.20  # 20% chance of not receiving the daily
        self.daily_users = {}  # Dictionary to track users with active daily tasks
        
    def get_succubus_id(self):
        """
        Returns the ID of Mimi
        
        Returns:
            str: The succubus ID
        """
        return self.succubus_id
    
    async def apply_ability(self, ctx, **kwargs):
        """
        Applies Mimi's ability: Automatically grants the daily reward
        
        Args:
            ctx: The command context
            **kwargs: Additional arguments
            
        Returns:
            bool: True if the ability was applied successfully
        """
        user_id = str(ctx.author.id)
        
        # Check if the user is already being monitored for automatic daily rewards
        if user_id in self.daily_users:
            return True
            
        # Create a new task to automatically grant the daily reward every 12 hours
        task = asyncio.create_task(self.auto_grant_daily(user_id))
        self.daily_users[user_id] = task
        
        return True
    
    async def auto_grant_daily(self, user_id):
        """
        Automatically grants the daily reward to the user every 12 hours
        
        Args:
            user_id (str): The Discord user ID
        """
        try:
            while self.is_active_for_user(user_id):
                # Wait for 12 hours before granting the next daily reward
                await asyncio.sleep(12 * 3600)
                
                # Check if the succubus is still active for the user
                if not self.is_active_for_user(user_id):
                    break
                    
                # Apply the burden: 20% chance to skip the reward
                if random.random() < self.failure_chance:
                    print(f"Mimi's burden: User {user_id} did not receive the daily reward")
                    await self.send_daily_notification(user_id, success=False)
                else:
                    # Grant the daily reward (1 fapcoin)
                    file_manager = self.bot.get_cog('FileManager')
                    file_manager.db.update_fapcoins(user_id, 1)
                    file_manager.db.update_daily_timestamp(user_id)
                    current_fapcoins = file_manager.db.get_fapcoins(user_id)
                    print(f"Mimi's ability: Automatically granted daily reward to user {user_id}")
                    await self.send_daily_notification(user_id, success=True, total=current_fapcoins)
            
            # Clean up when the succubus is no longer active for the user
            if user_id in self.daily_users:
                del self.daily_users[user_id]
                
        except asyncio.CancelledError:
            # Task was cancelled, clean up
            if user_id in self.daily_users:
                del self.daily_users[user_id]
        except Exception as e:
            # Log any errors and clean up
            print(f"Error in auto_grant_daily for user {user_id}: {e}")
            if user_id in self.daily_users:
                del self.daily_users[user_id]
    
    async def send_daily_notification(self, user_id, success, total=None):
        """
        Sends a notification to the configured channel about the automatic daily reward status
        
        Args:
            user_id (str): The Discord user ID
            success (bool): Whether the daily reward was granted or not
            total (int, optional): The user's current fapcoin total (only for success)
        """
        # Get the notification channel from config, fallback to first allowed channel
        notification_channel_id = self.bot.config.get('notification_channel', self.bot.config['allowed_channels'][0])
        channel = self.bot.get_channel(notification_channel_id)
        if channel:
            if success:
                # Send text message with mention
                await channel.send(f"<@{user_id}>, you received your automatic daily reward!")
                # Send embed with details
                embed = discord.Embed(
                    title="✨ Automatic Daily Reward ✨",
                    description=f"You have received 1 fapcoin thanks to Mimi's ability! Total: {total} fapcoins.",
                    color=discord.Color.green()
                )
                await channel.send(embed=embed)
            else:
                # Send text message with mention
                await channel.send(f"<@{user_id}>, your automatic daily reward failed this time.")
                # Send embed with details
                embed = discord.Embed(
                    title="💀 Automatic Daily Failed 💀",
                    description="Due to Mimi's burden, you did not receive your daily reward.",
                    color=discord.Color.red()
                )
                await channel.send(embed=embed)
        else:
            print(f"Notification channel {notification_channel_id} not found for user {user_id}")
    
    async def apply_burden(self, ctx, **kwargs):
        """
        Applies Mimi's burden: 20% chance of not receiving the daily reward
        
        Note: This is handled within the auto_grant_daily method.
        
        Args:
            ctx: The command context
            **kwargs: Additional arguments
            
        Returns:
            bool: True if the burden logic is in place
        """
        # The burden is integrated into the ability logic, so no additional action is needed here
        return True
    
    def cleanup_tasks(self, user_id):
        """
        Cleans up any running tasks for a user
        
        Args:
            user_id (str): The Discord user ID
        """
        if user_id in self.daily_users:
            self.daily_users[user_id].cancel()
            del self.daily_users[user_id]