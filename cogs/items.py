import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random
from utils.succubus.manager import SuccubusManager

class Items(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shield_active = {}
        self.succubus_manager = SuccubusManager(bot)

    def is_shield_active(self, user_id):
        return user_id in self.shield_active and datetime.now() <= self.shield_active[user_id]

    @commands.command()
    async def fairtrade(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        # Check if Selphira is active
        active_succubus_id = file_manager.db.get_active_succubus(user_id)
        if active_succubus_id != "selphira":
            await ctx.send(f"{username}, you need to have Selphira active to use this command!")
            return
        
        # Check if the user has enough fapcoins
        fapcoins = file_manager.db.get_fapcoins(user_id)
        if fapcoins < 10:
            await ctx.send(f"{username}, you need at least 10 fapcoins to use this command!")
            return
        
        # Deduct 10 fapcoins
        file_manager.db.update_fapcoins(user_id, -10)
        
        # Remove 1 score
        user_data = file_manager.db.get_user(user_id)
        new_score = max(0, user_data['score'] - 1)  # Ensures that the score does not go negative
        file_manager.db.update_user_score(user_id, user_data['faps'], new_score)
        
        await ctx.send(f"{username}, You spent 10 fapcoins and removed 1 point from your score!")

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
            # Check item failure
            if self.succubus_manager.check_item_failure(user_id):
                await ctx.send(f'{username}, your Redemption failed to work due to Ravienna\'s burden!')
                file_manager.db.update_item_quantity(user_id, "Redemption", -1)
                return
                
            file_manager.db.update_item_quantity(user_id, "Redemption", -1)
            user_data = file_manager.db.get_user(user_id)
            # Apply effectiveness modifier
            original_points = 1
            points_to_remove = self.succubus_manager.get_modified_item_effect(user_id, "Redemption", original_points)
            new_score = max(0, user_data['score'] - points_to_remove)
            file_manager.db.update_user_score(user_id, user_data['faps'], new_score)
            
            await ctx.send(f'{username}, you used a Redemption and removed {points_to_remove} point(s) from your Score.')
        else:
            await ctx.send(f'{username}, you don\'t have any Redemption. Buy one from the store using `{self.bot.command_prefix}store`')

    @commands.command()
    async def supremeredemption(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        items = file_manager.db.get_user_items(user_id)
        if items.get("Supreme Redemption", 0) > 0:
            # Check item failure
            if self.succubus_manager.check_item_failure(user_id):
                await ctx.send(f'{username}, your Supreme Redemption failed to work due to Ravienna\'s burden!')
                file_manager.db.update_item_quantity(user_id, "Supreme Redemption", -1)
                return
                
            file_manager.db.update_item_quantity(user_id, "Supreme Redemption", -1)
            user_data = file_manager.db.get_user(user_id)
            # Apply effectiveness modifier
            original_points = 5
            points_to_remove = self.succubus_manager.get_modified_item_effect(user_id, "Supreme Redemption", original_points)
            new_score = max(0, user_data['score'] - points_to_remove)
            file_manager.db.update_user_score(user_id, user_data['faps'], new_score)
            
            await ctx.send(f'{username}, you used a Supreme Redemption and removed {points_to_remove} points from your Score.')
        else:
            await ctx.send(f'{username}, you don\'t have any Supreme Redemption. Buy one from the store using `{self.bot.command_prefix}store`')

    @commands.command()
    async def fapshield(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        items = file_manager.db.get_user_items(user_id)
        if items.get("Fap Shield", 0) > 0:
            # Check item failure
            if self.succubus_manager.check_item_failure(user_id):
                await ctx.send(f'{username}, your Fap Shield failed to work due to Ravienna\'s burden!')
                file_manager.db.update_item_quantity(user_id, "Fap Shield", -1)
                return
                
            file_manager.db.update_item_quantity(user_id, "Fap Shield", -1)
            # Apply effectiveness modifier
            original_hours = 1
            modified_hours = self.succubus_manager.get_modified_item_effect(user_id, "Fap Shield", original_hours)
            self.shield_active[user_id] = datetime.now() + timedelta(hours=modified_hours)
            await ctx.send(f'{username}, you activated the Fap Shield! For {modified_hours} hours, your points won\'t increase your score.')
        else:
            await ctx.send(f'{username}, you don\'t have any Fap Shield. Buy one from the store using `{self.bot.command_prefix}store`')

    @commands.command()
    async def ultrafapshield(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        
        items = file_manager.db.get_user_items(user_id)
        if items.get("Ultra Fap Shield", 0) > 0:
            # Check item failure
            if self.succubus_manager.check_item_failure(user_id):
                await ctx.send(f'{username}, your Ultra Fap Shield failed to work due to Ravienna\'s burden!')
                file_manager.db.update_item_quantity(user_id, "Ultra Fap Shield", -1)
                return
                
            file_manager.db.update_item_quantity(user_id, "Ultra Fap Shield", -1)
            # Apply effectiveness modifier
            original_hours = 2
            modified_hours = self.succubus_manager.get_modified_item_effect(user_id, "Ultra Fap Shield", original_hours)
            self.shield_active[user_id] = datetime.now() + timedelta(hours=modified_hours)
            await ctx.send(f'{username}, you activated the Ultra Fap Shield! For {modified_hours} hours, your points won\'t increase your score.')
        else:
            await ctx.send(f'{username}, you don\'t have any Ultra Fap Shield. Buy one from the store using `{self.bot.command_prefix}store`')

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
            # Filter only item probabilities (excluding ritual_probabilities)
            item_probabilities = {k: v for k, v in probabilities.items() if k != 'ritual_probabilities'}
            
            items_list = list(item_probabilities.keys())
            weights = list(item_probabilities.values())
            
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