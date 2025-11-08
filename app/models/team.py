from sqlalchemy.testing.schema import mapped_column

from app.db.session import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped


class Team(Base):
    __tablename__ = "teams"

    title: Mapped[str]
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    workspace_link: Mapped[str]
    final_mark = Mapped[int | 0]