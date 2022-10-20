import aiosqlite

async def get_user_from_trade_id(trade_id: int) -> bool:
    """
    This function will check if the user started a trade or has enough permission to modify a trade
    """
    # Query for user_id linked to trade_id
    async with aiosqlite.connect("database/database.db") as connection:
        async with connection.execute("SELECT user_id FROM trades WHERE id=? LIMIT 1", (trade_id)) as cursor:
            rows = await cursor.fetchone()
            return rows

async def open_trade(user_id: int, trade_type: str, coin: str, open_price: float, target: float, stoploss: float, leverage: int = 10, vip: bool = False) -> int:
    """
    This function will add a trade to the database

    :param user_id: The ID of the user that is opening the trade
    :param *args: Arguments to open a trade
    """
    async with aiosqlite.connect("database/database.db") as connection:
        cursor = connection.cursor()
        # Get the last `id`
        rows = cursor.execute(
            "SELECT id FROM trades ORDER BY id DESC LIMIT 1").fetchone()
        trade_id = rows[0]+1 if rows is not None else 1
        cursor.execute("INSERT INTO trades(id, user_id, type, coin, open, target, stoploss, leverage, vip) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (trade_id, user_id, trade_type, coin, open_price, target, stoploss, leverage, vip))
        connection.commit()
        connection.close()
        set_initial_close_trade(trade_id,open_price)
        return trade_id

async def set_initial_close_trade(trade_id: int, open_price: float) -> None:
    """
    This function updates the close price for a trade

    :param user_id: The ID of the user that is closing the trade
    :param trader_id: The ID of the trade to be closed
    :param close: The price at which the trade was closed
    """
    connection = async with aiosqlite.connect("database/database.db")
    cursor = connection.cursor()  
    # Get the last `id`
    rows = cursor.execute(
        "SELECT id FROM closing_points ORDER BY id DESC LIMIT 1").fetchone()
    close_id = rows[0]+1 if rows is not None else 1
    cursor.execute("INSERT INTO closing_points(id, trade_id, closed_price, closed_percent, closed_at) VALUES (?, ?, ?, 0, CURRENT_TIMESTAMP)", (close_id, trade_id, open_price)) 
    connection.commit()
    return

async def get_trade_left_to_close(trade_id: int):
    # Get left to close trade
    connection = async with aiosqlite.connect("database/database.db")
    cursor = connection.cursor()  
    rows = cursor.execute(
        "SELECT left_to_close FROM trades_progress WHERE trade_id=?", (trade_id)).fetchone()
    left_to_close = rows[0]
    return left_to_close

async def close_trade_percent(trade_id: int, closed_price: float, closed_percent: int = 100) -> int:
    """
    This function updates the close price for a trade

    :param user_id: The ID of the user that is closing the trade
    :param trader_id: The ID of the trade to be closed
    :param close: The price at which the trade was closed
    """
    connection = async with aiosqlite.connect("database/database.db")
    cursor = connection.cursor()  
    rows = cursor.execute(
        "SELECT id FROM closing_points ORDER BY id DESC LIMIT 1").fetchone()
    close_id = rows[0]+1 if rows is not None else 1
    cursor.execute("INSERT INTO closing_points(id, trade_id, closed_price, closed_percent, closed_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)", (close_id, trade_id, closed_price, closed_percent)) 
    connection.commit()
    connection.close()

    return get_trade_left_to_close(trade_id)

async def close_trade(trade_id: int, close: float) -> list:
    """
    This function updates the close price for a trade

    :param user_id: The ID of the user that is closing the trade
    :param trader_id: The ID of the trade to be closed
    :param close: The price at which the trade was closed
    """

    connection = async with aiosqlite.connect("database/database.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE trades SET close=?, closed_at=CURRENT_TIMESTAMP WHERE id=?", (close, trade_id))
    connection.commit()
    rows = cursor.execute(
        "SELECT id, type, coin, open, target, stoploss, vip FROM trades WHERE id=?", (trade_id)).fetchone()
    connection.close()
    return rows

async def add_trade(user_id: int, trade_type: str, coin: str, open_price: float, close: float, target: float, stoploss: float, leverage: int = 10, vip: bool = False) -> list:
    """
    This function will add a warn to the database

    :param user_id: The ID of the user that should be warned
    :param reason: The reason why the user should be warned
    """
    connection = async with aiosqlite.connect("database/database.db")
    cursor = connection.cursor()
    # Get the last `id`
    rows = cursor.execute(
        "SELECT id FROM trades ORDER BY id DESC LIMIT 1").fetchone()
    trade_id = rows[0]+1 if rows is not None else 1
    cursor.execute("INSERT INTO trades(id, user_id, type, coin, open, close, target, stoploss, leverage, vip) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (trade_id, user_id, trade_type, coin, open_price, close, target, stoploss, leverage, vip))
    connection.commit()
    rows = cursor.execute(
        "SELECT id, type, coin, open, target, stoploss, vip FROM trades WHERE user_id=? AND close IS NULL", (user_id)).fetchall()
    connection.close()
    return rows

async def remove_trade(user_id: int, trade_id: int) -> list:
    """
    This function will remove a trade from the database.

    :param user_id: The ID of the user that should be warned.
    :param reason: The reason why the user should be warned.
    """
    connection = async with aiosqlite.connect("database/database.db")
    cursor = connection.cursor()
    # Get the last `id`
    rows = cursor.execute(
        "SELECT id FROM trades ORDER BY id DESC LIMIT 1").fetchone()
    trade_id = rows[0]+1 if rows is not None else 1
    cursor.execute("DELETE FROM trades WHERE id=?", (trade_id))
    connection.commit()
    rows = cursor.execute(
        "SELECT id, type, coin, open, target, stoploss, vip  FROM trades WHERE user_id=? AND close IS NULL", (user_id)).fetchall()
    connection.close()
    return rows

async def get_open_trades(user_id: int, status: str) -> list:
    """
    Description.

    :param user_id: 
    """
    connection = async with aiosqlite.connect("database/database.db")
    cursor = connection.cursor()

    return 

async def get_closed_trades() -> list:
    """
    Description.

    :param user_id: 
    """
    connection = async with aiosqlite.connect("database/database.db")
    cursor = connection.cursor()

    return 

async def get_all_trades() -> list:
    """
    Description.

    :param user_id: 
    """
    connection = async with aiosqlite.connect("database/database.db")
    cursor = connection.cursor()

    return 