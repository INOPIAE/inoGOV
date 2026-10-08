import pytest

from app.create_admin import create_admin
from app.deps import get_roles
from app.models import Role


def test_create_admin_can_login(client, db):
    db.add(Role(rolename="admin"))
    db.commit()
    user = create_admin(db, "root", "root@example.com", "supergeheim")
    assert get_roles(db, user.id) == ["admin"]
    response = client.post("/auth/login", json={"username": "root", "password": "supergeheim"})
    assert response.status_code == 200


def test_create_admin_rejects_duplicate_and_short_password(db):
    db.add(Role(rolename="admin"))
    db.commit()
    create_admin(db, "root", "root@example.com", "supergeheim")
    with pytest.raises(ValueError):
        create_admin(db, "root", "x@example.com", "supergeheim")
    with pytest.raises(ValueError):
        create_admin(db, "other", "o@example.com", "kurz")


def test_create_admin_needs_role(db):
    with pytest.raises(ValueError):
        create_admin(db, "root", "root@example.com", "supergeheim")
