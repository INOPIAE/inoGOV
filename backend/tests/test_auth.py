from datetime import UTC, datetime, timedelta

import pyotp
import pytest

from app.lockout import lock_duration, parse_tiers
from app.models import User
from app.security import hash_password

TIERS = parse_tiers("3:3,5:10,10:60")


@pytest.mark.parametrize(
    "failed, minutes",
    [(0, None), (2, None), (3, 3), (4, 3), (5, 10), (9, 10), (10, 60), (25, 60)],
)
def test_lock_duration(failed, minutes):
    expected = timedelta(minutes=minutes) if minutes else None
    assert lock_duration(failed, TIERS) == expected


def test_parse_tiers_sorts():
    assert parse_tiers("10:60, 3:3") == [(3, 3), (10, 60)]


def make_user(db, **kwargs):
    user = User(username="marcus", email="m@example.com", hashed_password=hash_password("geheim"), **kwargs)
    db.add(user)
    db.commit()
    return user


def login(client, password="geheim", **extra):
    return client.post("/auth/login", json={"username": "marcus", "password": password, **extra})


def test_login_success_resets_counter(client, db):
    user = make_user(db, unsuccessful_logins=2)
    response = login(client)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    db.refresh(user)
    assert user.unsuccessful_logins == 0
    assert user.last_login is not None


def test_unknown_user(client):
    assert client.post("/auth/login", json={"username": "x", "password": "y"}).status_code == 401


def test_three_failures_lock_for_three_minutes(client, db):
    user = make_user(db)
    for _ in range(3):
        assert login(client, "falsch").status_code == 401
    response = login(client)  # richtiges Passwort, aber gesperrt
    assert response.status_code == 423
    assert 0 < int(response.headers["Retry-After"]) <= 180
    db.refresh(user)
    assert user.unsuccessful_logins == 3


def test_lock_expires(client, db):
    user = make_user(db, unsuccessful_logins=3, blocked_until=datetime.now(UTC) - timedelta(seconds=1))
    assert login(client).status_code == 200
    db.refresh(user)
    assert user.blocked_until is None


@pytest.mark.parametrize("before, minutes", [(4, 10), (9, 60)])
def test_higher_tiers(client, db, before, minutes):
    user = make_user(db, unsuccessful_logins=before)
    assert login(client, "falsch").status_code == 401
    db.refresh(user)
    remaining = user.blocked_until.replace(tzinfo=UTC) - datetime.now(UTC)
    assert timedelta(minutes=minutes) - timedelta(seconds=10) < remaining <= timedelta(minutes=minutes)


def test_manually_blocked(client, db):
    make_user(db, blocked=True)
    assert login(client).status_code == 403


def test_otp_required(client, db):
    secret = pyotp.random_base32()
    make_user(db, otp_enabled=True, otp_secret=secret)
    assert login(client).status_code == 401
    assert login(client, otp=pyotp.TOTP(secret).now()).status_code == 200
