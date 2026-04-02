"""
Migration Script: Encrypt and HMAC Existing User Emails

This script migrates all users in the database:
- Encrypts the plaintext email into email_encrypted
- Computes HMAC for email_hmac
- Sets legacy email field to None (optional, for privacy)
- Logs all actions to MigrationLog

Run this script in a safe environment after backing up the database.
"""

from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import User, MigrationLog
from auth.security import encrypt_email, email_hmac
from datetime import datetime

def migrate_emails():
    db: Session = SessionLocal()
    users = db.query(User).filter(User.email != None).all()
    for user in users:
        try:
            orig_email = user.email
            user.email_encrypted = encrypt_email(orig_email)
            user.email_hmac = email_hmac(orig_email)
            user.email = None  # Optionally clear legacy field
            db.add(MigrationLog(
                timestamp=datetime.utcnow(),
                user_id=user.id,
                action="email_encryption",
                status="success",
                error_message=None
            ))
        except Exception as e:
            db.add(MigrationLog(
                timestamp=datetime.utcnow(),
                user_id=user.id,
                action="email_encryption",
                status="error",
                error_message=str(e)
            ))
    db.commit()
    db.close()

if __name__ == "__main__":
    migrate_emails()
    print("Migration complete.")
