import uuid
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Kreis, MapOnline, Ort, RegionalMap, Role, Sprache, User, UserRole


def test_defaults_are_set(db):
    user = User(username="marcus", email="m@example.com")
    db.add(user)
    db.commit()

    assert isinstance(user.id, uuid.UUID)
    assert user.created_on is not None
    assert user.active is True
    assert user.otp_enabled is False
    assert user.blocked is False
    assert user.unsuccessful_logins == 0


def test_username_unique(db):
    db.add(User(username="a", email="a@example.com"))
    db.commit()
    db.add(User(username="a", email="b@example.com"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_email_required(db):
    db.add(User(username="a"))
    with pytest.raises(IntegrityError):
        db.commit()


def test_user_role_unique_pair(db):
    user = User(username="a", email="a@example.com")
    role = Role(rolename="admin")
    db.add_all([user, role])
    db.commit()
    db.add(UserRole(user_id=user.id, role_id=role.id))
    db.commit()
    db.add(UserRole(user_id=user.id, role_id=role.id))
    with pytest.raises(IntegrityError):
        db.commit()


def test_sprache_unique(db):
    de = dict(sprache="Deutsch", sprache_land="Deutsch", sprache2="de", sprache3="deu", sprache5="de-DE")
    db.add(Sprache(**de))
    db.commit()
    db.add(Sprache(**de))
    with pytest.raises(IntegrityError):
        db.commit()


def test_ort_coordinates(db):
    kreis = Kreis(gov_id="K1")
    db.add(kreis)
    db.commit()
    ort = Ort(kreis_id=kreis.id, gov_id="O1", lon=Decimal("22.858178"), lat=Decimal("49.525716"))
    db.add(ort)
    db.commit()
    db.refresh(ort)
    assert ort.lat == Decimal("49.525716")


def test_online_map_and_regional_map_audit_fields_and_unique_assignment(db):
    ort = Ort(lat=Decimal("49.5"), lon=Decimal("22.5"))
    online_map = MapOnline(
        mapname="OpenStreetMap",
        map_short="OSM",
        map_url_basis="https://www.openstreetmap.org/",
        map_url_pattern="?mlat={lat}&mlon={lon}",
        global_map=True,
    )
    db.add_all([ort, online_map])
    db.flush()
    mapping = RegionalMap(ort_id=ort.id, map_online_id=online_map.id)
    db.add(mapping)
    db.commit()

    assert isinstance(online_map.id, uuid.UUID)
    assert online_map.created_on is not None and online_map.active is True
    assert mapping.created_on is not None and mapping.active is True
    assert mapping.map_online.map_short == "OSM"

    db.add(RegionalMap(ort_id=ort.id, map_online_id=online_map.id))
    with pytest.raises(IntegrityError):
        db.commit()
