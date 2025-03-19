import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Shows all available commands"""
        prefix = self.bot.command_prefix
        embed = discord.Embed(
            title="🍆 FapBot Commands",
            description="Here's everything you can do!",
            color=discord.Color.blue()
        )

        # Scoreboard Commands
        embed.add_field(
            name="📊 Scoreboard",
            value="```\n"
                  f"{prefix}scoreboard - View the current scoreboard\n"
                  "```",
            inline=False
        )

        # Store & Economy Commands
        embed.add_field(
            name="💰 Store & Economy",
            value="```\n"
                  f"{prefix}store      - View the item store\n"
                  f"{prefix}daily      - Get your daily Fapcoin (every 12 hours)\n"
                  f"{prefix}fapcoin    - Check your Fapcoin balance\n"
                  "```",
            inline=False
        )

        # Items Commands
        embed.add_field(
            name="🎒 Items",
            value="```\n"
                  f"{prefix}items             - View your inventory\n"
                  f"{prefix}faproll           - Use a Faproll to get random items\n"
                  f"{prefix}fapshield         - Activate 1-hour protection\n"
                  f"{prefix}ultrafapshield    - Activate 2-hour protection\n"
                  f"{prefix}redemption        - Remove 1 point from score\n"
                  f"{prefix}supremeredemption - Remove 5 points from score\n"
                  f"{prefix}ritual            - Draw a succubus with abilities and burdens\n"
                  "```",
            inline=False
        )

        # Succubus Commands
        embed.add_field(
            name="😈 Succubus System",
            value="```\n"
                  f"{prefix}ritual        - Perform a ritual to summon a succubus\n"
                  f"{prefix}mysuccubus    - View your succubus collection\n"
                  f"{prefix}succubusinfo  - View info about a specific succubus\n"
                  f"{prefix}listsuccubus  - View all available succubus\n"
                  f"{prefix}activate      - Activates a succubus, gaining its abilities (Cooldown - 1 week)\n"
                  f"{prefix}activesuccubus - Show active effects from your succubus\n"
                  f"{prefix}fairtrade     - Trade 10 fapcoins for 1 less score (Must have Selphira active)\n"
                  "```",
            inline=False
        )

        # Admin Commands (only shown to admins)
        if ctx.author.guild_permissions.administrator:
            embed.add_field(
                name="⚡ Admin Commands",
                value="```\n"
                      f"{prefix}remove <user> <amount> - Remove points from user\n"
                      f"{prefix}addcoin <user> <amount> - Give fapcoins to user\n"
                      f"{prefix}givesuccubus <user> <succubus> - Give succubus to user\n"
                      "```",
                inline=False
            )

        embed.set_footer(text="Remember: The goal is to have the lowest score! 😉")
        
        await ctx.send(embed=embed)

async def setup(bot):
    # Remove the default help command before adding our custom one
    if bot.help_command is not None:
        bot.help_command = None
    
    await bot.add_cog(HelpCog(bot))