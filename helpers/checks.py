import json
from typing import Callable, TypeVar

from discord.ext import commands
from exceptions import *

from helpers import db_manager

T = TypeVar("T")


def is_owner() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is an owner of the bot.
    """

    async def predicate(context: commands.Context) -> bool:
        with open("config.json") as file:
            data = json.load(file)
        if context.author.id not in data["owners"]:
            raise UserNotOwner
        return True

    return commands.check(predicate)

def is_moderator() -> Callable[[T], T]:
    """
    Custom check to verify that the user executing the command is at least a moderator.
    """

    async def predicate(context: commands.Context) -> bool:
        with open("config.json") as file:
            data = json.load(file)
        found = False
        for role in context.author.roles:
            if role in data["moderators"] or role in data["owners"]:
                found = True
                break
        if not found:
            raise UserNotModerator
        return True

    return commands.check(predicate)