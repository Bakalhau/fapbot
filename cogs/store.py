import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime, timedelta
from utils.succubus.manager import SuccubusManager
from utils.succubus.trinerva import TrinervaHandler

class PurchaseButton(Button):
    def __init__(self, item, item_info, user_id, bot):
        self.item = item
        self.bot = bot
        self.user_id = user_id
        
        # Get the file manager
        self.file_manager = bot.get_cog('FileManager')
        
        # Get the succubus manager
        self.succubus_manager = SuccubusManager(bot)
        
        # Get the original cost and apply any active succubus effects
        original_cost = item_info["cost"]
        self.cost = self.succubus_manager.get_modified_price(user_id, original_cost)
        
        super().__init__(
            label=f"{item}",
            emoji=item_info["emoji"],
            style=discord.ButtonStyle.secondary
        )

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("This store view is not for you!", ephemeral=True)
            return
            
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(interaction.user.id)
        username = interaction.user.name
        item = self.item

        # Ensure user exists in database
        file_manager.db.create_or_update_user(user_id, username)
        
        if file_manager.db.get_fapcoins(user_id) >= self.cost:
            file_manager.db.update_fapcoins(user_id, -self.cost)
            file_manager.db.update_item_quantity(user_id, item, 1)
            await interaction.response.send_message(
                f'{username} successfully bought {item} {file_manager.store_items[item]["emoji"]} for {self.cost} Fapcoins!',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f'{username}, you don\'t have enough Fapcoins to buy {item}. You need {self.cost} Fapcoins.',
                ephemeral=True
            )

class StoreView(View):
    def __init__(self, store_items, user_id, bot):
        super().__init__(timeout=120)  # 2 minute timeout
        for item, info in store_items.items():
            self.add_item(PurchaseButton(item, info, user_id, bot))

class Store(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.succubus_manager = SuccubusManager(bot)

    @commands.command(aliases=["loja"])
    async def store(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        
        # Check if user has Astarielle active
        has_astarielle = False
        active_succubus_id = file_manager.db.get_active_succubus(user_id)
        if active_succubus_id == "astarielle":
            has_astarielle = True
        
        embed = discord.Embed(title="🏢 Item Store", color=discord.Color.gold())
        
        # Add information about price increase if Astarielle is active
        if has_astarielle:
            embed.description = "⚠️ Prices are increased by 20% due to Astarielle's burden!"
        
        for item, info in file_manager.store_items.items():
            original_cost = info["cost"]
            modified_cost = self.succubus_manager.get_modified_price(user_id, original_cost)
            
            # Show price difference if Astarielle is active
            price_text = f"Cost: {modified_cost} Fapcoins"
            if has_astarielle:
                price_text += f" (Original: {original_cost})"
                
            embed.add_field(
                name=f'{info["emoji"]} {item}',
                value=f'{info["description"]}\n{price_text}',
                inline=False
            )
        await ctx.send(embed=embed, view=StoreView(file_manager.store_items, user_id, self.bot))

    @commands.command()
    async def daily(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        now = datetime.utcnow()  # Use UTC time for consistency
        
        # Ensure user exists in database
        file_manager.db.create_or_update_user(user_id, username)
        
        # Get the daily cooldown based on active succubus
        handler = self.succubus_manager.get_handler_for_user(user_id)
        if handler and isinstance(handler, TrinervaHandler):
            daily_cooldown = handler.get_daily_cooldown()
        else:
            daily_cooldown = 12
        
        last_daily = file_manager.db.get_last_daily(user_id)
        if not last_daily or (now - last_daily) >= timedelta(hours=daily_cooldown):
            # Check if Trinerva's ability grants double reward
            if handler and isinstance(handler, TrinervaHandler) and handler.check_double_reward():
                reward = 2
            else:
                reward = 1
                
            file_manager.db.update_fapcoins(user_id, reward)
            file_manager.db.update_daily_timestamp(user_id)
            coins = file_manager.db.get_fapcoins(user_id)
            
            # Add note about Astarielle if active
            active_succubus_id = file_manager.db.get_active_succubus(user_id)
            if active_succubus_id == "astarielle":
                await ctx.send(f'{username}, you received {reward} Fapcoin! 💰 Total: {coins} Fapcoins.\n'
                              f'*Astarielle\'s ability reduced your daily cooldown to {daily_cooldown} hours.*')
            else:
                await ctx.send(f'{username}, you received {reward} Fapcoin! 💰 Total: {coins} Fapcoins.')
        else:
            time_since_last = now - last_daily
            remaining_time = timedelta(hours=daily_cooldown) - time_since_last
            
            # Make sure remaining time is positive
            if remaining_time.total_seconds() <= 0:
                # If we get here, there's a timezone issue - allow claiming daily
                if handler and isinstance(handler, TrinervaHandler) and handler.check_double_reward():
                    reward = 2
                else:
                    reward = 1
                file_manager.db.update_fapcoins(user_id, reward)
                file_manager.db.update_daily_timestamp(user_id)
                coins = file_manager.db.get_fapcoins(user_id)
                
                # Log the timezone issue
                print(f"WARNING: Timezone issue detected for user {user_id}, allowing daily claim")
                
                # Add note about Astarielle if active
                active_succubus_id = file_manager.db.get_active_succubus(user_id)
                if active_succubus_id == "astarielle":
                    await ctx.send(f'{username}, you received {reward} Fapcoin! 💰 Total: {coins} Fapcoins.\n'
                                  f'*Astarielle\'s ability reduced your daily cooldown to {daily_cooldown} hours.*')
                else:
                    await ctx.send(f'{username}, you received {reward} Fapcoin! 💰 Total: {coins} Fapcoins.')
                return
            
            # Extract hours and minutes
            total_seconds = int(remaining_time.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            # Add note about Astarielle if active
            active_succubus_id = file_manager.db.get_active_succubus(user_id)
            if active_succubus_id == "astarielle":
                await ctx.send(f'{username}, you already got your daily Fapcoin! Try again in {hours}h {minutes}m.\n'
                              f'*Your cooldown is {daily_cooldown} hours due to Astarielle\'s ability.*')
            else:
                await ctx.send(f'{username}, you already got your daily Fapcoin! Try again in {hours}h {minutes}m.')

    @commands.command(aliases=["fc"])
    async def fapcoin(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        coins = file_manager.db.get_fapcoins(user_id)
        await ctx.send(f'{username}, you have {coins} Fapcoins.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addcoin(self, ctx, user: discord.Member, amount: int):
        """Add Fapcoins to a user (Admin only)"""
        if amount <= 0:
            await ctx.send("The amount must be greater than 0!")
            return
            
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(user.id)
        
        # Ensure user exists in database
        file_manager.db.create_or_update_user(user_id, user.name)
        
        # Add Fapcoins
        file_manager.db.update_fapcoins(user_id, amount)
        
        # Get updated balance
        new_balance = file_manager.db.get_fapcoins(user_id)
        
        embed = discord.Embed(
            title="💰 Fapcoins Added!",
            description=f"Added {amount} Fapcoins to {user.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="New Balance", value=f"{new_balance} Fapcoins")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Store(bot))