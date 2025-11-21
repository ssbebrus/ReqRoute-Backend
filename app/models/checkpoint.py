import datetime

from app.db.session import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    number: Mapped[int]
    date: Mapped[datetime.date | None]
    project_state: Mapped[str | None]
    mark: Mapped[int]
    video_link: Mapped[str | None]
    presentation_link: Mapped[str | None]
    university_mark: Mapped[int | None]
    university_comment: Mapped[str | None]

    team = relationship("Team", back_populates="checkpoints")