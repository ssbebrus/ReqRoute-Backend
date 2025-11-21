from app.db.session import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped


class Team(Base):
    __tablename__ = "teams"

    title: Mapped[str]
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    workspace_link: Mapped[str | None]
    final_mark: Mapped[int] = mapped_column(default=0)

    team_memberships = relationship("TeamMembership", back_populates="team")
    checkpoints = relationship("Checkpoint", back_populates="team")