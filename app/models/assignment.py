from app.db.session import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped


class Assignment(Base):
    __tablename__ = "assignments"

    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    text: Mapped[str]
    completed: Mapped[bool | None]

    meeting = relationship("Meeting", back_populates="assignments")