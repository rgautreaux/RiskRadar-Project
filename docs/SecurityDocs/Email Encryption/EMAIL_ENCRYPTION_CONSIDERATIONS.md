# RiskRadar — Email Encryption: Deterministic vs. Non-Deterministic Analysis

**Prepared by:** Noah Benoit (Security Lead)
**Date:** March 22, 2026
**Scope:** Choosing the right AES-256 encryption approach for email storage given the need for uniqueness checking and login lookup

---

## Background

The team has agreed to encrypt user email addresses in the database using AES-256 encryption. The draft migration script (`backend/db/migrations/draft_email_encryption_migration.py`) proposes AES-256-GCM with a unique, randomly generated initialization vector (IV) per email.

This document analyzes a critical tradeoff in that design: **non-deterministic encryption (unique IV per email) vs. deterministic encryption (fixed IV or HMAC-based)**, and makes a recommendation for RiskRadar's specific use case.

---

## Why This Matters

RiskRadar's backend must do two things with user email addresses:

1. **Check for duplicates at registration** — `db.query(User).filter(User.email == body.email).first()`
2. **Look up a user at login** — `db.query(User).filter(User.email == body.email).first()`

Both of these require the backend to find a user record by their email address. With **non-deterministic encryption**, the same email encrypted twice produces two completely different ciphertext values (because the IV is random). This means you cannot simply query the database for a matching encrypted value — the query will never find a match.

---

## Option A — Non-Deterministic AES-256-GCM (Current Draft Approach)

### How it works
Each email is encrypted with a randomly generated 12-byte IV:
```python
iv = os.urandom(12)
aesgcm = AESGCM(key)
encrypted = aesgcm.encrypt(iv, email.encode(), None)
```

### Security
- Strongest option cryptographically. Even if two users have the same email (not possible by constraint, but hypothetically), their ciphertext values are different.
- Authenticated encryption — AES-GCM detects tampering.
- Provides the highest level of confidentiality.

### Problem for RiskRadar
- You **cannot query** for a matching encrypted email in the database. To find a user by email at login, you would need to decrypt every row and compare in application code — this is O(n) and unacceptable at scale.
- Duplicate detection at registration has the same problem.

### Verdict
**Not viable as the sole storage mechanism** for RiskRadar without an additional lookup mechanism. However, it is appropriate for storing the actual email content (the "payload").

---

## Option B — Deterministic AES-256 (Fixed IV)

### How it works
Use a single, fixed IV for all email encryptions, so the same email always produces the same ciphertext.

### Security
- **Significantly weaker.** A fixed IV in GCM mode is a known vulnerability — it allows an attacker to detect when two users share the same plaintext (frequency analysis), and in some configurations can break the confidentiality guarantee of AES-GCM entirely.
- Do not use this approach.

### Verdict
**Not recommended.**

---

## Option C — HMAC-SHA256 Lookup Hash + Non-Deterministic Encryption (Recommended)

### How it works
Store two values for each user email:

1. **`email_lookup_hash`** — An HMAC-SHA256 of the email address, keyed with a separate secret (`EMAIL_HMAC_KEY`). This is deterministic: the same email always produces the same hash. Used for uniqueness checking and login lookup.
2. **`encrypted_email`** + **`email_iv`** — The actual email content, encrypted with AES-256-GCM using a random IV. Used only for display (e.g., showing the user their own account info).

```
email_lookup_hash = HMAC-SHA256(key=EMAIL_HMAC_KEY, message=email.lower())
```

### Lookup at login
```python
lookup_hash = hmac_email(body.email)
user = db.query(User).filter(User.email_lookup_hash == lookup_hash).first()
```

### Uniqueness at registration
```python
existing = db.query(User).filter(User.email_lookup_hash == lookup_hash).first()
if existing:
    raise HTTPException(status_code=400, detail="Email already registered")
```

### Security
- The HMAC hash is one-way — an attacker who obtains the database cannot reverse it to get the plaintext email (as long as `EMAIL_HMAC_KEY` is not compromised).
- The actual email content is protected by AES-256-GCM with a random IV, providing full ciphertext confidentiality.
- Because lookup is done via the hash, not the ciphertext, the query is O(1) with a database index.
- Normalizing the email to lowercase before hashing prevents `Alice@test.com` and `alice@test.com` from appearing as different users.

### Weakness to be aware of
- HMAC-SHA256 lookup hashes are technically vulnerable to offline dictionary attacks if `EMAIL_HMAC_KEY` is compromised — an attacker with the key and the hash database could precompute hashes for common email addresses and compare. This is mitigated by keeping `EMAIL_HMAC_KEY` separate from `EMAIL_ENCRYPTION_KEY` and storing both in AWS Secrets Manager with strict access controls.

### Verdict
**This is the recommended approach for RiskRadar.** It provides strong confidentiality for the email content while preserving the ability to do O(1) uniqueness checks and login lookups.

---

## Summary Table

| Approach | Lookup Possible | Uniqueness Check | Cryptographic Strength | Recommended |
|---|---|---|---|---|
| Non-deterministic GCM only | No (O(n)) | Not practical | Strongest | No |
| Deterministic (fixed IV) | Yes | Yes | Weak — vulnerable | No |
| HMAC hash + non-deterministic GCM | Yes (O(1)) | Yes | Strong | **Yes** |

---

## Required Schema Changes (Option C)

The `users` table needs the following additions:

| Column | Type | Purpose |
|---|---|---|
| `email_lookup_hash` | Text, UNIQUE, INDEXED | HMAC-SHA256 of normalized email; used for login and duplicate detection |
| `encrypted_email` | Text | AES-256-GCM ciphertext of email |
| `email_iv` | Text | Base64-encoded IV used during encryption |

The existing `email` column should be retained until migration is complete and validated, then dropped.

---

## Required New Environment Variables

```
EMAIL_ENCRYPTION_KEY=<32-byte AES key, hex-encoded>
EMAIL_HMAC_KEY=<32-byte HMAC key, hex-encoded — different from encryption key>
```

Both keys should be generated using:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

See `KEY_MANAGEMENT_PLAN.md` for storage and rotation instructions.

---

## Impact on Existing Code

| File | Change Required |
|---|---|
| `backend/db/models.py` | Add `email_lookup_hash`, `encrypted_email`, `email_iv` columns to User model |
| `backend/api/users.py` | Update register and login queries to use `email_lookup_hash` |
| `backend/auth/security.py` or new `backend/auth/encryption.py` | Add `encrypt_email()`, `decrypt_email()`, `hmac_email()` functions |
| `backend/db/migrations/draft_email_encryption_migration.py` | Update to implement Option C (HMAC hash + GCM encryption) |
| `backend/tests/test_api_users.py` | Add tests for encrypted email storage, duplicate detection via hash, login via hash |

These changes should be coordinated between Qui (Backend Developer) and Rebecca (Database Administrator), with Noah reviewing for security correctness.

---

*Prepared as part of the RiskRadar User Security Plan. Last updated March 22, 2026.*
