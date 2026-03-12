from app.models.team import Team


def seed_team(db, **kwargs):
    defaults = dict(id=1, name="ferrari", full_name="Scuderia Ferrari", nationality="Italian", active=True)
    defaults.update(kwargs)
    team = Team(**defaults)
    db.add(team)
    db.commit()
    return team


class TestListTeams:
    def test_returns_all_teams(self, client, db):
        seed_team(db, id=1, name="ferrari")
        seed_team(db, id=2, name="mclaren", full_name="McLaren Racing", nationality="British")
        response = client.get("/teams/")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetTeam:
    def test_existing_team(self, client, db):
        seed_team(db)
        response = client.get("/teams/1")
        assert response.status_code == 200
        assert response.json()["name"] == "ferrari"

    def test_not_found(self, client):
        response = client.get("/teams/999")
        assert response.status_code == 404


class TestCreateTeam:
    def test_create_team(self, client):
        payload = {"name": "red_bull", "full_name": "Red Bull Racing", "nationality": "Austrian", "active": True}
        response = client.post("/teams/", json=payload)
        assert response.status_code == 201
        assert response.json()["name"] == "red_bull"

    def test_duplicate_name_rejected(self, client, db):
        seed_team(db, name="ferrari")
        payload = {"name": "ferrari", "full_name": "Ferrari 2", "nationality": "Italian", "active": True}
        response = client.post("/teams/", json=payload)
        assert response.status_code == 409


class TestDeleteTeam:
    def test_delete_team(self, client, db):
        seed_team(db)
        response = client.delete("/teams/1")
        assert response.status_code == 204
        assert client.get("/teams/1").status_code == 404

    def test_delete_not_found(self, client):
        response = client.delete("/teams/999")
        assert response.status_code == 404
