# RiskRadar — Code Review: Email Encryption Migration & Rollback Scripts

**Reviewer:** Noah Benoit (Security Lead)
**Date:** March 22, 2026
**Files Reviewed:**
- `backend/db/migrations/draft_email_encryption_migration.py`
- `backend/db/migrations/draft_email_encryption_rollback.py`

---

## Summary

Both scripts are well-labeled planning documents and serve their intended purpose as drafts for team review. They use correct library choices and demonstrate sound conceptual design. However, several issues must be resolved before either script can be considered production-ready. The most critical issue is that the current draft uses non-deterministic AES-GCM without a lookup mechanism, which breaks the login and duplicate-detection flows. The recommended fix is outlined in `EMAIL_ENCRYPTION_CONSIDERATIONS.md`.

**Overall verdict: Not ready to execute. Revisions required before staging.**

---

## Migration Script Review

**File:** `backend/db/migrations/draft_email_encryption_migration.py`

### What it does

- Defines a connection to the database via SQLAlchemy.
- Provides an `encrypt_email()` function using `cryptography.hazmat.primitives.ciphers.aead.AESGCM` with a randomly generated 12-byte IV.
- Outlines (in commented pseudo-code) the steps to add new columns, encrypt emails batch-by-batch, validate uniqueness, and drop the old column.

---

### Issue 1 — Hardcoded Database Credentials (CRITICAL)

**Line 14:**
```python
DATABASE_URL = "mysql+pymysql://user:password@localhost/riskradar_db"
```

The database connection string contains a placeholder `user:password`. If a developer fills in real credentials here and commits the file, those credentials are exposed in version control history.

**Required fix:** Load `DATABASE_URL` from the environment, not a hardcoded string:
```python
import os
DATABASE_URL = os.environ["DATABASE_URL"]
```

Or, better, import from `config.settings`:
```python
from config.settings import settings
DATABASE_URL = settings.DATABASE_URL
```

---

### Issue 2 — Encryption Key Not Loaded or Validated (CRITICAL)

The `encrypt_email()` function accepts a `key` parameter, but the script contains no code that loads the key from the environment or validates its length. The key variable is never defined anywhere in the script — the migration would fail immediately at runtime.

**Required fix:** Add key loading and validation before the migration loop:
```python
import binascii
from config.settings import settings

raw_key_hex = settings.EMAIL_ENCRYPTION_KEY
if not raw_key_hex or len(raw_key_hex) != 64:
    raise RuntimeError("EMAIL_ENCRYPTION_KEY must be a 64-character hex string (32 bytes).")
key = binascii.unhexlify(raw_key_hex)
```

---

### Issue 3 — No HMAC Lookup Hash (CRITICAL — Architecture Issue)

The draft stores only `encrypted_email` and `email_iv`. As analyzed in `EMAIL_ENCRYPTION_CONSIDERATIONS.md`, non-deterministic AES-GCM means the same email encrypted twice produces different ciphertext. This breaks the login lookup and duplicate-email check in `backend/api/users.py`.

**Required fix:** Add an `email_lookup_hash` column and populate it with `HMAC-SHA256(EMAIL_HMAC_KEY, email.lower())` during migration. Update the schema plan and migration steps to include this column.

---

### Issue 4 — No Transaction Wrapping or Batch Commit (HIGH)

The pseudo-code processes each user individually but does not wrap operations in a transaction. If the migration fails halfway through, some users will have encrypted emails and others will not, leaving the database in an inconsistent state.

**Required fix:** Wrap the migration in a database transaction, or use batch commits with rollback on failure:
```python
with engine.begin() as conn:
    # all migration steps here — auto-rollback on exception
```

---

### Issue 5 — No Progress Logging (MEDIUM)

The script has no logging. If it runs on a table with thousands of users and fails at row 800, there is no way to know where it stopped.

**Required fix:** Add logging for each batch processed:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Inside loop:
logger.info(f"Encrypted email for user ID {user.id}")
```

---

### Issue 6 — No Dry-Run Mode (MEDIUM)

The script has no way to simulate the migration without writing to the database. A dry-run mode allows the team to validate logic without risk.

**Required fix:** Add a `DRY_RUN` flag (from environment or CLI argument) that logs what would happen without executing writes.

---

### Issue 7 — Dropping the Old Email Column is Commented Out but Risky (LOW — Process)

The final step (dropping the old `email` column) is commented out, which is correct for a draft. However, this step should only be executed after:
- All users have been migrated and validated.
- The application code has been updated to use `email_lookup_hash` and `encrypted_email`.
- A full test run in staging has passed.

**Recommendation:** Keep the drop step separate from the migration script entirely. Execute it manually after the above checklist is confirmed. Document this in the migration notes.

---

## Rollback Script Review

**File:** `backend/db/migrations/draft_email_encryption_rollback.py`

### What it does

- Outlines (in commented pseudo-code) the steps to reverse the email encryption migration: restore the old `email` column, decrypt each row back to plaintext, and remove the `encrypted_email` and `email_iv` columns.

---

### Issue 1 — Hardcoded Database Credentials (CRITICAL)

Same as migration script. See Migration Issue 1. Apply the same fix.

---

### Issue 2 — `decrypt_email()` Function Not Defined (CRITICAL)

The rollback pseudo-code calls `decrypt_email(user.encrypted_email, user.email_iv, key)`, but no such function is defined anywhere in the script or the codebase.

**Required fix:** Define the decryption function before the rollback logic:
```python
def decrypt_email(encrypted_b64: str, iv_b64: str, key: bytes) -> str:
    import base64
    encrypted = base64.b64decode(encrypted_b64)
    iv = base64.b64decode(iv_b64)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(iv, encrypted, None).decode()
```

---

### Issue 3 — No Key Loading (CRITICAL)

Same issue as migration script — the key is never loaded. Apply the same fix as Migration Issue 2.

---

### Issue 4 — No Transaction Wrapping (HIGH)

Same concern as migration — a partial rollback leaves the database inconsistent. Wrap in a transaction.

---

### Issue 5 — Rollback Drops `email_lookup_hash` Not Mentioned (MEDIUM)

Once the migration is updated to include the `email_lookup_hash` column (per the recommendation in `EMAIL_ENCRYPTION_CONSIDERATIONS.md`), the rollback script must also drop that column. The current draft does not mention it.

**Required fix:** After the schema is finalized, update the rollback to cover all new columns.

---

## Checklist Before Scripts Are Executed in Staging

- [ ] Remove all hardcoded credentials; load from environment
- [ ] Add `EMAIL_ENCRYPTION_KEY` and `EMAIL_HMAC_KEY` loading and validation
- [ ] Add `email_lookup_hash` column and HMAC population to migration
- [ ] Define `decrypt_email()` in rollback script
- [ ] Wrap all operations in database transactions
- [ ] Add dry-run mode to migration script
- [ ] Add progress logging
- [ ] Coordinate with Rebecca to take a full database backup before running
- [ ] Test both scripts end-to-end in staging with a copy of real-format data
- [ ] Confirm the application code (users.py, models.py) is updated to match the new schema
- [ ] Get sign-off from Qui and Rebecca before staging run

---

*Code review conducted March 22, 2026 by Noah Benoit (Security Lead) as part of the RiskRadar User Security Plan.*
