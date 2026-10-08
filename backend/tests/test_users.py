import pytest

NEW = {"username": "neu", "email": "neu@example.com", "password": "passwort1"}


def test_requires_token(client):
    assert client.get("/users/me").status_code in (401, 403)
    assert client.get("/users/me", headers={"Authorization": "Bearer kaputt"}).status_code == 401


def test_me(client, admin_h):
    body = client.get("/users/me", headers=admin_h).json()
    assert body["username"] == "boss"
    assert body["roles"] == ["admin"]
    assert "hashed_password" not in body


def test_normal_user_forbidden(client, user_h):
    assert client.get("/users", headers=user_h).status_code == 403
    assert client.post("/users", json=NEW, headers=user_h).status_code == 403


def test_create_and_login(client, admin_h):
    response = client.post("/users", json=NEW, headers=admin_h)
    assert response.status_code == 201
    assert response.json()["roles"] == ["user"]
    assert client.post("/auth/login", json={"username": "neu", "password": "passwort1"}).status_code == 200


def test_create_duplicate(client, admin_h):
    client.post("/users", json=NEW, headers=admin_h)
    assert client.post("/users", json=NEW, headers=admin_h).status_code == 409


def test_create_unknown_role(client, admin_h):
    response = client.post("/users", json={**NEW, "roles": ["gott"]}, headers=admin_h)
    assert response.status_code == 422


def test_create_short_password(client, admin_h):
    assert client.post("/users", json={**NEW, "password": "kurz"}, headers=admin_h).status_code == 422


def test_list_and_get(client, admin_h):
    created = client.post("/users", json=NEW, headers=admin_h).json()
    assert len(client.get("/users", headers=admin_h).json()) == 2
    assert client.get(f"/users/{created['id']}", headers=admin_h).json()["username"] == "neu"
    assert client.get("/users/00000000-0000-0000-0000-000000000000", headers=admin_h).status_code == 404


def test_update_roles_and_names(client, admin_h):
    uid = client.post("/users", json=NEW, headers=admin_h).json()["id"]
    response = client.patch(
        f"/users/{uid}", json={"first_name": "Ann", "roles": ["admin", "user"]}, headers=admin_h
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Ann"
    assert response.json()["roles"] == ["admin", "user"]


def test_unblock_resets_counter(client, db, admin_h):
    uid = client.post("/users", json=NEW, headers=admin_h).json()["id"]
    for _ in range(3):
        client.post("/auth/login", json={"username": "neu", "password": "falsch"})
    assert client.post("/auth/login", json={"username": "neu", "password": "passwort1"}).status_code == 423
    client.patch(f"/users/{uid}", json={"blocked": False}, headers=admin_h)
    assert client.post("/auth/login", json={"username": "neu", "password": "passwort1"}).status_code == 200


def test_deactivate_prevents_login(client, admin_h):
    uid = client.post("/users", json=NEW, headers=admin_h).json()["id"]
    assert client.delete(f"/users/{uid}", headers=admin_h).status_code == 204
    assert client.post("/auth/login", json={"username": "neu", "password": "passwort1"}).status_code == 401


def test_admin_cannot_lock_self_out(client, admin, admin_h):
    uid = str(admin.id)
    assert client.delete(f"/users/{uid}", headers=admin_h).status_code == 400
    assert client.patch(f"/users/{uid}", json={"roles": ["user"]}, headers=admin_h).status_code == 400
    assert client.patch(f"/users/{uid}", json={"blocked": True}, headers=admin_h).status_code == 400


def test_change_password(client, user_h):
    wrong = client.put("/users/me/password", json={"current_password": "x", "new_password": "neuespass1"}, headers=user_h)
    assert wrong.status_code == 400
    ok = client.put("/users/me/password", json={"current_password": "geheim123", "new_password": "neuespass1"}, headers=user_h)
    assert ok.status_code == 204
    assert client.post("/auth/login", json={"username": "normal", "password": "neuespass1"}).status_code == 200
