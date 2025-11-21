from typing import Optional
from pydantic import BaseModel

class AssignmentBase(BaseModel):
    meeting_id: int
    text: str
    completed: Optional[bool] = None

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    completed: Optional[bool] = None
    text: Optional[str] = None

class AssignmentRead(AssignmentBase):
    id: int

    class Config:
        from_attributes = True