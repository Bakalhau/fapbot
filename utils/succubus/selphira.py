from .base import SuccubusHandler
from datetime import datetime, timedelta
import asyncio
import discord

class SelphiraHandler(SuccubusHandler):
    def __init__(self, bot):
        super().__init__(bot)
        self.succubus_id = "selphira"
        self.burden_interval = timedelta(days=3)
        self.burden_users = {}  # Tracks users with active burden tasks
        
    def get_succubus_id(self):
        """
        Returns Selphira's ID
        
        Returns:
            str: The succubus ID
        """
        return self.succubus_id
    
    async def apply_ability(self, ctx, **kwargs):
        # The $fairtrade command will take care of the skill logic
        return True
    
    async def apply_burden(self, ctx, **kwargs):
        """
        Applies Selphira's burden: Every 3 days, adds 1 score to the user

        Args:
            ctx: The context of the command
            **kwargs: Additional arguments

        Returns:
            bool: True if the burden was applied
        """
        user_id = str(ctx.author.id)
        
        # Check if the user is already being monitored
        if user_id in self.burden_users:
            return True
            
        # Create a new task to apply the burden periodically
        task = asyncio.create_task(self.apply_periodic_burden(user_id))
        self.burden_users[user_id] = task
        
        return True
    
    async def apply_periodic_burden(self, user_id):
        """
        Adds 1 score to the user every 3 days and sends a notification

        Args:
            user_id (str): The user's Discord ID
        """
        try:
            while self.is_active_for_user(user_id):
                # Wait 3 days
                await asyncio.sleep(self.burden_interval.total_seconds())
                
                # Check if it is still active
                if not self.is_active_for_user(user_id):
                    break
                    
                # Add 1 score to the user
                file_manager = self.bot.get_cog('FileManager')
                user_data = file_manager.db.get_user(user_id)
                if user_data:
                    new_score = user_data['score'] + 1
                    file_manager.db.update_user_score(user_id, user_data['faps'], new_score)
                    print(f"Selphira's Burden applied: +1 score to user {user_id}")
                    
                    # Send notification to the user
                    await self.send_burden_notification(user_id)
            
            # Clean up the task when it is no longer active
            if user_id in self.burden_users:
                del self.burden_users[user_id]
                
        except asyncio.CancelledError:
            # Task was canceled, perform cleanup
            if user_id in self.burden_users:
                del self.burden_users[user_id]
        except Exception as e:
            # Log the error
            print(f"Error in apply_periodic_burden for user {user_id}: {e}")
            if user_id in self.burden_users:
                del self.burden_users[user_id]
    
    async def send_burden_notification(self, user_id):
        """
        Sends a notification to the configured channel when the burden is applied

        Args:
            user_id (str): The user's Discord ID
        """
        # Get the notification channel from config, fallback to first allowed channel
        notification_channel_id = self.bot.config.get('notification_channel', self.bot.config['allowed_channels'][0])
        channel = self.bot.get_channel(notification_channel_id)
        if channel:
            # Send a text message mentioning the user
            await channel.send(f"<@{user_id}>")
            
            # Send an embed with details
            embed = discord.Embed(
                title="💀 Selphira's Burden 💀",
                description="You have received +1 score due to Selphira's burden.",
                color=discord.Color.red()
            )
            await channel.send(embed=embed)
        else:
            print(f"Notification channel {notification_channel_id} not found for burden notification to user {user_id}")
    
    def cleanup_tasks(self, user_id):
        """
        Cleans up any running tasks for a user

        Args:
            user_id (str): The user's Discord ID
        """
        if user_id in self.burden_users:
            self.burden_users[user_id].cancel()
            del self.burden_users[user_id]