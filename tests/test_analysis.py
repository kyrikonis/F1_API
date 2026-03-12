from datetime import date

from app.models.driver import Driver
from app.models.race import Race
from app.models.result import Result
from app.models.team import Team


def setup_season(db):
    team = Team(id=1, name="red_bull", full_name="Red Bull Racing", nationality="Austrian", active=True)

    db.add(team)
    verstappen = Driver(id=1,code="VER", forename="Max", surname="Verstappen", nationality="Dutch", active=True)
    perez = Driver(id=2,code="PER", forename="Sergio", surname="Perez", nationality="Mexican", active=True)
    db.add_all([verstappen, perez])

    race = Race(
        id=1, year=2024, round=1, name="Bahrain Grand Prix",
        circuit_name="Bahrain International Circuit",
        circuit_location="Sakhir", country="Bahrain",
        date=date(2024, 3,2),
    )
    db.add(race)

    ver_result = Result(id=1, race_id=1, driver_id=1, team_id=1, position=1,grid=1, points=25.0, laps=57, status="Finished")
    per_result = Result(id=2, race_id=1, driver_id=2, team_id=1, position=2,grid=2, points=18.0, laps=57, status="Finished")
    db.add_all([ver_result, per_result])
    db.commit()


class TestDriverStandings:
    def test_standings_returned(self, client, db):
        setup_season(db)
        response = client.get("/analysis/standings/drivers/2024")
        assert response.status_code == 200
        assert response.json()[0]["code"] == "VER"
        assert response.json()[0]["points"] == 25.0

    def test_no_data_returns_404(self, client):
        response = client.get("/analysis/standings/drivers/1800")
        assert response.status_code == 404


class TestWinsLeaderboard:
    def test_leaderboard_returns_winner(self, client, db):
        setup_season(db)
        response = client.get("/analysis/leaderboard/wins")
        assert response.status_code == 200
        assert response.json()[0]["code"] == "VER"
        assert response.json()[0]["wins"] == 1

    def test_leaderboard_ordered_by_wins(self, client, db):
        setup_season(db)
        response = client.get("/analysis/leaderboard/wins")
        assert response.status_code == 200
        wins = [entry["wins"] for entry in response.json()]
        assert wins == sorted(wins, reverse=True)

    def test_empty_leaderboard(self, client):
        response = client.get("/analysis/leaderboard/wins")
        assert response.status_code == 200
        assert response.json() == []


class TestDriverCareer:
    def test_career_summary(self, client, db):
        setup_season(db)
        response = client.get("/analysis/drivers/1/career")
        assert response.status_code == 200
        career = response.json()
        assert career["code"] == "VER"
        assert career["career_totals"]["wins"] == 1
        assert career["career_totals"]["points"] == 25.0

    def test_driver_not_found(self, client):
        response = client.get("/analysis/drivers/999/career")
        assert response.status_code == 404
