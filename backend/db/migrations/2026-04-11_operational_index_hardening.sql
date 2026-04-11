-- Add low-risk operational indexes for the most common query and monitoring paths.
-- Target: MariaDB 10.4+

START TRANSACTION;

-- alerts
SET @idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'alerts'
    AND index_name = 'idx_alerts_source_fetched_at'
);
SET @sql_idx := IF(
  @idx_exists = 0,
  'CREATE INDEX idx_alerts_source_fetched_at ON alerts (source(32), fetched_at(32))',
  'SELECT 1'
);
PREPARE stmt FROM @sql_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'alerts'
    AND index_name = 'idx_alerts_type_severity_fetched_at'
);
SET @sql_idx := IF(
  @idx_exists = 0,
  'CREATE INDEX idx_alerts_type_severity_fetched_at ON alerts (alert_type(32), severity(16), fetched_at(32))',
  'SELECT 1'
);
PREPARE stmt FROM @sql_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- summaries
SET @idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'summaries'
    AND index_name = 'idx_summaries_summary_type_generated_at'
);
SET @sql_idx := IF(
  @idx_exists = 0,
  'CREATE INDEX idx_summaries_summary_type_generated_at ON summaries (summary_type(32), generated_at(32))',
  'SELECT 1'
);
PREPARE stmt FROM @sql_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- scrape_log
SET @idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'scrape_log'
    AND index_name = 'idx_scrape_log_source_started_at'
);
SET @sql_idx := IF(
  @idx_exists = 0,
  'CREATE INDEX idx_scrape_log_source_started_at ON scrape_log (source(32), started_at(32))',
  'SELECT 1'
);
PREPARE stmt FROM @sql_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'scrape_log'
    AND index_name = 'idx_scrape_log_status_completed_at'
);
SET @sql_idx := IF(
  @idx_exists = 0,
  'CREATE INDEX idx_scrape_log_status_completed_at ON scrape_log (status(16), completed_at(32))',
  'SELECT 1'
);
PREPARE stmt FROM @sql_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- cleanup_runs
SET @idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'cleanup_runs'
    AND index_name = 'idx_cleanup_runs_status_started_at'
);
SET @sql_idx := IF(
  @idx_exists = 0,
  'CREATE INDEX idx_cleanup_runs_status_started_at ON cleanup_runs (status(32), started_at(32))',
  'SELECT 1'
);
PREPARE stmt FROM @sql_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- notification_dispatch_log
SET @idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'notification_dispatch_log'
    AND index_name = 'idx_notification_dispatch_status_created_at'
);
SET @sql_idx := IF(
  @idx_exists = 0,
  'CREATE INDEX idx_notification_dispatch_status_created_at ON notification_dispatch_log (status(32), created_at(32))',
  'SELECT 1'
);
PREPARE stmt FROM @sql_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

COMMIT;