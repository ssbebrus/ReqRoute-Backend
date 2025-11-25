from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    full_name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    full_name: Optional[str]
    email: Optional[str]

class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)