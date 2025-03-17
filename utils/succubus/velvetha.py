import random
from .base import SuccubusHandler

class VelvethaHandler(SuccubusHandler):
    """
    Handler for the Velvetha succubus
    
    Ability: When adding a fap, there is a 15% chance the score will go to another random user.
    Burden: There is a 20% chance to receive 3 extra points when adding a fap.
    """
    
    def __init__(self, bot):
        super().__init__(bot)
        self.succubus_id = "velvetha"  # Unique identifier for Velvetha
        self.transfer_chance = 0.15  # 15% chance to transfer score
        self.extra_points_chance = 0.20  # 20% chance for extra points
        self.extra_points_amount = 3  # 3 extra points
    
    def get_succubus_id(self):
        """
        Returns the ID of Velvetha
        
        Returns:
            str: The succubus ID
        """
        return self.succubus_id
    
    async def apply_ability(self, ctx, **kwargs):
        """
        Applies Velvetha's ability: 15% chance to transfer score to another user when adding a fap.
        
        Note: The actual logic is handled in the scoreboard callback.
        
        Returns:
            bool: True to indicate the ability is active
        """
        return True

    async def apply_burden(self, ctx, **kwargs):
        """
        Applies Velvetha's burden: 20% chance to receive 3 extra points when adding a fap.
        
        Note: The actual logic is handled in the scoreboard callback.
        
        Returns:
            bool: True to indicate the burden is active
        """
        return True
    
    def check_transfer(self):
        """
        Checks if the score should be transferred to another user
        
        Returns:
            bool: True if transfer occurs, False otherwise
        """
        return random.random() < self.transfer_chance
    
    def check_extra_points(self):
        """
        Checks if the user receives extra points
        
        Returns:
            bool: True if extra points are added, False otherwise
        """
        return random.random() < self.extra_points_chance
    
    def get_extra_points_amount(self):
        """
        Returns the amount of extra points
        
        Returns:
            int: The number of extra points
        """
        return self.extra_points_amount