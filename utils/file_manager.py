import json
import os
from discord.ext import commands
from .database_manager import DatabaseManager

class FileManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = 'data'
        self.ensure_data_folder_exists()
        
        # Initialize database
        self.db = DatabaseManager(os.path.join(self.data_folder, 'fapbot.db'))
        
        # Load static data
        self.store_file = os.path.join(self.data_folder, 'store.json')
        self.probabilities_file = os.path.join(self.data_folder, 'probabilities.json')
        self.store_items = self.load_json(self.store_file, {})

    def ensure_data_folder_exists(self):
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def load_json(self, file_path, default_value):
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return default_value
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return default_value

    def get_probabilities(self):
        return self.load_json(self.probabilities_file, {})

async def setup(bot):
    cog = FileManager(bot)
    await bot.add_cog(cog)
    # Uncomment the following line to migrate data when setting up the bot