from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.term import SeasonEnum
from datetime import date

class TermBase(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    year: int
    season: SeasonEnum

class TermCreate(TermBase):
    pass

class TermUpdate(TermBase):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    year: Optional[int] = None
    season: Optional[SeasonEnum] = None

class TermRead(TermBase):
    id: int

    model_config = ConfigDict(from_attributes=True)