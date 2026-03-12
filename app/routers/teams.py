from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_database
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamResponse, TeamUpdate

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/", response_model=list[TeamResponse])
def list_teams(
    active_only: bool = Query(False, description="Filter to active teams only"),
    db: Session = Depends(get_database),
):
    query = db.query(Team)
    if active_only:
        query = query.filter(Team.active == True)
    return query.order_by(Team.name).all()


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_database)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.post("/", response_model=TeamResponse, status_code=201, dependencies=[Security(require_api_key)])
def create_team(payload: TeamCreate, db: Session = Depends(get_database)):
    existing = db.query(Team).filter(Team.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="A team with this name already exists")
    team = Team(**payload.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.patch("/{team_id}", response_model=TeamResponse, dependencies=[Security(require_api_key)])
def update_team(team_id: int, payload: TeamUpdate, db: Session = Depends(get_database)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team cannot be found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(team, field, value)
    db.commit()
    db.refresh(team)
    return team


@router.delete("/{team_id}", status_code=204, dependencies=[Security(require_api_key)])
def delete_team(team_id: int, db: Session = Depends(get_database)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team cannot be found")
    db.delete(team)
    db.commit()
