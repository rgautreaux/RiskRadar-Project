-- Enforce referential integrity for archive lineage and notification dispatch references.
-- Target: MariaDB 10.4+

START TRANSACTION;

-- ---------------------------------------------------------------------------
-- Ensure supporting indexes exist for foreign key columns.
-- ---------------------------------------------------------------------------
SET @idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'notification_dispatch_log'
    AND index_name = 'idx_notification_dispatch_initiated_by_user_id'
);
SET @sql_idx := IF(
  @idx_exists = 0,
  'CREATE INDEX idx_notification_dispatch_initiated_by_user_id ON notification_dispatch_log (initiated_by_user_id)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- Add archive lineage foreign keys.
-- ---------------------------------------------------------------------------
SET @fk_exists := (
  SELECT COUNT(*)
  FROM information_schema.table_constraints
  WHERE constraint_schema = DATABASE()
    AND table_name = 'alerts_archive'
    AND constraint_type = 'FOREIGN KEY'
    AND constraint_name = 'fk_alerts_archive_cleanup_run'
);
SET @sql_fk := IF(
  @fk_exists = 0,
  'ALTER TABLE alerts_archive ADD CONSTRAINT fk_alerts_archive_cleanup_run FOREIGN KEY (cleanup_run_id) REFERENCES cleanup_runs(id) ON DELETE SET NULL ON UPDATE CASCADE',
  'SELECT 1'
);
PREPARE stmt FROM @sql_fk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @fk_exists := (
  SELECT COUNT(*)
  FROM information_schema.table_constraints
  WHERE constraint_schema = DATABASE()
    AND table_name = 'summaries_archive'
    AND constraint_type = 'FOREIGN KEY'
    AND constraint_name = 'fk_summaries_archive_cleanup_run'
);
SET @sql_fk := IF(
  @fk_exists = 0,
  'ALTER TABLE summaries_archive ADD CONSTRAINT fk_summaries_archive_cleanup_run FOREIGN KEY (cleanup_run_id) REFERENCES cleanup_runs(id) ON DELETE SET NULL ON UPDATE CASCADE',
  'SELECT 1'
);
PREPARE stmt FROM @sql_fk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @fk_exists := (
  SELECT COUNT(*)
  FROM information_schema.table_constraints
  WHERE constraint_schema = DATABASE()
    AND table_name = 'scrape_log_archive'
    AND constraint_type = 'FOREIGN KEY'
    AND constraint_name = 'fk_scrape_log_archive_cleanup_run'
);
SET @sql_fk := IF(
  @fk_exists = 0,
  'ALTER TABLE scrape_log_archive ADD CONSTRAINT fk_scrape_log_archive_cleanup_run FOREIGN KEY (cleanup_run_id) REFERENCES cleanup_runs(id) ON DELETE SET NULL ON UPDATE CASCADE',
  'SELECT 1'
);
PREPARE stmt FROM @sql_fk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- Add dispatch log foreign keys.
-- ---------------------------------------------------------------------------
SET @fk_exists := (
  SELECT COUNT(*)
  FROM information_schema.table_constraints
  WHERE constraint_schema = DATABASE()
    AND table_name = 'notification_dispatch_log'
    AND constraint_type = 'FOREIGN KEY'
    AND constraint_name = 'fk_notification_dispatch_alert'
);
SET @sql_fk := IF(
  @fk_exists = 0,
  'ALTER TABLE notification_dispatch_log ADD CONSTRAINT fk_notification_dispatch_alert FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE RESTRICT ON UPDATE CASCADE',
  'SELECT 1'
);
PREPARE stmt FROM @sql_fk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @fk_exists := (
  SELECT COUNT(*)
  FROM information_schema.table_constraints
  WHERE constraint_schema = DATABASE()
    AND table_name = 'notification_dispatch_log'
    AND constraint_type = 'FOREIGN KEY'
    AND constraint_name = 'fk_notification_dispatch_user'
);
SET @sql_fk := IF(
  @fk_exists = 0,
  'ALTER TABLE notification_dispatch_log ADD CONSTRAINT fk_notification_dispatch_user FOREIGN KEY (initiated_by_user_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE',
  'SELECT 1'
);
PREPARE stmt FROM @sql_fk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

COMMIT;