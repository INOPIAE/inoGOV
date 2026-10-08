import pytest

from app.config import settings

READ_PATHS = ["/sprachen", "/kreise", "/orte"]


@pytest.mark.parametrize("path", READ_PATHS)
def test_public_search_allows_anonymous_reads(client, monkeypatch, path):
    monkeypatch.setattr(settings, "public_search", True)
    assert client.get(path).status_code == 200


@pytest.mark.parametrize("path", READ_PATHS)
def test_private_search_requires_login(client, monkeypatch, user_h, path):
    monkeypatch.setattr(settings, "public_search", False)
    assert client.get(path).status_code == 401
    assert client.get(path, headers={"Authorization": "Bearer kaputt"}).status_code == 401
    assert client.get(path, headers=user_h).status_code == 200


def test_private_search_rejects_deactivated_user(client, monkeypatch, db, roles, admin_h):
    from app.models import User

    monkeypatch.setattr(settings, "public_search", False)
    db.query(User).filter(User.username == "boss").one().active = False
    db.commit()
    assert client.get("/orte", headers=admin_h).status_code == 401


def test_settings_reports_mode(client, monkeypatch):
    monkeypatch.setattr(settings, "public_search", False)
    assert client.get("/settings").json()["public_search"] is False
