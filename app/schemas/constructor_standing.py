from pydantic import BaseModel, Field


class ConstructorStandingBase(BaseModel):
    season: int = Field(..., ge=1950, le=2100)
    team_id: int
    final_position: int = Field(..., ge=1)
    final_points: float = Field(..., ge=0)

class ConstructorStandingCreate(ConstructorStandingBase):
    pass

class ConstructorStandingResponse(ConstructorStandingBase):
    id: int

    model_config = {"from_attributes": True}
