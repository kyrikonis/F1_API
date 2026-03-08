from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    round = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    circuit_name = Column(String(200), nullable=False)
    circuit_location = Column(String(200))
    country = Column(String(100), nullable=False, index=True)
    date = Column(Date, nullable=False)

    results = relationship("Result", back_populates="race", cascade="all, delete-orphan")
