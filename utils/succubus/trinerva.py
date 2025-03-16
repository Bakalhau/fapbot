from .base import SuccubusHandler
import random

class TrinervaHandler(SuccubusHandler):
    """
    Handler for the Trinerva succubus
    
    Ability: You have a 20% chance of receiving 2 fapcoins from the daily reward
    Burden: The daily reward cooldown is increased to 16 hours
    """
    
    def __init__(self, bot):
        super().__init__(bot)
        self.succubus_id = "trinerva"  # Unique identifier for Trinerva
        self.double_reward_chance = 0.20  # 20% chance for double reward
        self.cooldown_hours = 16  # Cooldown increased to 16 hours
        
    def get_succubus_id(self):
        """
        Returns the ID of Trinerva
        
        Returns:
            str: The succubus ID
        """
        return self.succubus_id
    
    async def apply_ability(self, ctx, **kwargs):
        """
        Applies Trinerva's ability: 20% chance to receive 2 fapcoins from daily
        
        Note: This is handled in the daily command logic.
        
        Args:
            ctx: The command context
            **kwargs: Additional arguments
            
        Returns:
            bool: True if the ability logic is in place
        """
        return True
    
    async def apply_burden(self, ctx, **kwargs):
        """
        Applies Trinerva's burden: Daily cooldown is increased to 16 hours
        
        Note: This is handled in the get_daily_cooldown method.
        
        Args:
            ctx: The command context
            **kwargs: Additional arguments
            
        Returns:
            bool: True if the burden logic is in place
        """
        return True
    
    def get_daily_cooldown(self):
        """
        Returns the modified daily cooldown time
        
        Returns:
            int: The cooldown time in hours (16 for Trinerva)
        """
        return self.cooldown_hours
    
    def check_double_reward(self):
        """
        Checks if the user receives double fapcoins from the daily reward
        
        Returns:
            bool: True if the user gets double reward, False otherwise
        """
        return random.random() < self.double_reward_chance