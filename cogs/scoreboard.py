import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime

class ScoreboardButton(Button):
    def __init__(self, bot):
        super().__init__(emoji='💦', style=discord.ButtonStyle.primary)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        file_manager = self.bot.get_cog('FileManager')
        user = interaction.user.name
        
        if user not in file_manager.scoreboard:
            file_manager.scoreboard[user] = {"faps": 0, "score": 0}
        file_manager.scoreboard[user]["faps"] += 1
        
        # Check if shield is active
        items_cog = self.bot.get_cog('Items')
        if not items_cog.is_shield_active(user):
            file_manager.scoreboard[user]["score"] += 1
        
        file_manager.save_scoreboard()
        await interaction.response.edit_message(
            embed=create_scoreboard_embed(file_manager.scoreboard),
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
            embed=create_scoreboard_embed(file_manager.scoreboard),
            view=ScoreboardView(self.bot)
        )

    @commands.command()
    async def remove(self, ctx, name: str, amount: int):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You don't have permission to use this command.")
            return

        file_manager = self.bot.get_cog('FileManager')
        if name in file_manager.scoreboard:
            file_manager.scoreboard[name]["score"] = max(0, file_manager.scoreboard[name]["score"] - amount)
            file_manager.save_scoreboard()
            await ctx.send(f'Removed {amount} points from {name}.')
        else:
            await ctx.send(f'{name} is not on the scoreboard.')

def create_scoreboard_embed(scoreboard):
    embed = discord.Embed(title='FAPOMETER 🍆', color=discord.Color.blue())
    if not scoreboard:
        embed.add_field(name="No faps yet", value="Click the emoji to start!", inline=False)
    else:
        sorted_scores = sorted(scoreboard.items(), key=lambda x: (x[1]["score"], x[0]))
        for player, stats in sorted_scores:
            embed.add_field(name=player, value=f'Faps: {stats["faps"]} | Score: {stats["score"]}', inline=False)
    return embed

async def setup(bot):
    await bot.add_cog(Scoreboard(bot))