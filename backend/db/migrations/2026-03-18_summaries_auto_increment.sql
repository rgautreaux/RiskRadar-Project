-- Add AUTO_INCREMENT to summaries.id so new rows get unique IDs.
-- The column was missing AUTO_INCREMENT in the original schema and
-- the 2026-03-03 migration that fixed alerts/scrape_log/users.

START TRANSACTION;

-- Fix any existing row that was inserted with id=0
UPDATE summaries SET id = (SELECT COALESCE(MAX(id), 0) + 1 FROM (SELECT id FROM summaries) AS t) WHERE id = 0;

-- Add AUTO_INCREMENT
ALTER TABLE summaries MODIFY COLUMN `id` INT(11) NOT NULL AUTO_INCREMENT;

COMMIT;
