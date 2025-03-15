from .base import SuccubusHandler
from datetime import datetime, timedelta
import asyncio
import random

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
                    continue
                
                # Grant the daily reward (e.g., 1 fapcoin)
                file_manager = self.bot.get_cog('FileManager')
                file_manager.db.update_fapcoins(user_id, 1)
                print(f"Mimi's ability: Automatically granted daily reward to user {user_id}")
            
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