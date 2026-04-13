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
import logging
<<<<<<< HEAD
=======
import time
from collections import defaultdict
>>>>>>> QuiV2

from fastapi import APIRouter, Depends, HTTPException, Request

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session
from sqlalchemy import or_

<<<<<<< HEAD
from db.database import get_db, db_write
from db.models import User
from db.normalization import get_effective_user_coords, get_user_alert_types, set_user_alert_types, upsert_zip_geo
from config.settings import settings
from auth.security import hash_password, verify_password, create_access_token, get_current_user, encrypt_email, decrypt_email, email_hmac
from logging_utils import log_event
=======
from db.database import get_db
from db.models import User, SavedDestination
from auth.security import hash_password, verify_password, create_access_token, get_current_user, encrypt_email, decrypt_email, email_hmac


# ---------------------------------------------------------------------------
# Simple in-memory rate limiter for auth endpoints
# ---------------------------------------------------------------------------
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_WINDOW = 60       # seconds
_RATE_LIMIT_MAX_REQUESTS = 10  # max attempts per window


def _check_rate_limit(request: Request) -> None:
    """Raise 429 if the client IP exceeds the auth rate limit."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    # Prune old entries outside the window
    timestamps = _rate_limit_store[client_ip]
    _rate_limit_store[client_ip] = [t for t in timestamps if now - t < _RATE_LIMIT_WINDOW]
    if len(_rate_limit_store[client_ip]) >= _RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
        )
    _rate_limit_store[client_ip].append(now)
>>>>>>> QuiV2
from schemas.user import (
    UserCreate,
    UserLogin,
    UserPrefsUpdate,
    DeviceTokenUpdate,
    UserOut,
    TokenOut,
    NotificationSettingsUpdate,
    NotificationSettingsOut,
    SavedDestinationCreate,
    SavedDestinationOut,
)

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


def _user_out_with_email(user: User) -> UserOut:
    """Build a UserOut response with email decrypted from email_encrypted."""
    user_out = UserOut.model_validate(user)
    if user.email_encrypted:
        user_out.email = decrypt_email(user.email_encrypted)
    elif user.email:
        user_out.email = user.email  # fallback for legacy plaintext records
    else:
        logger.warning("User %s has no email_encrypted or email on record", user.id)
    return user_out


def _set_user_out_alert_types(db: Session, user_out: UserOut, user: User) -> None:
    if settings.USERS_USE_PREFERENCE_JUNCTION_TABLE:
        user_out.alert_types = json.dumps(get_user_alert_types(db, user))
        return
    user_out.alert_types = user.alert_types


# ---------------------------------------------------------------------------
# Public endpoints (no JWT required)
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserOut)
def register_user(body: UserCreate, request: Request, db: Session = Depends(get_db)):
    """
    Create a new user account with encrypted email and HMAC lookup.
    - Checks that the email_hmac is not already taken.
    - Hashes the password with bcrypt (see auth/security.py).
    - Stores the user row in the 'users' table.
    - Returns the created user (without password_hash).
    """
    _check_rate_limit(request)
    hmac_val = email_hmac(body.email)
    existing = db.query(User).filter(
        or_(User.email_hmac == hmac_val, User.email == body.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        display_name=body.display_name,
<<<<<<< HEAD
        # New records should avoid plaintext email persistence.
=======
>>>>>>> QuiV2
        email=None,
        email_encrypted=encrypt_email(body.email),
        email_hmac=hmac_val,
        password_hash=hash_password(body.password),
        zip_code=body.zip_code,
    )
    with db_write(db):
        db.add(user)
    db.refresh(user)
    # Return user with decrypted email for API response
    user_out = UserOut.model_validate(user)
    user_out.email = body.email
    return user_out


@router.post("/login", response_model=TokenOut)
def login_user(body: UserLogin, request: Request, db: Session = Depends(get_db)):
    """
    Authenticate with email + password, receive a JWT.
    - Look up user by email_hmac in the database.
    - Verify the password against the stored bcrypt hash.
    - Create a JWT with the user's ID in the "sub" claim.
    - Return { access_token, token_type: "bearer" }.
    """
    _check_rate_limit(request)
    hmac_val = email_hmac(body.email)
    # Prefer HMAC lookup; allow plaintext fallback only for legacy rows.
    user = db.query(User).filter(User.email_hmac == hmac_val).first()
    if not user:
        user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(data={"sub": str(user.id)})
    return TokenOut(access_token=token)


# ---------------------------------------------------------------------------
# Protected endpoints (JWT required)
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserOut)
def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the profile of the currently authenticated user."""
    user_out = _user_out_with_email(current_user)
    _set_user_out_alert_types(db, user_out, current_user)
    lat, lon = get_effective_user_coords(db, current_user)
    user_out.latitude = lat
    user_out.longitude = lon
    return user_out


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
    user_out = _user_out_with_email(current_user)
    _set_user_out_alert_types(db, user_out, current_user)
    lat, lon = get_effective_user_coords(db, current_user)
    user_out.latitude = lat
    user_out.longitude = lon
    return user_out


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
    changed_fields: list[str] = []
    if body.zip_code is not None:
        user.zip_code = body.zip_code
        changed_fields.append("zip_code")
        if settings.GEO_USE_ZIP_LOOKUP:
            lat, lon = get_effective_user_coords(db, user)
            if lat is not None and lon is not None and body.latitude is None and body.longitude is None:
                user.latitude = lat
                user.longitude = lon
    if body.latitude is not None:
        user.latitude = body.latitude
        changed_fields.append("latitude")
    if body.longitude is not None:
        user.longitude = body.longitude
        changed_fields.append("longitude")
    if body.alert_types is not None:
        set_user_alert_types(
            db,
            user,
            body.alert_types,
            dual_write_legacy=settings.NORMALIZATION_DUAL_WRITE_LEGACY_JSON,
        )
        changed_fields.append("alert_types")
    if body.notify_severity is not None:
        user.notify_severity = body.notify_severity
        changed_fields.append("notify_severity")
    if body.notify_push is not None:
        user.notify_push = body.notify_push
        changed_fields.append("notify_push")
    if body.notify_email is not None:
        user.notify_email = body.notify_email
        changed_fields.append("notify_email")
    if body.notify_sms is not None:
        user.notify_sms = body.notify_sms
        changed_fields.append("notify_sms")
    if body.device_token is not None:
        user.device_token = body.device_token
        changed_fields.append("device_token")

    with db_write(db):
        if body.zip_code is not None and user.latitude is not None and user.longitude is not None:
            upsert_zip_geo(db, user.zip_code, user.latitude, user.longitude)
    db.refresh(user)
    log_event(
        logger,
        "users.preferences_updated",
        user_id=user.id,
        changed_fields=changed_fields,
    )
    user_out = _user_out_with_email(user)
    _set_user_out_alert_types(db, user_out, user)
    lat, lon = get_effective_user_coords(db, user)
    user_out.latitude = lat
    user_out.longitude = lon
    return user_out


@router.post("/{user_id}/device-token", response_model=NotificationSettingsOut)
def register_device_token(
    user_id: int,
    body: DeviceTokenUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register or refresh the current user's push notification token."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot modify another user's device token")

    current_user.device_token = body.device_token
    with db_write(db):
        pass
    db.refresh(current_user)
    log_event(logger, "users.device_token_registered", user_id=current_user.id)
    return NotificationSettingsOut(
        notify_severity=current_user.notify_severity,
        device_token=current_user.device_token,
    )


@router.post("/{user_id}/device-token/revoke", response_model=NotificationSettingsOut)
def revoke_device_token(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clear the stored push notification token (e.g., on logout)."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot modify another user's device token")

    current_user.device_token = None
    with db_write(db):
        pass
    db.refresh(current_user)
    log_event(logger, "users.device_token_revoked", user_id=current_user.id)
    return NotificationSettingsOut(
        notify_severity=current_user.notify_severity,
        device_token=current_user.device_token,
    )


@router.get("/notifications", response_model=NotificationSettingsOut)
def get_notifications(current_user: User = Depends(get_current_user)):
    """Get the current user's notification settings."""
    return NotificationSettingsOut(
        notify_severity=current_user.notify_severity,
        notify_push=current_user.notify_push,
        notify_email=current_user.notify_email,
        notify_sms=current_user.notify_sms,
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
    if body.notify_push is not None:
        current_user.notify_push = body.notify_push
    if body.notify_email is not None:
        current_user.notify_email = body.notify_email
    if body.notify_sms is not None:
        current_user.notify_sms = body.notify_sms
    if body.device_token is not None:
        current_user.device_token = body.device_token

    with db_write(db):
        pass
    db.refresh(current_user)
    return NotificationSettingsOut(
        notify_severity=current_user.notify_severity,
        notify_push=current_user.notify_push,
        notify_email=current_user.notify_email,
        notify_sms=current_user.notify_sms,
        device_token=current_user.device_token,
    )


# ---------------------------------------------------------------------------
# Saved destinations (JWT required)
# ---------------------------------------------------------------------------

@router.get("/destinations", response_model=list[SavedDestinationOut])
def list_destinations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all saved destinations for the current user."""
    return (
        db.query(SavedDestination)
        .filter(SavedDestination.user_id == current_user.id)
        .order_by(SavedDestination.created_at.desc())
        .all()
    )


@router.post("/destinations", response_model=SavedDestinationOut)
def save_destination(
    body: SavedDestinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a travel destination for the current user."""
    existing = (
        db.query(SavedDestination)
        .filter_by(user_id=current_user.id, city=body.city, state=body.state)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Destination already saved")

    dest = SavedDestination(
        user_id=current_user.id,
        city=body.city,
        state=body.state,
        zip_code=body.zip_code,
        latitude=body.latitude,
        longitude=body.longitude,
    )
    db.add(dest)
    db.commit()
    db.refresh(dest)
    return dest


@router.delete("/destinations/{dest_id}")
def delete_destination(
    dest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a saved destination."""
    dest = (
        db.query(SavedDestination)
        .filter_by(id=dest_id, user_id=current_user.id)
        .first()
    )
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    db.delete(dest)
    db.commit()
    return {"detail": "Destination removed"}
