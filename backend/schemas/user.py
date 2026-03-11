from pydantic import BaseModel, ConfigDict

"""
Pydantic schemas for the User resource.

These schemas validate request bodies and shape response payloads
for the /api/v1/users/* endpoints.
"""

from pydantic import BaseModel

from typing import Optional

# --- Request schemas -------------------------------------------------------

class UserCreate(BaseModel):
    """POST /users/register — required fields to create an account."""
    display_name: str
    email: str
    password: str
    zip_code: Optional[str] = None

class UserLogin(BaseModel):
    """POST /users/login — email + password to get a JWT back."""
    email: str
    password: str

class UserPrefsUpdate(BaseModel):
    """PUT /users/{id}/preferences — all fields optional, only set what changes."""
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    alert_types: Optional[list[str]] = None
    notify_severity: Optional[str] = None
    device_token: Optional[str] = None

class NotificationSettingsUpdate(BaseModel):
    """PUT /users/notifications — notification preferences."""
    notify_severity: Optional[str] = None
    device_token: Optional[str] = None

# --- Response schemas ------------------------------------------------------

class TokenOut(BaseModel):
    """Response from POST /users/login — the JWT access token."""
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    """Standard user response — never expose password_hash."""
    id: int
    display_name: Optional[str] = None
    email: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    alert_types: Optional[str] = None
    notify_severity: Optional[str] = None
    created_at: str
    model_config = ConfigDict(from_attributes=True)

    class Config:
        from_attributes = True

class NotificationSettingsOut(BaseModel):
    """Response for GET /users/notifications."""
    notify_severity: Optional[str] = None
    device_token: Optional[str] = None

    class Config:
        from_attributes = True
