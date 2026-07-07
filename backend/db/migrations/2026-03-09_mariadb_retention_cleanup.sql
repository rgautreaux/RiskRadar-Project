-- Add retention cleanup archive + run logging tables and supporting indexes.
-- Target: MariaDB 10.4+

START TRANSACTION;

-- ---------------------------------------------------------------------------
-- Archive tables
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `alerts_archive` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `original_id` INT(11) NOT NULL,
  `source` TEXT NOT NULL,
  `source_id` TEXT NULL,
  `alert_type` TEXT NOT NULL,
  `severity` TEXT NOT NULL,
  `title` TEXT NOT NULL,
  `description` TEXT NULL,
  `raw_data` LONGTEXT NULL,
  `latitude` FLOAT NULL,
  `longitude` FLOAT NULL,
  `location_name` TEXT NULL,
  `event_start` TEXT NULL,
  `event_end` TEXT NULL,
  `fetched_at` TEXT NOT NULL,
  `created_at` TEXT NOT NULL,
  `updated_at` TEXT NOT NULL,
  `archived_at` TEXT NOT NULL,
  `cleanup_run_id` INT(11) NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_alerts_archive_original_id` (`original_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `summaries_archive` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `original_id` INT(11) NOT NULL,
  `title` TEXT NOT NULL,
  `content` LONGTEXT NOT NULL,
  `summary_type` TEXT NOT NULL,
  `alert_ids` LONGTEXT NULL,
  `region` TEXT NULL,
  `generated_at` TEXT NOT NULL,
  `model_used` TEXT NULL,
  `token_count` INT(11) NULL,
  `created_at` TEXT NOT NULL,
  `archived_at` TEXT NOT NULL,
  `cleanup_run_id` INT(11) NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_summaries_archive_original_id` (`original_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `scrape_log_archive` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `original_id` INT(11) NOT NULL,
  `source` TEXT NOT NULL,
  `status` TEXT NOT NULL,
  `alerts_fetched` INT(11) DEFAULT 0,
  `alerts_new` INT(11) DEFAULT 0,
  `error_message` TEXT NULL,
  `duration_ms` INT(11) NULL,
  `started_at` TEXT NOT NULL,
  `completed_at` TEXT NOT NULL,
  `archived_at` TEXT NOT NULL,
  `cleanup_run_id` INT(11) NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_scrape_log_archive_original_id` (`original_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------------
-- Cleanup run monitoring table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `cleanup_runs` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `table_name` TEXT NOT NULL,
  `schedule_kind` TEXT NOT NULL,
  `cutoff_at` TEXT NOT NULL,
  `rows_eligible` INT(11) NOT NULL DEFAULT 0,
  `rows_archived` INT(11) NOT NULL DEFAULT 0,
  `rows_deleted` INT(11) NOT NULL DEFAULT 0,
  `storage_bytes_estimated` BIGINT NOT NULL DEFAULT 0,
  `duration_ms` INT(11) NOT NULL DEFAULT 0,
  `dry_run` TINYINT(1) NOT NULL DEFAULT 1,
  `status` TEXT NOT NULL,
  `error_message` TEXT NULL,
  `started_at` TEXT NOT NULL,
  `completed_at` TEXT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------------
-- Cleanup/routing indexes on live tables
-- NOTE: Text columns require prefix lengths in MariaDB indexes.
-- ---------------------------------------------------------------------------
ALTER TABLE `alerts`
  ADD INDEX `idx_alerts_created_at` (`created_at`(32)),
  ADD INDEX `idx_alerts_fetched_at` (`fetched_at`(32)),
  ADD INDEX `idx_alerts_routing` (`alert_type`(32), `severity`(16), `fetched_at`(32));

ALTER TABLE `summaries`
  ADD INDEX `idx_summaries_created_at` (`created_at`(32)),
  ADD INDEX `idx_summaries_generated_at` (`generated_at`(32));

ALTER TABLE `scrape_log`
  ADD INDEX `idx_scrape_log_completed_at` (`completed_at`(32)),
  ADD INDEX `idx_scrape_log_status_completed` (`status`(16), `completed_at`(32));

ALTER TABLE `alerts_archive`
  ADD INDEX `idx_alerts_archive_archived_at` (`archived_at`(32));

ALTER TABLE `summaries_archive`
  ADD INDEX `idx_summaries_archive_archived_at` (`archived_at`(32));

ALTER TABLE `scrape_log_archive`
  ADD INDEX `idx_scrape_log_archive_archived_at` (`archived_at`(32));

ALTER TABLE `cleanup_runs`
  ADD INDEX `idx_cleanup_runs_started_at` (`started_at`(32)),
  ADD INDEX `idx_cleanup_runs_table_schedule` (`table_name`(32), `schedule_kind`(16));

COMMIT;
