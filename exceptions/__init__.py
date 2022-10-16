from discord.ext import commands

class UserNotOwner(commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is not an owner of the bot.
    """

    def __init__(self, message="User is not an owner of the bot!"):
        self.message = message
        super().__init__(self.message)

class UserBlacklisted(commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is blacklisted.
    """

    def __init__(self, message="User is blacklisted!"):
        self.message = message
        super().__init__(self.message)

class UserNotModerator(commands.CheckFailure):
    """
    Thrown when user is attempting something, but is not a moderator of the server.
    """
    def __init__(self, message="User is not a moderator of the server!"):
        self.message=message
        super().__init__(self.message)

class BadLongFormat(commands.CommandError):
    """
    Thrown when user sends a bad long format.
    """
    def __init__(self, message="Make sure you specify target and stoploss are correctly for LONG position."):
        self.message = message
        super().__init__(self.message)

class BadShortFormat(commands.CommandError):
    """
    Thrown when user sends a bad short format.
    """
    def __init__(self, message="Make sure you specify target and stoploss are correctly for SHORT position."):
        self.message = message
        super().__init__(self.message)

class InvalidOrUnavailableCoin(commands.CommandError):
    """
    Thrown when user sends a coin we don't have.
    """
    def __init__(self, message="The specified coin is either invalid or unavailable."):
        self.message = message
        super().__init__(self.message)

class InvalidId(commands.CommandError):
    """
    Thrown when user sends a bad long format.
    """
    def __init__(self, message="The specified id is either invalid or unavailable."):
        self.message = message
        super().__init__(self.message)

class IdNotFound(commands.CommandError):
    """
    Thrown when user sends a bad long format.
    """
    def __init__(self, message="The specified id was not found."):
        self.message = message
        super().__init__(self.message)

class UserNotAllowed(commands.CommandError):
    """
    Thrown when user sends a bad long format.
    """
    def __init__(self, message="Are you sure you own this trade?"):
        self.message = message
        super().__init__(self.message)

