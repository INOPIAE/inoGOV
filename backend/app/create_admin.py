"""Legt den ersten Admin an: python -m app.create_admin --username NAME --email MAIL"""
import argparse
import getpass
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Role, User, UserRole
from app.security import hash_password


def create_admin(db: Session, username: str, email: str, password: str) -> User:
    if db.scalar(select(User.id).where(User.username == username)):
        raise ValueError(f"Benutzer '{username}' existiert bereits")
    if len(password) < 8:
        raise ValueError("Passwort muss mindestens 8 Zeichen haben")
    role = db.scalar(select(Role).where(Role.rolename == "admin"))
    if role is None:
        raise ValueError("Rolle 'admin' fehlt (alembic upgrade head ausgeführt?)")
    user = User(username=username, email=email, hashed_password=hash_password(password))
    db.add(user)
    db.flush()
    db.add(UserRole(user_id=user.id, role_id=role.id))
    db.commit()
    return user


def main() -> int:
    parser = argparse.ArgumentParser(description="Ersten Admin anlegen")
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()

    password = getpass.getpass("Passwort: ")
    if password != getpass.getpass("Passwort wiederholen: "):
        print("Passwörter stimmen nicht überein", file=sys.stderr)
        return 1
    try:
        with SessionLocal() as db:
            create_admin(db, args.username, args.email, password)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Admin '{args.username}' angelegt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
