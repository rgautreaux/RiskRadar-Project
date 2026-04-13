-- Phase 0 index hardening for safer query plans and migration preflight enforcement.
-- Target: MariaDB 10.4+

START TRANSACTION;

-- ---------------------------------------------------------------------------
-- alerts
-- ---------------------------------------------------------------------------
SET @idx_alerts_source_fetched_at_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'alerts'
    AND index_name = 'idx_alerts_source_fetched_at'
);
SET @sql_alerts_source_fetched_at := IF(
  @idx_alerts_source_fetched_at_exists = 0,
  'CREATE INDEX idx_alerts_source_fetched_at ON alerts (source(64), fetched_at)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_alerts_source_fetched_at;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_alerts_type_severity_fetched_at_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'alerts'
    AND index_name = 'idx_alerts_type_severity_fetched_at'
);
SET @sql_alerts_type_severity_fetched_at := IF(
  @idx_alerts_type_severity_fetched_at_exists = 0,
  'CREATE INDEX idx_alerts_type_severity_fetched_at ON alerts (alert_type(64), severity(32), fetched_at)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_alerts_type_severity_fetched_at;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- summaries
-- ---------------------------------------------------------------------------
SET @idx_summaries_summary_type_generated_at_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'summaries'
    AND index_name = 'idx_summaries_summary_type_generated_at'
);
SET @sql_summaries_summary_type_generated_at := IF(
  @idx_summaries_summary_type_generated_at_exists = 0,
  'CREATE INDEX idx_summaries_summary_type_generated_at ON summaries (summary_type(64), generated_at)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_summaries_summary_type_generated_at;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- scrape_log
-- ---------------------------------------------------------------------------
SET @idx_scrape_log_source_started_at_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'scrape_log'
    AND index_name = 'idx_scrape_log_source_started_at'
);
SET @sql_scrape_log_source_started_at := IF(
  @idx_scrape_log_source_started_at_exists = 0,
  'CREATE INDEX idx_scrape_log_source_started_at ON scrape_log (source(64), started_at)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_scrape_log_source_started_at;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_scrape_log_status_completed_at_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'scrape_log'
    AND index_name = 'idx_scrape_log_status_completed_at'
);
SET @sql_scrape_log_status_completed_at := IF(
  @idx_scrape_log_status_completed_at_exists = 0,
  'CREATE INDEX idx_scrape_log_status_completed_at ON scrape_log (status(32), completed_at)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_scrape_log_status_completed_at;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- cleanup_runs
-- ---------------------------------------------------------------------------
SET @idx_cleanup_runs_status_started_at_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'cleanup_runs'
    AND index_name = 'idx_cleanup_runs_status_started_at'
);
SET @sql_cleanup_runs_status_started_at := IF(
  @idx_cleanup_runs_status_started_at_exists = 0,
  'CREATE INDEX idx_cleanup_runs_status_started_at ON cleanup_runs (status(16), started_at)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_cleanup_runs_status_started_at;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- notification_dispatch_log
-- ---------------------------------------------------------------------------
SET @idx_notification_dispatch_status_created_at_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'notification_dispatch_log'
    AND index_name = 'idx_notification_dispatch_status_created_at'
);
SET @sql_notification_dispatch_status_created_at := IF(
  @idx_notification_dispatch_status_created_at_exists = 0,
  'CREATE INDEX idx_notification_dispatch_status_created_at ON notification_dispatch_log (status(16), created_at)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_notification_dispatch_status_created_at;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

COMMIT;
