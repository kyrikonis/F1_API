from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_database
from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverResponse, DriverUpdate

router = APIRouter(prefix="/drivers", tags=["Drivers"])

@router.get("/", response_model=list[DriverResponse])
def list_drivers(
    active_only: bool = Query(False, description="Filter to active drivers"),
    nationality: str | None = Query(None, description="Filter by nationality"),
    team_id: int | None = Query(None, description="Filter by team ID"),
    db: Session = Depends(get_database),
):
    query = db.query(Driver)
    if active_only:
        query = query.filter(Driver.active == True)
    if nationality:
        query = query.filter(Driver.nationality.ilike(f"%{nationality}%"))
    if team_id:
        query = query.filter(Driver.team_id == team_id)
    return query.order_by(Driver.surname).all()

@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(driver_id: int, db: Session = Depends(get_database)):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@router.post("/", response_model=DriverResponse, status_code=201)
def create_driver(payload: DriverCreate, db: Session = Depends(get_database)):
    existing = db.query(Driver).filter(Driver.code == payload.code.upper()).first()
    if existing:
        raise HTTPException(status_code=409, detail="A driver with this code already exists")
    driver = Driver(**payload.model_dump())
    driver.code = driver.code.upper()
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.patch("/{driver_id}", response_model=DriverResponse)
def update_driver(driver_id: int, payload: DriverUpdate, db: Session = Depends(get_database)):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver cannot be found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)
    db.commit()
    db.refresh(driver)
    return driver

@router.delete("/{driver_id}", status_code=204)
def delete_driver(driver_id: int, db: Session = Depends(get_database)):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver cannot be found")
    db.delete(driver)
    db.commit()