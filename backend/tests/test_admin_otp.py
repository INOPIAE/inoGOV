import pyotp
import pytest

from app.security import create_access_token
from tests.conftest import add_user


def with_otp(db, roles, username, role):
    user = add_user(db, roles, username, role)
    user.otp_secret = pyotp.random_base32()
    user.otp_enabled = True
    db.commit()
    return user, {"Authorization": f"Bearer {create_access_token(str(user.id))}"}


def disable(client, user, headers, password="geheim123"):
    body = {"password": password, "otp": pyotp.TOTP(user.otp_secret).now()}
    return client.post("/users/me/otp/disable", json=body, headers=headers)


def test_admin_cannot_disable_otp(client, db, roles):
    admin, headers = with_otp(db, roles, "boss", "admin")
    assert disable(client, admin, headers).status_code == 403
    db.refresh(admin)
    assert admin.otp_enabled is True and admin.otp_secret is not None


def test_admin_cannot_disable_otp_even_with_valid_credentials_only(client, db, roles):
    admin, headers = with_otp(db, roles, "boss", "admin")
    wrong = client.post("/users/me/otp/disable", json={"password": "falsch"}, headers=headers)
    assert wrong.status_code == 403


def test_user_with_both_roles_is_treated_as_admin(client, db, roles):
    from app.models import UserRole

    user, headers = with_otp(db, roles, "both", "user")
    db.add(UserRole(user_id=user.id, role_id=roles["admin"].id))
    db.commit()
    assert disable(client, user, headers).status_code == 403


def test_normal_user_can_still_disable_otp(client, db, roles):
    user, headers = with_otp(db, roles, "normal", "user")
    assert disable(client, user, headers).status_code == 204
    db.refresh(user)
    assert user.otp_enabled is False


def test_admin_can_still_replace_otp(client, db, roles):
    admin, headers = with_otp(db, roles, "boss", "admin")
    body = {"password": "geheim123", "otp": pyotp.TOTP(admin.otp_secret).now()}
    start = client.post("/users/me/otp/start", json=body, headers=headers)
    assert start.status_code == 200
    code = pyotp.TOTP(start.json()["secret"]).now()
    confirm = client.post(
        "/users/me/otp/confirm", json={"setup_token": start.json()["setup_token"], "code": code}, headers=headers
    )
    assert confirm.status_code == 204
    db.refresh(admin)
    assert admin.otp_enabled is True and admin.otp_secret == start.json()["secret"]


def test_admin_without_otp_can_enable_it(client, db, roles):
    admin = add_user(db, roles, "boss", "admin")
    headers = {"Authorization": f"Bearer {create_access_token(str(admin.id))}"}
    start = client.post("/users/me/otp/start", json={"password": "geheim123"}, headers=headers)
    assert start.status_code == 200
