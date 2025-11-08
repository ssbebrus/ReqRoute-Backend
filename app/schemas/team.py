from typing import Optional
from pydantic import BaseModel

class TeamBase(BaseModel):
    title: str
    case_id: int
    workspace_link: Optional[str] = None
    final_mark: Optional[int] = 0

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    pass

class TeamRead(TeamBase):
    id: int

    class Config:
        from_attributes = True