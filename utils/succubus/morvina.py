import asyncio
import random
import discord
import json
from .base import SuccubusHandler

class MorvinaHandler(SuccubusHandler):
    """
    Handler for the Morvina succubus
    
    Ability: Every hour, there is a 10% chance for a Loot Box to appear in the configured chat.
             The user has 5 seconds to claim it by reacting with an emoji. Only the user with Morvina active can claim.
    Burden: The user loses 3 Fapcoins every time a fap is added.
    """
    
    def __init__(self, bot):
        super().__init__(bot)
        self.succubus_id = "morvina"  # Unique identifier for Morvina
        self.loot_box_chance = 0.10  # 10% chance per hour
        self.loot_box_duration = 5  # 5 seconds to claim
        self.burden_cost = 3  # Lose 3 Fapcoins per fap
        self.loot_box_users = {}  # Track users with active loot box tasks
        self.config = self.load_config()  # Load config for channel ID
        
    def load_config(self):
        """Loads the configuration from config.json"""
        with open('config.json', 'r') as f:
            return json.load(f)
    
    def get_succubus_id(self):
        """
        Returns the ID of Morvina
        
        Returns:
            str: The succubus ID
        """
        return self.succubus_id
    
    async def apply_ability(self, ctx, **kwargs):
        """
        Applies Morvina's ability: Periodically spawns a Loot Box for the user
        
        Args:
            ctx: The command context
            **kwargs: Additional arguments
            
        Returns:
            bool: True if the ability was applied
        """
        user_id = str(ctx.author.id)
        
        # Check if the user is already being monitored for loot boxes
        if user_id in self.loot_box_users:
            return True
            
        # Create a new task to spawn loot boxes periodically
        task = asyncio.create_task(self.spawn_loot_boxes(user_id))
        self.loot_box_users[user_id] = task
        
        return True
    
    async def spawn_loot_boxes(self, user_id):
        """
        Periodically spawns loot boxes for the user in the configured channel
        
        Args:
            user_id (str): The Discord user ID
        """
        try:
            while self.is_active_for_user(user_id):
                # Wait for 1 hour
                await asyncio.sleep(3600) 
                
                # Check if still active
                if not self.is_active_for_user(user_id):
                    break
                    
                # 10% chance to spawn a loot box
                if random.random() < self.loot_box_chance:
                    # Get the configured channel
                    channel_id = self.config['allowed_channels'][0]  # Assuming the first channel
                    channel = self.bot.get_channel(channel_id)
                    if not channel:
                        print(f"Channel {channel_id} not found")
                        continue
                    
                    # Send the loot box message
                    embed = discord.Embed(
                        title="✨ Loot Box Appeared! ✨",
                        description=f"<@{user_id}>, clique no 🎁 para reivindicar em 5 segundos!",
                        color=discord.Color.gold()
                    )
                    message = await channel.send(embed=embed)
                    await message.add_reaction("🎁")  # Add the emoji reaction
                    
                    # Define check for claiming (only the user with Morvina can claim)
                    def check(reaction, user):
                        return user.id == int(user_id) and str(reaction.emoji) == "🎁" and reaction.message.id == message.id
                    
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=self.loot_box_duration)
                        # Grant a reward (e.g., random item)
                        reward = random.choice(["Fap Shield", "Ultra Fap Shield", "Redemption", "Supreme Redemption", "Faproll", "Ritual"])
                        file_manager = self.bot.get_cog('FileManager')
                        file_manager.db.update_item_quantity(user_id, reward, 1)
                        await channel.send(f"{user.mention} claimed the loot box and received {reward}!")
                    except asyncio.TimeoutError:
                        await channel.send("The loot box expired!")
                    finally:
                        # Optionally clear reactions
                        await message.clear_reactions()
            
            # Clean up when no longer active
            if user_id in self.loot_box_users:
                del self.loot_box_users[user_id]
                
        except Exception as e:
            print(f"Error in spawn_loot_boxes for user {user_id}: {e}")
            if user_id in self.loot_box_users:
                del self.loot_box_users[user_id]
    
    async def apply_burden(self, ctx, **kwargs):
        """
        Applies Morvina's burden: Lose 3 Fapcoins every time a fap is added
        
        Note: This will be handled in the scoreboard logic.
        
        Returns:
            bool: True if the burden logic is in place
        """
        return True
    
    def get_burden_cost(self):
        """
        Returns the Fapcoin cost per fap added
        
        Returns:
            int: The number of Fapcoins lost per fap
        """
        return self.burden_cost

    def cleanup_tasks(self, user_id):
        """
        Cleans up any running tasks for a user
        
        Args:
            user_id (str): The Discord user ID
        """
        if user_id in self.loot_box_users:
            self.loot_box_users[user_id].cancel()
            del self.loot_box_users[user_id]