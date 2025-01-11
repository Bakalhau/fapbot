import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

class FapBot(commands.Bot):
    def __init__(self, config):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        self.config = config
        super().__init__(command_prefix=config['prefix'], intents=intents)
    
    async def setup_hook(self):
        # Load all cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        await self.load_extension('utils.file_manager')

    async def on_ready(self):
        print(f'Bot connected as {self.user}')

    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return

        # Check if the message is in an allowed channel
        if message.channel.id not in self.config['allowed_channels']:
            return

        await self.process_commands(message)

def main():
    config = load_config()
    bot = FapBot(config)
    bot.run(TOKEN)

if __name__ == "__main__":
    main()