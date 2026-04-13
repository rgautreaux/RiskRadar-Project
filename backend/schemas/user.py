from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal, Optional
from datetime import datetime
import re

ZIP_PATTERN = r"^\d{5}$"
SEVERITY_VALUES = ("low", "moderate", "high", "critical")
ALERT_TYPE_VALUES = ("all", "weather", "air_quality", "wildfire", "pollution", "earthquake")

# --- Request schemas -------------------------------------------------------

class UserCreate(BaseModel):
    """POST /users/register — required fields to create an account."""
    display_name: str = Field(min_length=1, max_length=120)
    email: str
    password: str = Field(min_length=6)
    zip_code: Optional[str] = Field(default=None, pattern=ZIP_PATTERN)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        # Keep validation lightweight and dependency-free for test environments.
        normalized = value.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", normalized):
            raise ValueError("Invalid email format")
        return normalized

class UserLogin(BaseModel):
    """POST /users/login — email + password to get a JWT back."""
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

class UserPrefsUpdate(BaseModel):
    """PUT /users/{id}/preferences — all fields optional, only set what changes."""
    zip_code: Optional[str] = Field(default=None, pattern=ZIP_PATTERN)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    alert_types: Optional[list[str]] = None
    notify_severity: Optional[Literal["low", "moderate", "high", "critical"]] = None
    notify_push: Optional[bool] = None
    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None
    device_token: Optional[str] = None

    @field_validator("alert_types")
    @classmethod
    def validate_alert_types(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        if value is None:
            return value
        invalid = [item for item in value if item not in ALERT_TYPE_VALUES]
        if invalid:
            raise ValueError(f"Invalid alert type(s): {', '.join(invalid)}")
        return value


class DeviceTokenUpdate(BaseModel):
    """POST /users/{id}/device-token — register a device token for push notifications."""
    device_token: str = Field(min_length=1, max_length=1000)

    @field_validator("device_token")
    @classmethod
    def token_not_blank(cls, value: str) -> str:
        token = value.strip()
        if not token:
            raise ValueError("device_token cannot be blank")
        return token

class NotificationSettingsUpdate(BaseModel):
    """PUT /users/notifications — notification preferences."""
    notify_severity: Optional[Literal["low", "moderate", "high", "critical"]] = None
    notify_push: Optional[bool] = None
    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None
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
    notify_push: Optional[bool] = None
    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None
    device_token: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NotificationSettingsOut(BaseModel):
    """Response for GET /users/notifications."""
    notify_severity: Optional[str] = None
    notify_push: Optional[bool] = None
    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None
    device_token: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
