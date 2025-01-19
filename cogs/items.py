import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random

class Items(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shield_active = {}

    def is_shield_active(self, user_id):
        return user_id in self.shield_active and datetime.now() <= self.shield_active[user_id]

    @commands.command()
    async def items(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Ensure user exists in database
        file_manager.db.create_or_update_user(user_id, username)
        
        user_items = file_manager.db.get_user_items(user_id)
        if user_items:
            embed = discord.Embed(title=f'{username}\'s Items', color=discord.Color.green())
            for item, quantity in user_items.items():
                embed.add_field(name=item, value=f'Quantity: {quantity}', inline=False)
        else:
            embed = discord.Embed(title=f'{username}\'s Items', description="You don't have any items.", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command()
    async def redemption(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        items = file_manager.db.get_user_items(user_id)
        if items.get("Redemption", 0) > 0:
            file_manager.db.update_item_quantity(user_id, "Redemption", -1)
            
            user_data = file_manager.db.get_user(user_id)
            new_score = max(0, user_data['score'] - 1)
            file_manager.db.update_user_score(user_id, user_data['faps'], new_score)
            
            await ctx.send(f'{username}, you used a Redemption and removed 1 point from your Score.')
        else:
            await ctx.send(f'{username}, you don\'t have any Redemption.')

    @commands.command()
    async def supremeredemption(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        items = file_manager.db.get_user_items(user_id)
        if items.get("Supreme Redemption", 0) > 0:
            file_manager.db.update_item_quantity(user_id, "Supreme Redemption", -1)
            
            user_data = file_manager.db.get_user(user_id)
            new_score = max(0, user_data['score'] - 5)
            file_manager.db.update_user_score(user_id, user_data['faps'], new_score)
            
            await ctx.send(f'{username}, you used a Supreme Redemption and removed 5 points from your Score.')
        else:
            await ctx.send(f'{username}, you don\'t have any Supreme Redemption.')

    @commands.command()
    async def fapshield(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        items = file_manager.db.get_user_items(user_id)
        if items.get("Fap Shield", 0) > 0:
            file_manager.db.update_item_quantity(user_id, "Fap Shield", -1)
            self.shield_active[user_id] = datetime.now() + timedelta(hours=1)
            await ctx.send(f'{username}, you activated the Fap Shield! For 1 hour, your points won\'t increase your score.')
        else:
            await ctx.send(f'{username}, you don\'t have any Fap Shield.')

    @commands.command()
    async def ultrafapshield(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        items = file_manager.db.get_user_items(user_id)
        if items.get("Ultra Fap Shield", 0) > 0:
            file_manager.db.update_item_quantity(user_id, "Ultra Fap Shield", -1)
            self.shield_active[user_id] = datetime.now() + timedelta(hours=2)
            await ctx.send(f'{username}, you activated the Ultra Fap Shield! For 2 hours, your points won\'t increase your score.')
        else:
            await ctx.send(f'{username}, you don\'t have any Ultra Fap Shield.')

    @commands.command()
    async def faproll(self, ctx):
        prefix = self.bot.command_prefix
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name

        items = file_manager.db.get_user_items(user_id)
        if items.get("Faproll", 0) > 0:
            file_manager.db.update_item_quantity(user_id, "Faproll", -1)

            probabilities = file_manager.get_probabilities()
            items_list = list(probabilities.keys())
            weights = list(probabilities.values())
            
            result = random.choices(items_list, weights=weights, k=1)[0]

            if result == "Nothing":
                await ctx.send(f'🎰 {username} spun the slot machine and... won nothing. 😞')
            else:
                file_manager.db.update_item_quantity(user_id, result, 1)
                await ctx.send(f'🎰 {username} won **{result}** {file_manager.store_items[result]["emoji"]}!')
        else:
            await ctx.send(f'{username}, you don\'t have any Faproll. Buy one from the store using `{prefix}store`.')

async def setup(bot):
    await bot.add_cog(Items(bot))