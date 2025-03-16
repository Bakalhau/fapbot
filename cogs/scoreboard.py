import discord
from discord.ext import commands
from discord.ui import View, Button
from utils.succubus.manager import SuccubusManager

class ScoreboardButton(Button):
    def __init__(self, bot):
        super().__init__(emoji='💦', style=discord.ButtonStyle.primary)
        self.bot = bot
        self.succubus_manager = SuccubusManager(bot)

    async def callback(self, interaction: discord.Interaction):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(interaction.user.id)
        username = interaction.user.name
        
        # Create or update user if they don't exist
        file_manager.db.create_or_update_user(user_id, username)
        
        # Get current user data
        user_data = file_manager.db.get_user(user_id) or {'faps': 0, 'score': 0}
        new_faps = user_data['faps'] + 1
        
        # Check if shield is active
        items_cog = self.bot.get_cog('Items')
        new_score = user_data['score']
        if not items_cog.is_shield_active(user_id):
            new_score += 1
        
        # Update user's score
        file_manager.db.update_user_score(user_id, new_faps, new_score)
        
        # Apply Morvina's burden if active
        handler = self.succubus_manager.get_handler_for_user(user_id)
        if handler and handler.get_succubus_id() == "morvina":
            burden_cost = handler.get_burden_cost()
            current_fapcoins = file_manager.db.get_fapcoins(user_id)
            if current_fapcoins >= burden_cost:
                file_manager.db.update_fapcoins(user_id, -burden_cost)
        
        await interaction.response.edit_message(
            embed=create_scoreboard_embed(file_manager.db.get_scoreboard()),
            view=ScoreboardView(self.bot)
        )

class ScoreboardView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(ScoreboardButton(bot))

class Scoreboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def scoreboard(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        await ctx.send(
            embed=create_scoreboard_embed(file_manager.db.get_scoreboard()),
            view=ScoreboardView(self.bot)
        )

    @commands.command()
    async def remove(self, ctx, name: str, amount: int):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You don't have permission to use this command.")
            return

        file_manager = self.bot.get_cog('FileManager')
        user_data = file_manager.db.get_user(name)
        if user_data:
            new_score = max(0, user_data['score'] - amount)
            file_manager.db.update_user_score(name, user_data['faps'], new_score)
            await ctx.send(f'Removed {amount} points from {name}.')
        else:
            await ctx.send(f'{name} is not on the scoreboard.')

def create_scoreboard_embed(scoreboard_data):
    embed = discord.Embed(title='FAPOMETER 🍆', color=discord.Color.blue())
    if not scoreboard_data:
        embed.add_field(name="No faps yet", value="Click the emoji to start!", inline=False)
    else:
        for entry in scoreboard_data:
            embed.add_field(
                name=entry['username'],
                value=f'Faps: {entry["faps"]} | Score: {entry["score"]}',
                inline=False
            )
    return embed

async def setup(bot):
    await bot.add_cog(Scoreboard(bot))