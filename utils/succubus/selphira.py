from .base import SuccubusHandler
from datetime import datetime, timedelta
import asyncio

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
        Adds 1 score to the user every 3 days

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
            
            # Clears the task when it is no longer active
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
    
    def cleanup_tasks(self, user_id):
        """
        Clears running tasks for a user

        Args:
        user_id (str): The user's Discord ID
        """
        if user_id in self.burden_users:
            self.burden_users[user_id].cancel()
            del self.burden_users[user_id]