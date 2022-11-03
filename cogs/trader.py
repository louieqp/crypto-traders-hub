from distutils.command.build import build
from datetime import datetime
import json
from logging import exception

import aiohttp
import discord
from discord import Embed, Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, db_manager
from helpers import constants as c
from helpers import trading as th
from helpers.modals import Confirm
from helpers import decorators as d
from enum import Enum

import exceptions

class Trader(commands.Cog, name="trade"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="open",
        description="Opens a position."
    )
    async def open(self, context: Context, trade_type: c.TradeType, coin: str, open_price: float, target: float, stoploss: float, leverage: int = 10, chart_url: str = '', vip: str = 'no'):
        trade_type = trade_type.value
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
            await db_manager.set_initial_close_trade(trade_id,open_price)
            if vip in c.YES_OPTIONS:
                channel_id = c.VIP_SIGNALS_CHANNEL
            else:
                channel_id = c.PUBLIC_SIGNALS_CHANNEL
            signal_embed = th.get_signal_message(msg, trade_type)
            signal_embed.set_author(name=context.author.display_name, icon_url=context.author.display_avatar)
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
            await self.__validate_long(open_price, target, stoploss)
        else:
            await self.__validate_short(open_price, target, stoploss)

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

    @commands.hybrid_command(
        name="profile",
        description="Displays a user's profile"
    )
    async def profile(self, context: Context, user: discord.Member = None):
        if not user:
            user = context.author
    
        userProfile = await db_manager.getUserProfile(user.id)
        if userProfile is None:
            wins, loses, total_profit, avg_profit = [0]*4
        else:
            _, wins, loses, total_profit, avg_profit = userProfile
        embed = discord.Embed(title=f"{user.display_name}", description="Profile", color=c.PROFILE_COLOR)
        embed.add_field(name="Wins" ,value=wins, inline=True)
        embed.add_field(name="Loses", value=loses, inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=False)
        embed.add_field(name="Total Profit", value=f'{total_profit:.2f}%', inline=True)
        embed.add_field(name="Average Win", value=f'{avg_profit:.2f}%', inline=True)
        embed.set_thumbnail(url=user.display_avatar)

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="trades",
        description="Displays a user's trades list"
    )
    async def trades(self, context: Context, user: discord.Member = None):
        if not user:
            user = context.author
    
        trades = await db_manager.getUserTrades(user.id)
        open_trades_section = []
        closed_trades_section = []
        
        for trade in trades:
            trade_id, coin, trade_type, profit, close_price = trade
            trade_detail = f'**Trade id**: {trade_id}\n'
            trade_detail += f'> Coin: {str.upper(coin)}\n'
            trade_detail += f'> Type: {trade_type}\n'
            trade_detail += f'> Profit: {profit:.2f}%'
            if close_price is None:
                open_trades_section.append(trade_detail)
            else:
                closed_trades_section.append(trade_detail)

        if trades is None:
            open_trades_section = ['No trades available']
            closed_trades_section = ['No trades available']
        if len(open_trades_section) == 0:
            open_trades_section = ['No trades available']
        if len(closed_trades_section) == 0:
            closed_trades_section = ['No trades available']

        embed = discord.Embed(title=f"{user.display_name}", color=c.PROFILE_COLOR)
        embed.add_field(name="Open Trades" ,value='\n'.join(open_trades_section), inline=False)
        embed.add_field(name="Closed Trades" ,value='\n'.join(closed_trades_section), inline=False)
        embed.set_thumbnail(url=user.display_avatar)

        await context.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Trader(bot))
