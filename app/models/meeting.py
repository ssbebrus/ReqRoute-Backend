from app.db.session import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime


class Meeting(Base):
    __tablename__ = "meetings"

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    previous_meeting_id: Mapped[int | None] = mapped_column(ForeignKey("meetings.id"))
    recording_link: Mapped[str | None]
    date_time: Mapped[datetime]
    summary: Mapped[str | None]

    users = relationship("MeetingUser", back_populates="meeting")
    assignments = relationship("Assignment", back_populates="meeting")

class MeetingUser(Base):
    __tablename__ = "meeting_users"

    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    meeting = relationship("Meeting", back_populates="users")
    user = relationship("User", back_populates="meetings")