from typing import Optional
from pydantic import BaseModel

class TeamMembershipBase(BaseModel):
    student_id: int
    team_id: int
    role: Optional[str]
    group: str

class TeamMembershipCreate(TeamMembershipBase):
    pass

class TeamMembershipUpdate(BaseModel):
    student_id: Optional[int] = None
    team_id: Optional[int] = None
    role: Optional[str] = None
    group: Optional[str] = None

class TeamMembershipRead(TeamMembershipBase):
    id: int

    class Config:
        from_attributes = True