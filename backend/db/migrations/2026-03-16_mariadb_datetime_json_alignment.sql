-- Convert timestamp-like TEXT columns to DATETIME(6) and raw_data payload columns to JSON.
-- Target: MariaDB 10.4+

START TRANSACTION;

-- Normalize ISO-ish timestamp strings into MariaDB DATETIME format.
-- Handles values like:
--   2026-03-16T02:10:00
--   2026-03-16T02:10:00Z
--   2026-03-16T02:10:00.123456+00:00

UPDATE alerts
SET
  fetched_at = REPLACE(REPLACE(SUBSTRING_INDEX(fetched_at, '+', 1), 'T', ' '), 'Z', ''),
  created_at = REPLACE(REPLACE(SUBSTRING_INDEX(created_at, '+', 1), 'T', ' '), 'Z', ''),
  updated_at = REPLACE(REPLACE(SUBSTRING_INDEX(updated_at, '+', 1), 'T', ' '), 'Z', '')
WHERE fetched_at IS NOT NULL OR created_at IS NOT NULL OR updated_at IS NOT NULL;

UPDATE summaries
SET
  generated_at = REPLACE(REPLACE(SUBSTRING_INDEX(generated_at, '+', 1), 'T', ' '), 'Z', ''),
  created_at = REPLACE(REPLACE(SUBSTRING_INDEX(created_at, '+', 1), 'T', ' '), 'Z', '')
WHERE generated_at IS NOT NULL OR created_at IS NOT NULL;

UPDATE users
SET
  created_at = REPLACE(REPLACE(SUBSTRING_INDEX(created_at, '+', 1), 'T', ' '), 'Z', ''),
  updated_at = REPLACE(REPLACE(SUBSTRING_INDEX(updated_at, '+', 1), 'T', ' '), 'Z', '')
WHERE created_at IS NOT NULL OR updated_at IS NOT NULL;

UPDATE scrape_log
SET
  started_at = REPLACE(REPLACE(SUBSTRING_INDEX(started_at, '+', 1), 'T', ' '), 'Z', ''),
  completed_at = REPLACE(REPLACE(SUBSTRING_INDEX(completed_at, '+', 1), 'T', ' '), 'Z', '')
WHERE started_at IS NOT NULL OR completed_at IS NOT NULL;

UPDATE alerts_archive
SET
  fetched_at = REPLACE(REPLACE(SUBSTRING_INDEX(fetched_at, '+', 1), 'T', ' '), 'Z', ''),
  created_at = REPLACE(REPLACE(SUBSTRING_INDEX(created_at, '+', 1), 'T', ' '), 'Z', ''),
  updated_at = REPLACE(REPLACE(SUBSTRING_INDEX(updated_at, '+', 1), 'T', ' '), 'Z', ''),
  archived_at = REPLACE(REPLACE(SUBSTRING_INDEX(archived_at, '+', 1), 'T', ' '), 'Z', '')
WHERE fetched_at IS NOT NULL OR created_at IS NOT NULL OR updated_at IS NOT NULL OR archived_at IS NOT NULL;

UPDATE summaries_archive
SET
  generated_at = REPLACE(REPLACE(SUBSTRING_INDEX(generated_at, '+', 1), 'T', ' '), 'Z', ''),
  created_at = REPLACE(REPLACE(SUBSTRING_INDEX(created_at, '+', 1), 'T', ' '), 'Z', ''),
  archived_at = REPLACE(REPLACE(SUBSTRING_INDEX(archived_at, '+', 1), 'T', ' '), 'Z', '')
WHERE generated_at IS NOT NULL OR created_at IS NOT NULL OR archived_at IS NOT NULL;

UPDATE scrape_log_archive
SET
  started_at = REPLACE(REPLACE(SUBSTRING_INDEX(started_at, '+', 1), 'T', ' '), 'Z', ''),
  completed_at = REPLACE(REPLACE(SUBSTRING_INDEX(completed_at, '+', 1), 'T', ' '), 'Z', ''),
  archived_at = REPLACE(REPLACE(SUBSTRING_INDEX(archived_at, '+', 1), 'T', ' '), 'Z', '')
WHERE started_at IS NOT NULL OR completed_at IS NOT NULL OR archived_at IS NOT NULL;

UPDATE cleanup_runs
SET
  cutoff_at = REPLACE(REPLACE(SUBSTRING_INDEX(cutoff_at, '+', 1), 'T', ' '), 'Z', ''),
  started_at = REPLACE(REPLACE(SUBSTRING_INDEX(started_at, '+', 1), 'T', ' '), 'Z', ''),
  completed_at = REPLACE(REPLACE(SUBSTRING_INDEX(completed_at, '+', 1), 'T', ' '), 'Z', '')
WHERE cutoff_at IS NOT NULL OR started_at IS NOT NULL OR completed_at IS NOT NULL;

-- Convert main live tables.
ALTER TABLE alerts
  MODIFY COLUMN raw_data JSON NULL,
  MODIFY COLUMN fetched_at DATETIME(6) NOT NULL,
  MODIFY COLUMN created_at DATETIME(6) NOT NULL,
  MODIFY COLUMN updated_at DATETIME(6) NOT NULL;

ALTER TABLE summaries
  MODIFY COLUMN generated_at DATETIME(6) NOT NULL,
  MODIFY COLUMN created_at DATETIME(6) NOT NULL;

ALTER TABLE users
  MODIFY COLUMN created_at DATETIME(6) NOT NULL,
  MODIFY COLUMN updated_at DATETIME(6) NOT NULL;

ALTER TABLE scrape_log
  MODIFY COLUMN started_at DATETIME(6) NOT NULL,
  MODIFY COLUMN completed_at DATETIME(6) NOT NULL;

-- Convert archive and cleanup tracking tables.
ALTER TABLE alerts_archive
  MODIFY COLUMN raw_data JSON NULL,
  MODIFY COLUMN fetched_at DATETIME(6) NOT NULL,
  MODIFY COLUMN created_at DATETIME(6) NOT NULL,
  MODIFY COLUMN updated_at DATETIME(6) NOT NULL,
  MODIFY COLUMN archived_at DATETIME(6) NOT NULL;

ALTER TABLE summaries_archive
  MODIFY COLUMN generated_at DATETIME(6) NOT NULL,
  MODIFY COLUMN created_at DATETIME(6) NOT NULL,
  MODIFY COLUMN archived_at DATETIME(6) NOT NULL;

ALTER TABLE scrape_log_archive
  MODIFY COLUMN started_at DATETIME(6) NOT NULL,
  MODIFY COLUMN completed_at DATETIME(6) NOT NULL,
  MODIFY COLUMN archived_at DATETIME(6) NOT NULL;

ALTER TABLE cleanup_runs
  MODIFY COLUMN cutoff_at DATETIME(6) NOT NULL,
  MODIFY COLUMN started_at DATETIME(6) NOT NULL,
  MODIFY COLUMN completed_at DATETIME(6) NOT NULL;

COMMIT;
