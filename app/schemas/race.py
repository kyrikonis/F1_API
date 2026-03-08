from datetime import date

from pydantic import BaseModel, Field


class RaceBase(BaseModel):
    year: int = Field(..., ge=1950, le=2100, description="Season year")
    round: int = Field(..., ge=1, description="Round number within the season")
    name: str = Field(..., max_length=200, description="Grand Prix name, e.g. British Grand Prix")
    circuit_name: str = Field(..., max_length=200)
    circuit_location: str | None = Field(None, max_length=200)
    country: str = Field(..., max_length=100)
    date: date


class RaceCreate(RaceBase):
    pass


class RaceUpdate(BaseModel):
    year: int | None = Field(None, ge=1950, le=2100)
    round: int | None = Field(None, ge=1)
    name: str | None = Field(None, max_length=200)
    circuit_name: str | None = Field(None, max_length=200)
    circuit_location: str | None = None
    country: str | None = Field(None, max_length=100)
    date: date | None = None


class RaceResponse(RaceBase):
    id: int

    model_config = {"from_attributes": True}
