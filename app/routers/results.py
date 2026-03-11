from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_database
from app.models.driver import Driver
from app.models.race import Race
from app.models.result import Result
from app.models.team import Team
from app.schemas.result import ResultCreate, ResultResponse, ResultUpdate

router = APIRouter(prefix="/results", tags=["Results"])


@router.get("/", response_model=list[ResultResponse])
def list_results(
    race_id: int | None = Query(None, description="Filter by race ID"),
    driver_id: int | None = Query(None, description="Filter by driver ID"),
    team_id: int | None = Query(None, description="Filter by team ID"),
    db: Session = Depends(get_database),
):
    query = db.query(Result)
    if race_id:
        query = query.filter(Result.race_id == race_id)
    if driver_id:
        query = query.filter(Result.driver_id == driver_id)
    if team_id:
        query = query.filter(Result.team_id == team_id)
    return query.order_by(Result.race_id, Result.position).all()


@router.get("/{result_id}", response_model=ResultResponse)
def get_result(result_id: int, db: Session = Depends(get_database)):
    result = db.get(Result, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.post("/", response_model=ResultResponse, status_code=201)
def create_result(payload: ResultCreate, db: Session = Depends(get_database)):
    if not db.get(Race, payload.race_id):
        raise HTTPException(status_code=404, detail=f"Race {payload.race_id} not found")
    if not db.get(Driver, payload.driver_id):
        raise HTTPException(status_code=404, detail=f"Driver {payload.driver_id} not found")
    if not db.get(Team, payload.team_id):
        raise HTTPException(status_code=404, detail=f"Team {payload.team_id} not found")

    duplicate = db.query(Result).filter(
        Result.race_id == payload.race_id,
        Result.driver_id == payload.driver_id,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Result already exists for this driver in this race")

    result = Result(**payload.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.patch("/{result_id}", response_model=ResultResponse)
def update_result(result_id: int, payload: ResultUpdate, db: Session = Depends(get_database)):
    result = db.get(Result, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(result, field, value)
    db.commit()
    db.refresh(result)
    return result


@router.delete("/{result_id}", status_code=204)
def delete_result(result_id: int, db: Session = Depends(get_database)):
    result = db.get(Result, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    db.delete(result)
    db.commit()
