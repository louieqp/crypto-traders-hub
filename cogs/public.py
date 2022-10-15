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

class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        description="List all commands the bot has loaded."
    )
    async def help(self, context: Context) -> None:
        prefix = self.bot.config["prefix"]
        embed = discord.Embed(title="Help", description="List of available commands:", color=c.PURPLE)
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            data = []
            for command in commands:
                description = command.description.partition('\n')[0]
                data.append(f"{prefix}{command.name}: {description}")
            help_text = "\n".join(data)
            embed.add_field(name=i.capitalize(), value=f'```{help_text}```', inline=False)
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="recap",
        description="Sends a recap of closed trades in the last 16 hours."
    )
    # async def long(self, context: Context, interaction: Interaction, coin: str, open_price: float, tp: float, sl: float) -> None:
    async def recap(self, context: Context) -> None:
        data = []
        for arg in context.args:
            data.append(f"arg: {arg}")
        trade_text = "\n".join(data)
        trade_text = ''
        embed= discord.Embed(title="__**Daily Recap**__", color=c.PURPLE)
        free_title = "__Free Signals:__"
        free_text = f'''
:green_circle: MATIC/USDT +35% (open)
:red_circle: SUSHI/USDT -8% (open)
:green_circle: SHIB/USDT +6% (open)
        '''
        embed.add_field(name=free_title, value=free_text, inline=False)
        vip_title = "__VIP Signals:__"
        vip_text = f'''
:green_circle: XLM/USDT +23% (open)
:green_circle: LUNA2/USDT +32% (Closed)

``Total Winrate: 80%``
``Total Profit: 88%``
        '''
        embed.add_field(name=vip_title, value=vip_text, inline=False)
        await context.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))