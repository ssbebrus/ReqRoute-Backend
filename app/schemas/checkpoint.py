import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CheckpointBase(BaseModel):
    team_id: int
    number: int
    date: Optional[datetime.date] = None
    project_state: Optional[str] = None
    mark: int
    video_link: Optional[str] = None
    presentation_link: Optional[str] = None
    university_mark: Optional[int] = None
    university_comment: Optional[str] = None

class CheckpointCreate(CheckpointBase):
    pass

class CheckpointUpdate(BaseModel):
    date: Optional[datetime.date] = None
    project_state: Optional[str] = None
    mark: Optional[int] = None
    video_link: Optional[str] = None
    presentation_link: Optional[str] = None
    university_mark: Optional[int] = None
    university_comment: Optional[str] = None

class CheckpointRead(CheckpointBase):
    id: int

    model_config = ConfigDict(from_attributes=True)