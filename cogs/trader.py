from dis import disco
import platform
import random
from tokenize import Double

import aiohttp
import discord
from discord import Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks
from helpers import constants as c

class Trader(commands.Cog, name="trade"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="long",
        description="Opens a BUY/LONG trade."
    )
    async def long(self, context: Context) -> None:
        
        await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Trader(bot))