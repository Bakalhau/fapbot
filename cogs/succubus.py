import discord
from discord.ext import commands
import random
import json
import os

class Succubus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = 'data/succubus.json'
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "available_succubus": {},
                "user_succubus": {}
            }

    def save_data(self):
        with open(self.data_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    @commands.command()
    async def mysuccubus(self, ctx):
        """Show all succubus owned by the user"""
        user_id = str(ctx.author.id)
        
        if user_id not in self.data["user_succubus"] or not self.data["user_succubus"][user_id]:
            await ctx.send("You don't have any succubus yet!")
            return

        embed = discord.Embed(title=f"{ctx.author.name}'s Succubus Collection", color=discord.Color.purple())
        
        for succubus_id, succubus_data in self.data["user_succubus"][user_id].items():
            succubus_info = self.data["available_succubus"][succubus_id]
            embed.add_field(
                name=f"{succubus_info['name']} ({succubus_info['rarity'].capitalize()})",
                value=f"✨ Ability: {succubus_info['ability_description']}\n"
                      f"💀 Burden: {succubus_info['burden_description']}",
                inline=False
            )
            if succubus_info["image"]:
                embed.set_thumbnail(url=succubus_info["image"])

        await ctx.send(embed=embed)

    @commands.command()
    async def succubusinfo(self, ctx, name: str):
        """Show detailed information about a specific succubus"""
        name = name.lower()
        if name not in self.data["available_succubus"]:
            await ctx.send("That succubus doesn't exist!")
            return

        succubus = self.data["available_succubus"][name]
        embed = discord.Embed(title=succubus["name"], color=discord.Color.purple())
        embed.add_field(name="✨ Ability", value=succubus["ability_description"], inline=False)
        embed.add_field(name="💀 Burden", value=succubus["burden_description"], inline=False)
        embed.add_field(name="Rarity", value=succubus["rarity"].capitalize(), inline=False)
        
        if succubus["image"]:
            embed.set_image(url=succubus["image"])

        await ctx.send(embed=embed)
    
    @commands.command()
    async def ritual(self, ctx):
        """Perform a ritual to summon a succubus"""
        file_manager = self.bot.get_cog('FileManager')
        user = ctx.author.name
        user_id = str(ctx.author.id)

        # Check if user has a Ritual item
        if not file_manager.user_items.get(user, {}).get("Ritual", 0) > 0:
            await ctx.send(f"{user}, you don't have any Ritual items! Buy one from the store using `!store`")
            return

        # Use the Ritual item
        file_manager.user_items[user]["Ritual"] -= 1
        file_manager.save_items()

        # Determine rarity based on probabilities
        with open('data/probabilities.json', 'r') as f:
            probs = json.load(f)
        
        rarity_probs = probs.get("ritual_probabilities", {})
        rarity = random.choices(
            list(rarity_probs.keys()),
            weights=list(rarity_probs.values()),
            k=1
        )[0]

        # Get all succubus of the chosen rarity
        available_succubus = [
            succ_id for succ_id, succ in self.data["available_succubus"].items()
            if succ["rarity"] == rarity
        ]

        if not available_succubus:
            await ctx.send("Error: No succubus available of the chosen rarity!")
            return

        # Randomly select a succubus of the chosen rarity
        chosen_succubus = random.choice(available_succubus)
        succubus_data = self.data["available_succubus"][chosen_succubus]

        # Check if user already has this succubus
        if user_id not in self.data["user_succubus"]:
            self.data["user_succubus"][user_id] = {}

        if chosen_succubus in self.data["user_succubus"][user_id]:
            # If user already has this succubus, give them some compensation
            compensation_coins = {
                "common": 20,
                "rare": 40,
                "epic": 80,
                "legendary": 150
            }
            coin_amount = compensation_coins.get(rarity, 20)
            file_manager.fapcoins[user] = file_manager.fapcoins.get(user, 0) + coin_amount
            file_manager.save_items()
            
            embed = discord.Embed(
                title="Duplicate Succubus!",
                description=f"You already have {succubus_data['name']}! You received {coin_amount} Fapcoins as compensation.",
                color=discord.Color.gold()
            )
        else:
            # Add the succubus to user's collection
            self.data["user_succubus"][user_id][chosen_succubus] = {
                "acquired_date": ctx.message.created_at.isoformat()
            }
            self.save_data()

            # Create embed for new succubus
            embed = discord.Embed(
                title="✨ New Succubus Summoned! ✨",
                description=f"You summoned {succubus_data['name']} ({rarity.capitalize()})!",
                color=discord.Color.purple()
            )

        embed.add_field(name="✨ Ability", value=succubus_data["ability_description"], inline=False)
        embed.add_field(name="💀 Burden", value=succubus_data["burden_description"], inline=False)
        
        if succubus_data["image"]:
            embed.set_image(url=succubus_data["image"])

        await ctx.send(embed=embed)

    def apply_succubus_effects(self, user_id, effect_type, value):
        """Apply both abilities and burdens of succubus to a value"""
        user_id = str(user_id)
        if user_id not in self.data["user_succubus"]:
            return value

        multiplier = 1.0
        for succubus_id in self.data["user_succubus"][user_id]:
            succubus = self.data["available_succubus"][succubus_id]
            
            # Apply positive abilities
            if succubus["ability"] == effect_type:
                if effect_type == "score_multiplier":
                    multiplier *= 1.5
                elif effect_type == "coin_boost" and random.random() < 0.3:
                    multiplier *= 1.3
                elif effect_type == "shield_extension":
                    multiplier *= 1.5
            
            # Apply burdens
            if succubus["burden"] == effect_type:
                if effect_type == "coin_reduction":
                    multiplier *= 0.7
                elif effect_type == "shield_reduction":
                    multiplier *= 0.85
                elif effect_type == "double_points" and random.random() < 0.2:
                    multiplier *= 2

        return value * multiplier

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def givesuccubus(self, ctx, user: discord.Member, succubus_name: str):
        """Give a succubus to a user (Admin only)"""
        succubus_name = succubus_name.lower()
        if succubus_name not in self.data["available_succubus"]:
            await ctx.send("That succubus doesn't exist!")
            return

        user_id = str(user.id)
        if user_id not in self.data["user_succubus"]:
            self.data["user_succubus"][user_id] = {}

        self.data["user_succubus"][user_id][succubus_name] = {
            "acquired_date": ctx.message.created_at.isoformat()
        }
        
        self.save_data()
        
        succubus = self.data["available_succubus"][succubus_name]
        embed = discord.Embed(
            title="New Succubus Acquired!",
            description=f"{user.mention} received {succubus['name']}!",
            color=discord.Color.purple()
        )
        embed.add_field(name="✨ Ability", value=succubus["ability_description"], inline=False)
        embed.add_field(name="💀 Burden", value=succubus["burden_description"], inline=False)
        
        if succubus["image"]:
            embed.set_image(url=succubus["image"])
        
        await ctx.send(embed=embed)

    @commands.command()
    async def listsuccubus(self, ctx):
        """List all available succubus"""
        embed = discord.Embed(title="Available Succubus", color=discord.Color.purple())
        
        for succubus_id, succubus in self.data["available_succubus"].items():
            embed.add_field(
                name=f"{succubus['name']} ({succubus['rarity'].capitalize()})",
                value=f"✨ Ability: {succubus['ability_description']}\n"
                      f"💀 Burden: {succubus['burden_description']}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command()
    async def activesuccubus(self, ctx):
        """Show active effects from your succubus"""
        user_id = str(ctx.author.id)
        
        if user_id not in self.data["user_succubus"] or not self.data["user_succubus"][user_id]:
            await ctx.send("You don't have any succubus!")
            return

        embed = discord.Embed(title="Active Succubus Effects", color=discord.Color.purple())
        
        # Calculate total effects
        score_mult = self.apply_succubus_effects(user_id, "score_multiplier", 1.0)
        coin_mult = self.apply_succubus_effects(user_id, "coin_boost", 1.0)
        shield_mult = self.apply_succubus_effects(user_id, "shield_extension", 1.0)

        # Show total effects
        effects_text = (
            f"Score Multiplier: x{score_mult:.2f}\n"
            f"Coin Multiplier: x{coin_mult:.2f}\n"
            f"Shield Duration: x{shield_mult:.2f}"
        )
        
        embed.add_field(name="Total Effects", value=effects_text, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Succubus(bot))