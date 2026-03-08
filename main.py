from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import drivers, teams, races

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="F1 Statistics API",
    description=(
        "A RESTful API for Formula 1 race data including drivers, teams, races, and results."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drivers.router)
app.include_router(teams.router)
app.include_router(races.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "F1 Statistics API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }
