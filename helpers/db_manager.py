import aiosqlite

async def get_user_from_trade_id(trade_id: int) -> int:
    """
    This function will check if the user started a trade or has enough permission to modify a trade
    """
    # Query for user_id linked to trade_id
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT user_id FROM trades WHERE id=? LIMIT 1", (trade_id,)) as cursor:
            rows = await cursor.fetchone()
            return rows[0] if rows is not None else -1

async def get_leaderboard() -> list:
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT user_id, trade_id, coin, profit FROM leaderboard") as cursor:
            rows = await cursor.fetchall()
            return rows

async def getUserProfile(user_id: int):
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT user_id, wins, losses, total_profit, avg_profit FROM user_profiles WHERE user_id=?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result

async def getUserTrades(user_id: int) -> list:
    """
    Description.

    :param user_id: 
    """
    async with aiosqlite.connect("database/database.db") as db:
        result = await db.execute(
            "SELECT trade_id, coin, type, profit, close_price FROM user_trades WHERE user_id=? ORDER BY trade_id", (user_id,))
        async with result as cursor:
            rows = await cursor.fetchall()
            return rows

async def open_trade(user_id: int, trade_type: str, coin: str, open_price: float, target: float, stoploss: float, leverage: int = 10, vip: bool = False) -> int:
    """
    This function will add a trade to the database

    :param user_id: The ID of the user that is opening the trade
    :param *args: Arguments to open a trade
    """
    async with aiosqlite.connect("database/database.db") as db:
        result = await db.execute("SELECT id FROM trades ORDER BY id DESC LIMIT 1")
        # Get the last `id`
        async with result as cursor:
            rows = await cursor.fetchone()
            trade_id = rows[0]+1 if rows is not None else 1
            await db.execute("INSERT INTO trades(id, user_id, type, coin, open_price, target, stoploss, leverage, vip) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (trade_id, user_id, trade_type, coin, open_price, target, stoploss, leverage, vip))
            await db.commit()
            return trade_id
    # Return trade_id or open trades?

async def set_initial_close_trade(trade_id: int, open_price: float) -> None:
    """
    This function updates the close price for a trade

    :param user_id: The ID of the user that is closing the trade
    :param trader_id: The ID of the trade to be closed
    :param close: The price at which the trade was closed
    """
    async with aiosqlite.connect("database/database.db") as db:
        result = await db.execute("SELECT id FROM trades ORDER BY id DESC LIMIT 1")
        # Get the last `id`
        async with result as cursor:
            rows = await cursor.fetchone()
            close_id = rows[0]+1 if rows is not None else 1
            await db.execute("INSERT INTO closing_points(id, trade_id, closed_price, closed_percent, closed_at) VALUES (?, ?, ?, 0, CURRENT_TIMESTAMP)", (close_id, trade_id, open_price)) 
            await db.commit()

async def get_trade_left_to_close(trade_id: int) -> int:
    # Get left to close trade
    async with aiosqlite.connect("database/database.db") as db:
        result = await db.execute("SELECT left_to_close FROM trades_progress WHERE trade_id=?", (trade_id,))
        async with result as cursor:
            rows = await cursor.fetchone()
            left_to_close = rows[0]
            return left_to_close

async def close_trade_percent(trade_id: int, closed_price: float, closed_percent: int = 100) -> int:
    """
    This function updates the close price for a trade

    :param user_id: The ID of the user that is closing the trade
    :param trader_id: The ID of the trade to be closed
    :param close: The price at which the trade was closed
    """
    async with aiosqlite.connect("database/database.db") as db:
        result = await db.execute("SELECT id FROM closing_points ORDER BY id DESC LIMIT 1")
        # Get the last `id`
        async with result as cursor:
            rows = await cursor.fetchone()
            close_id = rows[0]+1 if rows is not None else 1
            await db.execute("INSERT INTO closing_points(id, trade_id, closed_price, closed_percent, closed_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)", (close_id, trade_id, closed_price, closed_percent))
            await db.commit()
        
        result = await db.execute("SELECT left_to_close FROM trades_progress WHERE trade_id=?", (trade_id,))
        async with result as cursor:
            rows = await cursor.fetchone()
            left_to_close = rows[0]
            return left_to_close

async def close_trade(trade_id: int, close: float) -> list:
    """
    This function updates the close price for a trade

    :param user_id: The ID of the user that is closing the trade
    :param trader_id: The ID of the trade to be closed
    :param close: The price at which the trade was closed
    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("UPDATE trades SET close_price=?, closed_at=CURRENT_TIMESTAMP WHERE id=?", (close, trade_id))
        await db.commit()
        result = await db.execute(
            "SELECT id, type, coin, open_price, target, stoploss, vip FROM trades WHERE id=?", (trade_id,))
        async with result as cursor:
            rows = await cursor.fetchone()
            return rows

async def add_trade(user_id: int, trade_type: str, coin: str, open_price: float, close: float, target: float, stoploss: float, leverage: int = 10, vip: bool = False) -> list:
    """
    This function will add a warn to the database

    :param user_id: The ID of the user that should be warned
    :param reason: The reason why the user should be warned
    """
    async with aiosqlite.connect("database/database.db") as db:
        # Get the last `id`
        result = await db.execute(
            "SELECT id FROM trades ORDER BY id DESC LIMIT 1")
        async with result as cursor:
            rows = await cursor.fetchone()
            trade_id = rows[0]+1 if rows is not None else 1
            await db.execute("INSERT INTO trades(id, user_id, type, coin, open_price, close_price, target, stoploss, leverage, vip) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (trade_id, user_id, trade_type, coin, open_price, close, target, stoploss, leverage, vip))
            await db.commit()

        user_trades = await db.execute(
            "SELECT id, type, coin, open_price, target, stoploss, vip FROM trades WHERE user_id=? AND close IS NULL", (user_id,))
        async with user_trades as cursor:
            rows = await user_trades.fetchall()
            return rows

async def remove_trade(user_id: int, trade_id: int) -> list:
    """
    This function will remove a trade from the database.

    :param user_id: The ID of the user that should be warned.
    :param reason: The reason why the user should be warned.
    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("DELETE FROM trades WHERE id=?", (trade_id,))
        await db.commit()
        result = await db.execute(
            "SELECT id, type, coin, open_price, target, stoploss, vip  FROM trades WHERE user_id=? AND close IS NULL", (user_id,))
        async with result as rows:
            open_trades = await rows.fetchall()
            return open_trades