from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
import datetime


class MeetingScheduleBase(BaseModel):
    team_id: int
    start_date: datetime.date
    day_of_week: int = Field(ge=0, le=6, description="0=Monday, 6=Sunday")
    time: datetime.time
    interval_weeks: int = Field(ge=1, le=2, description="1 or 2 weeks")
    active: bool = True


class MeetingScheduleCreate(MeetingScheduleBase):
    pass


class MeetingScheduleUpdate(BaseModel):
    start_date: Optional[datetime.date] = None
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    time: Optional[datetime.time] = None
    interval_weeks: Optional[int] = Field(None, ge=1, le=2)
    active: Optional[bool] = None


class MeetingScheduleRead(MeetingScheduleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

