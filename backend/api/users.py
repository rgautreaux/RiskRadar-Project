"""
RiskRadar - User API endpoints.

Endpoints:
  POST /users/register          — Create a new account (public)
  POST /users/login             — Authenticate and receive a JWT (public)
  GET  /users/me                — Get current user profile (protected)
  GET  /users/{id}/preferences  — Get user preferences (protected)
  PUT  /users/{id}/preferences  — Update user preferences (protected)
  GET  /users/notifications     — Get notification settings (protected)
  PUT  /users/notifications     — Update notification settings (protected)

HOW IT CONNECTS TO THE DATABASE:
  - All endpoints receive a SQLAlchemy Session via Depends(get_db).
  - The Session talks to the SQLite file at backend/riskradar.db
    (configured in config/settings.py -> DB_PATH).
  - Protected routes use Depends(get_current_user) which decodes the
    JWT Bearer token from the Authorization header and loads the User.
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User
from auth.security import hash_password, verify_password, create_access_token, get_current_user, encrypt_email, decrypt_email, email_hmac
from schemas.user import (
    UserCreate,
    UserLogin,
    UserPrefsUpdate,
    UserOut,
    TokenOut,
    NotificationSettingsUpdate,
    NotificationSettingsOut,
)

router = APIRouter(prefix="/users", tags=["Users"])


def _user_out_with_email(user: User) -> UserOut:
    """Build a UserOut response with email decrypted from email_encrypted."""
    user_out = UserOut.model_validate(user)
    if user.email_encrypted:
        user_out.email = decrypt_email(user.email_encrypted)
    elif user.email:
        user_out.email = user.email  # fallback for legacy plaintext records
    return user_out


# ---------------------------------------------------------------------------
# Public endpoints (no JWT required)
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserOut)
def register_user(body: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account with encrypted email and HMAC lookup.
    - Checks that the email_hmac is not already taken.
    - Hashes the password with bcrypt (see auth/security.py).
    - Stores the user row in the 'users' table.
    - Returns the created user (without password_hash).
    """
    hmac_val = email_hmac(body.email)
    existing = db.query(User).filter(User.email_hmac == hmac_val).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        display_name=body.display_name,
        email=None,  # legacy field, not used
        email_encrypted=encrypt_email(body.email),
        email_hmac=hmac_val,
        password_hash=hash_password(body.password),
        zip_code=body.zip_code,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Return user with decrypted email for API response
    user_out = UserOut.model_validate(user)
    user_out.email = body.email
    return user_out


@router.post("/login", response_model=TokenOut)
def login_user(body: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate with email + password, receive a JWT.
    - Look up user by email_hmac in the database.
    - Verify the password against the stored bcrypt hash.
    - Create a JWT with the user's ID in the "sub" claim.
    - Return { access_token, token_type: "bearer" }.
    """
    hmac_val = email_hmac(body.email)
    user = db.query(User).filter(User.email_hmac == hmac_val).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(data={"sub": str(user.id)})
    return TokenOut(access_token=token)


# ---------------------------------------------------------------------------
# Protected endpoints (JWT required)
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return _user_out_with_email(current_user)


@router.get("/{user_id}/preferences", response_model=UserOut)
def get_preferences(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a user's preferences (location, alert types, severity filter).
    Only the user themselves can access their preferences.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot access another user's preferences")
    return _user_out_with_email(current_user)


@router.put("/{user_id}/preferences", response_model=UserOut)
def update_preferences(
    user_id: int,
    body: UserPrefsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update user preferences. Only set fields that are provided (non-None).

    Updatable fields: zip_code, latitude, longitude, alert_types,
    notify_severity, device_token.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot modify another user's preferences")

    user = current_user
    if body.zip_code is not None:
        user.zip_code = body.zip_code
    if body.latitude is not None:
        user.latitude = body.latitude
    if body.longitude is not None:
        user.longitude = body.longitude
    if body.alert_types is not None:
        user.alert_types = json.dumps(body.alert_types)
    if body.notify_severity is not None:
        user.notify_severity = body.notify_severity
    if body.device_token is not None:
        user.device_token = body.device_token

    db.commit()
    db.refresh(user)
    return _user_out_with_email(user)


@router.get("/notifications", response_model=NotificationSettingsOut)
def get_notifications(current_user: User = Depends(get_current_user)):
    """Get the current user's notification settings."""
    return NotificationSettingsOut(
        notify_severity=current_user.notify_severity,
        device_token=current_user.device_token,
    )


@router.put("/notifications", response_model=NotificationSettingsOut)
def update_notifications(
    body: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update notification preferences for the current user."""
    if body.notify_severity is not None:
        current_user.notify_severity = body.notify_severity
    if body.device_token is not None:
        current_user.device_token = body.device_token

    db.commit()
    db.refresh(current_user)
    return NotificationSettingsOut(
        notify_severity=current_user.notify_severity,
        device_token=current_user.device_token,
    )
