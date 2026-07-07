-- Rollback for Phase 5 contract migration.
-- Restores legacy compatibility columns if contract migration needs to be reverted.
-- Target: MariaDB 10.4+

START TRANSACTION;

SET @has_alert_ids := (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'summaries'
    AND column_name = 'alert_ids'
);
SET @sql_add_alert_ids := IF(
  @has_alert_ids = 0,
  'ALTER TABLE summaries ADD COLUMN alert_ids LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL CHECK (json_valid(alert_ids))',
  'SELECT 1'
);
PREPARE stmt FROM @sql_add_alert_ids;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @has_alert_types := (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'users'
    AND column_name = 'alert_types'
);
SET @sql_add_alert_types := IF(
  @has_alert_types = 0,
  'ALTER TABLE users ADD COLUMN alert_types LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL CHECK (json_valid(alert_types))',
  'SELECT 1'
);
PREPARE stmt FROM @sql_add_alert_types;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @has_raw_data := (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'alerts'
    AND column_name = 'raw_data'
);
SET @sql_add_raw_data := IF(
  @has_raw_data = 0,
  'ALTER TABLE alerts ADD COLUMN raw_data LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL CHECK (json_valid(raw_data))',
  'SELECT 1'
);
PREPARE stmt FROM @sql_add_raw_data;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

COMMIT;
