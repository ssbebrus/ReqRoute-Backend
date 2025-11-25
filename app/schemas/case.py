from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.case import CaseStatus

class CaseBase(BaseModel):
    term_id: int
    user_id: int
    title: str
    description: Optional[str] = None
    status: CaseStatus = CaseStatus.draft

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CaseStatus] = None

class CaseRead(CaseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)