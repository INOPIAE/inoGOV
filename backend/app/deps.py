import uuid

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Role, User, UserRole

bearer = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)


def get_roles(db: Session, user_id: uuid.UUID) -> list[str]:
    stmt = (
        select(Role.rolename)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id, UserRole.active, Role.active)
        .order_by(Role.rolename)
    )
    return list(db.scalars(stmt))


def get_current_user(creds=Depends(bearer), db: Session = Depends(get_db)) -> User:
    unauthorized = HTTPException(status_code=401, detail="Nicht angemeldet")
    try:
        payload = jwt.decode(creds.credentials, settings.secret_key, algorithms=["HS256"])
        user_id = uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauthorized
    if "purpose" in payload:
        raise unauthorized
    user = db.get(User, user_id)
    if user is None or not user.active or user.blocked:
        raise unauthorized
    return user


def require_roles(*allowed: str):
    def dependency(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        if not set(allowed) & set(get_roles(db, user.id)):
            raise HTTPException(status_code=403, detail="Keine Berechtigung")
        return user

    return dependency


require_admin = require_roles("admin")
require_editor = require_roles("admin", "user")


def read_access(creds=Depends(optional_bearer), db: Session = Depends(get_db)) -> None:
    """Lesezugriff auf die Stammdaten: öffentlich oder nur angemeldet (PUBLIC_SEARCH)."""
    if settings.public_search:
        return
    if creds is None:
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
    get_current_user(creds, db)
