import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random

class Items(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shield_active = {}

    def is_shield_active(self, user):
        return user in self.shield_active and datetime.now() <= self.shield_active[user]

    @commands.command()
    async def items(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user = ctx.author.name
        
        if user in file_manager.user_items and file_manager.user_items[user]:
            embed = discord.Embed(title=f'{user}\'s Items', color=discord.Color.green())
            for item, quantity in file_manager.user_items[user].items():
                embed.add_field(name=item, value=f'Quantity: {quantity}', inline=False)
        else:
            embed = discord.Embed(title=f'{user}\'s Items', description="You don't have any items.", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command()
    async def redemption(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user = ctx.author.name
        
        if user in file_manager.user_items and file_manager.user_items[user].get("Redemption", 0) > 0:
            file_manager.user_items[user]["Redemption"] -= 1
            file_manager.scoreboard[user]["score"] = max(0, file_manager.scoreboard[user]["score"] - 1)
            file_manager.save_items()
            file_manager.save_scoreboard()
            await ctx.send(f'{user}, you used a Redemption and removed 1 point from your Score.')
        else:
            await ctx.send(f'{user}, you don\'t have any Redemption.')

    @commands.command()
    async def supremeredemption(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user = ctx.author.name
        
        if user in file_manager.user_items and file_manager.user_items[user].get("Supreme Redemption", 0) > 0:
            file_manager.user_items[user]["Supreme Redemption"] -= 1
            file_manager.scoreboard[user]["score"] = max(0, file_manager.scoreboard[user]["score"] - 5)
            file_manager.save_items()
            file_manager.save_scoreboard()
            await ctx.send(f'{user}, you used a Supreme Redemption and removed 5 points from your Score.')
        else:
            await ctx.send(f'{user}, you don\'t have any Supreme Redemption.')

    @commands.command()
    async def fapshield(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user = ctx.author.name
        
        if user in file_manager.user_items and file_manager.user_items[user].get("Fap Shield", 0) > 0:
            file_manager.user_items[user]["Fap Shield"] -= 1
            self.shield_active[user] = datetime.now() + timedelta(hours=1)
            file_manager.save_items()
            await ctx.send(f'{user}, you activated the Fap Shield! For 1 hour, your points won\'t increase your score.')
        else:
            await ctx.send(f'{user}, you don\'t have any Fap Shield.')

    @commands.command()
    async def ultrafapshield(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user = ctx.author.name
        
        if user in file_manager.user_items and file_manager.user_items[user].get("Ultra Fap Shield", 0) > 0:
            file_manager.user_items[user]["Ultra Fap Shield"] -= 1
            self.shield_active[user] = datetime.now() + timedelta(hours=2)
            file_manager.save_items()
            await ctx.send(f'{user}, you activated the Ultra Fap Shield! For 2 hours, your points won\'t increase your score.')
        else:
            await ctx.send(f'{user}, you don\'t have any Ultra Fap Shield.')

    @commands.command()
    async def faproll(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user = ctx.author.name

        # Check if user has Faprolls
        if file_manager.user_items.get(user, {}).get("Faproll", 0) > 0:
            file_manager.user_items[user]["Faproll"] -= 1
            file_manager.save_items()

            # Get roll result based on probabilities
            probabilities = file_manager.get_probabilities()
            items = list(probabilities.keys())
            weights = list(probabilities.values())
            
            result = random.choices(items, weights=weights, k=1)[0]

            if result == "Nothing":
                await ctx.send(f'🎰 {user} spun the slot machine and... won nothing. 😞')
            else:
                # Add item to user's inventory
                if result not in file_manager.user_items[user]:
                    file_manager.user_items[user][result] = 0
                file_manager.user_items[user][result] += 1
                file_manager.save_items()
                await ctx.send(f'🎰 {user} won **{result}** {file_manager.store_items[result]["emoji"]}!')
        else:
            await ctx.send(f'{user}, you don\'t have any Faproll. Buy one from the store using `!store`.')

async def setup(bot):
    await bot.add_cog(Items(bot))