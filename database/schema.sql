-- CREATE TABLE IF NOT EXISTS `roles` (
--     `role_id` int(11) NOT NULL,
--     `role_name` varchar(20) NOT NULL,
--     `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
-- );

-- CREATE TABLE IF NOT EXISTS `user_roles` (
--     `role_id` int(11) NOT NULL,
--     `user_id` varchar(20) NOT NULL,
--     `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
-- )

CREATE TABLE IF NOT EXISTS `trades` (
    `id` int(11) NOT NULL,
    `user_id` varchar(20) NOT NULL,
    `type` varchar(20) NOT NULL,
    `coin` varchar(20) NOT NULL,
    `open` real NOT NULL,
    `close` real NOT NULL,
    `tp` real NOT NULL,
    `sl` real NOT NULL,
    `vip` boolean NOT NULL,
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);