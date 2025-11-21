from app.db.session import Base
from sqlalchemy.orm import relationship, Mapped


class User(Base):
    __tablename__ = "users"

    full_name: Mapped[str]
    email: Mapped[str]
    password: Mapped[str]

    cases = relationship("Case", back_populates="user")
    meetings = relationship("MeetingUser", back_populates="user")