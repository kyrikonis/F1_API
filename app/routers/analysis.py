from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_database
from app.models.driver import Driver
from app.models.race import Race
from app.models.result import Result
from app.models.team import Team

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("/standings/drivers/{year}")
def driver_standings(year: int, db: Session = Depends(get_database)):
    """World Drivers' Championship standings for a given season"""
    rows = (
        db.query(
            Driver.id,
            Driver.forename,
            Driver.surname,
            Driver.code,
            Team.name.label("team"),
            func.sum(Result.points).label("points"),
            func.count(Result.id).label("races"),
            func.sum(case((Result.position == 1,1), else_=0)).label("wins"),
            func.sum(case((Result.position <= 3,1), else_=0)).label("podiums"),
        )
        .join(Result, Result.driver_id == Driver.id)
        .join(Race, Race.id == Result.race_id)
        .outerjoin(Team, Team.id == Result.team_id)
        .filter(Race.year == year)
        .group_by(Driver.id, Team.name)
        .order_by(func.sum(Result.points).desc())
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail=f"No results found for {year}")

    return [
        {
            "position": idx + 1,
            "driver_id": row.id,
            "driver": f"{row.forename} {row.surname}",
            "code": row.code,
            "team": row.team,
            "points": row.points or 0,
            "races": row.races,
            "wins": row.wins or 0,
            "podiums": row.podiums or 0,
        }
        for idx, row in enumerate(rows)
    ]


@router.get("/standings/constructors/{year}")
def constructor_standings(year: int, db: Session = Depends(get_database)):
    """World Constructors' Championship standings for a given season"""
    rows = (
        db.query(
            Team.id,
            Team.name,
            Team.nationality,
            func.sum(Result.points).label("points"),
            func.count(Result.id).label("entries"),
            func.sum(case((Result.position == 1,1), else_=0)).label("wins"),
        )
        .join(Result, Result.team_id == Team.id)
        .join(Race, Race.id == Result.race_id)
        .filter(Race.year == year)
        .group_by(Team.id)
        .order_by(func.sum(Result.points).desc())
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail=f"No results found for {year}")

    return [
        {
            "position": idx + 1,
            "team_id": row.id,
            "team": row.name,
            "nationality": row.nationality,
            "points": row.points or 0,
            "entries": row.entries,
            "wins": row.wins or 0,
        }
        for idx, row in enumerate(rows)
    ]


@router.get("/leaderboard/wins")
def all_time_wins(
    limit: int = Query(10, ge=1, le=100, description="Number of drivers to return"),
    db: Session = Depends(get_database),
):
    """All time race wins leaderboard"""
    rows = (
        db.query(
            Driver.id,
            Driver.forename,
            Driver.surname,
            Driver.code,
            Driver.nationality,
            func.count(Result.id).label("wins"),
        )
        .join(Result, Result.driver_id ==Driver.id)
        .filter(Result.position == 1)
        .group_by(Driver.id)
        .order_by(func.count(Result.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "rank": idx + 1,
            "driver_id": row.id,
            "driver": f"{row.forename} {row.surname}",
            "code": row.code,
            "nationality": row.nationality,
            "wins": row.wins,
        }
        for idx, row in enumerate(rows)
    ]


@router.get("/drivers/{driver_id}/career")
def driver_career(driver_id: int, db: Session = Depends(get_database)):
    """Driver Career Summary: points, wins, podiums, and season breakdowns"""
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    totals = (
        db.query(
            func.count(Result.id).label("races"),
            func.sum(Result.points).label("points"),
            func.sum(case((Result.position == 1, 1), else_=0)).label("wins"),
            func.sum(case((Result.position <= 3, 1), else_=0)).label("podiums"),
            func.sum(case((Result.position <= 10, 1), else_=0)).label("points_finishes"),
        )
        .join(Race, Race.id == Result.race_id)
        .filter(Result.driver_id == driver_id)
        .first()
    )

    seasons = (
        db.query(
            Race.year,
            func.count(Result.id).label("races"),
            func.sum(Result.points).label("points"),
            func.sum(case((Result.position == 1, 1), else_=0)).label("wins"),
            Team.name.label("team"),
        )
        .join(Race, Race.id == Result.race_id)
        .outerjoin(Team, Team.id == Result.team_id)
        .filter(Result.driver_id == driver_id)
        .group_by(Race.year, Team.name)
        .order_by(Race.year)
        .all()
    )

    return {
        "driver_id": driver.id,
        "driver": f"{driver.forename} {driver.surname}",
        "code": driver.code,
        "nationality": driver.nationality,
        "career_totals": {
            "races": totals.races or 0,
            "points": totals.points or 0,
            "wins": totals.wins or 0,
            "podiums": totals.podiums or 0,
            "points_finishes": totals.points_finishes or 0,
        },
        "seasons": [
            {
                "year": s.year,
                "team": s.team,
                "races": s.races,
                "points": s.points or 0,
                "wins": s.wins or 0,
            }
            for s in seasons
        ],
    }
