from utils.succubus.astarielle import AstarielleHandler
from utils.succubus.eryndra import EryndraHandler
from utils.succubus.ravienna import RaviennaHandler

class SuccubusManager:
    """
    Manager class for handling succubus abilities and burdens.
    This class provides methods to access and apply succubus effects.
    """
    
    def __init__(self, bot):
        """
        Initialize the SuccubusManager.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.handlers = {}
        
        # Initialize handlers
        self.handlers["astarielle"] = AstarielleHandler(bot)
        self.handlers["eryndra"] = EryndraHandler(bot)
        self.handlers["ravienna"] = RaviennaHandler(bot)
    
    @property
    def file_manager(self):
        """
        Get the FileManager cog from the bot.
        This is a property to ensure we always get the latest instance.
        
        Returns:
            FileManager: The FileManager cog
        """
        return self.bot.get_cog('FileManager')
    
    def get_handler_for_user(self, user_id):
        """
        Get the appropriate handler for a user's active succubus.
        
        Args:
            user_id (str): The Discord user ID
            
        Returns:
            SuccubusHandler or None: The handler for the user's active succubus,
            or None if the user has no active succubus
        """
        active_succubus_id = self.file_manager.db.get_active_succubus(user_id)
        if not active_succubus_id:
            return None
        
        return self.handlers.get(active_succubus_id)
    
    def get_daily_cooldown(self, user_id):
        """
        Get the daily cooldown for a user, taking into account any active succubus effects.
        
        Args:
            user_id (str): The Discord user ID
            
        Returns:
            int: The cooldown time in hours (default: 12)
        """
        handler = self.get_handler_for_user(user_id)
        if handler and isinstance(handler, AstarielleHandler):
            cooldown = handler.get_daily_cooldown()
            return cooldown
        return 12  # Default cooldown
    
    def get_modified_price(self, user_id, original_price):
        """
        Get the modified price for store items based on active succubus.
        
        Args:
            user_id (str): The Discord user ID
            original_price (int): The original price of the item
            
        Returns:
            int: The modified price
        """
        handler = self.get_handler_for_user(user_id)
        if handler and isinstance(handler, AstarielleHandler):
            return handler.get_modified_price(original_price)
        return original_price  # Default price
    
    def get_modified_item_effect(self, user_id, item_name, original_value):
        """
        Get the modified effect value for an item based on active succubus.
        
        Args:
            user_id (str): The Discord user ID
            item_name (str): The name of the item
            original_value: The original effect value (hours or points)
            
        Returns:
            float or int: The modified effect value
        """
        handler = self.get_handler_for_user(user_id)
        if handler and isinstance(handler, RaviennaHandler):
            return handler.get_modified_item_effect(item_name, original_value)
        return original_value
    
    def check_item_failure(self, user_id):
        """
        Check if an item fails to work due to active succubus burden.
        
        Args:
            user_id (str): The Discord user ID
            
        Returns:
            bool: True if the item fails, False if it works
        """
        handler = self.get_handler_for_user(user_id)
        if handler and isinstance(handler, RaviennaHandler):
            return handler.check_item_failure()
        return False
