from typing import Optional
from pydantic import BaseModel, ConfigDict


class MeetingUserBase(BaseModel):
    meeting_id: int
    user_id: int

class MeetingUserCreate(MeetingUserBase):
    pass

class MeetingUserUpdate(BaseModel):
    meeting_id: Optional[int] = None
    user_id: Optional[int] = None

class MeetingUserRead(MeetingUserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)