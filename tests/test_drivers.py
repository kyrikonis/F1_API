from datetime import date

from app.models.driver import Driver


def seed_driver(db, **kwargs):
    defaults = dict(
        id=1, code="VER", forename="Max", surname="Verstappen",
        nationality="Dutch", date_of_birth=date(1997, 9, 30),number=1,
        team_id=None, active=True
    )
    defaults.update(kwargs)
    driver = Driver(**defaults)
    db.add(driver)
    db.commit()
    return driver

class TestListDrivers:
    def test_returns_all_drivers(self, client, db):
        seed_driver(db, id=1, code="VER")
        seed_driver(db, id=2, code="HAM", forename="Lewis", surname="Hamilton", nationality="British")
        response = client.get("/drivers/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_active_only_filter(self, client, db):
        seed_driver(db, id=1, code="VER", active=True)
        seed_driver(db, id=2, code="SCH", forename="Michael", surname="Schumacher", nationality="German", active=False)
        response = client.get("/drivers/?active_only=true")
        assert response.status_code == 200
        codes = [d["code"] for d in response.json()]
        assert "VER" in codes
        assert "SCH" not in codes


class TestGetDriver:
    def test_existing_driver(self, client,db):
        seed_driver(db)
        response = client.get("/drivers/1")
        assert response.status_code == 200
        assert response.json()["code"] == "VER"

    def test_not_found(self, client):
        response = client.get("/drivers/999")
        assert response.status_code == 404


class TestCreateDriver:
    def test_create_driver(self, client):
        payload = {
            "code": "NOR", "forename": "Lando", "surname": "Norris",
            "nationality": "British", "active": True,
        }
        response = client.post("/drivers/", json=payload)
        assert response.status_code == 201
        assert response.json()["code"] == "NOR"

    def test_duplicate_code_rejected(self, client, db):
        seed_driver(db, code="VER")
        payload = {
            "code": "VER", "forename": "Other", "surname": "Driver",
            "nationality": "Dutch", "active": True,
        }
        response = client.post("/drivers/", json=payload)
        assert response.status_code == 409


class TestUpdateDriver:
    def test_patch_driver(self, client, db):
        seed_driver(db)
        response = client.patch("/drivers/1", json={"active": False})
        assert response.status_code == 200
        assert response.json()["active"] is False

    def test_patch_not_found(self, client):
        response = client.patch("/drivers/999", json={"active": False})
        assert response.status_code == 404


class TestDeleteDriver:
    def test_delete_driver(self, client, db):
        seed_driver(db)
        response = client.delete("/drivers/1")
        assert response.status_code == 204
        assert client.get("/drivers/1").status_code == 404

    def test_delete_not_found(self, client):
        response = client.delete("/drivers/999")
        assert response.status_code == 404
