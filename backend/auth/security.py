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
_EMAIL_AES_KEY = settings.JWT_SECRET_KEY[:32].encode("utf-8")  # Use a 32-byte key (for demo; use a dedicated key in prod)
_EMAIL_AES_IV = b"RiskRadarEmailIV!"  # 16 bytes (for demo; use random IV in prod)

def encrypt_email(email: str) -> str:
    """Encrypt an email address using AES-CBC."""
    backend = default_backend()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(email.encode("utf-8")) + padder.finalize()
    cipher = Cipher(algorithms.AES(_EMAIL_AES_KEY), modes.CBC(_EMAIL_AES_IV), backend=backend)
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(ct).decode("utf-8")

def decrypt_email(encrypted_email: str) -> str:
    """Decrypt an AES-encrypted email address."""
    backend = default_backend()
    cipher = Cipher(algorithms.AES(_EMAIL_AES_KEY), modes.CBC(_EMAIL_AES_IV), backend=backend)
    decryptor = cipher.decryptor()
    ct = base64.b64decode(encrypted_email)
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

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user
