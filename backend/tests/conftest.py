import os

os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, Role, User, UserRole
from app.security import hash_password


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def roles(db):
    admin, user = Role(rolename="admin"), Role(rolename="user")
    db.add_all([admin, user])
    db.commit()
    return {"admin": admin, "user": user}


def add_user(db, roles, username, role, password="geheim123"):
    u = User(username=username, email=f"{username}@example.com", hashed_password=hash_password(password))
    db.add(u)
    db.flush()
    db.add(UserRole(user_id=u.id, role_id=roles[role].id))
    db.commit()
    return u


def auth(client, username, password="geheim123"):
    token = client.post("/auth/login", json={"username": username, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin(db, roles):
    return add_user(db, roles, "boss", "admin")


@pytest.fixture
def admin_h(client, admin):
    return auth(client, "boss")


@pytest.fixture
def user_h(client, db, roles):
    add_user(db, roles, "normal", "user")
    return auth(client, "normal")


