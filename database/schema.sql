/* TABLES */

CREATE TABLE IF NOT EXISTS `blacklist` (
  `user_id` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `warns` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `moderator_id` varchar(20) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `trades` (
    `id` int(11) NOT NULL,
    `user_id` varchar(20) NOT NULL,
    `type` varchar(20) NOT NULL,
    `coin` varchar(20) NOT NULL,
    `open_price` real NOT NULL,
    `close_price` real,
    `target` real NOT NULL,
    `stoploss` real NOT NULL,
    `leverage` int(11) DEFAULT 10 NOT NULL,
    `vip` boolean NOT NULL,
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `closed_at` timestamp
);

CREATE TABLE IF NOT EXISTS `closing_points` (
  `id` int(11) NOT NULL,
  `trade_id` int(11) NOT NULL,
  `closed_price` real NOT NULL,
  `closed_percent` int(11) NOT NULL,
  `closed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

/* VIEWS */
CREATE VIEW IF NOT EXISTS `trades_progress` AS
  SELECT 
    cp.trade_id AS `trade_id`, 
    t.open_price AS `open_price`, 
    t.close_price AS `close_price`, -- NULL close indicates that the trade is still open, otherwise we have the price at which the trade was totally closed
    (100-SUM(cp.closed_percent)) AS `left_to_close`,
    (CASE WHEN SUM(cp.closed_percent) = 0 THEN 0 ELSE ((SUM(cp.closed_percent/100 * cp.closed_price)-t.open_price)/t.open_price) * 100 * t.leverage END) AS `profit`
  FROM trades t JOIN closing_points cp ON t.id = cp.trade_id
  GROUP BY cp.trade_id
;

CREATE VIEW IF NOT EXISTS `leaderboard` AS
  SELECT
    t.user_id AS `user_id`,
    t.trade_id AS `trade_id`,
    t.coin AS `coin`,
    tp.profit * t.leverage AS `profit`
  FROM trades t JOIN trades_progress tp ON t.id = tp.trade_id
  ORDER BY tp.profit DESC LIMIT 10
;

CREATE VIEW IF NOT EXISTS `user_profiles` AS
  SELECT 
    t.user_id AS `user_id`,
    COUNT(CASE WHEN profit > 0 THEN 1 END) AS `wins`,
    COUNT(CASE WHEN profit <= 0 THEN 1 END) AS `losses`,
    COUNT(*) AS `total`,
    SUM(profit) AS `total_profit`,
    AVG(CASE WHEN profit > 0 THEN profit END) AS `avg_profit`
  FROM trades t JOIN trades_progress tp ON t.id = tp.trade_id
  WHERE t.close_price IS NOT NULL
  GROUP BY t.user_id
;

CREATE VIEW IF NOT EXISTS `user_trades` AS
  SELECT 
    t.user_id AS `user_id`,
    t.id AS `trade_id`,
    t.coin AS `coin`,
    t.type AS `type`,
    t.close_price AS `close_price`,
    tp.profit AS `profit`
  FROM trades t JOIN trades_progress tp on t.id=tp.trade_id
;