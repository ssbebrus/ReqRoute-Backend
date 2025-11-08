from typing import Optional
from pydantic import BaseModel
from app.models.case import CaseStatus

class CaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: CaseStatus = CaseStatus.draft

class CaseCreate(CaseBase):
    pass

class CaseUpdate(CaseBase):
    pass

class CaseRead(CaseBase):
    id: int

    class Config:
        from_attributes = True