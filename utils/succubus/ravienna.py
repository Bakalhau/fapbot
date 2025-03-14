from .base import SuccubusHandler
import random
from datetime import timedelta

class RaviennaHandler(SuccubusHandler):
    """
    Handler for Ravienna succubus
    
    Ability: All items are 50% more effective
    Burden: All items have a 20% chance of failing to work
    """
    
    def __init__(self, bot):
        super().__init__(bot)
        self.succubus_id = "ravienna"
        self.effectiveness_multiplier = 1.5  # 50% more effective
        self.failure_chance = 0.20  # 20% chance to fail
        
    def get_succubus_id(self):
        """
        Get the ID of Ravienna
        
        Returns:
            str: The succubus ID
        """
        return self.succubus_id
    
    async def apply_ability(self, ctx, **kwargs):
        """
        Apply Ravienna's ability: All items are 50% more effective
        
        This ability modifies the effectiveness of items when used:
        - Fap Shield: 1 hour → 1.5 hours
        - Ultra Fap Shield: 2 hours → 3 hours
        - Redemption: 1 point → 1.5 points (rounded down to 1)
        - Supreme Redemption: 5 points → 7.5 points (rounded down to 7)
        
        Args:
            ctx: The command context
            **kwargs: Additional arguments
            
        Returns:
            bool: True if the ability was applied
        """
        # The actual effect modification will be handled in get_modified_item_effect
        return True
    
    async def apply_burden(self, ctx, **kwargs):
        """
        Apply Ravienna's burden: 20% chance for items to fail
        
        When an item is used, there's a 20% chance it will fail to work.
        
        Args:
            ctx: The command context
            **kwargs: Additional arguments
            
        Returns:
            bool: True if the burden was applied
        """
        # The failure chance will be checked in check_item_failure
        return True
    
    def get_modified_item_effect(self, item_name, original_value):
        """
        Get the modified effect value for an item
        
        Args:
            item_name (str): The name of the item
            original_value: The original effect value (can be hours or points)
            
        Returns:
            float or int: The modified effect value
        """
        if isinstance(original_value, (int, float)):
            modified = original_value * self.effectiveness_multiplier
            # For point-based items (Redemption, Supreme Redemption), round down
            if item_name in ["Redemption", "Supreme Redemption"]:
                return int(modified)
            return modified
        return original_value
    
    def check_item_failure(self):
        """
        Check if an item fails to work due to Ravienna's burden
        
        Returns:
            bool: True if the item fails, False if it works
        """
        return random.random() < self.failure_chance
