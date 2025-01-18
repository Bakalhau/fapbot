import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime, timedelta

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
        embed = discord.Embed(title="🏢 Item Store", color=discord.Color.gold())
        for item, info in file_manager.store_items.items():
            embed.add_field(
                name=f'{info["emoji"]} {item}',
                value=f'{info["description"]}\nCost: {info["cost"]} Fapcoins',
                inline=False
            )
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

async def setup(bot):
    await bot.add_cog(Store(bot))