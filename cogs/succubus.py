import discord
from discord.ext import commands
import random
import json
import os
import time
from datetime import datetime, timedelta
from utils.succubus.manager import SuccubusManager
import asyncio

class Succubus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.succubus_data = self.load_succubus_data()
        self.succubus_manager = SuccubusManager(bot)
        self.bot.loop.create_task(self.initialize_active_succubus())
        
    async def initialize_active_succubus(self):
        """
        Initialize all active succubus abilities and burdens when the bot starts
        """
        # Wait for bot to be ready
        await self.bot.wait_until_ready()
        
        try:
            file_manager = self.bot.get_cog('FileManager')
            if not file_manager:
                print("ERROR: FileManager not found, cannot initialize succubus")
                return
                
            # Get all users with active succubus
            conn, cur = file_manager.db.get_connection()
            cur.execute("SELECT user_id, active_succubus FROM users WHERE active_succubus IS NOT NULL")
            users_with_active = cur.fetchall()
            conn.close()
            
            print(f"Initializing {len(users_with_active)} active succubus...")
            
            # Initialize each active succubus
            for user_data in users_with_active:
                user_id = user_data['user_id']
                succubus_id = user_data['active_succubus']
                
                # Get the handler
                handler = self.succubus_manager.handlers.get(succubus_id)
                if handler:
                    # Get the user object
                    user = await self.bot.fetch_user(int(user_id))
                    if user:
                        # Create a context-like object with just the necessary attributes
                        ctx = type('obj', (object,), {
                            'author': user,
                            'bot': self.bot,
                            'guild': None,
                            'channel': None,
                            'message': None,
                            'command': None
                        })
                        
                        # Apply ability and burden
                        try:
                            await handler.apply_ability(ctx)
                            await handler.apply_burden(ctx)
                            print(f"Initialized {succubus_id} for user {user_id}")
                        except Exception as e:
                            print(f"Error initializing {succubus_id} for user {user_id}: {e}")
        except Exception as e:
            print(f"Error in initialize_active_succubus: {e}")

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

    @commands.command(aliases=["ms"])
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
                level = user_succ.get('level', 1)
                xp = user_succ.get('xp', 0)
                xp_needed = self.calculate_xp_needed(level)
                embed.add_field(
                    name=f"{succubus['name']} ({succubus['rarity'].capitalize()}) - Level {level}",
                    value=f"XP: {xp}/{xp_needed}\n"
                        f"✨ Ability: {succubus['ability_description']}\n"
                        f"💀 Burden: {succubus['burden_description']}",
                    inline=False
                )
                if succubus['image']:
                    embed.set_thumbnail(url=succubus['image'])

        await ctx.send(embed=embed)

    @commands.command(aliases=["si"])
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
        file_manager = self.bot.get_cog('FileManager')
        user = ctx.author.name
        user_id = str(ctx.author.id)

        # Check if user has a Ritual item
        user_items = file_manager.db.get_user_items(user_id)
        if not user_items.get("Ritual", 0) > 0:
            await ctx.send(f"{user}, you don't have any Ritual items! Buy one from the store using `{self.bot.command_prefix}store`")
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
        existing_succubus = next((s for s in user_succubus if s['succubus_id'] == chosen_succubus['id']), None)

        await ctx.send("<:roulette:1352049721413206016> Rolling...")
        await asyncio.sleep(3)  # Use asyncio.sleep instead of time.sleep for async compatibility
        
        if existing_succubus:
            # Add XP to the existing succubus
            current_xp = existing_succubus.get('xp', 0)
            current_level = existing_succubus.get('level', 1)
            new_xp = current_xp + 1
            xp_needed = self.calculate_xp_needed(current_level)
            
            if new_xp >= xp_needed:
                # Level up the succubus
                new_level = current_level + 1
                new_xp = new_xp - xp_needed  # Reset XP after leveling up
                file_manager.db.update_succubus_level(user_id, chosen_succubus['id'], new_level, new_xp)
                await ctx.send(f"Your {chosen_succubus['name']} leveled up to level {new_level}!")
            else:
                # Just update XP
                file_manager.db.update_succubus_xp(user_id, chosen_succubus['id'], new_xp)
                await ctx.send(f"Your {chosen_succubus['name']} gained 1 XP! Current XP: {new_xp}/{xp_needed}")
        else:
            # Add new succubus with XP=0 and LVL=1
            file_manager.db.add_user_succubus(user_id, chosen_succubus['id'], xp=0, level=1)
            await ctx.send(f"You obtained a new succubus: {chosen_succubus['name']} (Level 1)!")

        # Display succubus info
        embed = discord.Embed(
            title="Succubus Info",
            description=f"{chosen_succubus['name']} ({rarity.capitalize()})",
            color=discord.Color.purple()
        )
        embed.add_field(name="✨ Ability", value=chosen_succubus['ability_description'], inline=False)
        embed.add_field(name="💀 Burden", value=chosen_succubus['burden_description'], inline=False)
        if chosen_succubus['image']:
            embed.set_image(url=chosen_succubus['image'])
        await ctx.send(embed=embed)

        @commands.command(aliases=["ls"])
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

    @commands.command(aliases=["ativar"])
    @commands.cooldown(1, 604800, commands.BucketType.user)  # 1-week cooldown
    async def activate(self, ctx, *, name: str):
        """Activates a succubus that the user owns (cooldown: 1 week)"""
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        
        # Check if the user has a succubus
        user_succubus = file_manager.db.get_user_succubus(user_id)
        if not user_succubus:
            await ctx.send("You don't own any succubus yet!")
            ctx.command.reset_cooldown(ctx)  # Reset cooldown if it fails
            return
        
        # Find the succubus by name
        succubus_id = None
        for sid, sdata in self.get_all_succubus().items():
            if sdata['name'].lower() == name.lower():
                succubus_id = sid
                succubus = sdata
                break
                
        if not succubus_id:
            await ctx.send(f"Succubus '{name}' not found!")
            ctx.command.reset_cooldown(ctx)  # Reset cooldown if it fails
            return
            
        # Check if the user owns this succubus
        if not any(s['succubus_id'] == succubus_id for s in user_succubus):
            await ctx.send(f"You do not own the succubus {name}!")
            ctx.command.reset_cooldown(ctx)  # Reset cooldown if it fails
            return
            
        # Check the timestamp of the last activation
        last_activation = file_manager.db.get_succubus_activation_time(user_id)
        if last_activation:
            time_diff = datetime.utcnow() - last_activation
            if time_diff < timedelta(days=7):
                days_left = 7 - time_diff.days
                hours_left = 24 - (time_diff.seconds // 3600)
                await ctx.send(f"You need to wait {days_left} more days and {hours_left} hours to activate another succubus!")
                ctx.command.reset_cooldown(ctx)  # Reset cooldown if it fails
                return
        
        # Confirmation message
        embed = discord.Embed(
            title="⚠️ Confirmation Required ⚠️",
            description=(
                f"Are you sure you want to activate **{succubus['name']}**?\n"
                "Once activated, you will be bound to this succubus for 1 week "
                "and cannot change to another one during that period.\n\n"
                "Reply with 'yes' to confirm or 'no' to cancel."
            ),
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.strip().lower() in ["yes", "no"]
        
        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            if response.content.strip().lower() == "yes":
                # Clean up any existing active succubus tasks
                active_succubus_id = file_manager.db.get_active_succubus(user_id)
                if active_succubus_id:
                    old_handler = self.succubus_manager.handlers.get(active_succubus_id)
                    if old_handler and hasattr(old_handler, 'cleanup_tasks'):
                        old_handler.cleanup_tasks(user_id)
                
                # Activate the succubus
                success = file_manager.db.activate_succubus(user_id, succubus_id)
                if success:
                    embed = discord.Embed(
                        title="✨ Succubus Activated! ✨",
                        description=f"You activated {succubus['name']} ({succubus['rarity'].capitalize()})!",
                        color=discord.Color.purple()
                    )
                    
                    embed.add_field(name="✨ Ability", value=succubus['ability_description'], inline=False)
                    embed.add_field(name="💀 Burden", value=succubus['burden_description'], inline=False)
                    
                    if succubus['image']:
                        embed.set_image(url=succubus['image'])
                    
                    # Apply the succubus ability and burden
                    handler = self.succubus_manager.handlers.get(succubus_id)
                    if handler:
                        await handler.apply_ability(ctx)
                        await handler.apply_burden(ctx)
                        
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Error activating the succubus!")
                    ctx.command.reset_cooldown(ctx)  # Reset cooldown if activation fails
            else:
                await ctx.send("Activation cancelled.")
                ctx.command.reset_cooldown(ctx)  # Reset cooldown since activation was cancelled
        except asyncio.TimeoutError:
            await ctx.send("Activation cancelled due to timeout.")
            ctx.command.reset_cooldown(ctx)  # Reset cooldown since activation was cancelled

    @commands.command(aliases=["as"])
    async def activesuccubus(self, ctx):
        """Shows the user's currently active succubus"""
        file_manager = self.bot.get_cog('FileManager')
        user_id = str(ctx.author.id)
        
        active_succubus_id = file_manager.db.get_active_succubus(user_id)
        if not active_succubus_id:
            await ctx.send("You don't have any active succubus at the moment!")
            return
            
        # Get succubus information
        succubus = self.get_succubus_by_id(active_succubus_id)
        if not succubus:
            await ctx.send("Error: Succubus not found in the database!")
            return
            
        # Get activation timestamp
        activation_time = file_manager.db.get_succubus_activation_time(user_id)
        if activation_time:
            time_diff = datetime.utcnow() - activation_time
            days_active = time_diff.days
            hours_active = time_diff.seconds // 3600
            
            # Calculate remaining time until the next activation
            next_activation = activation_time + timedelta(days=7)
            time_until = next_activation - datetime.utcnow()
            days_left = time_until.days
            hours_left = time_until.seconds // 3600
            
            activation_info = f"Active for: {days_active} days and {hours_active} hours\n"
            activation_info += f"Next activation available in: {days_left} days and {hours_left} hours"
        else:
            activation_info = "Activation details unavailable"
            
        embed = discord.Embed(
            title="🌟 Your Active Succubus 🌟",
            description=activation_info,
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name=f"{succubus['name']} ({succubus['rarity'].capitalize()})",
            value=f"✨ Ability: {succubus['ability_description']}\n"
                f"💀 Burden: {succubus['burden_description']}",
            inline=False
        )
        
        if succubus['image']:
            embed.set_image(url=succubus['image'])
            
        await ctx.send(embed=embed)
        
    @activate.error
    async def activate_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify the name of the succubus to activate!")
            ctx.command.reset_cooldown(ctx)  # Reset cooldown if name is missing
        elif isinstance(error, commands.CommandOnCooldown):
            # Convert seconds into days/hours
            cooldown = error.retry_after
            days = int(cooldown // (24 * 3600))
            hours = int((cooldown % (24 * 3600)) // 3600)
            await ctx.send(f"You need to wait {days} days and {hours} hours to activate another succubus!")
        else:
            await ctx.send(f"Error: {error}")

    @staticmethod
    def calculate_xp_needed(current_level):
        """
        Calculate the XP needed to reach the next level.
        
        Args:
            current_level (int): The current level of the succubus.
        
        Returns:
            int: The XP required to reach the next level.
        """
        return 5 * current_level

async def setup(bot):
    await bot.add_cog(Succubus(bot))