import pyotp
import pytest

from app.config import settings
from app.models import UserRole
from app.security import create_access_token
from tests.conftest import add_user, auth


@pytest.fixture(autouse=True)
def required(monkeypatch):
    monkeypatch.setattr(settings, "admin_otp_required", True)


def token(user):
    return {"Authorization": f"Bearer {create_access_token(str(user.id))}"}


@pytest.fixture
def admin_no_otp(db, roles):
    return add_user(db, roles, "boss", "admin")


def test_admin_without_otp_can_still_log_in(client, admin_no_otp):
    response = client.post("/auth/login", json={"username": "boss", "password": "geheim123"})
    assert response.status_code == 200


def test_me_reports_that_setup_is_required(client, admin_no_otp):
    me = client.get("/users/me", headers=token(admin_no_otp))
    assert me.status_code == 200
    assert me.json()["otp_setup_required"] is True


@pytest.mark.parametrize(
    "method, path, body",
    [
        ("get", "/users", None),
        ("post", "/users/invite", {"email": "a@example.com"}),
        ("post", "/kreise", {}),
        ("post", "/orte", {}),
        ("post", "/sprachen", {"sprache": "x", "sprache_land": "x", "sprache2": "xx", "sprache3": "xxx", "sprache5": "xx-XX"}),
        ("patch", "/users/me", {"first_name": "Ann"}),
        ("put", "/users/me/password", {"current_password": "geheim123", "new_password": "neuespass1"}),
        ("post", "/users/me/otp/disable", {"password": "geheim123"}),
    ],
)
def test_everything_else_is_blocked_until_otp_is_set_up(client, admin_no_otp, method, path, body):
    response = getattr(client, method)(path, headers=token(admin_no_otp), **({"json": body} if body is not None else {}))
    assert response.status_code == 403
    assert response.json()["detail"] == "otp_setup_required"


def test_blocked_admin_cannot_use_reads_in_private_mode(client, admin_no_otp, monkeypatch):
    monkeypatch.setattr(settings, "public_search", False)
    assert client.get("/orte", headers=token(admin_no_otp)).status_code == 403


def test_public_reads_are_unaffected(client, admin_no_otp):
    assert client.get("/orte", headers=token(admin_no_otp)).status_code == 200
    assert client.get("/orte").status_code == 200


def test_setup_lifts_the_restriction(client, admin_no_otp, db):
    headers = token(admin_no_otp)
    start = client.post("/users/me/otp/start", json={"password": "geheim123"}, headers=headers)
    assert start.status_code == 200
    wrong = client.post(
        "/users/me/otp/confirm", json={"setup_token": start.json()["setup_token"], "code": "000000"}, headers=headers
    )
    assert wrong.status_code == 400
    assert client.get("/users", headers=headers).status_code == 403  # noch nicht bestätigt

    code = pyotp.TOTP(start.json()["secret"]).now()
    done = client.post(
        "/users/me/otp/confirm", json={"setup_token": start.json()["setup_token"], "code": code}, headers=headers
    )
    assert done.status_code == 204
    assert client.get("/users", headers=headers).status_code == 200
    assert client.get("/users/me", headers=headers).json()["otp_setup_required"] is False


def test_setup_still_needs_the_password(client, admin_no_otp):
    response = client.post("/users/me/otp/start", json={"password": "falsch"}, headers=token(admin_no_otp))
    assert response.status_code == 400


def test_login_afterwards_asks_for_the_code(client, admin_no_otp, db):
    admin_no_otp.otp_secret = pyotp.random_base32()
    admin_no_otp.otp_enabled = True
    db.commit()
    response = client.post("/auth/login", json={"username": "boss", "password": "geheim123"})
    assert response.json()["detail"] == "otp_required"


def test_admin_with_otp_is_not_restricted(client, admin_no_otp, db):
    admin_no_otp.otp_secret = pyotp.random_base32()
    admin_no_otp.otp_enabled = True
    db.commit()
    assert client.get("/users", headers=token(admin_no_otp)).status_code == 200


def test_normal_users_are_not_restricted(client, db, roles):
    user = add_user(db, roles, "normal", "user")
    headers = token(user)
    assert client.get("/users/me", headers=headers).json()["otp_setup_required"] is False
    assert client.post("/kreise", json={}, headers=headers).status_code == 201


def test_user_who_is_also_admin_is_restricted(client, db, roles):
    user = add_user(db, roles, "both", "user")
    db.add(UserRole(user_id=user.id, role_id=roles["admin"].id))
    db.commit()
    assert client.post("/kreise", json={}, headers=token(user)).status_code == 403


def test_switch_turns_the_requirement_off(client, admin_no_otp, monkeypatch):
    monkeypatch.setattr(settings, "admin_otp_required", False)
    assert client.get("/users", headers=token(admin_no_otp)).status_code == 200
    assert client.get("/users/me", headers=token(admin_no_otp)).json()["otp_setup_required"] is False


def test_password_reset_link_still_works_for_blocked_admin(client, admin_no_otp, monkeypatch):
    from app import mail

    sent = []
    monkeypatch.setattr(mail, "send_mail", lambda to, subject, body: sent.append(body))
    client.post("/auth/forgot-password", json={"email": "boss@example.com"})
    assert len(sent) == 1
    assert auth(client, "boss")  # Passwort-Login funktioniert weiterhin
