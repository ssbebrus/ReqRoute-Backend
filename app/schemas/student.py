from pydantic import BaseModel, ConfigDict


class StudentBase(BaseModel):
    full_name: str

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass

class StudentRead(StudentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)