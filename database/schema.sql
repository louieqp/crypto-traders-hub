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
    `open` real NOT NULL,
    `close` real,
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
  `closed_percent` real NOT NULL,
  `closed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

/* VIEWS */
CREATE VIEW IF NOT EXISTS `trades_progress` AS
  SELECT 
    p.trade_id, 
    open, 
    close, -- NULL close indicates that the trade is still open
    (SUM(closed_percent/100 * closed_price)-open)/open AS profit
  FROM trades t JOIN closing_points cp ON t.id = cp.trade_id
  GROUP BY cp.trade_id
;