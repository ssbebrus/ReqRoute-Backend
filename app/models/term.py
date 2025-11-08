from app.db.session import Base
import enum
from datetime import date
from sqlalchemy import Column, Integer, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column

class SeasonEnum(str, enum.Enum):
    autumn = "autumn"
    spring = "spring"

class Term(Base):
    __tablename__ = "terms"

    start_date: Mapped[date | None]
    end_date: Mapped[date | None]
    year: Mapped[int]
    season: Mapped[SeasonEnum] = mapped_column(Enum(SeasonEnum), nullable=False)
