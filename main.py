import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

class FapBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(command_prefix='&', intents=intents)

    async def on_ready(self):
        print(f'Bot connected as {self.user}')

def main():
    bot = FapBot()
    bot.run(TOKEN)

if __name__ == "__main__":
    main()