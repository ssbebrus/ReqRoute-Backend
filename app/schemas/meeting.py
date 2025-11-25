from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MeetingBase(BaseModel):
    team_id: int
    previous_meeting_id: Optional[int] = None
    recording_link: Optional[str] = None
    date_time: datetime
    summary: Optional[str] = None

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    summary: Optional[str] = None
    recording_link: Optional[str] = None
    date_time: Optional[datetime] = None

class MeetingRead(MeetingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)