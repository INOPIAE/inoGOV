import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.deps import read_access, require_editor
from app.models import Kreis, MapReference, Ort, Ortsname, User
from app.routers.common import apply_changes, ensure_sprache, get_active
from app.schemas_geo import (
    KarteIn,
    KarteOut,
    OrtCreate,
    OrtOut,
    OrtsnameIn,
    OrtsnameOut,
    OrtUpdate,
    OrtStatistics,
)

router = APIRouter(prefix="/orte", tags=["orte"])


def to_out(db: Session, orte: list[Ort]) -> list[OrtOut]:
    ids = [o.id for o in orte]
    names = db.scalars(select(Ortsname).where(Ortsname.ort_id.in_(ids), Ortsname.active)).all()
    maps = db.scalars(select(MapReference).where(MapReference.ort_id.in_(ids), MapReference.active)).all()
    result = []
    for ort in orte:
        out = OrtOut.model_validate(ort)
        out.namen = [OrtsnameOut.model_validate(n) for n in names if n.ort_id == ort.id]
        out.karten = [KarteOut.model_validate(m) for m in maps if m.ort_id == ort.id]
        result.append(out)
    return result


def ensure_kreis(db: Session, kreis_id: uuid.UUID | None) -> None:
    if kreis_id is None:
        return
    kreis = db.get(Kreis, kreis_id)
    if kreis is None or not kreis.active:
        raise HTTPException(status_code=422, detail="Unbekannter Kreis")


@router.get("", response_model=list[OrtOut], dependencies=[Depends(read_access)])
def list_orte(
    q: str | None = None,
    kreis_id: uuid.UUID | None = None,
    sprache_id: uuid.UUID | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = select(Ort).where(Ort.active)
    if kreis_id:
        stmt = stmt.where(Ort.kreis_id == kreis_id)
    if q:
        matching = select(Ortsname.ort_id).where(
            Ortsname.active, Ortsname.ortsname.icontains(q, autoescape=True)
        )
        if sprache_id:
            matching = matching.where(Ortsname.sprache_id == sprache_id)
        stmt = stmt.where(Ort.id.in_(matching))
    orte = db.scalars(stmt.order_by(Ort.gov_id, Ort.id).limit(limit).offset(offset)).all()
    return to_out(db, list(orte))


@router.get("/{ort_id}", response_model=OrtOut, dependencies=[Depends(read_access)])
def get_ort(ort_id: uuid.UUID, db: Session = Depends(get_db)):
    return to_out(db, [get_active(db, Ort, ort_id, "Ort")])[0]


@router.post("", response_model=OrtOut, status_code=201)
def create_ort(data: OrtCreate, user: User = Depends(require_editor), db: Session = Depends(get_db)):
    ensure_kreis(db, data.kreis_id)
    for name in data.namen:
        ensure_sprache(db, name.sprache_id)
    ort = Ort(**data.model_dump(exclude={"namen", "karten"}), created_by=user.id)
    db.add(ort)
    db.flush()
    db.add_all(Ortsname(ort_id=ort.id, created_by=user.id, **n.model_dump()) for n in data.namen)
    db.add_all(MapReference(ort_id=ort.id, created_by=user.id, **k.model_dump()) for k in data.karten)
    db.commit()
    return to_out(db, [ort])[0]


@router.patch("/{ort_id}", response_model=OrtOut)
def update_ort(
    ort_id: uuid.UUID,
    data: OrtUpdate,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    ort = get_active(db, Ort, ort_id, "Ort")
    changes = data.model_dump(exclude_unset=True)
    ensure_kreis(db, changes.get("kreis_id"))
    apply_changes(ort, changes, user.id)
    db.commit()
    return to_out(db, [ort])[0]


@router.delete("/{ort_id}", status_code=204)
def delete_ort(ort_id: uuid.UUID, user: User = Depends(require_editor), db: Session = Depends(get_db)):
    apply_changes(get_active(db, Ort, ort_id, "Ort"), {"active": False}, user.id)
    db.commit()
    return Response(status_code=204)


@router.post("/{ort_id}/namen", response_model=OrtsnameOut, status_code=201)
def add_name(
    ort_id: uuid.UUID,
    data: OrtsnameIn,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    get_active(db, Ort, ort_id, "Ort")
    ensure_sprache(db, data.sprache_id)
    name = Ortsname(ort_id=ort_id, created_by=user.id, **data.model_dump())
    db.add(name)
    db.commit()
    return name


@router.delete("/{ort_id}/namen/{name_id}", status_code=204)
def delete_name(
    ort_id: uuid.UUID,
    name_id: uuid.UUID,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    name = get_active(db, Ortsname, name_id, "Ortsname")
    if name.ort_id != ort_id:
        raise HTTPException(status_code=404, detail="Ortsname nicht gefunden")
    apply_changes(name, {"active": False}, user.id)
    db.commit()
    return Response(status_code=204)


@router.post("/{ort_id}/karten", response_model=KarteOut, status_code=201)
def add_karte(
    ort_id: uuid.UUID,
    data: KarteIn,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    get_active(db, Ort, ort_id, "Ort")
    karte = MapReference(ort_id=ort_id, created_by=user.id, **data.model_dump())
    db.add(karte)
    db.commit()
    return karte


@router.delete("/{ort_id}/karten/{karte_id}", status_code=204)
def delete_karte(
    ort_id: uuid.UUID,
    karte_id: uuid.UUID,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    karte = get_active(db, MapReference, karte_id, "Karte")
    if karte.ort_id != ort_id:
        raise HTTPException(status_code=404, detail="Karte nicht gefunden")
    apply_changes(karte, {"active": False}, user.id)
    db.commit()
    return Response(status_code=204)

@router.get("/statistics/", response_model=OrtStatistics)
def ort_statistics(
    db: Session = Depends(get_db),
):
    print("ort_statistics wurde aufgerufen")
    total = db.scalar(select(func.count()).select_from(Ort).where(Ort.active))
    gov = db.scalar(select(func.count()).select_from(Ort).where(Ort.active, Ort.gov_id.isnot(None)))
    geo = db.scalar(select(func.count()).select_from(Ort).where(Ort.active, Ort.lon.isnot(None), Ort.lat.isnot(None)))
    return OrtStatistics(total=total, gov=gov, geo=geo)
