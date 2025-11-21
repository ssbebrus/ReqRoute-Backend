from app.db.session import Base
from sqlalchemy.orm import relationship, Mapped


class Student(Base):
    __tablename__ = "students"

    full_name: Mapped[str]
    team_memberships = relationship("TeamMembership", back_populates="student")
