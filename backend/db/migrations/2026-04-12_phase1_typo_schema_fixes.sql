-- Phase 1 typo schema fixes for legacy MariaDB snapshots.
-- Target: MariaDB 10.4+

START TRANSACTION;

-- ---------------------------------------------------------------------------
-- Rename legacy typo table: user_prefernces -> user_preferences
-- ---------------------------------------------------------------------------
SET @has_user_prefernces := (
  SELECT COUNT(*)
  FROM information_schema.tables
  WHERE table_schema = DATABASE()
    AND table_name = 'user_prefernces'
);
SET @has_user_preferences := (
  SELECT COUNT(*)
  FROM information_schema.tables
  WHERE table_schema = DATABASE()
    AND table_name = 'user_preferences'
);
SET @sql_table_rename := IF(
  @has_user_prefernces = 1 AND @has_user_preferences = 0,
  'RENAME TABLE user_prefernces TO user_preferences',
  'SELECT 1'
);
PREPARE stmt FROM @sql_table_rename;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Ensure expected primary key exists on user_preferences.
SET @has_user_preferences := (
  SELECT COUNT(*)
  FROM information_schema.tables
  WHERE table_schema = DATABASE()
    AND table_name = 'user_preferences'
);
SET @pk_matches := (
  SELECT COUNT(*)
  FROM information_schema.key_column_usage
  WHERE table_schema = DATABASE()
    AND table_name = 'user_preferences'
    AND constraint_name = 'PRIMARY'
    AND column_name IN ('user_id', 'category_id')
);
SET @pk_len := (
  SELECT COUNT(*)
  FROM information_schema.key_column_usage
  WHERE table_schema = DATABASE()
    AND table_name = 'user_preferences'
    AND constraint_name = 'PRIMARY'
);
SET @sql_user_preferences_pk := IF(
  @has_user_preferences = 1 AND NOT (@pk_len = 2 AND @pk_matches = 2),
  'ALTER TABLE user_preferences DROP PRIMARY KEY, ADD PRIMARY KEY (user_id, category_id)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_user_preferences_pk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------------
-- Rename legacy typo column: user_reads.articlle_id -> article_id
-- ---------------------------------------------------------------------------
SET @has_user_reads := (
  SELECT COUNT(*)
  FROM information_schema.tables
  WHERE table_schema = DATABASE()
    AND table_name = 'user_reads'
);
SET @has_old_col := (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'user_reads'
    AND column_name = 'articlle_id'
);
SET @has_new_col := (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'user_reads'
    AND column_name = 'article_id'
);
SET @sql_user_reads_col := IF(
  @has_user_reads = 1 AND @has_old_col = 1 AND @has_new_col = 0,
  'ALTER TABLE user_reads CHANGE COLUMN articlle_id article_id INT(11) NOT NULL',
  'SELECT 1'
);
PREPARE stmt FROM @sql_user_reads_col;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Ensure expected primary key exists on user_reads.
SET @pk_matches := (
  SELECT COUNT(*)
  FROM information_schema.key_column_usage
  WHERE table_schema = DATABASE()
    AND table_name = 'user_reads'
    AND constraint_name = 'PRIMARY'
    AND column_name IN ('user_id', 'article_id')
);
SET @pk_len := (
  SELECT COUNT(*)
  FROM information_schema.key_column_usage
  WHERE table_schema = DATABASE()
    AND table_name = 'user_reads'
    AND constraint_name = 'PRIMARY'
);
SET @pk_exists := (
  SELECT COUNT(*)
  FROM information_schema.table_constraints
  WHERE table_schema = DATABASE()
    AND table_name = 'user_reads'
    AND constraint_name = 'PRIMARY'
    AND constraint_type = 'PRIMARY KEY'
);
SET @sql_user_reads_pk := IF(
  @has_user_reads = 1 AND NOT (@pk_len = 2 AND @pk_matches = 2) AND @pk_exists = 1,
  'ALTER TABLE user_reads DROP PRIMARY KEY, ADD PRIMARY KEY (user_id, article_id)',
  IF(
    @has_user_reads = 1 AND NOT (@pk_len = 2 AND @pk_matches = 2) AND @pk_exists = 0,
    'ALTER TABLE user_reads ADD PRIMARY KEY (user_id, article_id)',
    'SELECT 1'
  )
);
PREPARE stmt FROM @sql_user_reads_pk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

COMMIT;
