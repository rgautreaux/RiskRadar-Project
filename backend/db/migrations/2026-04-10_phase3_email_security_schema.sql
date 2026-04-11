-- Add Phase 3 email security schema support.
-- Target: MariaDB 10.4+

START TRANSACTION;

-- ---------------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------------
ALTER TABLE `users`
  ADD COLUMN IF NOT EXISTS `email_encrypted` TEXT NULL AFTER `email`,
  ADD COLUMN IF NOT EXISTS `email_hmac` VARCHAR(64) NULL AFTER `email_encrypted`;

ALTER TABLE `users`
  ADD UNIQUE KEY `uq_users_email_hmac` (`email_hmac`);

-- ---------------------------------------------------------------------------
-- migration_log
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `migration_log` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `timestamp` DATETIME(6) NOT NULL,
  `user_id` INT(11) NULL,
  `action` TEXT NULL,
  `status` TEXT NULL,
  `error_message` TEXT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

COMMIT;