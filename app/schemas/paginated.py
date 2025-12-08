from pydantic import BaseModel, ConfigDict
from typing import List, Generic, TypeVar

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: List[T]

    model_config = ConfigDict(from_attributes=True)