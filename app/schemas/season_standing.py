from pydantic import BaseModel, Field

class SeasonStandingBase(BaseModel):
    season: int = Field(..., ge=1950, le=2100)
    driver_id: int
    team_id: int | None = None
    final_position: int = Field(..., ge=1)
    final_points: float = Field(..., ge=0)

class SeasonStandingCreate(SeasonStandingBase):
    pass

class SeasonStandingResponse(SeasonStandingBase):
    id: int

    model_config = {"from_attributes": True}
