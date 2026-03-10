import os
import pandas as pd
from datetime import date

from app.database import Base, SessionLocal, engine
from app.models.constructor_standing import ConstructorStanding
from app.models.driver import Driver
from app.models.race import Race
from app.models.result import Result
from app.models.season_standing import SeasonStanding
from app.models.team import Team

DATA = "data"

def na(val):
    """Return None for \\N in Ergast dataset, or pandas NaN values"""
    if val is None:
        return None
    if isinstance(val, float):
        import math
        if math.isnan(val):
            return None
    if str(val) in (r"\N", "nan", "None",""):
        return None
    return val

def load(filename):
    return pd.read_csv(
        os.path.join(DATA, filename),
        na_values=[r"\N"],
        keep_default_na=True,
    )

def seed_teams(db, constructors):
    print("Seeding teams...")
    # seeing which constructors are most recently active
    results_df = load("results.csv")
    races_df = load("races.csv")
    recent = set(
        results_df[results_df["raceId"].isin(
            races_df[races_df["year"] >= 2023]["raceId"]
        )]["constructorId"].dropna().astype(int)
    )

    for _, row in constructors.iterrows():
        team = Team(
            id=int(row["constructorId"]),
            name=str(row["constructorRef"]),
            full_name=str(row["name"]),
            nationality=str(row["nationality"]),
            active=int(row["constructorId"]) in recent,
        )
        db.merge(team)
    db.commit()
    print(f"{len(constructors)} teams added.")


def seed_drivers(db, drivers):
    print("Seeding drivers...")
    results_df = load("results.csv")
    races_df = load("races.csv")
    recent_driver_ids = set(
        results_df[results_df["raceId"].isin(
            races_df[races_df["year"] >= 2023]["raceId"]
        )]["driverId"].dropna().astype(int)
    )

    # Most recent team for each driver (by latest raceId they appear in)
    latest = (
        results_df.sort_values("raceId")
        .dropna(subset=["driverId", "constructorId"])
        .drop_duplicates(subset=["driverId"], keep="last")
        .set_index("driverId")["constructorId"]
        .astype(int)
        .to_dict()
    )

    # Processing most recent drivers first so they can keep their driver code
    # older drivers that share a code will get an alternative generated for them
    drivers_sorted = drivers.copy()
    drivers_sorted["_recent"] = drivers_sorted["driverId"].isin(recent_driver_ids).astype(int)
    drivers_sorted = drivers_sorted.sort_values(["_recent", "driverId"], ascending=[False, True])

    used_codes = set()
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for _, row in drivers_sorted.iterrows():
        driver_id = int(row["driverId"])
        raw_code = na(row.get("code"))

        if raw_code:
            code = str(raw_code).upper()[:3]
        else:
            code = str(row["driverRef"]).upper()[:3]

        # max 3 characters, ensures theyre unique
        if code in used_codes:
            base = code[:2]
            code = base + chars[0]
            i = 0
            while code in used_codes:
                i +=1
                code = base + chars[i % len(chars)]

        used_codes.add(code)
        raw_number = na(row.get("number"))
        number = int(raw_number) if raw_number is not None else None
        if number is not None and not (0 <= number <= 99):
            number = None

        raw_dob = na(row.get("dob"))
        dob = None
        if raw_dob:
            try:
                dob = date.fromisoformat(str(raw_dob))
            except ValueError:
                dob = None

        driver = Driver(
            id=driver_id,
            code=code,
            forename=str(row["forename"]),
            surname=str(row["surname"]),
            nationality=str(row["nationality"]),
            date_of_birth=dob,
            number=number,
            team_id=latest.get(driver_id),
            active=driver_id in recent_driver_ids,
        )
        db.merge(driver)

    db.commit()
    print(f"{len(drivers)} drivers added.")


def seed_races(db, races, circuits):
    print("Seeding races...")
    circuit_dict = circuits.set_index("circuitId")

    for _, row in races.iterrows():
        circuit = circuit_dict.loc[int(row["circuitId"])]
        race = Race(
            id=int(row["raceId"]),
            year=int(row["year"]),
            round=int(row["round"]),
            name=str(row["name"]),
            circuit_name=str(circuit["name"]),
            circuit_location=str(circuit["location"]),
            country=str(circuit["country"]),
            date=date.fromisoformat(str(row["date"])),
        )
        db.merge(race)

    db.commit()
    print(f"{len(races)} races added.")


def seed_results(db, results, status_dict):
    print("Seeding results...")
    count = 0
    for _, row in results.iterrows():
        raw_pos = na(row.get("position"))
        position = int(raw_pos) if raw_pos is not None else None
        raw_grid = na(row.get("grid"))
        grid = int(raw_grid) if raw_grid is not None else None
        raw_laps = na(row.get("laps"))
        laps = int(raw_laps) if raw_laps is not None else None
        raw_rank = na(row.get("rank"))
        fastest_lap_rank = int(raw_rank) if raw_rank is not None else None
        raw_lap_time = na(row.get("fastestLapTime"))
        fastest_lap_time = str(raw_lap_time) if raw_lap_time is not None else None
        raw_points = na(row.get("points"))
        points = float(raw_points) if raw_points is not None else 0.0

        status_id = na(row.get("statusId"))
        status = status_dict.get(int(status_id), "Unknown") if status_id is not None else "Unknown"

        result = Result(
            id=int(row["resultId"]),
            race_id=int(row["raceId"]),
            driver_id=int(row["driverId"]),
            team_id=int(row["constructorId"]),
            grid=grid,
            position=position,
            points=points,
            laps=laps,
            status=status,
            fastest_lap_rank=fastest_lap_rank,
            fastest_lap_time=fastest_lap_time,
        )
        db.merge(result)
        count += 1

    db.commit()
    print(f"{count} results added.")


def seed_season_standings(db, driver_standings, races):
    print("Seeding season standings...")
    results_df = load("results.csv")

    last_race = races.groupby("year")["raceId"].max().reset_index()
    last_race_ids = set(last_race["raceId"])
    race_year_dict = races.set_index("raceId")["year"].to_dict()

    # Build lookup: (season, driver_id) to team_id from the last race they were in
    last_race_per_year = races.groupby("year")["raceId"].max()
    driver_team = {}
    for year, last_rid in last_race_per_year.items():
        season_results = results_df[results_df["raceId"] == last_rid][["driverId", "constructorId"]]
        for _, r in season_results.iterrows():
            driver_team[(int(year), int(r["driverId"]))] = int(r["constructorId"])

    final = driver_standings[driver_standings["raceId"].isin(last_race_ids)].copy()

    count = 0
    for _, row in final.iterrows():
        season = race_year_dict.get(int(row["raceId"]))
        if season is None:
            continue
        driver_id = int(row["driverId"])
        standing = SeasonStanding(
            season=int(season),
            driver_id=driver_id,
            team_id=driver_team.get((int(season), driver_id)),
            final_position=int(row["position"]),
            final_points=float(row["points"]),
        )
        db.merge(standing)
        count += 1

    db.commit()
    print(f"  {count} driver season standings added.")


def seed_constructor_standings(db, constructor_standings, races):
    print("Seeding constructor standings.")
    last_race = races.groupby("year")["raceId"].max().reset_index()
    last_race_ids = set(last_race["raceId"])

    final = constructor_standings[constructor_standings["raceId"].isin(last_race_ids)].copy()
    race_year_dict = races.set_index("raceId")["year"].to_dict()

    count = 0
    for _, row in final.iterrows():
        season = race_year_dict.get(int(row["raceId"]))
        if season is None:
            continue
        standing = ConstructorStanding(
            season=int(season),
            team_id=int(row["constructorId"]),
            final_position=int(row["position"]),
            final_points=float(row["points"]),
        )
        db.merge(standing)
        count += 1
    db.commit()
    print(f"{count} constructor season standings added.")


def main():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    print("Loading CSVs...")
    circuits = load("circuits.csv")
    constructors = load("constructors.csv")
    drivers = load("drivers.csv")
    races = load("races.csv")
    results = load("results.csv")
    driver_standings = load("driver_standings.csv")
    constructor_standings = load("constructor_standings.csv")
    status_df = load("status.csv")
    status_dict = dict(zip(status_df["statusId"].astype(int), status_df["status"]))

    db = SessionLocal()
    try:
        seed_teams(db, constructors)
        seed_drivers(db, drivers)
        seed_races(db, races, circuits)
        seed_results(db, results, status_dict)
        seed_season_standings(db, driver_standings, races)
        seed_constructor_standings(db, constructor_standings, races)
    finally:
        db.close()

    print("Database successfully seeded")


if __name__ == "__main__":
    main()
