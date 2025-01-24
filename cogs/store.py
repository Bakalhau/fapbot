import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime, timedelta
from succubus_mechanics.astarielle import Astarielle

class PurchaseButton(Button):
    def __init__(self, item, item_info, bot):
        self.item = item
        self.bot = bot
        super().__init__(
            label=item,
            emoji=item_info["emoji"],
            style=discord.ButtonStyle.secondary
        )

    async def callback(self, interaction: discord.Interaction):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(interaction.user.id)
        username = interaction.user.name
        item = self.item
        cost = file_manager.store_items[item]["cost"]

        # Ensure user exists in database
        file_manager.db.create_or_update_user(user_id, username)
        
        if file_manager.db.get_fapcoins(user_id) >= cost:
            file_manager.db.update_fapcoins(user_id, -cost)
            file_manager.db.update_item_quantity(user_id, item, 1)
            await interaction.response.send_message(
                f'{username} successfully bought {item} {file_manager.store_items[item]["emoji"]}!',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f'{username}, you don\'t have enough Fapcoins to buy {item}.',
                ephemeral=True
            )

class StoreView(View):
    def __init__(self, store_items, bot):
        super().__init__(timeout=None)
        for item, info in store_items.items():
            self.add_item(PurchaseButton(item, info, bot))

class Store(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def store(self, ctx):
        file_manager = self.bot.get_cog('FileManager')

        # Define user-related variables
        user_id = str(ctx.author.id)
        username = ctx.author.name
        file_manager.db.create_or_update_user(user_id, username)
        embed = discord.Embed(title="🏪 Item Store", color=discord.Color.gold())

        # Iterate over store items and add fields to the embed
        for item, info in file_manager.store_items.items():
            price = info["cost"]  # Original price of the item

            # Check if the user owns the succubus "Astarielle" and apply inflation if necessary
            user_succubus = file_manager.db.get_user_succubus(user_id)  # Retrieve user succubus list
            if any(succubus['succubus_id'] == 'astarielle' for succubus in user_succubus):
                price = Astarielle.apply_price_inflation(price)  # Apply price inflation

            # Add item details to the embed
            embed.add_field(
                name=f'{info["emoji"]} {item}',
                value=f'{info["description"]}\nCost: {price} Fapcoins',
                inline=False
            )
        # Send the store embed with interactive buttons
        await ctx.send(embed=embed, view=StoreView(file_manager.store_items, self.bot))

    @commands.command()
    async def daily(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        username = ctx.author.name
        now = datetime.now()
        
        # Ensure user exists in database
        file_manager.db.create_or_update_user(user_id, username)

        last_daily = file_manager.db.get_last_daily(user_id)
        user_succubus = file_manager.db.get_user_succubus(user_id)
        if any(succubus['succubus_id'] == 'astarielle' for succubus in user_succubus):
            if last_daily:
                last_daily = Astarielle.apply_daily_reduction(last_daily)
        if not last_daily or (now - last_daily) >= timedelta(hours=12):
            file_manager.db.update_fapcoins(user_id, 1)
            file_manager.db.update_daily_timestamp(user_id)
            coins = file_manager.db.get_fapcoins(user_id)
            await ctx.send(f'{username}, you received 1 Fapcoin! 💰 Total: {coins} Fapcoins.')
        else:
            remaining_time = timedelta(hours=12) - (now - last_daily)
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            await ctx.send(f'{username}, you already got your daily Fapcoin! Try again in {hours}h {minutes}m.')

    @commands.command()
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