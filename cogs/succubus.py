import discord
from discord.ext import commands
import random

class Succubus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mysuccubus(self, ctx):
        """Show all succubus owned by the user"""
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        
        succubus_list = file_manager.db.get_user_succubus(user_id)
        if not succubus_list:
            await ctx.send("You don't have any succubus yet!")
            return

        embed = discord.Embed(title=f"{ctx.author.name}'s Succubus Collection", color=discord.Color.purple())
        
        for succubus in succubus_list:
            embed.add_field(
                name=f"{succubus['name']} ({succubus['rarity'].capitalize()})",
                value=f"✨ Ability: {succubus['ability_description']}\n"
                      f"💀 Burden: {succubus['burden_description']}",
                inline=False
            )
            if succubus['image_url']:
                embed.set_thumbnail(url=succubus['image_url'])

        await ctx.send(embed=embed)

    @commands.command()
    async def succubusinfo(self, ctx, *, name: str):
        """Show detailed information about a specific succubus"""
        file_manager = self.bot.get_cog('FileManager')
        succubus_list = file_manager.db.get_all_succubus()
        
        # Find succubus by name (case-insensitive)
        succubus = None
        for s in succubus_list:
            if s['name'].lower() == name.lower():
                succubus = s
                break
                
        if not succubus:
            await ctx.send("That succubus doesn't exist!")
            return

        embed = discord.Embed(title=succubus['name'], color=discord.Color.purple())
        embed.add_field(name="✨ Ability", value=succubus['ability_description'], inline=False)
        embed.add_field(name="💀 Burden", value=succubus['burden_description'], inline=False)
        embed.add_field(name="Rarity", value=succubus['rarity'].capitalize(), inline=False)
        
        if succubus['image_url']:
            embed.set_image(url=succubus['image_url'])

        await ctx.send(embed=embed)
    
    @commands.command()
    async def ritual(self, ctx):
        """Perform a ritual to summon a succubus"""
        file_manager = self.bot.get_cog('FileManager')
        user = ctx.author.name
        user_id = str(ctx.author.id)

        # Get user's items
        user_items = file_manager.db.get_user_items(user_id)
        
        # Check if user has a Ritual item
        if not user_items.get("Ritual", 0) > 0:
            await ctx.send(f"{user}, you don't have any Ritual items! Buy one from the store using `!store`")
            return

        # Use the Ritual item
        file_manager.db.update_item_quantity(user_id, "Ritual", -1)

        # Get probabilities from JSON (keep this in JSON for easy configuration)
        probabilities = file_manager.get_probabilities()
        rarity_probs = probabilities.get("ritual_probabilities", {})
        
        # Determine rarity based on probabilities
        rarity = random.choices(
            list(rarity_probs.keys()),
            weights=list(rarity_probs.values()),
            k=1
        )[0]

        # Get all succubus of the chosen rarity
        available_succubus = file_manager.db.get_succubus_by_rarity(rarity)
        if not available_succubus:
            await ctx.send("Error: No succubus available of the chosen rarity!")
            return

        # Randomly select a succubus
        chosen_succubus = random.choice(available_succubus)
        
        # Check if user already has this succubus
        user_succubus = file_manager.db.get_user_succubus(user_id)
        has_succubus = any(s['succubus_id'] == chosen_succubus['succubus_id'] for s in user_succubus)

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
            file_manager.db.add_user_succubus(user_id, chosen_succubus['succubus_id'])

            embed = discord.Embed(
                title="✨ New Succubus Summoned! ✨",
                description=f"You summoned {chosen_succubus['name']} ({rarity.capitalize()})!",
                color=discord.Color.purple()
            )

        embed.add_field(name="✨ Ability", value=chosen_succubus['ability_description'], inline=False)
        embed.add_field(name="💀 Burden", value=chosen_succubus['burden_description'], inline=False)
        
        if chosen_succubus['image_url']:
            embed.set_image(url=chosen_succubus['image_url'])

        await ctx.send(embed=embed)

    def apply_succubus_effects(self, user_id, effect_type, value):
        """Apply both abilities and burdens of succubus to a value"""
        file_manager = self.bot.get_cog('FileManager')
        user_succubus = file_manager.db.get_user_succubus(str(user_id))
        if not user_succubus:
            return value

        multiplier = 1.0
        for succubus in user_succubus:
            # Apply positive abilities
            if succubus['ability'] == effect_type:
                if effect_type == "score_multiplier":
                    multiplier *= 1.5
                elif effect_type == "coin_boost" and random.random() < 0.3:
                    multiplier *= 1.3
                elif effect_type == "shield_extension":
                    multiplier *= 1.5
            
            # Apply burdens
            if succubus['burden'] == effect_type:
                if effect_type == "coin_reduction":
                    multiplier *= 0.7
                elif effect_type == "shield_reduction":
                    multiplier *= 0.85
                elif effect_type == "double_points" and random.random() < 0.2:
                    multiplier *= 2

        return value * multiplier

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def givesuccubus(self, ctx, user: discord.Member, *, succubus_name: str):
        """Give a succubus to a user (Admin only)"""
        file_manager = self.bot.get_cog('FileManager')
        succubus_list = file_manager.db.get_all_succubus()
        
        # Find succubus by name
        succubus = None
        for s in succubus_list:
            if s['name'].lower() == succubus_name.lower():
                succubus = s
                break

        if not succubus:
            await ctx.send("That succubus doesn't exist!")
            return

        # Add succubus to user's collection
        file_manager.db.add_user_succubus(str(user.id), succubus['succubus_id'])
        
        embed = discord.Embed(
            title="New Succubus Acquired!",
            description=f"{user.mention} received {succubus['name']}!",
            color=discord.Color.purple()
        )
        embed.add_field(name="✨ Ability", value=succubus['ability_description'], inline=False)
        embed.add_field(name="💀️ Burden", value=succubus['burden_description'], inline=False)
        
        if succubus['image_url']:
            embed.set_image(url=succubus['image_url'])
        
        await ctx.send(embed=embed)

    @commands.command()
    async def listsuccubus(self, ctx):
        """List all available succubus"""
        file_manager = self.bot.get_cog('FileManager')
        succubus_list = file_manager.db.get_all_succubus()
        
        embed = discord.Embed(title="Available Succubus", color=discord.Color.purple())
        
        for succubus in succubus_list:
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
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        
        succubus_list = file_manager.db.get_user_succubus(user_id)
        if not succubus_list:
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