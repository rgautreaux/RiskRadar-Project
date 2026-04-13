-- Phase 5 contract migration: retire legacy compatibility columns.
-- PREREQUISITES (must be true before running):
-- 1) backfill_summary_alerts.py completed with zero errors
-- 2) backfill_user_alert_type_preferences.py completed with zero errors
-- 3) parity_validator_summaries_alerts.py returns 0
-- 4) parity_validator_user_alert_types.py returns 0
-- 5) safety_gate.py passes with MIGRATION_NORMALIZATION_CONTRACT_REQUIRED=true
--
-- This script is intentionally separate to preserve safe rollback boundaries.
-- Target: MariaDB 10.4+

START TRANSACTION;

SET @has_alert_ids := (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'summaries'
    AND column_name = 'alert_ids'
);
SET @sql_drop_alert_ids := IF(
  @has_alert_ids = 1,
  'ALTER TABLE summaries DROP COLUMN alert_ids',
  'SELECT 1'
);
PREPARE stmt FROM @sql_drop_alert_ids;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @has_alert_types := (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'users'
    AND column_name = 'alert_types'
);
SET @sql_drop_alert_types := IF(
  @has_alert_types = 1,
  'ALTER TABLE users DROP COLUMN alert_types',
  'SELECT 1'
);
PREPARE stmt FROM @sql_drop_alert_types;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @has_raw_data := (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'alerts'
    AND column_name = 'raw_data'
);
SET @sql_drop_raw_data := IF(
  @has_raw_data = 1,
  'ALTER TABLE alerts DROP COLUMN raw_data',
  'SELECT 1'
);
PREPARE stmt FROM @sql_drop_raw_data;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

COMMIT;
