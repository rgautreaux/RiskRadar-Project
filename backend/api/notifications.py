from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from auth.security import get_current_user
from db.database import get_db, db_write
from db.models import Alert, User, NotificationDispatchLog
from db.normalization import get_user_alert_types
from logging_utils import log_event
from notifications.provider import get_notification_provider

router = APIRouter(prefix="/notifications", tags=["Notifications"])
logger = logging.getLogger(__name__)

_SEVERITY_ORDER = {
    "low": 0,
    "moderate": 1,
    "high": 2,
    "critical": 3,
}


def _user_wants_alert(db: Session, user: User, alert: Alert) -> bool:
    """Return True when a user's saved preferences include the given alert."""
    if not user.device_token:
        return False

    preferred_types = [item.lower() for item in get_user_alert_types(db, user)]
    if "all" not in preferred_types and alert.alert_type.lower() not in preferred_types:
        return False

    user_floor = _SEVERITY_ORDER.get((user.notify_severity or "high").lower(), 2)
    alert_level = _SEVERITY_ORDER.get((alert.severity or "moderate").lower(), 1)
    return alert_level >= user_floor


@router.post("/alerts/{alert_id}/notify-subscribers")
def notify_subscribers_for_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Notification dispatch stub: selects subscribers and reports candidates.

    The endpoint is auth-gated and intentionally does not send provider pushes yet;
    it prepares safe recipient selection so mobile/backend teams can integrate later.
    """
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    users = db.query(User).filter(User.device_token.isnot(None)).all()
    recipients = [u for u in users if _user_wants_alert(db, u, alert)]
    provider = get_notification_provider()

    title = f"RiskRadar: {alert.title}"
    body = (alert.description or f"{alert.alert_type} alert from {alert.source}")[:200]

    sent_count = 0
    for recipient in recipients:
        if recipient.device_token and provider.send(recipient.device_token, title, body):
            sent_count += 1

    failed_count = max(len(recipients) - sent_count, 0)
    status = "success"
    if len(recipients) == 0:
        status = "no_recipients"
    elif sent_count == 0:
        status = "failed"
    elif failed_count > 0:
        status = "partial"

    dispatch_log = NotificationDispatchLog(
        alert_id=alert.id,
        initiated_by_user_id=current_user.id,
        provider=provider.name,
        recipients_total=len(recipients),
        sent_count=sent_count,
        failed_count=failed_count,
        status=status,
    )
    with db_write(db):
        db.add(dispatch_log)

    log_event(
        logger,
        "notifications.dispatch",
        alert_id=alert.id,
        initiated_by=current_user.id,
        provider=provider.name,
        candidates=len(recipients),
        sent=sent_count,
        failed=failed_count,
        status=status,
    )

    return {
        "status": "queued_stub",
        "alert_id": alert.id,
        "recipient_count": len(recipients),
        "recipient_user_ids": [u.id for u in recipients],
        "provider": provider.name,
        "sent_count": sent_count,
        "failed_count": failed_count,
        "dispatch_status": status,
    }
