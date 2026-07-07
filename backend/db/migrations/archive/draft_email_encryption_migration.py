"""
Draft Migration Script: Email Encryption & Unique Constraint

This script is for planning purposes only. Do NOT execute in production until reviewed and coordinated with backend team.
"""

import os
import base64
import binascii
import logging
import hmac
import hashlib
from sqlalchemy import Column, Text, MetaData, Table, DateTime, Integer
from sqlalchemy.engine import create_engine
from datetime import datetime, timezone
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Load config from environment
DATABASE_URL = os.environ.get("DATABASE_URL")
EMAIL_ENCRYPTION_KEY = os.environ.get("EMAIL_ENCRYPTION_KEY")
EMAIL_HMAC_KEY = os.environ.get("EMAIL_HMAC_KEY")
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

if not DATABASE_URL or not EMAIL_ENCRYPTION_KEY or not EMAIL_HMAC_KEY:
    raise RuntimeError("Missing required environment variables.")

key = binascii.unhexlify(EMAIL_ENCRYPTION_KEY)
hmac_key = binascii.unhexlify(EMAIL_HMAC_KEY)

engine = create_engine(DATABASE_URL)
metadata = MetaData()
users = Table("users", metadata, autoload_with=engine)
migration_log = Table("migration_log", metadata, autoload_with=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration")

def encrypt_email(email, key):
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(iv, email.encode(), None)
    return base64.b64encode(encrypted).decode(), base64.b64encode(iv).decode()

def hmac_email(email, hmac_key):
    # Lowercase and normalize email for hashing
    normalized = email.strip().lower()
    return hmac.new(hmac_key, normalized.encode(), hashlib.sha256).hexdigest()

def log_migration(conn, user_id, action, status, error_message=None):
    now = datetime.now(timezone.utc)
    ins = migration_log.insert().values(
        timestamp=now,
        user_id=user_id,
        action=action,
        status=status,
        error_message=error_message,
    )
    if not DRY_RUN:
        conn.execute(ins)
    logger.info(f"[MigrationLog] user_id={user_id} action={action} status={status} error={error_message}")

# Migration steps (pseudo-code)
# 1. Add new columns: encrypted_email, email_iv, email_lookup_hash
# 2. For each user, encrypt the email, compute HMAC hash, and store in new columns
# 3. Validate uniqueness of email_lookup_hash
# 4. Log all actions/errors to migration_log
# 5. Drop old email column after migration is validated (manual step)

# Example migration logic (not executable)
# with engine.connect() as conn:
#     # Add columns if not present
#     # ...
#     for user in conn.execute(users.select()):
#         try:
#             encrypted, iv = encrypt_email(user.email, key)
#             lookup_hash = hmac_email(user.email, hmac_key)
#             if not DRY_RUN:
#                 conn.execute(users.update().where(users.c.id == user.id).values(
#                     encrypted_email=encrypted,
#                     email_iv=iv,
#                     email_lookup_hash=lookup_hash,
#                 ))
#             log_migration(conn, user.id, "migrate_email", "success")
#         except Exception as e:
#             log_migration(conn, user.id, "migrate_email", "failure", str(e))
#     # Validate uniqueness
#     # ...
#     # conn.execute("ALTER TABLE users ADD UNIQUE (email_lookup_hash)")
#     # conn.execute("ALTER TABLE users DROP COLUMN email")

# Document all steps and validate in staging before production.
