import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Shows all available commands"""
        embed = discord.Embed(
            title="🍆 FapBot Commands",
            description="Here's everything you can do!",
            color=discord.Color.blue()
        )

        # Scoreboard Commands
        embed.add_field(
            name="📊 Scoreboard",
            value="```\n"
                  "!scoreboard - View the current scoreboard\n"
                  "```",
            inline=False
        )

        # Store & Economy Commands
        embed.add_field(
            name="💰 Store & Economy",
            value="```\n"
                  "!store      - View the item store\n"
                  "!daily      - Get your daily Fapcoin (every 12 hours)\n"
                  "!fapcoin    - Check your Fapcoin balance\n"
                  "```",
            inline=False
        )

        # Items Commands
        embed.add_field(
            name="🎒 Items",
            value="```\n"
                  "!items             - View your inventory\n"
                  "!faproll           - Use a Faproll to get random items\n"
                  "!fapshield         - Activate 1-hour protection\n"
                  "!ultrafapshield    - Activate 2-hour protection\n"
                  "!redemption        - Remove 1 point from score\n"
                  "!supremeredemption - Remove 5 points from score\n"
                  "```",
            inline=False
        )

        # Succubus Commands
        embed.add_field(
            name="😈 Succubus System",
            value="```\n"
                  "!ritual        - Perform a ritual to summon a succubus\n"
                  "!mysuccubus    - View your succubus collection\n"
                  "!succubusinfo  - View info about a specific succubus\n"
                  "!listsuccubus  - View all available succubus\n"
                  "!activesuccubus - Show active effects from your succubus\n"
                  "```",
            inline=False
        )

        # Admin Commands (only shown to admins)
        if ctx.author.guild_permissions.administrator:
            embed.add_field(
                name="⚡ Admin Commands",
                value="```\n"
                      "!remove <user> <amount> - Remove points from user\n"
                      "!givesuccubus <user> <succubus> - Give succubus to user\n"
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