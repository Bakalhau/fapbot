from datetime import datetime, timedelta
from .base import SuccubusHandler

class AstarielleHandler(SuccubusHandler):
    """
    Handler for Astarielle succubus
    
    Ability: Reduces daily cooldown by 2 hours (from 12 to 10 hours)
    Burden: Increases store prices by 20%
    """
    
    def __init__(self, bot):
        super().__init__(bot)
        self.succubus_id = "astarielle"
    
    def get_succubus_id(self):
        """
        Get the ID of Astarielle
        
        Returns:
            str: The succubus ID
        """
        return self.succubus_id
    
    async def apply_ability(self, ctx, **kwargs):
        """
        Apply Astarielle's ability: Reduce daily cooldown by 2 hours
        
        When checking if a user can claim their daily reward,
        this ability will reduce the required cooldown from 12 to 10 hours.
        
        Args:
            ctx: The command context
            **kwargs: Additional arguments
            
        Returns:
            bool: True if the ability was applied
        """
        # This will be applied in the get_daily_cooldown method
        return True
    
    async def apply_burden(self, ctx, **kwargs):
        """
        Apply Astarielle's burden: Increase store prices by 20%
        
        When a user views the store or purchases an item,
        the prices will be increased by 20% if Astarielle is active.
        
        Args:
            ctx: The command context
            **kwargs: Additional arguments
            
        Returns:
            bool: True if the burden was applied
        """
        # This will be applied in the get_modified_price method
        return True
    
    def get_daily_cooldown(self):
        """
        Get the modified daily cooldown time
        
        Returns:
            int: The cooldown time in hours (10 for Astarielle)
        """
        return 10  # Reduced from default 12 hours
    
    def get_modified_price(self, original_price):
        """
        Get the modified price for store items
        
        Args:
            original_price (int): The original price of the item
            
        Returns:
            int: The modified price (increased by 20%)
        """
        return int(original_price * 1.2)  # 20% increase