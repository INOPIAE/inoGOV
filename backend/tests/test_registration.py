import re

import pytest

from app import mail
from app.models import User


@pytest.fixture
def mails(monkeypatch):
    sent = []
    monkeypatch.setattr(mail, "send_mail", lambda to, subject, body: sent.append((to, subject, body)))
    return sent


def invite_token(client, admin_h, mails):
    client.post("/users/invite", json={"email": "neu@example.com"}, headers=admin_h)
    return re.search(r"token=(\S+)", mails[-1][2]).group(1)


def setup(client, token, **fields):
    body = {"token": token, "username": "neuer", "password": "passwort1", **fields}
    return client.post("/auth/setup-account", json=body)


# Einladung: nur E-Mail
def test_invite_needs_only_an_email(client, admin_h, db, mails):
    response = client.post("/users/invite", json={"email": "neu@example.com"}, headers=admin_h)
    assert response.status_code == 201
    body = response.json()
    assert body["first_name"] is None and body["last_name"] is None
    assert body["roles"] == ["user"]


def test_invite_ignores_names_from_admin(client, admin_h, db, mails):
    client.post(
        "/users/invite",
        json={"email": "neu@example.com", "first_name": "Admin", "last_name": "Wunsch"},
        headers=admin_h,
    )
    user = db.query(User).filter(User.email == "neu@example.com").one()
    assert user.first_name is None and user.last_name is None


def test_invite_rejects_invalid_email(client, admin_h):
    assert client.post("/users/invite", json={"email": "kein-mail"}, headers=admin_h).status_code == 422


# Registrierung: Name vom Benutzer, mindestens einer
@pytest.mark.parametrize(
    "fields",
    [{}, {"first_name": "", "last_name": ""}, {"first_name": "   "}, {"first_name": None, "last_name": None}],
)
def test_setup_requires_a_name(client, admin_h, mails, fields):
    token = invite_token(client, admin_h, mails)
    assert setup(client, token, **fields).status_code == 422


@pytest.mark.parametrize(
    "fields, expected",
    [
        ({"first_name": "Ann"}, ("Ann", None)),
        ({"last_name": "Muster"}, (None, "Muster")),
        ({"first_name": " Ann ", "last_name": " Muster "}, ("Ann", "Muster")),
    ],
)
def test_setup_stores_names(client, admin_h, db, mails, fields, expected):
    token = invite_token(client, admin_h, mails)
    assert setup(client, token, **fields).status_code == 200
    user = db.query(User).filter(User.username == "neuer").one()
    assert (user.first_name, user.last_name) == expected


def test_failed_setup_does_not_consume_link(client, admin_h, mails):
    token = invite_token(client, admin_h, mails)
    assert setup(client, token).status_code == 422
    assert setup(client, token, first_name="Ann").status_code == 200


# Eigene Daten ändern
def test_user_can_change_names(client, user_h):
    response = client.patch("/users/me", json={"first_name": "Ann", "last_name": "Muster"}, headers=user_h)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Ann"
    assert client.get("/users/me", headers=user_h).json()["last_name"] == "Muster"


def test_user_can_clear_one_name_but_not_both(client, user_h):
    client.patch("/users/me", json={"first_name": "Ann", "last_name": "Muster"}, headers=user_h)
    assert client.patch("/users/me", json={"last_name": ""}, headers=user_h).status_code == 200
    me = client.get("/users/me", headers=user_h).json()
    assert me["first_name"] == "Ann" and me["last_name"] is None
    assert client.patch("/users/me", json={"first_name": ""}, headers=user_h).status_code == 422
    assert client.get("/users/me", headers=user_h).json()["first_name"] == "Ann"


def test_user_without_names_can_still_change_email(client, admin_h):
    # Admin wurde ohne Namen angelegt
    response = client.patch(
        "/users/me", json={"email": "neu@example.com", "current_password": "geheim123"}, headers=admin_h
    )
    assert response.status_code == 200


def test_email_change_needs_current_password(client, user_h):
    assert client.patch("/users/me", json={"email": "neu@example.com"}, headers=user_h).status_code == 400
    wrong = client.patch("/users/me", json={"email": "neu@example.com", "current_password": "falsch"}, headers=user_h)
    assert wrong.status_code == 400
    assert client.get("/users/me", headers=user_h).json()["email"] == "normal@example.com"
    ok = client.patch("/users/me", json={"email": "neu@example.com", "current_password": "geheim123"}, headers=user_h)
    assert ok.status_code == 200 and ok.json()["email"] == "neu@example.com"


def test_unchanged_email_needs_no_password(client, user_h):
    response = client.patch(
        "/users/me", json={"email": "NORMAL@example.com", "first_name": "Ann"}, headers=user_h
    )
    assert response.status_code == 200


def test_email_must_be_valid(client, user_h):
    response = client.patch("/users/me", json={"email": "kein-mail", "current_password": "geheim123"}, headers=user_h)
    assert response.status_code == 422


def test_username_cannot_be_changed(client, user_h):
    response = client.patch("/users/me", json={"username": "hacker", "first_name": "Ann"}, headers=user_h)
    assert response.status_code == 200
    assert response.json()["username"] == "normal"


def test_profile_requires_login(client):
    assert client.patch("/users/me", json={"first_name": "Ann"}).status_code in (401, 403)


def test_other_fields_cannot_be_set_via_profile(client, user_h):
    client.patch("/users/me", json={"roles": ["admin"], "active": False, "blocked": True, "first_name": "Ann"}, headers=user_h)
    me = client.get("/users/me", headers=user_h).json()
    assert me["roles"] == ["user"] and me["active"] is True and me["blocked"] is False
