import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import read_access, require_editor
from app.models import MapOnline, Ort, RegionalMap, User
from app.routers.common import apply_changes, get_active
from app.schemas_geo import MapOnlineCreate, MapOnlineOut, MapOnlineUpdate, RegionalMapCreate, RegionalMapOut

router = APIRouter(tags=["online maps"])


def _check_map_unique(db: Session, mapname: str | None, map_short: str | None, exclude_id=None) -> None:
    conflicts = []
    if mapname is not None:
        conflicts.append(MapOnline.mapname == mapname)
    if map_short is not None:
        conflicts.append(MapOnline.map_short == map_short)
    if conflicts:
        query = select(MapOnline.id).where(or_(*conflicts))
        if exclude_id is not None:
            query = query.where(MapOnline.id != exclude_id)
        if db.scalar(query):
            raise HTTPException(status_code=409, detail="Kartenname oder Kürzel bereits vergeben")


def _sync_global_provider(db: Session, online_map: MapOnline, actor_id: uuid.UUID) -> None:
    if online_map.global_map:
        places = db.scalars(
            select(Ort).where(Ort.active, Ort.lat.is_not(None), Ort.lon.is_not(None))
        )
        for ort in places:
            mapping = db.scalar(
                select(RegionalMap).where(
                    RegionalMap.ort_id == ort.id,
                    RegionalMap.map_online_id == online_map.id,
                )
            )
            if mapping is None:
                db.add(RegionalMap(ort_id=ort.id, map_online_id=online_map.id, created_by=actor_id))
            elif not mapping.active:
                mapping.active = True
                mapping.last_modified_by = actor_id
    else:
        mappings = db.scalars(
            select(RegionalMap).where(RegionalMap.map_online_id == online_map.id, RegionalMap.active)
        )
        for mapping in mappings:
            mapping.active = False
            mapping.last_modified_by = actor_id


@router.get("/map-online", response_model=list[MapOnlineOut], dependencies=[Depends(read_access)])
def list_map_online(
    global_only: bool | None = None,
    db: Session = Depends(get_db),
):
    query = select(MapOnline).where(MapOnline.active)
    if global_only is not None:
        query = query.where(MapOnline.global_map.is_(global_only))
    return list(db.scalars(query.order_by(MapOnline.map_short, MapOnline.mapname)))


@router.post("/map-online", response_model=MapOnlineOut, status_code=201)
def create_map_online(
    data: MapOnlineCreate,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    _check_map_unique(db, data.mapname, data.map_short)
    online_map = MapOnline(
        mapname=data.mapname.strip(),
        map_short=data.map_short.strip(),
        map_url_basis=data.map_url_basis.strip(),
        map_url_pattern=data.map_url_pattern.strip(),
        global_map=data.global_,
        created_by=user.id,
    )
    db.add(online_map)
    db.flush()
    if online_map.global_map:
        _sync_global_provider(db, online_map, user.id)
    db.commit()
    db.refresh(online_map)
    return online_map


@router.patch("/map-online/{map_online_id}", response_model=MapOnlineOut)
def update_map_online(
    map_online_id: uuid.UUID,
    data: MapOnlineUpdate,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    online_map = get_active(db, MapOnline, map_online_id, "Karte")
    was_global = online_map.global_map
    changes = data.model_dump(exclude_unset=True)
    _check_map_unique(db, changes.get("mapname"), changes.get("map_short"), online_map.id)
    if "global_" in changes:
        changes["global_map"] = changes.pop("global_")
    if "mapname" in changes:
        changes["mapname"] = changes["mapname"].strip()
    if "map_short" in changes:
        changes["map_short"] = changes["map_short"].strip()
    if "map_url_basis" in changes:
        changes["map_url_basis"] = changes["map_url_basis"].strip()
    if "map_url_pattern" in changes:
        changes["map_url_pattern"] = changes["map_url_pattern"].strip()
    apply_changes(online_map, changes, user.id)
    if was_global != online_map.global_map:
        _sync_global_provider(db, online_map, user.id)
    db.commit()
    db.refresh(online_map)
    return online_map


@router.delete("/map-online/{map_online_id}", status_code=204)
def delete_map_online(
    map_online_id: uuid.UUID,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    online_map = get_active(db, MapOnline, map_online_id, "Karte")
    referenced = db.scalar(
        select(RegionalMap.id).where(RegionalMap.map_online_id == online_map.id, RegionalMap.active).limit(1)
    )
    if referenced:
        raise HTTPException(status_code=409, detail="Karte wird noch Orten zugeordnet")
    apply_changes(online_map, {"active": False}, user.id)
    db.commit()
    return Response(status_code=204)


@router.get("/regional-maps", response_model=list[RegionalMapOut], dependencies=[Depends(read_access)])
def list_regional_maps(
    ort_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    query = (
        select(RegionalMap)
        .join(MapOnline, MapOnline.id == RegionalMap.map_online_id)
        .where(RegionalMap.active, MapOnline.active)
    )
    if ort_id is not None:
        query = query.where(RegionalMap.ort_id == ort_id)
    return list(db.scalars(query.order_by(RegionalMap.created_on, RegionalMap.id)))


@router.post("/regional-maps", response_model=RegionalMapOut, status_code=201)
def create_regional_map(
    data: RegionalMapCreate,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    get_active(db, Ort, data.ort_id, "Ort")
    get_active(db, MapOnline, data.map_online_id, "Karte")
    existing = db.scalar(
        select(RegionalMap).where(
            RegionalMap.ort_id == data.ort_id,
            RegionalMap.map_online_id == data.map_online_id,
        )
    )
    if existing is not None and existing.active:
        raise HTTPException(status_code=409, detail="Karte ist dem Ort bereits zugeordnet")
    if existing is not None:
        existing.active = True
        existing.last_modified_by = user.id
        db.commit()
        db.refresh(existing)
        return existing
    mapping = RegionalMap(**data.model_dump(), created_by=user.id)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.delete("/regional-maps/{regional_map_id}", status_code=204)
def delete_regional_map(
    regional_map_id: uuid.UUID,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    mapping = get_active(db, RegionalMap, regional_map_id, "Kartenverknüpfung")
    apply_changes(mapping, {"active": False}, user.id)
    db.commit()
    return Response(status_code=204)