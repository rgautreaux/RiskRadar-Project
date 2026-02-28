from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Summary
from schemas.summary import SummaryOut

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.get("", response_model=list[SummaryOut])
def list_summaries(
    summary_type: str | None = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    q = db.query(Summary)
    if summary_type:
        q = q.filter(Summary.summary_type == summary_type)
    return q.order_by(Summary.generated_at.desc()).limit(limit).all()


@router.get("/latest", response_model=SummaryOut | None)
def latest_summary(db: Session = Depends(get_db)):
    return db.query(Summary).order_by(Summary.generated_at.desc()).first()


@router.post("/generate", response_model=SummaryOut)
def generate_summary(db: Session = Depends(get_db)):
    from llm.summarizer import Summarizer

    summarizer = Summarizer()
    summary = summarizer.generate_daily_digest(db)
    if not summary:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No alerts to summarize")
    return summary
