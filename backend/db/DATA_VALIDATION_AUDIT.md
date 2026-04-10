# Data Validation Layer Audit

**Date:** Apr 10, 2026  
**Owner:** Rebecca Gautreaux  
**Status:** COMPLETE (audit catalog ready for Phase 2-4 implementation)

This document catalogs validation gaps identified in the RiskRadar backend API across request schemas, query parameters, and database operations. Each gap is mapped to a specific endpoint or layer, priority-ranked, and includes remediation strategy.

---

## Executive Summary

**Total Gaps Identified:** 16 critical/high + 8 medium/low = **24 issues**

**Current State:**
- ✅ Password hashing exists (bcrypt)
- ✅ Encrypted email storage exists (AES + HMAC)
- ❌ Input validation mostly absent from Pydantic schemas
- ⚠️ Query parameters not validated (min_length, max_value, patterns)
- ⚠️ Type mismatches between schema fields and database expectations
- ❌ No password strength requirements
- ❌ No fallback error handling for external APIs (LLM, geocoding, etc.)

---

## Priority 1: CRITICAL (Must Fix Before Apr 13 Freeze)

### 1.1 Email Format Validation

**Endpoint:** `POST /users/register`, `POST /users/login`  
**Current:** Email is bare `str` type, no format validation  
**Risk:** Invalid emails accepted; registration allows non-email strings  
**Fix:** Use Pydantic `EmailStr`  

```python
# backend/schemas/user.py
from pydantic import EmailStr

class UserCreate(BaseModel):
    display_name: str
    email: EmailStr  # <-- CHANGE from: str
    password: str
    zip_code: Optional[str] = None
```

**Test Case:** `test_register_invalid_email_format_rejected()`

---

### 1.2 ZIP Code Format Validation (5-digit pattern)

**Endpoints:** `POST /users/register`, `PUT /users/{id}/preferences`, `GET /api/v1/summaries/latest/local?zip_code=`, `GET /api/v1/location/search?zip_code=`  
**Current:** Zip codes accepted as string without pattern validation  
**Risk:** 2-digit, 6-digit, or non-numeric strings accepted; geocoding API calls fail downstream  
**Fix:** Add `pattern` and `Field` constraint to all zip_code fields  

```python
# backend/schemas/user.py
class UserCreate(BaseModel):
    zip_code: Optional[str] = Field(None, pattern=r"^\d{5}$", description="5-digit US ZIP code")

class UserPrefsUpdate(BaseModel):
    zip_code: Optional[str] = Field(None, pattern=r"^\d{5}$")

# backend/schemas/summary.py
class SummaryGenerateLocal(BaseModel):
    zip_code: str = Field(..., pattern=r"^\d{5}$")
```

**Also fix query params:** In FastAPI, use `Query` with `pattern` and `regex`

```python
# backend/api/summaries.py
@router.get("/latest/local", response_model=SummaryOut | None)
def latest_local_summary(
    zip_code: str = Query(..., min_length=5, max_length=5, regex=r"^\d{5}$"),  # <-- ADD regex
    db: Session = Depends(get_db),
):
```

**Test Case:** `test_user_register_invalid_zip_rejected()`, `test_query_param_zip_format_rejected()`

---

### 1.3 Latitude/Longitude Bounds Validation

**Fields:** `User.latitude`, `User.longitude`, `Alert.latitude`, `Alert.longitude`  
**Current Schemas:** No bounds check on float fields  
**Risk:** Out-of-range coordinates silently accepted; geocoding/map rendering fails  
**Fix:** Add `Field(ge=-90, le=90)` for lat, `Field(ge=-180, le=180)` for lon  

```python
# backend/schemas/user.py
class UserPrefsUpdate(BaseModel):
    zip_code: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude (-90 to 90)")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude (-180 to 180)")
```

**Test Case:** `test_user_prefs_invalid_latitude_rejected()`, `test_user_prefs_invalid_longitude_rejected()`

---

### 1.4 Alert Type & Severity Enum Validation

**Endpoints:** `GET /api/v1/alerts?alert_type=`, `GET /api/v1/alerts?severity=`  
**Current:** Query params accepted as free strings  
**Risk:** Invalid alert_type or severity values accepted; filtering silently returns empty  
**Fix:** Create enum or validate against allowed values  

```python
# backend/schemas/alert.py
from enum import Enum

class AlertTypeEnum(str, Enum):
    WEATHER = "weather"
    AIR_QUALITY = "air_quality"
    WILDFIRE = "wildfire"
    POLLUTION = "pollution"
    EARTHQUAKE = "earthquake"

class SeverityEnum(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

# backend/api/alerts.py
@router.get("", response_model=list[AlertOut])
def list_alerts(
    alert_type: Optional[AlertTypeEnum] = None,  # <-- Use enum
    severity: Optional[SeverityEnum] = None,     # <-- Use enum
    source: Optional[str] = None,
    ...
):
```

**Test Case:** `test_alerts_list_invalid_alert_type_rejected()`, `test_alerts_list_invalid_severity_rejected()`

---

### 1.5 Query Parameter Bounds Validation

**Endpoints:** All pagination endpoints  
**Current:** `limit` and `offset` accept unbounded integers  
**Risk:** `limit=999999` fetches entire table; memory exhaustion possible  
**Fix:** Add max_length or `le` constraint  

```python
# backend/api/alerts.py
@router.get("", response_model=list[AlertOut])
def list_alerts(
    limit: int = Query(default=50, le=200),     # <-- ADD le=200
    offset: int = Query(default=0, ge=0),       # <-- ADD ge=0
    ...
):

# backend/api/summaries.py
@router.get("", response_model=list[SummaryOut])
def list_summaries(
    limit: int = Query(default=20, le=100),     # <-- ADD le=100
    ...
):
```

**Test Case:** `test_alerts_list_max_limit_enforced()`, `test_alerts_list_negative_offset_rejected()`

---

### 1.6 Device Token Non-Empty Validation

**Endpoint:** `POST /users/{id}/device-token` (NEW endpoint, Phase 3)  
**Current:** Field does not exist yet (new)  
**Risk:** Empty or whitespace-only tokens stored; notification sending fails silently  
**Fix:** Create schema with non-empty, length-bounded validation  

```python
# backend/schemas/user.py
class DeviceTokenUpdate(BaseModel):
    device_token: str = Field(..., min_length=1, max_length=1000, description="Expo push token or FCM ID")

class DeviceTokenRevoke(BaseModel):
    pass  # No required fields
```

**Test Case:** `test_device_token_empty_string_rejected()`, `test_device_token_max_length_enforced()`

---

## Priority 2: HIGH (Must Fix by Apr 13)

### 2.1 Summary Type Enum Validation

**Endpoints:** `GET /api/v1/summaries?summary_type=`, `POST /api/v1/summaries/generate`  
**Current:** summary_type accepted as free string  
**Risk:** Invalid types bypass filter (e.g., `summary_type=invalid` returns no results silently)  
**Fix:** Add enum or whitelist  

```python
# backend/schemas/summary.py
class SummaryTypeEnum(str, Enum):
    DAILY = "daily"
    LOCAL = "local"
    BREAKING = "breaking"  # future

# backend/api/summaries.py
def list_summaries(
    summary_type: Optional[SummaryTypeEnum] = None,
    ...
):
```

**Test Case:** `test_summaries_list_invalid_type_rejected()`

---

### 2.2 Alert Types Array Validation (in Preferences)

**Endpoint:** `PUT /users/{id}/preferences` (NEW endpoint, Phase 2)  
**Current:** `alert_types` is optional list; no validation on items  
**Risk:** Invalid alert type names stored; preference filtering breaks  
**Fix:** Validate array items against allowed types  

```python
# backend/schemas/user.py
from typing import Annotated

class UserPrefsUpdate(BaseModel):
    alert_types: Optional[Annotated[list[AlertTypeEnum], ...]] = None  # Validate each item
    notify_severity: Optional[SeverityEnum] = None
```

**Test Case:** `test_user_prefs_invalid_alert_type_in_array_rejected()`

---

### 2.3 Password Strength Validation

**Endpoint:** `POST /users/register`  
**Current:** Any non-empty password accepted  
**Risk:** Weak passwords allow brute-force attacks  
**Fix:** Add min length + complexity requirements  

```python
# backend/schemas/user.py
from pydantic import field_validator

class UserCreate(BaseModel):
    password: str = Field(..., min_length=8)  # At least 8 chars
    
    @field_validator('password')
    def password_strong(cls, v):
        """Require at least one digit and one letter."""
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v
```

**Test Case:** `test_register_weak_password_rejected()`, `test_register_password_no_digit_rejected()`

---

### 2.4 Notification Severity Enum Validation

**Endpoints:** `PUT /users/{id}/preferences`, `PUT /users/notifications`  
**Current:** notify_severity accepted as free string  
**Risk:** Invalid severity stored; alerting logic may fail  
**Fix:** Use `SeverityEnum` for notify_severity  

```python
# backend/schemas/user.py
class UserPrefsUpdate(BaseModel):
    notify_severity: Optional[SeverityEnum] = None  # <-- Restrict to enum
```

**Test Case:** `test_user_prefs_invalid_notify_severity_rejected()`

---

### 2.5 HTTP Response Code Consistency

**Issue:** Inconsistent error responses across endpoints  
**Current:** Some endpoints return 400, others 422, some don't handle validation  
**Fix:** Use Pydantic validation to auto-generate 422 (Unprocessable Entity) for all input errors  
**Test Case:** `test_all_endpoints_return_422_on_validation_error()`

---

## Priority 3: MEDIUM (Nice-to-Have, Can Defer Post-MVP)

### 3.1 Source Database Validation

**Fields:** `Alert.source`, `ScrapeLog.source`, `ScrapeLogArchive.source`  
**Current:** Accepted as free strings  
**Risk:** Typos or invalid sources silently accepted  
**Fix:** Create enum or validate against scraper registry  

```python
# backend/scrapers/SOURCE_ENUM.py
class SourceEnum(str, Enum):
    NWS = "nws"
    AIRNOW = "airnow"
    EPA = "epa"
    FIRMS = "firms"
    USGS = "usgs"
```

**Effort:** Low (define enum + add validation)

---

### 3.2 LLM Model Name Validation

**Field:** `Summary.model_used`  
**Current:** Any string accepted  
**Fix:** Validate against configured models in settings  

```python
# backend/llm/summarizer.py
VALID_MODELS = [settings.LLM_MODEL, settings.LLM_MODEL_GUEST, settings.LLM_MODEL_PREMIUM]
```

**Effort:** Low

---

### 3.3 User Email Uniqueness Index

**Database:** User table  
**Current:** `email_hmac` has unique constraint, but uniqueness checks happen at app layer  
**Risk:** Race conditions in concurrent registration  
**Fix:** Add database-level unique index on `email_hmac`  

```sql
ALTER TABLE users ADD UNIQUE INDEX uq_email_hmac (email_hmac);
```

**Status:** Already exists (check migration logs)

---

### 3.4 Latitude/Longitude Precision Limits

**Current:** Float accepts up to full precision  
**Fix:** Limit to useful precision (6 decimals = ~0.1m accuracy)  

```python
# backend/schemas/alert.py
latitude: Optional[float] = Field(None, ge=-90, le=90)
# Add documentation: "Precision rounded to 6 decimals (~0.1m accuracy)"
```

**Effort:** Low (documentation only)

---

### 3.5 JSON Field Validation (alert_types, raw_data)

**Fields:** `User.alert_types` (JSON array), `Alert.raw_data` (JSON)  
**Current:** Stored as JSON but no schema validation  
**Fix:** Parse and validate structure on read/write  

```python
# backend/db/models.py
import json
from typing import Any

def get_alert_types(self) -> list[str]:
    try:
        return json.loads(self.alert_types or '["all"]')
    except json.JSONDecodeError:
        return ["all"]

def set_alert_types(self, types: list[str]):
    self.alert_types = json.dumps(types)
```

**Effort:** Medium (add helper methods to ORM model)

---

## Priority 4: LOW (Post-MVP, Observability)

### 4.1 Query Performance Validation

**Issue:** No indexes on frequently-used query columns  
**Fix:** Add database indexes on `alert_type`, `severity`, `source`, `created_at`  

```sql
CREATE INDEX idx_alert_type ON alerts(alert_type);
CREATE INDEX idx_severity ON alerts(severity);
CREATE INDEX idx_source ON alerts(source);
CREATE INDEX idx_created_at ON alerts(created_at);
CREATE INDEX idx_summary_type ON summaries(summary_type);
```

---

### 4.2 Rate Limiting

**Issue:** No rate limits on API endpoints  
**Fix:** Use FastAPI `RateLimiter` middleware  

```python
# backend/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

---

### 4.3 Request Size Limits

**Issue:** No max payload size validation  
**Fix:** Add middleware to reject oversized requests  

```python
# backend/main.py
from fastapi import Request
from fastapi.exceptions import RequestValidationError

@app.middleware("http")
async def validate_request_size(request: Request, call_next):
    # Max 10MB
    if int(request.headers.get('content-length', 0)) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Payload too large")
    return await call_next(request)
```

---

## Audit Results Summary

| Category | Count | Priority | Phase |
|----------|-------|----------|-------|
| Email validation | 1 | P1 | 2-4 |
| ZIP code validation | 1 | P1 | 2-4 |
| Lat/lon bounds | 1 | P1 | 2-4 |
| Enum validation (alert_type, severity) | 3 | P1 | 2-4 |
| Query parameter bounds | 1 | P1 | 2-4 |
| Device token validation | 1 | P1 | 3 |
| Summary type enum | 1 | P2 | 2-4 |
| Alert types array validation | 1 | P2 | 2-4 |
| Password strength | 1 | P2 | 2-4 |
| Notification severity enum | 1 | P2 | 2-4 |
| Response code consistency | 1 | P2 | 4 |
| **SUBTOTAL** | **14** | **P1-P2** | **Done in Phases 2-4** |
| Source enum (deferred) | 1 | P3 | Post-MVP |
| LLM model validation | 1 | P3 | Post-MVP |
| Database indexes | 6 | P4 | Post-MVP |
| Rate limiting | 1 | P4 | Post-MVP |
| Request size limits | 1 | P4 | Post-MVP |
| **TOTAL** | **24** | Mixed | Phases 2-4 + Post-MVP |

---

## Implementation Timeline

### Phase 2-4 (Apr 11-13): DO NOW
- Email format validation (EmailStr)
- ZIP code pattern validation (regex)
- Lat/lon bounds validation (ge/le)
- Alert type & severity enum validation
- Query parameter bounds (le/ge)
- Device token validation
- Login error handling (user not found gracefully)
- LLM fallback error handling

### Phase 4 (Apr 12-13): SHOULD DO
- Password strength validation
- Summary type enum
- Alert types array validation
- Response code normalization

### Post-MVP (After Apr 13): NICE-TO-HAVE
- Database indexes
- Rate limiting
- Request size limits
- Source enum
- JSON schema validation helpers

---

## Test Coverage Checklist

**Files to Update:**
- `backend/tests/test_api_users.py` — email, zip, password validation
- `backend/tests/test_api_alerts.py` — enum validation, query bounds
- `backend/tests/test_api_summaries.py` — summary type enum
- `backend/tests/test_api_system.py` — error code consistency

**Minimum 20 new test cases** to cover all P1 and P2 gaps.

---

## Rollout Checklist

- [ ] Email validation implemented and tested
- [ ] ZIP code validation implemented and tested
- [ ] Lat/lon bounds validation implemented and tested
- [ ] Alert type & severity enums created and tested
- [ ] Query parameter bounds validated and tested
- [ ] Device token validation schema created and tested
- [ ] Error handling for LLM fallback implemented
- [ ] Password strength validation implemented and tested
- [ ] All tests passing: `pytest backend/ -v` (110+ tests)
- [ ] Manual smoke test: register/login.success → can save preferences → alerts filter correctly → can register device token
- [ ] Code review complete
- [ ] Merge to main before Apr 13 freeze

---

## Notes for Implementation

1. **Use Pydantic field validators** for complex logic (e.g., password strength check)
2. **Use FastAPI Query/Path/Body** for query param validation (auto-generates 422 errors)
3. **Create Enums** for all fixed-value fields (alert_type, severity, summary_type, source)
4. **Test all error paths** — invalid input, boundary conditions, combinations
5. **Update API docs** (`/docs` Swagger) — validation rules visible to frontend team
6. **No breaking changes** to existing endpoints — all validations are **tightening existing behavior**, not changing it

---

