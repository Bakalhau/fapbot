import json
import os
from discord.ext import commands

class FileManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = 'data'
        self.ensure_data_folder_exists()
        
        # File paths
        self.scoreboard_file = os.path.join(self.data_folder, 'scoreboard.json')
        self.items_file = os.path.join(self.data_folder, 'items.json')
        self.store_file = os.path.join(self.data_folder, 'store.json')
        self.probabilities_file = os.path.join(self.data_folder, 'probabilities.json')
        
        # Load data
        self.scoreboard = self.load_json(self.scoreboard_file, {})
        items_data = self.load_json(self.items_file, {"fapcoins": {}, "items": {}})
        self.fapcoins = items_data.get("fapcoins", {})
        self.user_items = items_data.get("items", {})
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

    def save_json(self, file_path, data):
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def save_scoreboard(self):
        self.save_json(self.scoreboard_file, self.scoreboard)

    def save_items(self):
        items_data = {
            "fapcoins": self.fapcoins,
            "items": self.user_items
        }
        self.save_json(self.items_file, items_data)

    def get_probabilities(self):
        return self.load_json(self.probabilities_file, {})

async def setup(bot):
    await bot.add_cog(FileManager(bot))