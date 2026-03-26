# RiskRadar — Key Management Plan

**Prepared by:** Noah Benoit (Security Lead)
**Date:** March 22, 2026
**Scope:** JWT secret key, email encryption key (AES-256), generation, storage, rotation, and recovery procedures

---

## Overview

RiskRadar requires two categories of cryptographic secrets before production deployment:

1. **JWT Secret Key** — Signs and verifies user authentication tokens. Already in use; needs to be set to a strong random value in `.env`.
2. **Email Encryption Key (AES-256)** — Will encrypt user email addresses at rest. Not yet in use; must be introduced alongside the email encryption migration.

This document covers how to generate each key, how to store it securely, how and when to rotate it, and what the recovery procedure is if a key is lost or compromised.

---

## Part 1 — JWT Secret Key

### Current State

The JWT secret key is loaded from the `JWT_SECRET_KEY` environment variable in `backend/config/settings.py`. If the variable is not set in `.env`, it falls back to the string `"CHANGE-ME-set-a-real-secret-in-dotenv"`. This default is publicly known and must never be used in staging or production.

### Generating a Strong JWT Secret

Run the following in any terminal with Python available:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

This produces a 64-character hexadecimal string (256 bits of entropy). Copy the output.

### Setting the Key

Open your `.env` file (copy from `.env.example` if it does not exist) and set:

```
JWT_SECRET_KEY=<paste the generated value here>
```

Never commit `.env` to version control. Confirm that `.env` is listed in `.gitignore`.

### Storage in Production (AWS)

For the AWS-hosted production environment:

- Store `JWT_SECRET_KEY` in **AWS Secrets Manager** under the path `riskradar/prod/jwt_secret_key`.
- Configure the application to load the secret at startup via the AWS SDK rather than a flat `.env` file.
- Restrict access to the secret using an IAM policy that allows only the RiskRadar application role to read it.
- Never log the secret value. Never print it in error messages.

### JWT Secret Rotation Schedule

| Event | Action |
|---|---|
| Initial production setup | Generate a new key; store in Secrets Manager |
| Every 90 days | Rotate the key (see procedure below) |
| Suspected compromise | Rotate immediately; invalidate all active sessions |
| Team member departure | Rotate within 24 hours |

### JWT Secret Rotation Procedure

Rotating the JWT secret will **invalidate all currently active user sessions** — all users will be logged out and will need to sign in again. Plan rotations for low-traffic periods and communicate in advance if users will be affected.

1. Generate a new secret: `python -c "import secrets; print(secrets.token_hex(32))"`
2. Update the value in AWS Secrets Manager.
3. Restart the application server so the new secret is loaded.
4. Verify that new logins succeed and that old tokens are rejected.
5. Document the rotation date and the team member who performed it in this file.

### Rotation Log

| Date | Performed By | Notes |
|---|---|---|
| *(not yet rotated — pre-production)* | — | — |

---

## Part 2 — Email Encryption Key (AES-256)

### Purpose

Once email encryption is implemented, user email addresses will be encrypted in the database using AES-256-GCM. The encryption key must be stored separately from the database so that a database breach alone does not expose user emails.

### Generating the Key

AES-256 requires a 32-byte (256-bit) key. Generate one with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Setting the Key

Add the following to your `.env` file:

```
EMAIL_ENCRYPTION_KEY=<paste the generated 64-char hex value here>
```

In `backend/config/settings.py`, add:

```python
EMAIL_ENCRYPTION_KEY: str = ""
```

In the encryption utility (`backend/auth/security.py` or a new `backend/auth/encryption.py`), load and decode the key:

```python
import os, binascii
key = binascii.unhexlify(settings.EMAIL_ENCRYPTION_KEY)
```

### Storage in Production (AWS)

- Store in **AWS Secrets Manager** at `riskradar/prod/email_encryption_key`.
- Restrict IAM access to the application role only.
- The key must never appear in logs, error messages, or API responses.

### Email Encryption Key Rotation

Rotating this key is significantly more involved than rotating the JWT secret, because all encrypted email values in the database must be re-encrypted with the new key.

**Rotation schedule:** Every 180 days, or immediately upon suspected compromise.

**Rotation procedure:**
1. Generate a new AES-256 key.
2. In a staging environment, verify the re-encryption script: for each user, decrypt the email with the old key, re-encrypt with the new key, and update the record.
3. Schedule a maintenance window and run the re-encryption script against production in batches (coordinate with Rebecca).
4. Once all records are updated, replace the old key in Secrets Manager with the new key.
5. Restart the application. Verify that login still works for existing users.
6. Securely delete the old key after confirming that no records reference it.

### Key Backup and Recovery

- AWS Secrets Manager automatically versions secrets. Previous versions are retained for 30 days by default — this acts as the key backup for the rotation window.
- For disaster recovery: if the encryption key is lost and no backup exists, encrypted emails **cannot be recovered**. Users would need to re-register. This is why backups and versioning are critical.
- Document the key ARN (Amazon Resource Name) in this file after it is created.

### Key ARN Log

| Key | AWS Secrets Manager ARN | Created | Last Rotated |
|---|---|---|---|
| JWT Secret | *(to be filled in at production setup)* | — | — |
| Email Encryption Key | *(to be filled in at production setup)* | — | — |

---

## Part 3 — General Key Security Rules

These rules apply to all cryptographic secrets used by RiskRadar:

1. **Never hard-code secrets in source code.** All keys must come from environment variables or a secrets manager.
2. **Never commit secrets to version control.** Verify that `.env` and any file containing keys is in `.gitignore`.
3. **Never log secrets.** Ensure that logging configuration does not capture environment variables.
4. **Limit access.** Only the application process and designated administrators should have read access to secrets. Use IAM roles to enforce this.
5. **Use separate keys per environment.** Development, staging, and production must each use different keys. Never use a production key in development.
6. **Document all keys.** Every key in use must be listed in this document with its purpose, storage location, and rotation schedule.

---

## Startup Validation (Recommended)

The backend should validate that required secrets are properly set at startup. The following check should be added to `backend/main.py` or the settings module (task for Qui):

```python
PLACEHOLDER = "CHANGE-ME-set-a-real-secret-in-dotenv"
if settings.JWT_SECRET_KEY == PLACEHOLDER or not settings.JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is not set. Set a strong random value in your .env file before running."
    )
```

This ensures the application fails fast rather than running insecurely with a known-bad default.

---

*Prepared as part of the RiskRadar User Security Plan. Last updated March 22, 2026.*
