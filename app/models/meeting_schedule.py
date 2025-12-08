from app.db.session import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, time


class MeetingSchedule(Base):
    __tablename__ = "meeting_schedules"

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    start_date: Mapped[date]
    day_of_week: Mapped[int]
    time: Mapped[time]
    interval_weeks: Mapped[int]
    active: Mapped[bool] = mapped_column(default=True)

    team = relationship("Team", back_populates="meeting_schedules")
    meetings = relationship("Meeting", back_populates="schedule")

