from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.id"), nullable=False, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    grid = Column(Integer) # Starting grid position
    position = Column(Integer) # Finishing position, None if DNF
    points = Column(Float, default=0.0)
    laps = Column(Integer)
    status = Column(String(100), default="Finished")  # Finished / DNF reason
    fastest_lap_rank = Column(Integer) # ranking in terms of fasted laps, e.g. 1 = Fasted Lap of the race
    fastest_lap_time = Column(String(20)) # fastest lap time

    race = relationship("Race", back_populates="results")
    driver = relationship("Driver", back_populates="results")
    team = relationship("Team", back_populates="results")
