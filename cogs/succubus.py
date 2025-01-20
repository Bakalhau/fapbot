import discord
from discord.ext import commands
import random
import json
import os

class Succubus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.succubus_data = self.load_succubus_data()

    def load_succubus_data(self):
        """Carrega os dados de succubus do JSON"""
        with open('data/succubus.json', 'r') as f:
            return json.load(f)

    def get_all_succubus(self):
        """Retorna todas as succubus disponíveis do JSON"""
        return self.succubus_data['available_succubus']

    def get_succubus_by_id(self, succubus_id):
        """Retorna uma succubus específica do JSON"""
        return self.succubus_data['available_succubus'].get(succubus_id)

    def get_succubus_by_rarity(self, rarity):
        """Retorna todas as succubus de uma determinada raridade"""
        return [
            {"id": sid, **sdata} 
            for sid, sdata in self.succubus_data['available_succubus'].items()
            if sdata['rarity'] == rarity
        ]

    @commands.command()
    async def mysuccubus(self, ctx):
        """Show all succubus owned by the user"""
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        
        user_succubus = file_manager.db.get_user_succubus(user_id)
        if not user_succubus:
            await ctx.send("You don't have any succubus yet!")
            return

        embed = discord.Embed(title=f"{ctx.author.name}'s Succubus Collection", color=discord.Color.purple())
        
        for user_succ in user_succubus:
            succubus = self.get_succubus_by_id(user_succ['succubus_id'])
            if succubus:
                embed.add_field(
                    name=f"{succubus['name']} ({succubus['rarity'].capitalize()})",
                    value=f"✨ Ability: {succubus['ability_description']}\n"
                          f"💀 Burden: {succubus['burden_description']}",
                    inline=False
                )
                if succubus['image']:
                    embed.set_thumbnail(url=succubus['image'])

        await ctx.send(embed=embed)

    @commands.command()
    async def succubusinfo(self, ctx, *, name: str):
        """Show detailed information about a specific succubus"""
        succubus = None
        for sid, sdata in self.get_all_succubus().items():
            if sdata['name'].lower() == name.lower():
                succubus = {"id": sid, **sdata}
                break

        if not succubus:
            await ctx.send("That succubus doesn't exist!")
            return

        embed = discord.Embed(title=succubus['name'], color=discord.Color.purple())
        embed.add_field(name="✨ Ability", value=succubus['ability_description'], inline=False)
        embed.add_field(name="💀 Burden", value=succubus['burden_description'], inline=False)
        embed.add_field(name="Rarity", value=succubus['rarity'].capitalize(), inline=False)
        
        if succubus['image']:
            embed.set_image(url=succubus['image'])

        await ctx.send(embed=embed)
    
    @commands.command()
    async def ritual(self, ctx):
        """Perform a ritual to summon a succubus"""
        prefix = self.bot.command_prefix
        file_manager = self.bot.get_cog('FileManager')
        user = ctx.author.name
        user_id = str(ctx.author.id)

        # Check if user has a Ritual item
        user_items = file_manager.db.get_user_items(user_id)
        if not user_items.get("Ritual", 0) > 0:
            await ctx.send(f"{user}, you don't have any Ritual items! Buy one from the store using `{prefix}store`")
            return

        # Use the Ritual item
        file_manager.db.update_item_quantity(user_id, "Ritual", -1)

        # Get probabilities from JSON
        probabilities = file_manager.get_probabilities()
        rarity_probs = probabilities.get("ritual_probabilities", {})
        
        # Determine rarity based on probabilities
        rarity = random.choices(
            list(rarity_probs.keys()),
            weights=list(rarity_probs.values()),
            k=1
        )[0]

        # Get all succubus of the chosen rarity
        available_succubus = self.get_succubus_by_rarity(rarity)
        if not available_succubus:
            await ctx.send("Error: No succubus available of the chosen rarity!")
            return

        # Randomly select a succubus
        chosen_succubus = random.choice(available_succubus)
        
        # Check if user already has this succubus
        user_succubus = file_manager.db.get_user_succubus(user_id)
        has_succubus = any(s['succubus_id'] == chosen_succubus['id'] for s in user_succubus)

        if has_succubus:
            # Compensation for duplicate
            compensation_coins = {
                "common": 20,
                "rare": 40,
                "epic": 80,
                "legendary": 150
            }
            coin_amount = compensation_coins.get(rarity, 20)
            file_manager.db.update_fapcoins(user_id, coin_amount)
            
            embed = discord.Embed(
                title="Duplicate Succubus!",
                description=f"You already have {chosen_succubus['name']}! You received {coin_amount} Fapcoins as compensation.",
                color=discord.Color.gold()
            )
        else:
            # Add succubus to user's collection
            file_manager.db.add_user_succubus(user_id, chosen_succubus['id'])

            embed = discord.Embed(
                title="✨ New Succubus Summoned! ✨",
                description=f"You summoned {chosen_succubus['name']} ({rarity.capitalize()})!",
                color=discord.Color.purple()
            )

        embed.add_field(name="✨ Ability", value=chosen_succubus['ability_description'], inline=False)
        embed.add_field(name="💀 Burden", value=chosen_succubus['burden_description'], inline=False)
        
        if chosen_succubus['image']:
            embed.set_image(url=chosen_succubus['image'])

        await ctx.send(embed=embed)

    @commands.command()
    async def listsuccubus(self, ctx):
        """List all available succubus"""
        succubus_list = self.get_all_succubus().values()
        
        embed = discord.Embed(title="Available Succubus", color=discord.Color.purple())
        
        for succubus in succubus_list:
            embed.add_field(
                name=f"{succubus['name']} ({succubus['rarity'].capitalize()})",
                value=f"✨ Ability: {succubus['ability_description']}\n"
                      f"💀 Burden: {succubus['burden_description']}",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Succubus(bot))