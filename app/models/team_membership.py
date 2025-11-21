from app.db.session import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class TeamMembership(Base):
    __tablename__ = "team_memberships"

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    role: Mapped[str | None]
    group: Mapped[str]

    student = relationship("Student", back_populates="team_memberships")
    team = relationship("Team", back_populates="team_memberships")
