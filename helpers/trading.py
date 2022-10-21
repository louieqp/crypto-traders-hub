import helpers.decorators as d
import json
import helpers.constants as c
import discord

def float_to_str(value: float) -> str:
    result = str(value)
    if value == int(value):
        result = f"{int(value)}"
    return result

def build_signal_message(coin: str, open_price: float, target: float, stoploss: float, trade_type: str, leverage: int = 10, chart_url: str = '', vip: str = 'no') -> str:
    msg = "$" + coin
    buy_long = ("(BUY/LONG)" if trade_type == "long" else "(SELL/SHORT)")
    msg = d.bold(msg + ' ' + buy_long) + "\n"
    msg += ("<@331216699095515138>" if vip == 'yes' or vip == 'y' else "<@187703597964853248>") + '\n\n'
    msg += d.bold('Entry: ') + f"{float_to_str(open_price)}\n"
    msg += d.bold('Target: ') + f"{float_to_str(target)}\n"
    msg += d.bold('Stoploss: ') + f"{float_to_str(stoploss)}\n"
    msg += d.bold('Leverage: ') + f'cross {leverage}x\n\n'
    risk = abs(stoploss-open_price)/open_price * 100
    gain = abs(target-open_price)/open_price * 100
    msg += f"Risking {risk:.2f}% to gain {gain:.2f}% on this trade (x {leverage})" + '\n\n'
    if chart_url != '':
        msg += chart_url
    return msg

def get_closed_message(trade_id: int, closed_percent: int, totally_closed: bool):
    msg = f"Closed {closed_percent}% of trade {trade_id}." if not totally_closed else f"Closed trade {trade_id}."
    embed = discord.Embed(description=msg, color=c.MONEY_GREEN)
    return embed

def is_valid_coin(coin: str) -> bool:
    if str.upper(coin) in c.VALID_COINS:
        return True
    return False

def get_sent_message_notification(trade_id: int) -> discord.Embed:
    embed = discord.Embed(
        description=f"Sent. The id for this trade is {trade_id}",
        color=c.MONEY_GREEN
    )
    embed.set_footer(text=f"For more information you can try /trades or /profile")
    return embed

def get_cancel_message_notification() -> discord.Embed:
    embed = discord.Embed(
        description="Canceled.",
        color=c.RED
    )
    return embed

def get_signal_message(msg: str, trade_type: str) -> discord.Embed:
    embed_color = (c.MONEY_GREEN if trade_type == 'long' else c.RED)
    embed = discord.Embed(
        description=msg,
        color=embed_color
    )
    return embed