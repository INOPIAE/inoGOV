import re

import pyotp
import pytest

from app import mail
from app.models import User


@pytest.fixture
def mails(monkeypatch):
    sent = []
    monkeypatch.setattr(mail, "send_mail", lambda to, subject, body: sent.append((to, subject, body)))
    return sent


def token_from(sent):
    return re.search(r"token=(\S+)", sent[-1][2]).group(1)


def login(client, username, password, **extra):
    return client.post("/auth/login", json={"username": username, "password": password, **extra})


def test_settings_public(client):
    body = client.get("/settings").json()
    assert set(body) == {"app_name", "copyright_name", "public_search"}


# Passwort vergessen
def test_forgot_password_flow(client, db, roles, mails):
    from tests.conftest import add_user  # noqa: PLC0415

    add_user(db, roles, "normal", "user")
    assert client.post("/auth/forgot-password", json={"email": "normal@example.com"}).status_code == 204
    assert len(mails) == 1 and mails[0][0] == "normal@example.com"
    token = token_from(mails)

    info = client.get("/auth/link-info", params={"token": token}).json()
    assert info["purpose"] == "reset" and info["username"] == "normal"

    ok = client.post("/auth/reset-password", json={"token": token, "new_password": "neuespass1"})
    assert ok.status_code == 204
    assert login(client, "normal", "neuespass1").status_code == 200
    # Link ist einmalig
    again = client.post("/auth/reset-password", json={"token": token, "new_password": "nochmal123"})
    assert again.status_code == 400


def test_forgot_password_unknown_email_is_silent(client, mails):
    assert client.post("/auth/forgot-password", json={"email": "x@example.com"}).status_code == 204
    assert mails == []


def test_reset_with_invalid_token(client):
    response = client.post("/auth/reset-password", json={"token": "kaputt", "new_password": "neuespass1"})
    assert response.status_code == 400


def test_access_token_not_usable_as_link(client, db, roles, mails):
    from tests.conftest import add_user, auth  # noqa: PLC0415

    add_user(db, roles, "normal", "user")
    bearer = auth(client, "normal")["Authorization"].split()[1]
    assert client.post("/auth/reset-password", json={"token": bearer, "new_password": "neuespass1"}).status_code == 400


def test_link_token_not_usable_as_access(client, db, roles, mails):
    from tests.conftest import add_user  # noqa: PLC0415

    add_user(db, roles, "normal", "user")
    client.post("/auth/forgot-password", json={"email": "normal@example.com"})
    token = token_from(mails)
    assert client.get("/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_reset_clears_lockout(client, db, roles, mails):
    from tests.conftest import add_user  # noqa: PLC0415

    user = add_user(db, roles, "normal", "user")
    for _ in range(3):
        login(client, "normal", "falsch")
    assert login(client, "normal", "geheim123").status_code == 423
    client.post("/auth/forgot-password", json={"email": "normal@example.com"})
    client.post("/auth/reset-password", json={"token": token_from(mails), "new_password": "neuespass1"})
    db.refresh(user)
    assert login(client, "normal", "neuespass1").status_code == 200


# Einladung
def test_invite_and_setup(client, admin_h, mails):
    response = client.post(
        "/users/invite", json={"email": "neu@example.com", "roles": ["user"]}, headers=admin_h
    )
    assert response.status_code == 201
    assert response.json()["pending"] is True
    token = token_from(mails)

    setup = client.post("/auth/setup-account", json={"token": token, "username": "neuer", "password": "passwort1"})
    assert setup.status_code == 200
    me = client.get("/users/me", headers={"Authorization": f"Bearer {setup.json()['access_token']}"}).json()
    assert me["username"] == "neuer" and me["pending"] is False
    assert login(client, "neuer", "passwort1").status_code == 200
    # Link ist einmalig
    again = client.post("/auth/setup-account", json={"token": token, "username": "zweiter", "password": "passwort1"})
    assert again.status_code == 400


def test_invite_requires_admin(client, user_h):
    assert client.post("/users/invite", json={"email": "a@example.com"}, headers=user_h).status_code == 403


def test_setup_username_taken(client, admin_h, mails):
    client.post("/users/invite", json={"email": "neu@example.com"}, headers=admin_h)
    token = token_from(mails)
    response = client.post("/auth/setup-account", json={"token": token, "username": "boss", "password": "passwort1"})
    assert response.status_code == 409


def test_pending_user_cannot_login(client, admin_h, db):
    client.post("/users/invite", json={"email": "neu@example.com"}, headers=admin_h)
    name = db.query(User).filter(User.email == "neu@example.com").one().username
    assert login(client, name, "irgendwas1").status_code == 401


# Admin-Resets
def test_admin_reset_password_and_otp(client, db, roles, admin_h, mails):
    from tests.conftest import add_user  # noqa: PLC0415

    user = add_user(db, roles, "normal", "user")
    assert client.post(f"/users/{user.id}/reset-password", headers=admin_h).status_code == 204
    token = token_from(mails)
    assert client.get("/auth/link-info", params={"token": token}).json()["purpose"] == "admin_reset"
    assert client.post("/auth/reset-password", json={"token": token, "new_password": "neuespass1"}).status_code == 204

    assert client.post(f"/users/{user.id}/reset-otp", headers=admin_h).status_code == 204
    token = token_from(mails)
    start = client.post("/auth/otp/start", json={"token": token}).json()
    code = pyotp.TOTP(start["secret"]).now()
    bad = client.post("/auth/otp/confirm", json={"token": token, "setup_token": start["setup_token"], "code": "000000"})
    assert bad.status_code == 400
    ok = client.post("/auth/otp/confirm", json={"token": token, "setup_token": start["setup_token"], "code": code})
    assert ok.status_code == 204
    db.refresh(user)
    assert user.otp_enabled is True
    assert login(client, "normal", "neuespass1").json()["detail"] == "otp_required"


def test_admin_resets_require_admin(client, db, roles, user_h):
    from tests.conftest import add_user  # noqa: PLC0415

    other = add_user(db, roles, "other", "user")
    assert client.post(f"/users/{other.id}/reset-password", headers=user_h).status_code == 403
    assert client.post(f"/users/{other.id}/reset-otp", headers=user_h).status_code == 403


# OTP Selbstverwaltung
def test_my_otp_setup_confirm_and_disable(client, db, roles):
    from tests.conftest import add_user, auth  # noqa: PLC0415

    user = add_user(db, roles, "normal", "user")
    headers = auth(client, "normal")

    assert client.post("/users/me/otp/start", json={"password": "falsch"}, headers=headers).status_code == 400
    start = client.post("/users/me/otp/start", json={"password": "geheim123"}, headers=headers).json()
    assert start["uri"].startswith("otpauth://totp/")
    db.refresh(user)
    assert user.otp_enabled is False  # noch nicht bestätigt

    wrong = client.post("/users/me/otp/confirm", json={"setup_token": start["setup_token"], "code": "000000"}, headers=headers)
    assert wrong.status_code == 400
    code = pyotp.TOTP(start["secret"]).now()
    assert client.post("/users/me/otp/confirm", json={"setup_token": start["setup_token"], "code": code}, headers=headers).status_code == 204
    db.refresh(user)
    assert user.otp_enabled is True

    # Deaktivieren braucht Passwort und Code
    no_code = client.post("/users/me/otp/disable", json={"password": "geheim123"}, headers=headers)
    assert no_code.status_code == 400
    ok = client.post(
        "/users/me/otp/disable", json={"password": "geheim123", "otp": pyotp.TOTP(start["secret"]).now()}, headers=headers
    )
    assert ok.status_code == 204
    db.refresh(user)
    assert user.otp_enabled is False and user.otp_secret is None


def test_otp_setup_token_of_other_user_rejected(client, db, roles):
    from tests.conftest import add_user, auth  # noqa: PLC0415

    add_user(db, roles, "a", "user")
    add_user(db, roles, "b", "user")
    start = client.post("/users/me/otp/start", json={"password": "geheim123"}, headers=auth(client, "a")).json()
    code = pyotp.TOTP(start["secret"]).now()
    response = client.post(
        "/users/me/otp/confirm", json={"setup_token": start["setup_token"], "code": code}, headers=auth(client, "b")
    )
    assert response.status_code == 400
