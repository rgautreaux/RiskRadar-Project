-- Align MariaDB schema with backend/db/models.py so scraper inserts work.
-- Target: MariaDB 10.4+

START TRANSACTION;

-- ---------------------------------------------------------------------------
-- alerts
-- ---------------------------------------------------------------------------
ALTER TABLE `alerts`
  CHANGE COLUMN `alert_id` `id` INT(11) NOT NULL;

ALTER TABLE `alerts`
  MODIFY COLUMN `id` INT(11) NOT NULL AUTO_INCREMENT,
  MODIFY COLUMN `source` VARCHAR(64) NOT NULL,
  MODIFY COLUMN `source_id` VARCHAR(255) NULL,
  MODIFY COLUMN `alert_type` VARCHAR(64) NOT NULL,
  MODIFY COLUMN `severity` VARCHAR(32) NOT NULL,
  MODIFY COLUMN `title` TEXT NOT NULL,
  MODIFY COLUMN `description` TEXT NULL,
  MODIFY COLUMN `raw_data` LONGTEXT NULL,
  MODIFY COLUMN `latitude` FLOAT NULL,
  MODIFY COLUMN `longitude` FLOAT NULL,
  MODIFY COLUMN `location_name` TEXT NULL,
  MODIFY COLUMN `event_start` TEXT NULL,
  MODIFY COLUMN `event_end` TEXT NULL,
  MODIFY COLUMN `fetched_at` TEXT NOT NULL,
  MODIFY COLUMN `created_at` TEXT NOT NULL,
  MODIFY COLUMN `updated_at` TEXT NOT NULL;

ALTER TABLE `alerts`
  DROP COLUMN `article_id`,
  DROP COLUMN `priority`;

ALTER TABLE `alerts`
  DROP INDEX `source`;

ALTER TABLE `alerts`
  ADD UNIQUE KEY `uq_source_alert` (`source`, `source_id`);

-- ---------------------------------------------------------------------------
-- scrape_log
-- ---------------------------------------------------------------------------
ALTER TABLE `scrape_log`
  CHANGE COLUMN `log_id` `id` INT(11) NOT NULL;

ALTER TABLE `scrape_log`
  MODIFY COLUMN `id` INT(11) NOT NULL AUTO_INCREMENT,
  MODIFY COLUMN `source` VARCHAR(64) NOT NULL,
  MODIFY COLUMN `status` VARCHAR(32) NOT NULL,
  MODIFY COLUMN `alerts_fetched` INT(11) NOT NULL DEFAULT 0,
  MODIFY COLUMN `alerts_new` INT(11) NOT NULL DEFAULT 0,
  MODIFY COLUMN `error_message` TEXT NULL,
  MODIFY COLUMN `duration_ms` INT(11) NULL,
  MODIFY COLUMN `started_at` TEXT NOT NULL,
  MODIFY COLUMN `completed_at` TEXT NOT NULL;

ALTER TABLE `scrape_log`
  DROP COLUMN `scraped_at`,
  DROP COLUMN `http_status`,
  DROP COLUMN `articles_found`,
  DROP COLUMN `articles_inserted`;

ALTER TABLE `scrape_log`
  DROP INDEX `source`;

-- ---------------------------------------------------------------------------
-- summaries
-- ---------------------------------------------------------------------------
ALTER TABLE `summaries`
  CHANGE COLUMN `reigon` `region` TEXT NULL;

ALTER TABLE `summaries`
  MODIFY COLUMN `id` INT(11) NOT NULL AUTO_INCREMENT,
  MODIFY COLUMN `title` TEXT NOT NULL,
  MODIFY COLUMN `content` TEXT NOT NULL,
  MODIFY COLUMN `summary_type` TEXT NOT NULL,
  MODIFY COLUMN `alert_ids` LONGTEXT NULL,
  MODIFY COLUMN `generated_at` TEXT NOT NULL,
  MODIFY COLUMN `model_used` TEXT NULL,
  MODIFY COLUMN `token_count` INT(11) NULL,
  MODIFY COLUMN `created_at` TEXT NOT NULL;

ALTER TABLE `summaries`
  DROP INDEX `alert_ids`;

-- ---------------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------------
ALTER TABLE `users`
  CHANGE COLUMN `user_id` `id` INT(11) NOT NULL;

ALTER TABLE `users`
  ADD COLUMN IF NOT EXISTS `device_token` TEXT NULL AFTER `id`;

ALTER TABLE `users`
  MODIFY COLUMN `id` INT(11) NOT NULL AUTO_INCREMENT,
  MODIFY COLUMN `device_token` TEXT NULL,
  MODIFY COLUMN `display_name` TEXT NULL,
  MODIFY COLUMN `email` VARCHAR(255) NULL,
  MODIFY COLUMN `password_hash` TEXT NULL,
  MODIFY COLUMN `zip_code` TEXT NULL,
  MODIFY COLUMN `latitude` FLOAT NULL,
  MODIFY COLUMN `longitude` FLOAT NULL,
  MODIFY COLUMN `alert_types` LONGTEXT NULL,
  MODIFY COLUMN `notify_severity` TEXT NULL,
  MODIFY COLUMN `created_at` TEXT NOT NULL,
  MODIFY COLUMN `updated_at` TEXT NOT NULL;

ALTER TABLE `users`
  DROP COLUMN `token_id`,
  DROP COLUMN `is_active`,
  DROP COLUMN `last_login_at`;

ALTER TABLE `users`
  DROP INDEX `email`,
  ADD UNIQUE KEY `uq_users_email` (`email`);

COMMIT;
