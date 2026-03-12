from datetime import date

from app.models.driver import Driver
from app.models.race import Race
from app.models.result import Result
from app.models.team import Team


def add_race_weekend(db):
    team = Team(id=1, name="ferrari", full_name="Scuderia Ferrari", nationality="Italian", active=True)
    driver = Driver(id=1, code="LEC", forename="Charles", surname="Leclerc", nationality="Monegasque", active=True)
    race = Race(
        id=1, year=2024, round=1, name="Bahrain Grand Prix",
        circuit_name="Bahrain International Circuit",
        circuit_location="Sakhir", country="Bahrain",
        date=date(2024,3,2)
    )
    db.add_all([team, driver, race])
    db.commit()


def seed_result(db, **kwargs):
    defaults = dict(
        id=1, race_id=1, driver_id=1, team_id=1,
        grid=1, position=1, points=25.0, laps=57, status="Finished"
    )
    defaults.update(kwargs)
    result = Result(**defaults)
    db.add(result)
    db.commit()
    return result


class TestListResults:
    def test_returns_all_results(self, client, db):
        add_race_weekend(db)
        seed_result(db)
        response = client.get("/results/")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestGetResult:
    def test_existing_result(self, client, db):
        add_race_weekend(db)
        seed_result(db)
        response = client.get("/results/1")
        assert response.status_code == 200
        assert response.json()["points"] == 25.0

    def test_not_found(self, client):
        response = client.get("/results/999")
        assert response.status_code == 404


class TestCreateResult:
    def test_create_result(self, client, db):
        add_race_weekend(db)
        payload = {
            "race_id": 1, "driver_id": 1, "team_id": 1,
            "grid": 1, "position": 1, "points": 25.0,
            "laps": 57, "status": "Finished",
        }
        response = client.post("/results/", json=payload)
        assert response.status_code == 201
        assert response.json()["position"] == 1

    def test_duplicate_result_rejected(self, client, db):
        add_race_weekend(db)
        seed_result(db)
        payload = {
            "race_id": 1, "driver_id": 1, "team_id": 1,
            "grid": 2, "position": 2, "points": 18.0,
            "laps": 57, "status": "Finished"
        }
        response = client.post("/results/", json=payload)
        assert response.status_code == 409

    def test_invalid_race_rejected(self, client, db):
        add_race_weekend(db)
        payload = {
            "race_id": 999, "driver_id": 1, "team_id": 1,
            "grid": 1, "position": 1, "points": 25.0,
            "laps": 57, "status": "Finished"
        }
        response = client.post("/results/", json=payload)
        assert response.status_code == 404

    def test_invalid_driver_rejected(self, client, db):
        add_race_weekend(db)
        payload = {
            "race_id": 1, "driver_id": 999, "team_id": 1,
            "grid": 1, "position": 1, "points": 25.0,
            "laps": 57, "status": "Finished"
        }
        response = client.post("/results/", json=payload)
        assert response.status_code == 404

    def test_invalid_team_rejected(self, client, db):
        add_race_weekend(db)
        payload = {
            "race_id": 1, "driver_id": 1, "team_id": 999,
            "grid": 1, "position": 1, "points": 25.0,
            "laps": 57, "status": "Finished"
        }
        response = client.post("/results/", json=payload)
        assert response.status_code == 404
