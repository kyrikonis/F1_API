from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    nationality = Column(String(100), nullable=False)
    base = Column(String(200))
    founded_year = Column(Integer)
    championships = Column(Integer, default=0)
    active = Column(Boolean, default=True)

    drivers = relationship("Driver", back_populates="team")
    results = relationship("Result", back_populates="team")
