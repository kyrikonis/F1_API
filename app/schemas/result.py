from pydantic import BaseModel, Field


class ResultBase(BaseModel):
    race_id: int
    driver_id: int
    team_id: int
    grid: int | None = Field(None, ge=0, description="Starting grid position; 0 = pit lane start")
    position: int | None = Field(None, ge=1, description="Finishing position; null means DNF/DSQ")
    points: float = Field(0, ge=0)
    laps: int | None = Field(None, ge=0)
    status: str = Field("Finished", max_length=100)
    fastest_lap_rank: int | None = Field(None, ge=1)
    fastest_lap_time: str | None = Field(None, max_length=20, description="e.g. 1:23.456")


class ResultCreate(ResultBase):
    pass


class ResultUpdate(BaseModel):
    grid: int | None = Field(None, ge=0)
    position: int | None = Field(None, ge=1)
    points: float | None = Field(None, ge=0)
    laps: int | None = Field(None, ge=0)
    status: str | None = Field(None, max_length=100)
    fastest_lap_rank: int | None = Field(None, ge=1)
    fastest_lap_time: str | None = Field(None, max_length=20)


class ResultResponse(ResultBase):
    id: int

    model_config = {"from_attributes": True}
