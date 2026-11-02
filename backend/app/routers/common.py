import uuid
from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MapOnline, Ort, RegionalMap, Sprache

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


def sync_global_maps_for_place(db: Session, ort: Ort, actor_id: uuid.UUID) -> None:
    global_maps = list(
        db.scalars(select(MapOnline).where(MapOnline.active, MapOnline.global_map))
    )
    existing = {
        item.map_online_id: item
        for item in db.scalars(select(RegionalMap).where(RegionalMap.ort_id == ort.id))
    }
    has_coordinates = ort.active and ort.lat is not None and ort.lon is not None

    for online_map in global_maps:
        mapping = existing.get(online_map.id)
        if has_coordinates:
            if mapping is None:
                db.add(
                    RegionalMap(
                        ort_id=ort.id,
                        map_online_id=online_map.id,
                        created_by=actor_id,
                    )
                )
            elif not mapping.active:
                mapping.active = True
                mapping.last_modified_by = actor_id
        elif mapping is not None and mapping.active:
            mapping.active = False
            mapping.last_modified_by = actor_id
