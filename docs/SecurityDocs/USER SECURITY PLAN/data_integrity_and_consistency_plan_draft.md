# RiskRadar Database 3NF Normalization Plan
## Data Integrity & Consistency Enhancement

**Status:** DRAFT - Requires Backend Lead & Security Lead Approval  
**Created:** April 2, 2026  
**Timeline:** After Phase 3-4 (Security Migration) completion  
**Document Owner:** Rebecca Gautreaux (Database Administrator)  

---

## ⚠️ APPROVAL REQUIREMENTS

**This plan requires explicit approval from:**
- **Backend Lead** (Qui Huynh) – Responsible for API/application impact assessment and code refactoring
- **Security Lead** (Noah Benoit) – Responsible for security implications and compliance validation

**Before implementation proceeds, both leads must:**
1. ✅ Review and validate the proposed schema changes
2. ✅ Confirm all code refactoring requirements are understood
3. ✅ Approve the staging environment testing plan
4. ✅ Sign off on the rollback strategy
5. ✅ Confirm timeline compatibility with other project work

---

## Executive Summary

This document outlines a phased plan to normalize the RiskRadar database schema to **Third Normal Form (3NF)**, addressing:
- **1NF Violations:** JSON denormalization (raw data, alert arrays, preference arrays)
- **3NF Violations:** Transitive dependencies (geographic data, lookup values)
- **Schema Typos:** Misspelled table/column names

**Key Principles:**
- ✅ Complete security migration (Phase 3-4) **before** proceeding
- ✅ Implement in **staging first**, then production
- ✅ Maintain backward compatibility where feasible
- ✅ Comprehensive testing at each phase
- ✅ Full audit logging and rollback capabilities
- ✅ Zero data loss through rigorous validation

---

## 1. Current Schema Violations Analysis

### 1.1 First Normal Form (1NF) Violations

| Violation | Table | Column | Impact | Severity |
|-----------|-------|--------|--------|----------|
| JSON without junction table | `alerts` | `raw_data` | Prevents querying raw fields; violates atomic values principle | **Medium** |
| JSON array without junction table | `summaries` | `alert_ids` | No referential integrity; difficult to query summary→alert relationship | **HIGH** |
| JSON array without junction table | `users` | `alert_types` | Cannot enforce valid alert types; aggregation queries complex | **HIGH** |

### 1.2 Third Normal Form (3NF) Violations

| Violation | Table | Columns | Transitive Dependency | Impact | Severity |
|-----------|-------|---------|----------------------|--------|----------|
| Non-key dependency | `users` | `zip_code` → `latitude`, `longitude` | Zip code determines geography | Data redundancy; geographic inconsistency | **HIGH** |
| Non-key dependency | `alerts` | `latitude`, `longitude` → `location_name` | Coordinates determine place name | Denormalization; location lookup inflexible | **MEDIUM** |

### 1.3 Schema Typos (Data Integrity Issues)

| Table | Column/Name | Current | Correct | Impact |
|-------|-------------|---------|---------|--------|
| `user_prefernces` | Table name | `user_prefernces` | `user_preferences` | Confusing; error-prone migrations | **MEDIUM** |
| `user_reads` | Column name | `articlle_id` | `article_id` | Query errors; foreign key issues | **MEDIUM** |
| `summaries` | Column name | `reigon` | `region` | Inconsistent nomenclature | **LOW** |

---

## 2. Proposed Normalized Schema

### 2.1 New/Modified Tables for Normalization

#### A. `zip_codes` (New Lookup Table)

**Purpose:** Extract geographic coordinates from zip codes to eliminate transitive dependency.

```sql
CREATE TABLE zip_codes (
    zip_code VARCHAR(10) PRIMARY KEY,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    city VARCHAR(100),
    state VARCHAR(2),
    country VARCHAR(100) DEFAULT 'USA',
    timezone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_coords (latitude, longitude)
);
```

**Impact:** Eliminates redundancy in `users` table; centralizes geographic data.

---

#### B. `locations` (New Lookup Table)

**Purpose:** Map geographic coordinates to standardized location names.

```sql
CREATE TABLE locations (
    location_id INT PRIMARY KEY AUTO_INCREMENT,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    location_name VARCHAR(255) NOT NULL,
    location_type ENUM('city', 'county', 'region', 'state', 'custom') DEFAULT 'custom',
    source VARCHAR(50) DEFAULT 'geocoding',  -- 'manual', 'geocoding', etc.
    is_verified TINYINT(1) DEFAULT 0,
    verified_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_coords (latitude, longitude),
    INDEX idx_name (location_name),
    INDEX idx_type (location_type)
);
```

**Impact:** Eliminates transitive dependency in `alerts`; enables flexible geocoding.

---

#### C. `alert_types` (New Lookup Table)

**Purpose:** Centralize valid alert type definitions.

```sql
CREATE TABLE alert_types (
    alert_type_id INT PRIMARY KEY AUTO_INCREMENT,
    alert_type VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    severity_default VARCHAR(20),  -- 'low', 'moderate', 'high', 'critical'
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (alert_type)
);
```

**Impact:** Enables validation and audit of alert types; improves data consistency.

---

#### D. `summary_alerts` (New Junction Table)

**Purpose:** Replace `summaries.alert_ids` JSON with proper M:M relationship.

```sql
CREATE TABLE summary_alerts (
    summary_id INT NOT NULL,
    alert_id INT NOT NULL,
    sequence_order INT DEFAULT 0,  -- Preserve order of alerts
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (summary_id, alert_id),
    FOREIGN KEY (summary_id) REFERENCES summaries(id) ON DELETE CASCADE,
    FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE,
    INDEX idx_alert (alert_id)
);
```

**Impact:** Enforces referential integrity; enables direct traversal of summary→alert relationships.

---

#### E. `user_alert_types` (New Junction Table)

**Purpose:** Replace `users.alert_types` JSON with proper M:M relationship.

```sql
CREATE TABLE user_alert_types (
    user_id INT NOT NULL,
    alert_type_id INT NOT NULL,
    is_subscribed TINYINT(1) DEFAULT 1,
    notify_enabled TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, alert_type_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (alert_type_id) REFERENCES alert_types(alert_type_id) ON DELETE CASCADE,
    INDEX idx_alert_type (alert_type_id)
);
```

**Impact:** Ensures only valid alert types; normalizes user preferences to 3NF.

---

#### F. `alert_raw_data_archive` (Optional Data Preservation)

**Purpose:** Archive raw JSON payloads separately for compliance/debugging without denormalizing active alerts.

```sql
CREATE TABLE alert_raw_data_archive (
    archive_id INT PRIMARY KEY AUTO_INCREMENT,
    alert_id INT NOT NULL,
    raw_data JSON NOT NULL,
    source_api VARCHAR(50),
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE,
    INDEX idx_alert (alert_id),
    INDEX idx_archived (archived_at)
);
```

**Impact:** Preserves raw data for debugging/compliance while keeping active schema clean.

---

### 2.2 Modified Tables

#### A. `users` (Normalized)

**Changes:**
- Remove `latitude`, `longitude` (FK to `zip_codes` instead)
- Add `zip_code_fk` foreign key
- Rename from current constraint approach

```sql
ALTER TABLE users
    DROP COLUMN latitude,
    DROP COLUMN longitude,
    ADD COLUMN zip_code_fk VARCHAR(10) AFTER zip_code,
    ADD FOREIGN KEY (zip_code_fk) REFERENCES zip_codes(zip_code) ON DELETE SET NULL;

-- Migrate data: populate zip_code_fk from existing zip_code
UPDATE users u
JOIN zip_codes z ON u.zip_code = z.zip_code
SET u.zip_code_fk = z.zip_code
WHERE u.zip_code IS NOT NULL;
```

**Before:**
```
user_id | zip_code | latitude | longitude | alert_types (JSON)
1       | 98001    | 47.5     | -122.2    | ["all"]
```

**After:**
```
user_id | zip_code | zip_code_fk | alert_types (FK to user_alert_types)
1       | 98001    | 98001       | (via junction table)
```

---

#### B. `alerts` (Normalized)

**Changes:**
- Remove `location_name` (FK to `locations` instead)
- Add `location_id` foreign key
- Remove `raw_data` from active table (optional; archive separately)
- Add FK to `alert_types` lookup

```sql
ALTER TABLE alerts
    ADD COLUMN location_id INT AFTER longitude,
    ADD COLUMN alert_type_id INT AFTER source_id,
    DROP COLUMN location_name,
    DROP COLUMN raw_data,
    ADD FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL,
    ADD FOREIGN KEY (alert_type_id) REFERENCES alert_types(alert_type_id) ON DELETE RESTRICT;
```

**Before:**
```
alert_id | latitude | longitude | location_name | alert_type | raw_data (JSON)
1        | 47.5     | -122.2    | "Seattle, WA" | "wildfire" | {entire payload}
```

**After:**
```
alert_id | latitude | longitude | location_id | alert_type_id | (raw_data archived separately)
1        | 47.5     | -122.2    | 42          | 3             |
```

---

#### C. `summaries` (Normalized)

**Changes:**
- Remove `alert_ids` JSON column
- Add `region_id` FK to `locations` (optional)
- Relationship now via `summary_alerts` junction table

```sql
ALTER TABLE summaries
    DROP COLUMN alert_ids,
    ADD COLUMN region_id INT AFTER region,
    DROP COLUMN region,
    ADD FOREIGN KEY (region_id) REFERENCES locations(location_id) ON DELETE SET NULL;
```

**Before:**
```
summary_id | alert_ids | reigon
1          | [1,2,3]   | "Seattle Area"
```

**After:**
```
summary_id | region_id | (alerts linked via summary_alerts junction table)
1          | 42        |
```

---

#### D. `user_preferences` (Renamed from `user_prefernces`)

**Changes:**
- Rename table to fix typo
- Links to normalized preferences structure

```sql
RENAME TABLE user_prefernces TO user_preferences;
-- Existing structure remains: user_id, category_id, is_enabled
```

---

#### E. `user_reads` (Fixed `article_id` typo)

**Changes:**
- Rename `articlle_id` → `article_id`

```sql
ALTER TABLE user_reads
    CHANGE COLUMN articlle_id article_id INT;
```

---

### 2.3 SQLAlchemy ORM Updates

#### Updated `User` Model

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_token = Column(Text)
    display_name = Column(Text)
    email_encrypted = Column(Text, nullable=True)
    email_hmac = Column(Text, unique=True, nullable=True)
    password_hash = Column(Text)
    zip_code = Column(Text)
    zip_code_fk = Column(String(10), ForeignKey("zip_codes.zip_code"), nullable=True)
    # latitude, longitude removed; via zip_codes relationship
    notify_severity = Column(Text, default="high")
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=_now, onupdate=_now)
    
    # Relationships
    zip_code_ref = relationship("ZipCode", foreign_keys=[zip_code_fk])
    alert_type_subscriptions = relationship("UserAlertType", back_populates="user")
```

#### New `ZipCode` Model

```python
class ZipCode(Base):
    __tablename__ = "zip_codes"
    
    zip_code = Column(String(10), primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    city = Column(String(100))
    state = Column(String(2))
    country = Column(String(100), default="USA")
    timezone = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)
    
    __table_args__ = (
        UniqueConstraint("latitude", "longitude", name="uq_coords"),
    )
```

#### New `Location` Model

```python
class Location(Base):
    __tablename__ = "locations"
    
    location_id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(255), nullable=False)
    location_type = Column(String(20), default="custom")  # ENUM in DB
    source = Column(String(50), default="geocoding")
    is_verified = Column(Integer, default=0)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)
    
    __table_args__ = (
        UniqueConstraint("latitude", "longitude", name="uq_location_coords"),
        Index("idx_location_name", "location_name"),
        Index("idx_location_type", "location_type"),
    )
```

#### New `AlertType` Model

```python
class AlertType(Base):
    __tablename__ = "alert_types"
    
    alert_type_id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    severity_default = Column(String(20))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=_now)
    
    # Relationships
    user_subscriptions = relationship("UserAlertType", back_populates="alert_type")
```

#### New `SummaryAlert` Model

```python
class SummaryAlert(Base):
    __tablename__ = "summary_alerts"
    
    summary_id = Column(Integer, ForeignKey("summaries.id", ondelete="CASCADE"), primary_key=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), primary_key=True)
    sequence_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=_now)
    
    # Relationships
    alert = relationship("Alert")
```

#### New `UserAlertType` Model

```python
class UserAlertType(Base):
    __tablename__ = "user_alert_types"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    alert_type_id = Column(Integer, ForeignKey("alert_types.alert_type_id", ondelete="CASCADE"), primary_key=True)
    is_subscribed = Column(Integer, default=1)
    notify_enabled = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)
    
    # Relationships
    user = relationship("User", back_populates="alert_type_subscriptions")
    alert_type = relationship("AlertType", back_populates="user_subscriptions")
```

---

## 3. Phased Migration Strategy

### Phase 1: Pre-Migration Setup (Week 1)

#### 1.1 Preparation Tasks
- ✅ **Complete security migration (Phase 3-4)** – Verify all email encryption deployed to production
- ✅ **Full database backup** – Create clean backup before any normalization work
- ✅ **Backup validation** – Restore to test environment and verify integrity
- ✅ **Staging sync** – Clone production data (anonymized) to staging
- ✅ **Code review schedule** – Coordinate backend/security leads for review gates

#### 1.2 Risk Assessment Review
| Risk | Mitigation | Owner |
|------|-----------|-------|
| Data loss during migration | Full backup + incremental rollback scripts | Rebecca Gautreaux |
| Query breaking changes | Staging testing + code refactoring validation | Qui Huynh |
| Foreign key constraint violations | Referential integrity validation before cutover | Rebecca Gautreaux |
| Zip code lookup accuracy | Populate with verified data; test coverage | Rebecca Gautreaux |
| Performance regression | Query optimization + index tuning | Qui Huynh |
| Compliance/audit trail loss | Archive raw data separately; migration logging | Noah Benoit |

---

### Phase 2: Staging Validation (Week 2-3)

#### 2.1 Create Lookup Tables (Staging)

**Task:** Populate new lookup tables with validated data.

```sql
-- Populate alert_types from distinct values in alerts table
INSERT INTO alert_types (alert_type, severity_default, is_active)
SELECT DISTINCT alert_type, 'moderate', 1
FROM alerts
WHERE alert_type IS NOT NULL;

-- Populate zip_codes (from confirmed data or external source)
-- Example: geocoding API integration or static file
INSERT INTO zip_codes (zip_code, latitude, longitude, city, state, country)
VALUES ('98001', 47.5006, -122.2120, 'Auburn', 'WA', 'USA'),
       ('98002', 47.3829, -122.3098, 'Auburn', 'WA', 'USA'),
       ... (all distinct zip codes from users table);

-- Populate locations from distinct coords in alerts
INSERT INTO locations (latitude, longitude, location_name, location_type, source, is_verified)
SELECT DISTINCT latitude, longitude, location_name, 'custom', 'migration', 1
FROM alerts
WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
```

**Validation:**
```sql
-- Verify all alert types covered
SELECT COUNT(*) as total_alerts, COUNT(DISTINCT alert_type) as unique_types
FROM alerts;
SELECT COUNT(*) FROM alert_types;
-- Both should match

-- Verify no NULL foreign keys
SELECT COUNT(*) FROM alerts WHERE alert_type NOT IN (SELECT alert_type FROM alert_types);
-- Should return 0
```

---

#### 2.2 Add New Columns (Staging)

**Task:** Add FK columns without dropping old ones yet (backward compatibility).

```sql
-- Add FKs to alerts
ALTER TABLE alerts
    ADD COLUMN location_id INT,
    ADD COLUMN alert_type_id INT,
    ADD FOREIGN KEY (location_id) REFERENCES locations(location_id),
    ADD FOREIGN KEY (alert_type_id) REFERENCES alert_types(alert_type_id);

-- Add FK to users
ALTER TABLE users
    ADD COLUMN zip_code_fk VARCHAR(10),
    ADD FOREIGN KEY (zip_code_fk) REFERENCES zip_codes(zip_code);

-- Add junction tables
CREATE TABLE summary_alerts (...);
CREATE TABLE user_alert_types (...);
```

---

#### 2.3 Migrate Data (Staging)

**Task:** Populate new columns from old data; validate referential integrity.

```sql
-- Migrate alerts.alert_type_id
UPDATE alerts a
JOIN alert_types at ON a.alert_type = at.alert_type
SET a.alert_type_id = at.alert_type_id;

-- Migrate alerts.location_id
UPDATE alerts a
JOIN locations l ON a.latitude = l.latitude AND a.longitude = l.longitude
SET a.location_id = l.location_id;

-- Migrate users.zip_code_fk
UPDATE users u
JOIN zip_codes z ON u.zip_code = z.zip_code
SET u.zip_code_fk = z.zip_code;

-- Migrate summaries.alert_ids (JSON) to summary_alerts (junction)
INSERT INTO summary_alerts (summary_id, alert_id, sequence_order)
SELECT s.id, JSON_UNQUOTE(JSON_EXTRACT(s.alert_ids, CONCAT('$[', idx, ']'))) as alert_id, idx
FROM summaries s,
     (SELECT 0 as idx UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) nums
WHERE JSON_EXTRACT(s.alert_ids, CONCAT('$[', idx, ']')) IS NOT NULL;

-- Migrate users.alert_types (JSON) to user_alert_types (junction)
INSERT INTO user_alert_types (user_id, alert_type_id, is_subscribed, notify_enabled)
SELECT u.id, at.alert_type_id, 1, 1
FROM users u,
     alert_types at,
     (SELECT JSON_UNQUOTE(JSON_EXTRACT(u.alert_types, CONCAT('$[', idx, ']'))) as alert_type
      FROM users, 
           (SELECT 0 as idx UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) nums
      WHERE JSON_EXTRACT(u.alert_types, CONCAT('$[', idx, ']')) IS NOT NULL) jat
WHERE jat.alert_type = at.alert_type;
```

**Validation Post-Migration:**
```sql
-- Verify all alerts have valid alert_type_id
SELECT COUNT(*) as orphaned_alerts FROM alerts WHERE alert_type_id IS NULL AND alert_type IS NOT NULL;
-- Should return 0

-- Verify all alerts have valid location_id (where applicable)
SELECT COUNT(*) as orphaned_locations FROM alerts WHERE location_id IS NULL AND latitude IS NOT NULL;
-- Should return 0

-- Verify summary_alerts count matches original alert_ids arrays
SELECT COUNT(*) as junction_count FROM summary_alerts;
-- Compare to total non-null alert_ids in summaries

-- Verify user_alert_types count makes sense
SELECT COUNT(*) as junction_count FROM user_alert_types;
SELECT COUNT(*) as total_users FROM users;
-- Junction count should be >= total_users (most users have multiple alert type preferences)
```

---

#### 2.4 Create Rollback Scripts (Staging)

**Purpose:** Prepare rollback for each step; test rollback execution.

```sql
-- Rollback 1: Remove constraints & foreign keys
ALTER TABLE alerts DROP FOREIGN KEY alerts_ibfk_new_1;
ALTER TABLE alerts DROP FOREIGN KEY alerts_ibfk_new_2;
ALTER TABLE users DROP FOREIGN KEY users_ibfk_new_1;
DROP TABLE IF EXISTS summary_alerts;
DROP TABLE IF EXISTS user_alert_types;

-- Rollback 2: Remove new columns
ALTER TABLE alerts DROP COLUMN location_id;
ALTER TABLE alerts DROP COLUMN alert_type_id;
ALTER TABLE users DROP COLUMN zip_code_fk;

-- Rollback 3: Restore lookup tables
DROP TABLE IF EXISTS alert_types;
DROP TABLE IF EXISTS zip_codes;
DROP TABLE IF EXISTS locations;
```

**Test Rollback:**
```bash
# In staging, after migration completes successfully:
1. Execute rollback script
2. Verify old data restored: SELECT * FROM alerts;
3. Re-execute migration script
4. Verify data matches original post-migration state
5. Document rollback execution time and any issues
```

---

#### 2.5 Code Refactoring (Staging)

**Task:** Update ORM models and queries to use new schema.

**Files to update:**
- `backend/db/models.py` – Update User, Alert, Summary models
- `backend/api/users.py` – Update registration/login queries
- `backend/api/alerts.py` – Update alert filtering/retrieval
- `backend/api/summaries.py` – Update summary queries
- `backend/schemas/*.py` – Update response schemas
- All tests referencing old schema

**Example Query Refactoring:**

**Before:**
```python
# backend/api/users.py
user = db.query(User).filter(User.zip_code == "98001").first()
# Returns: user.latitude, user.longitude directly
```

**After:**
```python
# backend/api/users.py
user = db.query(User).filter(User.zip_code_fk == "98001").first()
# Access coordinates via: user.zip_code_ref.latitude, user.zip_code_ref.longitude
# Or JOIN in query: 
# db.query(User, ZipCode).join(ZipCode).filter(User.zip_code_fk == "98001")
```

---

#### 2.6 Comprehensive Testing (Staging)

**Test Categories:**

1. **Unit Tests** – Update existing tests for new schema
   ```bash
   pytest backend/tests/test_models.py -v
   pytest backend/tests/test_api_users.py -v
   pytest backend/tests/test_api_alerts.py -v
   pytest backend/tests/test_api_summaries.py -v
   ```

2. **Integration Tests** – Verify end-to-end workflows
   - User registration with zip code lookup
   - Alert retrieval with location JOIN
   - Summary creation with M:M alert relationships
   - User alert type subscriptions

3. **Data Validation Tests** – Referential integrity
   - No orphaned FKs
   - Cascading deletes work correctly
   - Unique constraints enforced

4. **Performance Tests** – Query optimization
   - Alert queries with new location JOIN
   - User queries with zip code lookup
   - Summary queries with M:M traversal
   - Compare baseline to normalized (should be similar or better)

5. **Backward Compatibility Tests** – Existing code still works
   - API endpoints return same response format
   - Frontend queries unaffected
   - Report generation unchanged

---

### Phase 3: Production Preparation (Week 4)

#### 3.1 Final Approval & Sign-Off

**Checklist:**
- ✅ Backend Lead (Qui Huynh) reviews code refactoring; approves all query changes
- ✅ Security Lead (Noah Benoit) reviews compliance/audit implications; approves FKs & constraints
- ✅ All staging tests pass (unit, integration, performance, backward compat)
- ✅ Rollback scripts tested successfully in staging
- ✅ Data validation complete (no orphaned FKs, referential integrity OK)
- ✅ Team aware of timeline & any downtime requirements

#### 3.2 Pre-Production Communication

- Notify team of migration window
- Document any API changes for frontend/client consumers
- Prepare runbooks for deployment & rollback

#### 3.3 Final Production Backup

```bash
# Create dated backup
mysqldump -u root -p riskradar_db > riskradar_db_backup_2026_04_15_preNormalization.sql
# Verify restoration
mysql -u root -p riskradar_db < riskradar_db_backup_2026_04_15_preNormalization.sql
```

---

### Phase 4: Production Deployment (Week 5)

#### 4.1 Migration Execution

**Timeline: Low-traffic window (e.g., 2 AM UTC)**

```bash
# Step 1: Create lookup tables (5 min)
mysql riskradar_db < step_1_create_lookup_tables.sql

# Step 2: Populate lookup tables (10 min, depends on data volume)
mysql riskradar_db < step_2_populate_lookups.sql

# Step 3: Add new columns/FKs (5 min)
mysql riskradar_db < step_3_add_fk_columns.sql

# Step 4: Migrate data (15-30 min, depends on volume)
mysql riskradar_db < step_4_migrate_data.sql

# Step 5: Validate referential integrity (5 min)
mysql riskradar_db < step_5_validate_integrity.sql

# Step 6: Fix typos (rename tables/columns) (2 min)
mysql riskradar_db < step_6_fix_typos.sql

# Step 7: Drop old columns (optional; phase 2 if risky)
mysql riskradar_db < step_7_drop_old_columns.sql
```

**Total downtime estimate:** ~45 minutes (with 15-min validation buffer)

**Monitoring during migration:**
- Watch database logs for errors
- Monitor disk space (temp tables may spike)
- Alert on failed queries
- Rollback immediately if critical error detected

---

#### 4.2 Post-Migration Validation (Production)

```sql
-- Verify all data integrity constraints
SELECT 'alerts missing alert_type_id' as check_name, COUNT(*) as issue_count
FROM alerts WHERE alert_type_id IS NULL AND source IS NOT NULL;

SELECT 'alerts missing location_id (where applicable)' as check_name, COUNT(*) as issue_count
FROM alerts WHERE location_id IS NULL AND latitude IS NOT NULL;

SELECT 'users missing zip_code_fk (where applicable)' as check_name, COUNT(*) as issue_count
FROM users WHERE zip_code_fk IS NULL AND zip_code IS NOT NULL;

SELECT 'orphaned summary_alerts' as check_name, COUNT(*) as issue_count
FROM summary_alerts sa
WHERE NOT EXISTS (SELECT 1 FROM alerts a WHERE a.id = sa.alert_id);

SELECT 'orphaned user_alert_types' as check_name, COUNT(*) as issue_count
FROM user_alert_types uat
WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = uat.user_id);

-- Verify counts match expectations
SELECT COUNT(*) as total_alerts FROM alerts;
SELECT COUNT(*) as total_summary_alerts FROM summary_alerts;
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as total_user_alert_types FROM user_alert_types;
```

---

#### 4.3 Smoke Tests (Production)

- ✅ User login works (queries use new schema)
- ✅ Alert retrieval works (location JOINs correct)
- ✅ Summary retrieval works (M:M traversal OK)
- ✅ User registration works (FK validation passes)
- ✅ Frontend displays correctly (API responses same format)

---

### Phase 5: Post-Migration Cleanup & Monitoring (Week 6+)

#### 5.1 Remove Deprecated Columns (Staged)

**Timeline:** 2-4 weeks after Phase 4, only if no regressions detected.

```sql
-- Remove old JSON columns (after confirming data is safe in new structure)
ALTER TABLE summaries DROP COLUMN alert_ids;
ALTER TABLE users DROP COLUMN alert_types;

-- Optional: Remove old geographic columns from alerts (if archiving raw data separately)
ALTER TABLE alerts DROP COLUMN raw_data;
ALTER TABLE alerts DROP COLUMN location_name;

-- Remove old columns from users (after zip_code_fk fully adopted)
ALTER TABLE users DROP COLUMN latitude;
ALTER TABLE users DROP COLUMN longitude;
```

---

#### 5.2 Monitor for Regressions (Ongoing)

**Metrics to track:**
- Query performance (alert retrieval, user lookup, summary generation)
- Error rates on affected endpoints
- Slow query logs
- Application error logs
- User-reported issues

**Alarms:**
- ✚ If performance degrades > 10%, investigate indexes or query plans
- ✚ If error rates spike, check foreign key constraint violations
- ✚ If users report issues, document & escalate to Backend Lead

---

#### 5.3 Documentation & Handoff

- Update [DATA_MODEL.md](../DATA_MODEL.md) with normalized schema
- Document all schema changes in migration notes
- Train team on new ORM models & query patterns
- Archive pre-normalization documentation for reference

---

## 4. Risk Assessment & Mitigation

### 4.1 Critical Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|------------|--------|-----------|-------|
| **Data Loss** | Low | Critical | Full backup + restore testing + rollback scripts | Rebecca Gautreaux |
| **Query Breaking** | Medium | High | Comprehensive staging tests + code refactoring review | Qui Huynh |
| **FK Constraint Violations** | Medium | High | Referential integrity validation before cutover | Rebecca Gautreaux |
| **Zip Code Lookup Gaps** | Medium | Medium | Validate all user zip codes before migration; add defaults | Rebecca Gautreaux |
| **Location Geocoding Errors** | Low | Medium | Archive original lat/lon; verify location_id population | Rebecca Gautreaux |
| **Performance Regression** | Low | Medium | Query optimization + index tuning in staging | Qui Huynh |

### 4.2 Error Handling During Migration

**Scenario 1: Foreign Key Constraint Violation**
```sql
-- If migration fails with FK error:
-- 1. Check which records violate constraint
SELECT * FROM alerts WHERE alert_type NOT IN (SELECT alert_type FROM alert_types);

-- 2. Either:
--    a) Add missing alert types to lookup table, OR
--    b) Mark violating records as inactive, OR
--    c) Rollback & fix source data

-- 3. Retry migration after fixes
```

**Scenario 2: Data Type Mismatch**
```sql
-- If latitude/longitude conversion fails:
-- Check data types & ranges
SELECT MIN(latitude), MAX(latitude), MIN(longitude), MAX(longitude) FROM alerts;
-- MariaDB FLOAT should handle standard lat/lon ranges (-90 to 90, -180 to 180)
-- If values outside range, fix source data before migration
```

**Scenario 3: Out of Disk Space**
```sql
-- If migration fails due to disk space:
-- 1. Free temp tables/logs
-- 2. Verify sufficient space remains (need ~150% of DB size for temp tables)
-- 3. Rollback & try again after cleanup
-- 4. Consider partitioning large migrations
```

---

## 5. Testing Strategy

### 5.1 Test Categories

#### Unit Tests (Test Database)
```python
# test_models.py
def test_user_zip_code_relationship():
    """Verify User → ZipCode FK works"""
    user = User(zip_code_fk="98001")
    db.add(user)
    zip_code = ZipCode(zip_code="98001", latitude=47.5, longitude=-122.2)
    db.add(zip_code)
    db.commit()
    assert user.zip_code_ref.latitude == 47.5

def test_alert_location_relationship():
    """Verify Alert → Location FK works"""
    loc = Location(latitude=47.5, longitude=-122.2, location_name="Seattle")
    alert = Alert(location_id=loc.location_id)
    db.add(loc)
    db.add(alert)
    db.commit()
    assert alert.location.location_name == "Seattle"

def test_summary_alert_junction():
    """Verify Summary ↔ Alert M:M works"""
    summary = Summary()
    alert1 = Alert()
    alert2 = Alert()
    db.add_all([summary, alert1, alert2])
    db.flush()
    sa1 = SummaryAlert(summary_id=summary.id, alert_id=alert1.id)
    sa2 = SummaryAlert(summary_id=summary.id, alert_id=alert2.id)
    db.add_all([sa1, sa2])
    db.commit()
    assert len(summary.alerts) == 2
```

#### Integration Tests (Staging Database)
```python
# test_api_users.py
def test_user_registration_with_zip_code():
    """Verify registration populates zip_code_fk correctly"""
    response = client.post("/api/users/register", json={
        "email": "test@example.com",
        "password": "secure_password",
        "zip_code": "98001"
    })
    assert response.status_code == 201
    user = response.json()
    # Verify zip_code_fk was set
    db_user = db.query(User).filter(User.id == user["id"]).first()
    assert db_user.zip_code_fk == "98001"

def test_alert_retrieval_with_location():
    """Verify alert queries include location info"""
    alert = db.query(Alert).filter(Alert.id == 1).first()
    assert alert.location is not None
    assert hasattr(alert.location, 'location_name')
```

#### Data Validation Tests (Staging)
```sql
-- Verify referential integrity
SELECT 'Alerts with invalid alert_type_id' as check_name, COUNT(*) as count
FROM alerts a
WHERE a.alert_type_id IS NOT NULL 
  AND NOT EXISTS (SELECT 1 FROM alert_types WHERE alert_type_id = a.alert_type_id);
-- Should return 0

-- Verify M:M relationships are complete
SELECT COUNT(DISTINCT user_id) as users_with_prefs, COUNT(*) as total_prefs
FROM user_alert_types;
-- total_prefs should be >= users_with_prefs
```

#### Performance Tests (Staging Clone)
```sql
-- Compare query performance before/after normalization
-- Before: SELECT * FROM users WHERE zip_code = "98001";
-- After: SELECT * FROM users WHERE zip_code_fk = "98001";
-- Should have similar performance with proper indexing

-- Alert filtering (before had raw_data JSON, now has location FK)
EXPLAIN SELECT a.* FROM alerts a 
JOIN locations l ON a.location_id = l.location_id
WHERE l.location_name LIKE 'Seattle%';
-- Should show JOIN using indexes, no full table scans
```

---

## 6. Rollback Procedures

### 6.1 Full Rollback (If Critical Issue Post-Migration)

**Timeline:** ~15 minutes to execute and verify

```bash
# Step 1: Drop all new tables/FKs (5 min)
mysql riskradar_db < rollback_step_1_remove_fks.sql

# Step 2: Remove new columns (2 min)
mysql riskradar_db < rollback_step_2_remove_columns.sql

# Step 3: Drop lookup tables (1 min)
mysql riskradar_db < rollback_step_3_drop_lookups.sql

# Step 4: Restore from backup (5-10 min, depends on size)
mysql riskradar_db < riskradar_db_backup_2026_04_15_preNormalization.sql

# Step 5: Verify data integrity (2 min)
mysql riskradar_db < verify_rollback.sql
```

**Post-Rollback Checklist:**
- ✅ Verify all alerts present (same count as pre-migration)
- ✅ Verify all users present (same count)
- ✅ Run smoke tests on old queries
- ✅ Verify no data loss (spot-check random records)

---

### 6.2 Partial Rollback (If Specific Step Fails)

**Example: Migration of `user_alert_types` fails**

```sql
-- Step 1: Preserve data (as backup)
CREATE TABLE user_alert_types_failed AS SELECT * FROM user_alert_types;

-- Step 2: Remove just the failed relationship
DELETE FROM user_alert_types WHERE user_id > 1000;  -- Example: partial delete

-- Step 3: Fix source data
UPDATE users SET alert_types = '["all"]' WHERE alert_types IS NULL;

-- Step 4: Retry migration
INSERT INTO user_alert_types (...) SELECT ...;

-- Step 5: Verify & continue
SELECT COUNT(*) FROM user_alert_types;
```

---

## 7. Approval & Authorization

### 7.1 Approvers

| Role | Name | Responsibility | Approval Criteria |
|------|------|-----------------|------------------|
| **Backend Lead** | Qui Huynh | Code refactoring, API impact | All tests pass; no breaking changes to API responses |
| **Security Lead** | Noah Benoit | Compliance, audit trail | FKs/constraints maintain data integrity; compliance verified |
| **Database Admin** | Rebecca Gautreaux | Migration execution, data integrity | Migration scripts tested; rollback verified; backups confirmed |

### 7.2 Approval Process

**Before proceeding to production:**

1. **Backend Lead (Qui Huynh)** – Review & approve:
   - [ ] Code refactoring in `backend/db/models.py`
   - [ ] Updated queries in `backend/api/*.py`
   - [ ] All integration tests passing
   - [ ] No breaking API changes

2. **Security Lead (Noah Benoit)** – Review & approve:
   - [ ] Compliance implications of new FKs/constraints
   - [ ] Audit logging for FK relationships
   - [ ] Data retention policies align with normalized schema
   - [ ] No security regressions

3. **Database Administrator (Rebecca Gautreaux)** – Verify & approve:
   - [ ] Migration scripts execute without error in staging
   - [ ] Rollback scripts tested successfully
   - [ ] Data validation passes (no orphaned FKs)
   - [ ] Full backup & restore tested

---

## 8. Schedule & Timeline

| Phase | Duration | Start Date | End Date | Status | Owner |
|-------|----------|-----------|----------|--------|-------|
| **Phase 0: Security Migration** | — | — | ~Apr 15, 2026 | In Progress | Qui Huynh |
| **Phase 1: Pre-Migration Setup** | 1 week | Apr 16, 2026 | Apr 22, 2026 | Pending | Rebecca Gautreaux |
| **Phase 2: Staging Validation** | 2 weeks | Apr 23, 2026 | May 6, 2026 | Pending | Qui Huynh, Rebecca Gautreaux |
| **Phase 3: Production Prep** | 1 week | May 7, 2026 | May 13, 2026 | Pending | All leads |
| **Phase 4: Production Deployment** | 1 day | May 14, 2026 | May 14, 2026 | Pending | Rebecca Gautreaux |
| **Phase 5: Post-Migration Monitoring** | 4 weeks | May 15, 2026 | Jun 12, 2026 | Pending | All leads |

**Dependency:** Phase 0 must complete before Phase 1 begins.

---

## 9. Success Criteria

### 9.1 Pre-Deployment Validation

- ✅ All staging tests pass (unit, integration, performance, backward compat)
- ✅ Referential integrity verified (no orphaned FKs)
- ✅ Data counts match expected values
- ✅ Rollback scripts tested & execute successfully
- ✅ Backend & security leads approve

### 9.2 Post-Deployment Validation

- ✅ All smoke tests pass (user login, alert retrieval, summary generation)
- ✅ No increase in error rates on affected endpoints
- ✅ Query performance maintained (no > 10% regression)
- ✅ No user-reported issues for 2 weeks
- ✅ Data integrity checks all pass

### 9.3 Long-Term Success

- ✅ Schema fully normalized to 3NF
- ✅ Data consistency enforced by FKs & constraints
- ✅ All code refactored & tests passing
- ✅ Documentation updated
- ✅ Team trained on new schema

---

## 10. Implementation Artifacts

### 10.1 Migration Scripts (SQL)

To be created during Phase 1-2:
- `step_1_create_lookup_tables.sql` – Create alert_types, zip_codes, locations
- `step_2_populate_lookups.sql` – Populate from existing data
- `step_3_add_fk_columns.sql` – Add new columns & FKs
- `step_4_migrate_data.sql` – Populate new columns from old data
- `step_5_validate_integrity.sql` – Referential integrity checks
- `step_6_fix_typos.sql` – Rename tables/columns
- `step_7_drop_old_columns.sql` – Remove deprecated columns (optional)
- `rollback_*.sql` – Stepwise rollback scripts

### 10.2 ORM Updates

To be created during Phase 2:
- Updated `backend/db/models.py` – New models & relationships
- Updated `backend/api/*.py` – Refactored queries
- Updated `backend/tests/*.py` – New tests for normalized schema

### 10.3 Documentation

To be updated:
- [DATA_MODEL.md](../DATA_MODEL.md) – Normalized schema diagram
- [MIGRATION_NOTES.md](../MIGRATION_NOTES.md) – Migration summary
- [backend/db/migrations/README.md](../backend/db/migrations/README.md) – How to run scripts

---

## 11. Frequently Asked Questions (FAQ)

### Q1: Why proceed with normalization after the security migration?

**A:** The security migration (email encryption) is focused and low-risk. Once complete and verified, the codebase is stable. Normalization improves long-term data consistency and query performance, but sequencing is critical to avoid concurrent complex migrations.

---

### Q2: Will existing queries break after normalization?

**A:** Not if we refactor properly. During Phase 2 (staging), we update all queries to use the new schema. The API response format remains the same, so client code is unaffected. Internal queries change to use JOINs instead of direct column access.

---

### Q3: How long will the production migration take?

**A:** ~45 minutes total (with validation buffer). Most of that is data migration time. We'll perform during a low-traffic window (e.g., early morning UTC).

---

### Q4: What if something breaks during migration?

**A:** We have tested rollback scripts that restore the database to its pre-migration state within 15 minutes. The full backup is also available. We won't proceed to production until rollback is verified working in staging.

---

### Q5: Can we do this gradually (e.g., one table at a time)?

**A:** Not safely, because the interdependencies are tight. For example, normalizing `alerts` requires both `alert_types` and `locations` lookups. However, we can remove old columns gradually _after_ the main migration (Phase 5), once we're confident the new schema is stable.

---

### Q6: Will performance improve after normalization?

**A:** Potentially. Lookups become more efficient (indexed FKs). JSON parsing is eliminated. However, some queries will add JOINs. Net result: should be similar or slightly better, with proper indexing. We'll validate in staging.

---

### Q7: Why keep old columns during migration (backward compatibility)?

**A:** Allows rollback without losing data. We only drop old columns in Phase 5, after confirming the new schema is stable. This reduces risk of being stuck with an irreversible migration.

---

## 12. Sign-Off

**This plan requires approval from the following stakeholders:**

| Role | Name | Date | Signature | Notes |
|------|------|------|-----------|-------|
| Backend Lead | Qui Huynh | _____ | _____ | Code refactoring & API impact |
| Security Lead | Noah Benoit | _____ | _____ | Compliance & data integrity |
| Database Administrator | Rebecca Gautreaux | _____ | _____ | Migration execution |
| Project Manager | [Name] | _____ | _____ | Timeline & resource allocation |

---

## 13. Document History

| Date | Author | Status | Comments |
|------|--------|--------|----------|
| Apr 2, 2026 | Rebecca Gautreaux | DRAFT | Initial comprehensive plan; awaiting lead approval |
| — | Qui Huynh (Backend) | Pending | Code review & approval |
| — | Noah Benoit (Security) | Pending | Compliance & security review |

---

## Related Documents

- [USER_SECURITY_PLAN.md](USER_SECURITY_PLAN.md) – Email encryption & password hashing plan (prerequisite)
- [email_encryption_schema_plan.md](email_encryption_schema_plan.md) – Security migration schema details
- [stagingenvironmentsetup_plan.md](staging_environment_setup_plan.md) – Staging environment teardown post-security-migration
- [DATA_MODEL.md](../../DATA_MODEL.md) – Current normalized schema (to be updated post-migration)
- [MIGRATION_NOTES.md](MIGRATION_NOTES.md) – Historical migration logs

---

**END OF DOCUMENT**
