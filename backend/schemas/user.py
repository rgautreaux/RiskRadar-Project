from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    display_name: str
    email: str
    password: str
    zip_code: Optional[str] = None


class UserPrefsUpdate(BaseModel):
    zip_code: Optional[str] = None
    alert_types: Optional[list[str]] = None
    notify_severity: Optional[str] = None
    device_token: Optional[str] = None


class UserOut(BaseModel):
    id: int
    display_name: Optional[str] = None
    email: Optional[str] = None
    zip_code: Optional[str] = None
    alert_types: Optional[str] = None
    notify_severity: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True
