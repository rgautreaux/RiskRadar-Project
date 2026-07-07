"""
RiskRadar - Password hashing & JWT token utilities.

This module provides:
  - bcrypt-based password hashing (replacing the old SHA-256 approach)
  - JWT access-token creation and verification

HOW IT CONNECTS:
  - The /users/register endpoint calls hash_password() before storing.
  - The /users/login endpoint calls verify_password() to check credentials,
    then create_access_token() to issue a JWT.
  - Protected routes use get_current_user() as a FastAPI dependency
    to decode the JWT and load the User from the database.

CONFIGURATION:
  - JWT_SECRET_KEY must be set in your .env file (see .env.example).
  - JWT_ALGORITHM defaults to HS256.
  - ACCESS_TOKEN_EXPIRE_MINUTES defaults to 60 (1 hour).
"""

from datetime import datetime, timedelta, timezone


from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from config.settings import settings
from db.database import get_db
from db.models import User
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes, hmac
from cryptography.hazmat.backends import default_backend
import base64
# ---------------------------------------------------------------------------
# AES Email Encryption/Decryption & HMAC for lookup
# ---------------------------------------------------------------------------
def _derive_email_aes_key() -> bytes:
    """
    Derive a fixed 32-byte AES key for email encryption from JWT_SECRET_KEY.

    This avoids invalid AES key lengths when JWT_SECRET_KEY is shorter than
    32 characters by always producing a 32-byte SHA-256 digest.
    """
    secret_bytes = settings.JWT_SECRET_KEY.encode("utf-8")
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(secret_bytes)
    return digest.finalize()  # 32 bytes

_EMAIL_AES_KEY = _derive_email_aes_key()  # Always a valid 32-byte AES key
_LEGACY_EMAIL_AES_IV = b"RiskRadarEmailIV"  # 16 bytes — kept only for decrypting old records

def encrypt_email(email: str) -> str:
    """Encrypt an email address using AES-CBC with a random IV.

    The IV is prepended to the ciphertext so each encryption produces
    unique output even for identical plaintext.
    """
    import os
    iv = os.urandom(16)
    backend = default_backend()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(email.encode("utf-8")) + padder.finalize()
    cipher = Cipher(algorithms.AES(_EMAIL_AES_KEY), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + ct).decode("utf-8")

def decrypt_email(encrypted_email: str) -> str:
    """Decrypt an AES-encrypted email address.

    Supports both new format (random IV prepended) and legacy format
    (fixed IV, shorter ciphertext).
    """
    backend = default_backend()
    raw = base64.b64decode(encrypted_email)
    # New format: first 16 bytes are the random IV, rest is ciphertext.
    # Legacy format: entire blob is ciphertext encrypted with the fixed IV.
    # AES-CBC ciphertext is always a multiple of 16. If raw length > 16 and
    # the portion after the first 16 bytes is also a valid block size, treat
    # it as new format. Legacy emails (≤ 64 chars) produce ≤ 64 bytes of
    # ciphertext, so total raw length for new format is always > 16.
    if len(raw) > 32:
        # New format: IV + ciphertext (ciphertext is at least one block)
        iv = raw[:16]
        ct = raw[16:]
    else:
        # Legacy format (fixed IV)
        iv = _LEGACY_EMAIL_AES_IV
        ct = raw
    cipher = Cipher(algorithms.AES(_EMAIL_AES_KEY), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ct) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data.decode("utf-8")

def email_hmac(email: str) -> str:
    """Generate an HMAC (SHA256) of the email for uniqueness lookup."""
    h = hmac.HMAC(_EMAIL_AES_KEY, hashes.SHA256(), backend=default_backend())
    h.update(email.encode("utf-8"))
    return base64.b64encode(h.finalize()).decode("utf-8")

# ---------------------------------------------------------------------------
# Password hashing - bcrypt via passlib
# ---------------------------------------------------------------------------
# CryptContext handles hashing + verification. "bcrypt" is the recommended
# scheme; deprecated="auto" means older hashes are still verifiable but new
# hashes always use bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password with bcrypt. Used during registration."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a bcrypt hash. Used during login."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT token creation & verification
# ---------------------------------------------------------------------------
# OAuth2PasswordBearer tells FastAPI where the client sends the token.
# tokenUrl points to the login endpoint so Swagger UI knows where to
# authenticate.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login", auto_error=True)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login", auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a signed JWT.

    Args:
        data: payload dict - must include "sub" (the user ID).
        expires_delta: optional custom lifetime; defaults to
                       ACCESS_TOKEN_EXPIRE_MINUTES from settings.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency - decode the Bearer token, look up the user.

    Usage in a route:
        @router.get("/me")
        def me(user: User = Depends(get_current_user)):
            return user

    Raises HTTPException 401 if the token is missing, expired, or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception
    user = db.query(User).filter(User.id == uid).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> User | None:
    """Best-effort auth dependency for endpoints that support guest access."""
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    return db.query(User).filter(User.id == int(user_id)).first()
