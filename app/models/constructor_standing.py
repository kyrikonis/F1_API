from sqlalchemy import Column, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class ConstructorStanding(Base):
    __tablename__ = "constructor_standings"

    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    final_position = Column(Integer, nullable=False)
    final_points = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("season", "team_id", name="uq_season_team"),
    )

    team = relationship("Team")
