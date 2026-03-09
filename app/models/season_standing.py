from sqlalchemy import Column, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class SeasonStanding(Base):
    __tablename__ = "season_standings"

    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    final_position = Column(Integer, nullable=False)
    final_points = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("season", "driver_id", name="uq_season_driver"),
    )

    driver = relationship("Driver")
    team = relationship("Team")
