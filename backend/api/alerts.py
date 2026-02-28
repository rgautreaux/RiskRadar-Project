from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from db.models import Alert
from schemas.alert import AlertOut, AlertStats

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    alert_type: str | None = None,
    severity: str | None = None,
    source: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Alert)
    if alert_type:
        q = q.filter(Alert.alert_type == alert_type)
    if severity:
        q = q.filter(Alert.severity == severity)
    if source:
        q = q.filter(Alert.source == source)
    return q.order_by(Alert.fetched_at.desc()).offset(offset).limit(limit).all()


@router.get("/stats", response_model=AlertStats)
def alert_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Alert.id)).scalar()

    by_type = dict(
        db.query(Alert.alert_type, func.count(Alert.id))
        .group_by(Alert.alert_type)
        .all()
    )
    by_severity = dict(
        db.query(Alert.severity, func.count(Alert.id))
        .group_by(Alert.severity)
        .all()
    )

    return AlertStats(total=total or 0, by_type=by_type, by_severity=by_severity)


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
