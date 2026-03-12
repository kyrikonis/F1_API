from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_database
from app.models.race import Race
from app.schemas.race import RaceCreate, RaceResponse, RaceUpdate
from app.utils import resolve_race

router = APIRouter(prefix="/races", tags=["Races"])


@router.get("/", response_model=list[RaceResponse])
def list_races(
    year: int | None = Query(None, description="Filter by year"),
    country: str | None = Query(None, description="Filter by country"),
    circuit: str | None = Query(None, description="Search by circuit name"),
    db: Session = Depends(get_database),
):
    query = db.query(Race)
    if year:
        query = query.filter(Race.year == year)
    if country:
        query = query.filter(Race.country.ilike(f"%{country}%"))
    if circuit:
        query = query.filter(Race.circuit_name.ilike(f"%{circuit}%"))
    return query.order_by(Race.year, Race.round).all()


@router.get("/{race_ref}", response_model=RaceResponse)
def get_race(race_ref: str, db: Session = Depends(get_database)):
    """Fetch a race by numeric ID or name (e.g. 'Monaco' or 'British Grand Prix')."""
    return resolve_race(race_ref, db)


@router.post("/", response_model=RaceResponse, status_code=201, dependencies=[Security(require_api_key)])
def create_race(payload: RaceCreate, db: Session = Depends(get_database)):
    existing = db.query(Race).filter(
        Race.year == payload.year, Race.round == payload.round
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="A race for this year and round already exists")
    race = Race(**payload.model_dump())
    db.add(race)
    db.commit()
    db.refresh(race)
    return race


@router.patch("/{race_id}", response_model=RaceResponse, dependencies=[Security(require_api_key)])
def update_race(race_id: int, payload: RaceUpdate, db: Session = Depends(get_database)):
    race = db.get(Race, race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race cannot be found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(race, field, value)
    db.commit()
    db.refresh(race)
    return race


@router.delete("/{race_id}", status_code=204, dependencies=[Security(require_api_key)])
def delete_race(race_id: int, db: Session = Depends(get_database)):
    race = db.get(Race, race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race cannot be found")
    db.delete(race)
    db.commit()
