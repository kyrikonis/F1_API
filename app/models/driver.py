from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, nullable=False, index=True)
    forename = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    nationality = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    number = Column(Integer)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    active = Column(Boolean, default=True)

    team = relationship("Team", back_populates="drivers")
    results = relationship("Result", back_populates="driver")
