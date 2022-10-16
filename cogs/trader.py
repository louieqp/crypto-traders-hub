from distutils.command.build import build
from datetime import datetime
import json

import aiohttp
import discord
from discord import Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, db_manager
from helpers import constants as c
from helpers import trading as th
from helpers.modals import Confirm
from helpers import decorators as d

import exceptions

class Trader(commands.Cog, name="trade"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="long",
        description="Opens a BUY/LONG position."
    )
    async def long(self, context: Context, coin: str, open_price: float, target: float, stoploss: float, leverage: int = 10, chart_url: str = '', vip: str = 'no') -> None:
        # Input validation
        if open_price > target or open_price < stoploss:
            raise exceptions.BadLongFormat
        elif not th.is_valid_coin(coin):
            raise exceptions.InvalidOrUnavailableCoin

        # Confirm signal
        msg = th.build_signal_message(coin, open_price, target, stoploss, 'long', leverage, chart_url, vip)
        confirm_msg = f"Please confirm your BUY/LONG position:\n {msg}"
        buttons = Confirm()
        embed = discord.Embed(color=c.MONEY_GREEN)
        embed.add_field(name="Long", value=confirm_msg, inline=False)
        message = await context.send(embed=embed, view=buttons)
        await buttons.wait()
        if buttons.confirmed:
            trade_id = db_manager.open_trade(context.author.id, 'long', coin, open_price, target, stoploss, leverage, vip)
            if str.lower(vip) == 'y' or str.lower(vip) == 'yes':
                channel_id = c.VIP_SIGNALS_CHANNEL
            else:
                channel_id = c.PUBLIC_SIGNALS_CHANNEL
            signal_embed = th.get_signal_message(msg, 'long')
            print(context.author.mention)
            signal_embed.set_author(name=context.author.display_name, icon_url=context.author.display_icon)
            channel = self.bot.get_channel(channel_id)
            await channel.send(embed=signal_embed)
            embed = th.get_sent_message_notification(trade_id)
        else:
            embed = th.get_cancel_message_notification()
        await message.edit(embed=embed, view=None, content=None)

    @commands.hybrid_command(
        name="short",
        description="Opens a SELL/SHORT position."
    )
    async def short(self, context: Context, coin: str, open_price: float, target: float, stoploss: float, leverage: int = 10, chart_url: str = '', vip: str = 'no') -> None:
        # Input validation
        if open_price < target or open_price > stoploss:
            raise exceptions.BadShortFormat
        elif not th.is_valid_coin(coin):
            raise exceptions.InvalidOrUnavailableCoin

        # Confirm signal
        msg = th.build_signal_message(coin, open_price, target, stoploss, 'short', leverage, chart_url, vip)
        confirm_msg = f"Please confirm your SELL/SHORT position:\n {msg}"
        buttons = Confirm()
        embed = discord.Embed(color=c.MONEY_GREEN)
        embed.add_field(name="Short", value=confirm_msg, inline=False)
        message = await context.send(embed=embed, view=buttons)
        await buttons.wait()
        # Send signal to corresponding channel
        if buttons.confirmed:
            trade_id = db_manager.open_trade(context.author.id, 'short', coin, open_price, target, stoploss, leverage, vip)
            if str.lower(vip) == 'y' or str.lower(vip) == 'yes':
                channel_id = c.VIP_SIGNALS_CHANNEL
            else:
                channel_id = c.PUBLIC_SIGNALS_CHANNEL
            signal_embed = th.get_signal_message(msg, 'short')
            signal_embed.set_author(name=context.author.mention, icon_url=context.author.display_icon)
            channel = self.bot.get_channel(channel_id)
            await channel.send(embed=signal_embed)
            embed = th.get_sent_message_notification(trade_id)
        else:
            embed = th.get_cancel_message_notification()
        await message.edit(embed=embed, view=None, content=None)

    @commands.hybrid_command(
        name="close",
        description="Closes a position."
    )
    async def close(self, context: Context, trade_id: int, close: float):
        # Input validation
        rows = db_manager.get_user_from_trade_id(trade_id)
        if len(rows) < 1:
            raise exceptions.IdNotFound
        with open("config.json") as file:
            data = json.load(file)
        if context.author.id in data['owners'] or rows[0] == context.author.id:
            return True
        else:
            raise exceptions.UserNotAllowed

async def setup(bot):
    await bot.add_cog(Trader(bot))
