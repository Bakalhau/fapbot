class SuccubusHandler:
    """
    Base class for all succubus handlers.
    
    All succubus-specific handlers should inherit from this class and 
    implement the appropriate methods for their abilities and burdens.
    """
    
    def __init__(self, bot):
        """
        Initialize the succubus handler.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
    
    @property
    def file_manager(self):
        """
        Get the FileManager cog from the bot.
        This is a property to ensure we always get the latest instance.
        
        Returns:
            FileManager: The FileManager cog
        """
        return self.bot.get_cog('FileManager')
    
    async def apply_ability(self, ctx, *args, **kwargs):
        """
        Apply the succubus's ability effect.
        
        Args:
            ctx: The command context
            *args, **kwargs: Additional arguments that may be needed
            
        Returns:
            bool: True if the ability was applied successfully, False otherwise
        """
        raise NotImplementedError("Succubus handlers must implement apply_ability")
    
    async def apply_burden(self, ctx, *args, **kwargs):
        """
        Apply the succubus's burden effect.
        
        Args:
            ctx: The command context
            *args, **kwargs: Additional arguments that may be needed
            
        Returns:
            bool: True if the burden was applied successfully, False otherwise
        """
        raise NotImplementedError("Succubus handlers must implement apply_burden")
    
    def is_active_for_user(self, user_id):
        """
        Check if this succubus is the active one for the user.
        
        Args:
            user_id (str): The Discord user ID
            
        Returns:
            bool: True if this succubus is active for the user, False otherwise
        """
        active_succubus_id = self.file_manager.db.get_active_succubus(user_id)
        return active_succubus_id == self.get_succubus_id()
    
    def get_succubus_id(self):
        """
        Get the ID of this succubus.
        
        Returns:
            str: The succubus ID
        """
        raise NotImplementedError("Succubus handlers must implement get_succubus_id")

    def get_daily_cooldown(self):
        """
        Retorna o tempo de cooldown padrão do daily em horas.
        
        Returns:
            int: O tempo de cooldown em horas (padrão: 12)
        """
        return 12