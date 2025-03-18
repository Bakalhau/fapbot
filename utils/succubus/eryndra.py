import random
from datetime import datetime, timedelta
import discord
import asyncio
from .base import SuccubusHandler

class EryndraHandler(SuccubusHandler):
    """
    Handler for Eryndra succubus
    
    Ability: You receive a notification when daily is available
    Burden: Every hour you have a 30% chance of receiving a False Alarm
    """
    
    def __init__(self, bot):
        super().__init__(bot)
        self.succubus_id = "eryndra"
        self.false_alarm_chance = 0.30  # 30% chance
        self.false_alarm_users = {}  # Track users with active false alarm tasks
        self.daily_notification_users = {}  # Track users with active daily notification tasks
        self.false_alarm_messages = [
            "Oops! False alarm! Your daily isn't ready yet.",
            "Gotcha! It's not time for your daily reward.",
            "Just kidding! Your daily is still on cooldown.",
            "Psyche! You'll have to wait a bit longer for your daily.",
            "False alert! Your daily reward isn't available yet.",
            "Tricked ya! Check back later for your daily.",
            "Not yet! Your daily will be ready soon.",
            "Surprise! It's not daily time yet.",
            "Hold on! Your daily is still charging.",
            "Almost there! But not quite ready for your daily."
        ]
        
    def get_succubus_id(self):
        """
        Get the ID of Eryndra
        
        Returns:
            str: The succubus ID
        """
        return self.succubus_id
    
    async def apply_ability(self, ctx, **kwargs):
        """
        Apply Eryndra's ability: Notify user when daily is available
        
        Args:
            ctx: The command context
            **kwargs: Additional arguments
            
        Returns:
            bool: True if the ability was applied
        """
        user_id = str(ctx.author.id)
        
        # Check if user is already being monitored
        if user_id in self.daily_notification_users:
            # Task already exists, no need to create another one
            return True
            
        # Create a new task to monitor daily availability
        task = asyncio.create_task(self.monitor_daily_availability(user_id, ctx.author))
        self.daily_notification_users[user_id] = task
        
        return True
    
    async def monitor_daily_availability(self, user_id, user):
        """
        Monitor daily availability for a user and send a notification to the configured channel
        
        Args:
            user_id (str): The Discord user ID
            user (discord.User): The Discord user object
        """
        try:
            while self.is_active_for_user(user_id):
                # Get the last daily timestamp
                last_daily = self.file_manager.db.get_last_daily(user_id)
                now = datetime.utcnow()
                
                # If no last daily or it was more than 12 hours ago
                if not last_daily or (now - last_daily) >= timedelta(hours=12):
                    # Get the notification channel from config, fallback to first allowed channel
                    notification_channel_id = self.bot.config.get('notification_channel', self.bot.config['allowed_channels'][0])
                    channel = self.bot.get_channel(notification_channel_id)
                    if channel:
                        await channel.send(f"<@{user_id}>")
                        embed = discord.Embed(
                            title="✨ Daily Available! ✨",
                            description=f"<@{user_id}>, your daily reward is now available! Use the `daily` command to claim it.",
                            color=discord.Color.green()
                        )
                        embed.set_footer(text="Eryndra's ability: Daily notification")
                        await channel.send(embed=embed)
                        
                        # Wait for 12 hours before checking again to avoid spam
                        await asyncio.sleep(12 * 3600)
                    else:
                        print(f"Notification channel {notification_channel_id} not found for daily notification to user {user_id}")
                        break  # Stop monitoring if channel is not found
                
                # Check every 5 minutes
                await asyncio.sleep(300)  # 5 minutes
                
            # Clean up when no longer active
            if user_id in self.daily_notification_users:
                del self.daily_notification_users[user_id]
                
        except asyncio.CancelledError:
            # Task was cancelled, clean up
            if user_id in self.daily_notification_users:
                del self.daily_notification_users[user_id]
        except Exception as e:
            # Log the error
            print(f"Error in monitor_daily_availability for user {user_id}: {e}")
            if user_id in self.daily_notification_users:
                del self.daily_notification_users[user_id]
    
    async def apply_burden(self, ctx, **kwargs):
        """
        Apply Eryndra's burden: 30% chance of False Alarm every hour
        
        Args:
            ctx: The command context
            **kwargs: Additional arguments
            
        Returns:
            bool: True if the burden was applied
        """
        user_id = str(ctx.author.id)
        
        # Check if user is already being monitored
        if user_id in self.false_alarm_users:
            # Task already exists, no need to create another one
            return True
            
        # Create a new task to send false alarms
        task = asyncio.create_task(self.send_false_alarms(user_id, ctx.author))
        self.false_alarm_users[user_id] = task
        
        return True
    
    async def send_false_alarms(self, user_id, user):
        """
        Send false alarms to the configured channel for a user
        
        Args:
            user_id (str): The Discord user ID
            user (discord.User): The Discord user object
        """
        try:
            while self.is_active_for_user(user_id):
                # Wait for 1 hour
                await asyncio.sleep(3600)  # 1 hour
                
                # Check if still active
                if not self.is_active_for_user(user_id):
                    break
                    
                # 30% chance of false alarm
                if random.random() < self.false_alarm_chance:
                    # Get the notification channel from config, fallback to first allowed channel
                    notification_channel_id = self.bot.config.get('notification_channel', self.bot.config['allowed_channels'][0])
                    channel = self.bot.get_channel(notification_channel_id)
                    if channel:
                        await channel.send(f"<@{user_id}>")
                        embed = discord.Embed(
                            title="⚠️ False Alarm! ⚠️",
                            description=f"<@{user_id}>, {random.choice(self.false_alarm_messages)}",
                            color=discord.Color.red()
                        )
                        embed.set_footer(text="Eryndra's burden: False Alarm!")
                        await channel.send(embed=embed)
                    else:
                        print(f"Notification channel {notification_channel_id} not found for false alarm to user {user_id}")
                        break  # Stop monitoring if channel is not found
            
            # Clean up when no longer active
            if user_id in self.false_alarm_users:
                del self.false_alarm_users[user_id]
                
        except asyncio.CancelledError:
            # Task was cancelled, clean up
            if user_id in self.false_alarm_users:
                del self.false_alarm_users[user_id]
        except Exception as e:
            # Log the error
            print(f"Error in send_false_alarms for user {user_id}: {e}")
            if user_id in self.false_alarm_users:
                del self.false_alarm_users[user_id]
                
    def cleanup_tasks(self, user_id):
        """
        Clean up any running tasks for a user
        
        Args:
            user_id (str): The Discord user ID
        """
        if user_id in self.daily_notification_users:
            self.daily_notification_users[user_id].cancel()
            del self.daily_notification_users[user_id]
            
        if user_id in self.false_alarm_users:
            self.false_alarm_users[user_id].cancel()
            del self.false_alarm_users[user_id]