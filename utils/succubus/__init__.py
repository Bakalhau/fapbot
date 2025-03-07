# Import handlers after they are implemented
# This avoids circular imports
# from utils.succubus.astarielle import AstarielleHandler

# Dictionary to map succubus_id to appropriate handler class
SUCCUBUS_HANDLERS = {
    # "astarielle": AstarielleHandler,
    # Other handlers will be added here
}

def get_succubus_handler(succubus_id):
    """
    Get the appropriate handler for a succubus based on its ID
    
    Args:
        succubus_id (str): The ID of the succubus
        
    Returns:
        Class: The handler class for the succubus, or None if not found
    """
    return SUCCUBUS_HANDLERS.get(succubus_id)