-- Fix MariaDB error 1467 (HA_ERR_AUTOINC_READ_FAILED) on alerts INSERT.
--
-- Root cause: UNIQUE KEY uq_source_alert used USING HASH on a TEXT column
-- (source_id). MariaDB's "long unique" feature adds a hidden hash column
-- internally, triggering a known InnoDB bug that corrupts the auto-increment
-- counter (related to MDEV-20247). Replacing with a standard B-TREE prefix
-- index removes the hidden column and resolves the error.
--
-- Prefix length 191 is the safe maximum for utf8mb4 within InnoDB's
-- 767-byte index key limit. All real source_id values (NWS urn:oid:... etc.)
-- are well under this limit, so no real-world collisions are possible.

START TRANSACTION;

ALTER TABLE `alerts` DROP INDEX `uq_source_alert`;
ALTER TABLE `alerts` ADD UNIQUE KEY `uq_source_alert` (`source`, `source_id`(191));

-- Reset the auto-increment counter. MariaDB silently resolves this to
-- MAX(id)+1 when the table already has rows, so this is always safe.
ALTER TABLE `alerts` AUTO_INCREMENT = 1;

COMMIT;
