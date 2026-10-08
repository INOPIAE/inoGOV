import uuid
from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Sprache

T = TypeVar("T")


def get_active(db: Session, model: type[T], item_id: uuid.UUID, label: str) -> T:
    item = db.get(model, item_id)
    if item is None or not item.active:
        raise HTTPException(status_code=404, detail=f"{label} nicht gefunden")
    return item


def ensure_sprache(db: Session, sprache_id: uuid.UUID) -> None:
    sprache = db.get(Sprache, sprache_id)
    if sprache is None or not sprache.active:
        raise HTTPException(status_code=422, detail="Unbekannte Sprache")


def apply_changes(item, changes: dict, actor_id: uuid.UUID) -> None:
    for field, value in changes.items():
        setattr(item, field, value)
    item.last_modified_by = actor_id
