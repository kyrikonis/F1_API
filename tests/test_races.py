from datetime import date

from app.models.race import Race


def seed_race(db, **kwargs):
    defaults = dict(
        id=1, year=2024, round=1, name="Bahrain Grand Prix",
        circuit_name="Bahrain International Circuit",
        circuit_location="Sakhir", country="Bahrain",
        date=date(2024, 3, 2),
    )
    defaults.update(kwargs)
    race = Race(**defaults)
    db.add(race)
    db.commit()
    return race


class TestListRaces:
    def test_returns_all_races(self, client,db):
        seed_race(db, id=1, round=1)
        seed_race(db, id=2, round=2, name="Saudi Arabian Grand Prix",
                  circuit_name="Jeddah Corniche Circuit",
                  circuit_location="Jeddah", country="Saudi Arabia",
                  date=date(2024, 3, 9))
        response = client.get("/races/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_filter_by_year(self, client, db):
        seed_race(db, id=1, year=2024)
        seed_race(db, id=2, year=2023, round=2, name="Bahrain Grand Prix 2023",
                  date=date(2023, 3, 5))
        response = client.get("/races/?year=2024")
        assert response.status_code == 200
        assert all(race["year"] == 2024 for race in response.json())

    def test_filter_by_country(self, client, db):
        seed_race(db, id=1, country="Bahrain")
        seed_race(db, id=2, round=2, name="Saudi Arabian Grand Prix",
                  circuit_name="Jeddah Corniche Circuit",
                  circuit_location="Jeddah", country="Saudi Arabia",
                  date=date(2024,3,9))
        response = client.get("/races/?country=Bahrain")
        assert response.status_code == 200
        assert all(race["country"] == "Bahrain" for race in response.json())

class TestGetRace:
    def test_existing_race(self, client, db):
        seed_race(db)
        response = client.get("/races/1")
        assert response.status_code == 200
        assert response.json()["name"] == "Bahrain Grand Prix"

    def test_not_found(self, client):
        response = client.get("/races/999")
        assert response.status_code == 404


class TestCreateRace:
    def test_create_race(self, client):
        payload = {
            "year": 2025, "round": 1, "name": "Australian Grand Prix",
            "circuit_name": "Albert Park Circuit", "circuit_location": "Melbourne",
            "country": "Australia", "date": "2025-03-16",
        }
        response = client.post("/races/", json=payload)
        assert response.status_code == 201
        assert response.json()["name"] == "Australian Grand Prix"

    def test_duplicate_year_round_rejected(self, client, db):
        seed_race(db, year=2024, round=1)
        payload = {
            "year": 2024, "round": 1, "name": "Duplicate Race",
            "circuit_name": "Some Circuit", "circuit_location": "Somewhere",
            "country": "Nowhere", "date": "2024-03-02",
        }
        response = client.post("/races/", json=payload)
        assert response.status_code == 409

    def test_invalid_date_rejected(self, client):
        payload = {
            "year": 2025, "round": 1, "name": "Australian Grand Prix",
            "circuit_name": "Albert Park Circuit", "circuit_location": "Melbourne",
            "country": "Australia", "date": "not-a-date",
        }
        response = client.post("/races/", json=payload)
        assert response.status_code == 422

    def test_patch_not_found(self, client):
        response = client.patch("/races/999", json={"name": "Ghost Race"})
        assert response.status_code == 404
