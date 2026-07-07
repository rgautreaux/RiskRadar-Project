-- Add notification channel preferences and dispatch observability schema.
-- Target: MariaDB 10.4+

START TRANSACTION;

-- ---------------------------------------------------------------------------
-- users: persisted notification channel flags
-- ---------------------------------------------------------------------------
ALTER TABLE `users`
  ADD COLUMN IF NOT EXISTS `notify_push` TINYINT(1) NOT NULL DEFAULT 1 AFTER `notify_severity`,
  ADD COLUMN IF NOT EXISTS `notify_email` TINYINT(1) NOT NULL DEFAULT 0 AFTER `notify_push`,
  ADD COLUMN IF NOT EXISTS `notify_sms` TINYINT(1) NOT NULL DEFAULT 0 AFTER `notify_email`;

-- ---------------------------------------------------------------------------
-- notification_dispatch_log: notification delivery observability
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `notification_dispatch_log` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `alert_id` INT(11) NOT NULL,
  `initiated_by_user_id` INT(11) NOT NULL,
  `provider` TEXT NOT NULL,
  `recipients_total` INT(11) NOT NULL DEFAULT 0,
  `sent_count` INT(11) NOT NULL DEFAULT 0,
  `failed_count` INT(11) NOT NULL DEFAULT 0,
  `status` TEXT NOT NULL,
  `error_message` TEXT NULL,
  `created_at` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add supporting indexes idempotently (MariaDB 10.4 compatible pattern).
SET @idx_alert_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'notification_dispatch_log'
    AND index_name = 'idx_notification_dispatch_alert_id'
);
SET @sql_alert_idx := IF(
  @idx_alert_exists = 0,
  'CREATE INDEX idx_notification_dispatch_alert_id ON notification_dispatch_log (alert_id)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_alert_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_created_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'notification_dispatch_log'
    AND index_name = 'idx_notification_dispatch_created_at'
);
SET @sql_created_idx := IF(
  @idx_created_exists = 0,
  'CREATE INDEX idx_notification_dispatch_created_at ON notification_dispatch_log (created_at)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_created_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

COMMIT;
