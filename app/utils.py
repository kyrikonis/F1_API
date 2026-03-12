from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.models.race import Race
from app.models.team import Team


def resolve_driver(identifier: str, db: Session) -> Driver:
    """to get a driver by database ID, 3 letter code or name"""
    if identifier.isdigit():
        driver = db.get(Driver, int(identifier))
    else:
        driver = db.query(Driver).filter(Driver.code == identifier.upper()).first()
        if not driver:
            driver = (
                db.query(Driver)
                .filter(
                    Driver.forename.ilike(f"%{identifier}%")
                    | Driver.surname.ilike(f"%{identifier}%")
                )
                .first()
            )
    if not driver:
        raise HTTPException(status_code=404, detail=f"Driver '{identifier}' not found")
    return driver


def resolve_team(identifier: str, db: Session) -> Team:
    """getting a team by database ID or name  (red_bull, ferrari, etc.)"""
    if identifier.isdigit():
        team = db.get(Team, int(identifier))
    else:
        team = (
            db.query(Team)
            .filter(Team.name.ilike(f"%{identifier}%"))
            .first()
        )
    if not team:
        raise HTTPException(status_code=404, detail=f"Team '{identifier}' not found")
    return team


def resolve_race(identifier: str, db: Session) -> Race:
    """getting a race by database ID or name ('Monaco', 'British Grand Prix')."""
    if identifier.isdigit():
        race = db.get(Race, int(identifier))
    else:
        race = (
            db.query(Race)
            .filter(Race.name.ilike(f"%{identifier}%"))
            .first()
        )
    if not race:
        raise HTTPException(status_code=404, detail=f"Race '{identifier}' not found")
    return race
