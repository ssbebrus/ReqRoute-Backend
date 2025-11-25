from typing import Optional
from pydantic import BaseModel, ConfigDict


class TeamBase(BaseModel):
    title: str
    case_id: int
    workspace_link: Optional[str] = None
    final_mark: Optional[int] = 0

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    title: Optional[str] = None
    case_id: Optional[int] = None
    workspace_link: Optional[str] = None
    final_mark: Optional[int] = None

class TeamRead(TeamBase):
    id: int

    model_config = ConfigDict(from_attributes=True)