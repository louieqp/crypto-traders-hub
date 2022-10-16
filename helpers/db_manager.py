import sqlite3

def get_user_from_trade_id(trade_id: int) -> bool:
    """
    This function will check if the user started a trade or has enough permission to modify a trade
    """
    # Query for user_id linked to trade_id
    connection = sqlite3.connect("database/database.db")
    cursor = connection.cursor()
    rows = cursor.execute("SELECT user_id FROM trades WHERE id=? LIMIT 1", (trade_id)).fetchone()
    return rows

def open_trade(user_id: int, trade_type: str, coin: str, open_price: float, target: float, stoploss: float, leverage: int = 10, vip: bool = False) -> int:
    """
    This function will add a trade to the database

    :param user_id: The ID of the user that is opening the trade
    :param *args: Arguments to open a trade
    """
    connection = sqlite3.connect("database/database.db")
    cursor = connection.cursor()
    # Get the last `id`
    rows = cursor.execute(
        "SELECT id FROM trades ORDER BY id DESC LIMIT 1").fetchone()
    trade_id = rows[0]+1 if rows is not None else 1
    cursor.execute("INSERT INTO trades(id, user_id, type, coin, open, target, stoploss, leverage, vip) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (trade_id, user_id, trade_type, coin, open_price, target, stoploss, leverage, vip))
    connection.commit()
    connection.close()
    return trade_id

def close_trade(user_id: int, trade_id: int, close: float, closed_at: str) -> list:
    """
    This function updates the close price for a trade

    :param user_id: The ID of the user that is closing the trade
    :param trader_id: The ID of the trade to be closed
    :param close: The price at which the trade was closed
    """

    connection = sqlite3.connect("database/database.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE trades SET close=?, closed_at=? WHERE id=?", (close, closed_at, trade_id))
    connection.commit()
    rows = cursor.execute(
        "SELECT id, type, coin, open, target, stoploss, vip FROM trades WHERE id=?", (trade_id)).fetchone()
    connection.close()
    return rows

def add_trade(user_id: int, trade_type: str, coin: str, open_price: float, close: float, target: float, stoploss: float, leverage: int = 10, vip: bool = False) -> list:
    """
    This function will add a warn to the database

    :param user_id: The ID of the user that should be warned
    :param reason: The reason why the user should be warned
    """
    connection = sqlite3.connect("database/database.db")
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

def remove_trade(user_id: int, trade_id: int) -> list:
    """
    This function will remove a trade from the database.

    :param user_id: The ID of the user that should be warned.
    :param reason: The reason why the user should be warned.
    """
    connection = sqlite3.connect("database/database.db")
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

def get_open_trades(user_id: int, status: str) -> list:
    """
    Description.

    :param user_id: 
    """
    connection = sqlite3.connect("database/database.db")
    cursor = connection.cursor()

    return 

def get_closed_trades() -> list:
    """
    Description.

    :param user_id: 
    """
    connection = sqlite3.connect("database/database.db")
    cursor = connection.cursor()

    return 

def get_all_trades() -> list:
    """
    Description.

    :param user_id: 
    """
    connection = sqlite3.connect("database/database.db")
    cursor = connection.cursor()

    return 

def hard_reset() -> int:
    """
    This function will wipe the data from the database.
    """
