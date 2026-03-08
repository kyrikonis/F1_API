from pydantic import BaseModel, Field


class TeamBase(BaseModel):
    name: str = Field(..., max_length=100, description="Short constructor name, e.g. Red Bull")
    full_name: str = Field(..., max_length=200, description="Official full team name")
    nationality: str = Field(..., max_length=100)
    base: str | None = Field(None, max_length=200, description="Team headquarters location")
    founded_year: int | None = Field(None, ge=1900, le=2100)
    championships: int = Field(0, ge=0, description="Number of constructor championships won")
    active: bool = True


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    full_name: str | None = Field(None, max_length=200)
    nationality: str | None = Field(None, max_length=100)
    base: str | None = None
    founded_year: int | None = Field(None, ge=1900, le=2100)
    championships: int | None = Field(None, ge=0)
    active: bool | None = None


class TeamResponse(TeamBase):
    id: int

    model_config = {"from_attributes": True}
