from app.db.session import Base
from sqlalchemy import Column, Integer, String


class Student(Base):
    __tablename__ = "Students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)