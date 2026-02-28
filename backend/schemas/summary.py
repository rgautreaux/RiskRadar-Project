from pydantic import BaseModel
from typing import Optional


class SummaryOut(BaseModel):
    id: int
    title: str
    content: str
    summary_type: str
    region: Optional[str] = None
    generated_at: str
    model_used: Optional[str] = None

    model_config = {"from_attributes": True, "protected_namespaces": ()}
