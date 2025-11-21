from app.db.session import Base
import enum
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class CaseStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    voting = "voting in progress"
    done = "done"

class Case(Base):
    __tablename__ = "cases"

    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str]
    description: Mapped[str | None]
    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.draft)

    term = relationship("Term", back_populates="cases")
    user = relationship("User", back_populates="cases")
