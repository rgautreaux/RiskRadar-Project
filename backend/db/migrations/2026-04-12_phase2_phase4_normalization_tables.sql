-- Phase 2-4 normalization foundation tables.
-- Target: MariaDB 10.4+

START TRANSACTION;

CREATE TABLE IF NOT EXISTS summary_alerts (
  summary_id INT(11) NOT NULL,
  alert_id INT(11) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (summary_id, alert_id),
  KEY idx_summary_alerts_alert_id (alert_id),
  CONSTRAINT fk_summary_alerts_summary FOREIGN KEY (summary_id) REFERENCES summaries(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_summary_alerts_alert FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS user_alert_type_preferences (
  user_id INT(11) NOT NULL,
  alert_type VARCHAR(64) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, alert_type),
  KEY idx_user_alert_type_preferences_alert_type (alert_type),
  CONSTRAINT fk_user_alert_type_preferences_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS zip_geo (
  zip_code VARCHAR(10) NOT NULL,
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  state VARCHAR(8) NULL,
  city VARCHAR(128) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (zip_code),
  KEY idx_zip_geo_coords (latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS locations (
  id INT(11) NOT NULL AUTO_INCREMENT,
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  location_name TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_locations_lat_lon_name (latitude, longitude, location_name(191)),
  KEY idx_locations_lat_lon (latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS alert_raw_payloads (
  alert_id INT(11) NOT NULL,
  raw_payload LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(raw_payload)),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (alert_id),
  CONSTRAINT fk_alert_raw_payloads_alert FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

SET @has_location_id := (
  SELECT COUNT(*)
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'alerts'
    AND column_name = 'location_id'
);
SET @sql_add_location_id := IF(
  @has_location_id = 0,
  'ALTER TABLE alerts ADD COLUMN location_id INT(11) NULL',
  'SELECT 1'
);
PREPARE stmt FROM @sql_add_location_id;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_exists := (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'alerts'
    AND index_name = 'idx_alerts_location_id'
);
SET @sql_add_idx := IF(
  @idx_exists = 0,
  'CREATE INDEX idx_alerts_location_id ON alerts (location_id)',
  'SELECT 1'
);
PREPARE stmt FROM @sql_add_idx;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @fk_exists := (
  SELECT COUNT(*)
  FROM information_schema.table_constraints
  WHERE constraint_schema = DATABASE()
    AND table_name = 'alerts'
    AND constraint_type = 'FOREIGN KEY'
    AND constraint_name = 'fk_alerts_location'
);
SET @sql_add_fk := IF(
  @fk_exists = 0,
  'ALTER TABLE alerts ADD CONSTRAINT fk_alerts_location FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL ON UPDATE CASCADE',
  'SELECT 1'
);
PREPARE stmt FROM @sql_add_fk;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

COMMIT;
