from distutils.command.build import build
from datetime import datetime
import json
from logging import exception

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
        name="open",
        description="Opens a position."
    )
    async def open(self, context: Context, trade_type: str, coin: str, open_price: float, target: float, stoploss: float, leverage: int = 10, chart_url: str = '', vip: str = 'no'):
        trade_type = str.lower(trade_type)
        vip = str.lower(vip)
        coin = str.upper(coin)
        await self.__validate_position(trade_type, coin, open_price, target, stoploss, vip)

        # Confirm signal
        future_str = c.TRADE_TYPE_STR[trade_type]
        msg = th.build_signal_message(coin, open_price, target, stoploss, trade_type, leverage, chart_url, vip)
        confirm_msg = f"Please confirm your {future_str} position:\n {msg}"
        buttons = Confirm()
        embed = discord.Embed(color=c.MONEY_GREEN)
        embed.add_field(name=trade_type.capitalize(), value=confirm_msg, inline=False)
        message = await context.send(embed=embed, view=buttons)
        await buttons.wait()

        # Send signal
        if buttons.confirmed:
            trade_id = await db_manager.open_trade(context.author.id, trade_type, coin, open_price, target, stoploss, leverage, vip)
            if vip in c.YES_OPTIONS:
                channel_id = c.VIP_SIGNALS_CHANNEL
            else:
                channel_id = c.PUBLIC_SIGNALS_CHANNEL
            signal_embed = th.get_signal_message(msg, trade_type)
            signal_embed.set_author(name=context.author.mention, icon_url=context.author.display_avatar)
            channel = self.bot.get_channel(channel_id)
            await channel.send(embed=signal_embed)
            embed = th.get_sent_message_notification(trade_id)
        else:
            embed = th.get_cancel_message_notification()
        await message.edit(embed=embed, view=None, content=None)

    async def __validate_position(self, trade_type, coin: str, open_price: float, target: float, stoploss: float, vip: str) -> None:
        if trade_type not in c.VALID_OPEN_ARGUMENTS:
            raise exceptions.InvalidArgument(f'Invalid trade type argument: {trade_type}')

        if trade_type == 'long':
            self.__validate_long(open_price, target, stoploss)
        else:
            self.__validate_short(open_price, target, stoploss)

        if not th.is_valid_coin(coin):
            raise exceptions.InvalidOrUnavailableCoin

        if vip not in c.VALID_VIP_ARGUMENTS:
            raise exceptions.InvalidArgument(f'Invalid vip argument: {vip}, insert (yes/no)')

    async def __validate_long(self, open_price: float, target: float, stoploss: float) -> None:
        # Input validation for long position
        if open_price > target or open_price < stoploss:
            raise exceptions.BadLongFormat

    async def __validate_short(self, open_price: float, target: float, stoploss: float) -> None:
        # Input validation for short position
        if open_price < target or open_price > stoploss:
            raise exceptions.BadShortFormat

    @commands.hybrid_command(
        name="close",
        description="Closes a position or part of it."
    )
    async def close(self, context: Context, trade_id: int, closed_price: float, closed_percent: int = 100):
        # Check if user is allowed to make changes
        rows = await db_manager.get_user_from_trade_id(trade_id)
        if len(rows) < 1:
            raise exceptions.IdNotFound
        with open("config.json") as file:
            data = json.load(file)
        if context.author.id not in data['owners'] and rows[0] != context.author.id:
            raise exceptions.UserNotAllowed    
        
        # Check if closed_percent is valid
        left_to_close = await db_manager.get_trade_left_to_close(trade_id)
        # Closed_percent = 100 then trade is over
        if closed_percent == 100:
            await db_manager.close_trade_percent(trade_id, closed_price, left_to_close)
            await db_manager.close_trade(trade_id, closed_price)
            embed = th.get_closed_message(trade_id, closed_percent, True)
            await context.send(embed=embed)
            return
        # User wants to close more than available
        elif closed_percent > left_to_close:
            raise exceptions.InvalidClosedPercent(f"Trade {trade_id} has only {left_to_close}% left to close.")
        # Close trade
        # If we get here, closed percent is a correct amount
        totally_closed = False
        new_left_to_close = await db_manager.close_trade_percent(trade_id, closed_price, closed_percent)
        if new_left_to_close == 0:
            await db_manager.close_trade(trade_id, closed_price)
            totally_closed = True

        embed = th.get_closed_message(trade_id, closed_percent, totally_closed)
        await context.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Trader(bot))
