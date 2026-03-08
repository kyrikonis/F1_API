from datetime import date

from pydantic import BaseModel, Field


class DriverBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=3, description="3-letter driver code, e.g. VER")
    forename: str = Field(..., max_length=100)
    surname: str = Field(..., max_length=100)
    nationality: str = Field(..., max_length=100)
    date_of_birth: date | None = None
    number: int | None = Field(None, ge=0, le=99, description="Permanent driver number")
    team_id: int | None = Field(None, description="Current team ID")
    active: bool = True


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    code: str | None = Field(None, min_length=2, max_length=3)
    forename: str | None = Field(None, max_length=100)
    surname: str | None = Field(None, max_length=100)
    nationality: str | None = Field(None, max_length=100)
    date_of_birth: date | None = None
    number: int | None = Field(None, ge=0, le=99)
    team_id: int | None = None
    active: bool | None = None


class DriverResponse(DriverBase):
    id: int

    model_config = {"from_attributes": True}
