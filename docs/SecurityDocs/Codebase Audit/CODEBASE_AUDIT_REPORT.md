# RiskRadar — Codebase Security Audit Report

**Prepared by:** Noah Benoit (Security Lead)
**Date:** March 22, 2026
**Scope:** Email storage, password hashing, authentication, and related security surfaces

---

## Executive Summary

This audit examined all backend files that handle user email addresses, passwords, and authentication tokens. The review covered `backend/db/models.py`, `backend/api/users.py`, `backend/auth/security.py`, `backend/config/settings.py`, and `.env.example`. Several findings were identified ranging from a critical unresolved item (plaintext email storage) to a positive finding (bcrypt is already live). Specific findings and recommended actions are detailed below.

---

## Files Reviewed

| File | Purpose |
|---|---|
| `backend/db/models.py` | SQLAlchemy ORM models — defines the `User` table schema |
| `backend/api/users.py` | User registration, login, preferences, and notification endpoints |
| `backend/auth/security.py` | Password hashing (bcrypt), JWT token creation and verification |
| `backend/config/settings.py` | Application configuration loaded from `.env` |
| `.env.example` | Environment variable template |
| `backend/tests/test_api_users.py` | Existing test coverage for user endpoints |

---

## Findings

### Finding 1 — Email Stored in Plaintext (HIGH)

**File:** `backend/db/models.py`, line 57
**Code:**
```python
email = Column(Text, unique=True)
```

**Assessment:** User email addresses are stored as unencrypted plaintext in the database. In the event of a database breach, all user emails are immediately exposed with no additional protection. This is also a GDPR/CCPA concern, as email addresses qualify as personally identifiable information (PII).

**Required Action:** Implement AES-256-GCM email encryption before production deployment. Draft migration scripts already exist at `backend/db/migrations/draft_email_encryption_migration.py`. These require team review and execution. See `EMAIL_ENCRYPTION_CONSIDERATIONS.md` for the deterministic vs. non-deterministic tradeoff analysis.

---

### Finding 2 — Password Hashing is bcrypt (POSITIVE — Tech Stack Reference is Outdated)

**File:** `backend/auth/security.py`, lines 39–44
**Code:**
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)
```

**Assessment:** Password hashing is correctly implemented using bcrypt via `passlib`. This is the recommended algorithm for password storage — it is deliberately slow and includes built-in salting, making brute-force and rainbow table attacks computationally expensive.

**Important Note:** The Tech Stack Reference document (`docs/SecurityDocs/Tech Stack Reference/RiskRadar_Tech_Stack_Reference.md`) states that passwords are hashed with SHA-256. This is **incorrect** — the actual codebase uses bcrypt. The Tech Stack Reference should be updated to reflect the live implementation.

**Required Action:** Update the Tech Stack Reference "Known Gaps" table and the Security Notes section to reflect that bcrypt is already in place.

---

### Finding 3 — JWT Secret Key Has a Hardcoded Default (HIGH)

**File:** `backend/config/settings.py`, line 18
**Code:**
```python
JWT_SECRET_KEY: str = "CHANGE-ME-set-a-real-secret-in-dotenv"
```

**Assessment:** If the application is deployed without a `.env` file defining `JWT_SECRET_KEY`, the fallback value is a publicly known placeholder string. Any attacker aware of this default could forge valid JWT tokens, giving them unauthorized access to any user account. This is a critical misconfiguration risk.

**Required Action:** The `.env.example` already prompts teams to set this key. However, the application should add a startup check that raises an error (rather than silently using the default) if `JWT_SECRET_KEY` matches the placeholder. This is a task for Qui (Backend Developer) to implement. See `KEY_MANAGEMENT_PLAN.md` for key generation instructions.

---

### Finding 4 — CORS Wildcard Origin (MEDIUM)

**File:** `backend/main.py` (referenced in Tech Stack Reference)
**Assessment:** CORS is configured with `allow_origins=["*"]`, permitting cross-origin requests from any domain. This is acceptable for local development but constitutes a security risk in production, as it enables cross-site request forgery (CSRF)-style attacks from arbitrary web origins.

**Required Action:** Restrict `allow_origins` to the specific domains the app will be served from before production deployment. This is a task for Qui.

---

### Finding 5 — No Rate Limiting on Login Endpoint (MEDIUM)

**File:** `backend/api/users.py`, `POST /users/login`
**Assessment:** The login endpoint has no rate limiting. This leaves it exposed to credential-stuffing attacks, where an attacker submits large volumes of email/password combinations automatically. The endpoint currently returns a generic `401 Invalid email or password` (good — does not distinguish between unknown email and wrong password), but without throttling, an attacker can make unlimited guesses.

**Required Action:** Add rate limiting via `slowapi` or equivalent middleware before production deployment. This is a task for Qui.

---

### Finding 6 — Email Uniqueness Check Queries Plaintext Field (MEDIUM — Pending Migration)

**File:** `backend/api/users.py`, line 56
**Code:**
```python
existing = db.query(User).filter(User.email == body.email).first()
```

**Assessment:** The duplicate-email check works correctly today against the plaintext `email` field. Once email encryption is implemented, this query must be updated. If non-deterministic AES-GCM is used (as in the draft migration script), this query cannot be performed on the encrypted field directly. A canonical hash of the email (e.g., HMAC-SHA256 with a separate secret) stored alongside the encrypted value is needed for uniqueness checking. See `EMAIL_ENCRYPTION_CONSIDERATIONS.md` for the full analysis.

**Required Action:** Coordinate the uniqueness-check logic update with Qui and Rebecca before the email encryption migration is executed.

---

### Finding 7 — Existing Test Coverage is Solid (POSITIVE)

**File:** `backend/tests/test_api_users.py`
**Assessment:** The current user tests cover registration success, zip code inclusion, bcrypt hashing verification, and duplicate email rejection. The test `test_password_is_hashed` explicitly confirms that the stored value is not plaintext and that `verify_password` validates correctly. This is good baseline coverage.

**Required Action:** When email encryption is added, new tests are needed to confirm that encrypted emails are stored, that the uniqueness constraint still rejects duplicates, and that the login flow correctly decrypts and compares emails. This is a task for Qui, Ben, and Celeste.

---

## Summary Table

| # | Finding | Severity | Owner |
|---|---|---|---|
| 1 | Email stored in plaintext | HIGH | Qui, Rebecca (migration); Noah (oversight) |
| 2 | bcrypt already live — Tech Stack Ref outdated | INFO | Noah (update doc) |
| 3 | JWT secret key has hardcoded default fallback | HIGH | Qui (startup check); Noah (key management) |
| 4 | CORS wildcard origin | MEDIUM | Qui |
| 5 | No rate limiting on login | MEDIUM | Qui |
| 6 | Email uniqueness check must be updated post-encryption | MEDIUM | Qui, Rebecca, Noah |
| 7 | Existing test coverage is solid | POSITIVE | Team |

---

## Next Steps

1. Share this report with the team before the next sprint.
2. Address Findings 1 and 3 (HIGH severity) before any production deployment.
3. Use `EMAIL_ENCRYPTION_CONSIDERATIONS.md` to finalize the encryption approach.
4. Use `KEY_MANAGEMENT_PLAN.md` to set up the JWT secret and future email encryption key.
5. Update the Tech Stack Reference to correct the SHA-256 → bcrypt inaccuracy.

---

*This audit was conducted on March 22, 2026 as part of the RiskRadar User Security Plan implementation.*
