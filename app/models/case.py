from app.db.session import Base
import enum
from sqlalchemy import Integer, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

class CaseStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    voting = "voting in progress"
    done = "done"

class Case(Base):
    __tablename__ = "cases"

    title: Mapped[str]
    description: Mapped[Text | None]
    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.draft)
