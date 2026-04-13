-- Ensure users.email_hmac shape and unique index are MariaDB-safe and idempotent.
-- Target: MariaDB 10.4+

START TRANSACTION;

-- Keep column shape aligned with application expectations.
ALTER TABLE `users`
  MODIFY COLUMN `email_hmac` VARCHAR(64) NULL;

-- Drop existing index if present so reruns are deterministic.
SET @idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'users'
    AND index_name = 'uq_users_email_hmac'
);
SET @sql_drop_idx := IF(
  @idx_exists > 0,
  'ALTER TABLE users DROP INDEX uq_users_email_hmac',
  'SELECT 1'
);
PREPARE stmt FROM @sql_drop_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Recreate as strict unique key.
ALTER TABLE `users`
  ADD UNIQUE KEY `uq_users_email_hmac` (`email_hmac`);

COMMIT;
