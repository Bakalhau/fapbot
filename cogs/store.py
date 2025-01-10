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
        user = interaction.user.name
        item = self.item
        cost = file_manager.store_items[item]["cost"]

        if file_manager.fapcoins.get(user, 0) >= cost:
            file_manager.fapcoins[user] -= cost
            if user not in file_manager.user_items:
                file_manager.user_items[user] = {}
            if item not in file_manager.user_items[user]:
                file_manager.user_items[user][item] = 0
            file_manager.user_items[user][item] += 1
            file_manager.save_items()
            await interaction.response.send_message(
                f'{user} successfully bought {item} {file_manager.store_items[item]["emoji"]}!',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f'{user}, you don\'t have enough Fapcoins to buy {item}.',
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
        self.daily_usage = {}

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
        user = ctx.author.name
        now = datetime.now()
        
        if user not in self.daily_usage or now - self.daily_usage[user] >= timedelta(hours=12):
            file_manager = self.bot.get_cog('FileManager')
            file_manager.fapcoins[user] = file_manager.fapcoins.get(user, 0) + 1
            self.daily_usage[user] = now
            file_manager.save_items()
            await ctx.send(f'{user}, you received 1 Fapcoin! 💰 Total: {file_manager.fapcoins[user]} Fapcoins.')
        else:
            remaining_time = timedelta(hours=12) - (now - self.daily_usage[user])
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            await ctx.send(f'{user}, you already got your daily Fapcoin! Try again in {hours}h {minutes}m.')

    @commands.command()
    async def fapcoin(self, ctx):
        file_manager = self.bot.get_cog('FileManager')
        user = ctx.author.name
        coins = file_manager.fapcoins.get(user, 0)
        await ctx.send(f'{user}, you have {coins} Fapcoins.')

async def setup(bot):
    await bot.add_cog(Store(bot))