"""ImportStumpp: Orte der Karte Stumpp aus einer CSV-Datei (Ortsname; Kreisname; Koordinate)."""
import logging
import re
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.imports.common import ImportAborted, ImportResult, RowError
from app.models import Kreis, Kreisname, MapReference, Ort, Ortsname, Sprache

logger = logging.getLogger(__name__)

KEY = "ImportStumpp"
KARTE = "Stumpp"
COLUMNS = ["place_name_pl", "district_name_pl", "coordinate"]
MAX_PLACE, MAX_DISTRICT, MAX_COORDINATE = 255, 50, 2


def norm(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip().casefold()


def validate(values: list[str]) -> tuple[str, str, str]:
    if len(values) < 3:
        raise RowError("columns", "Weniger als 3 Spalten")
    place, district, coordinate = (v.strip() for v in values[:3])
    if not place:
        raise RowError("empty_place", "Ortsname fehlt")
    if not district:
        raise RowError("empty_district", "Kreisname fehlt")
    if not coordinate:
        raise RowError("empty_coordinate", "Koordinate fehlt")
    if len(place) > MAX_PLACE:
        raise RowError("place_too_long", f"Ortsname länger als {MAX_PLACE} Zeichen")
    if len(district) > MAX_DISTRICT:
        raise RowError("district_too_long", f"Kreisname länger als {MAX_DISTRICT} Zeichen")
    if len(coordinate) > MAX_COORDINATE:
        raise RowError("coordinate_too_long", f"Koordinate länger als {MAX_COORDINATE} Zeichen")
    return place, district, coordinate


def run(db: Session, rows: list[tuple[int, list[str]]], actor_id: uuid.UUID) -> ImportResult:
    german = db.scalar(select(Sprache).where(Sprache.sprache2 == "de", Sprache.active))
    if german is None:
        raise ImportAborted("no_german", "Sprache 'de' fehlt")

    districts: dict[str, uuid.UUID] = {}
    stmt = (
        select(Kreisname.kreisname, Kreisname.kreis_id)
        .join(Kreis, Kreis.id == Kreisname.kreis_id)
        .where(Kreisname.sprache_id == german.id, Kreisname.active, Kreis.active)
    )
    for name, kreis_id in db.execute(stmt):
        districts.setdefault(norm(name), kreis_id)

    result = ImportResult()
    for line, values in rows:
        result.total += 1
        try:
            place, district, coordinate = validate(values)
            created = None
            with db.begin_nested():
                kreis_id = districts.get(norm(district))
                if kreis_id is None:
                    kreis = Kreis(created_by=actor_id)
                    db.add(kreis)
                    db.flush()
                    db.add(Kreisname(kreis_id=kreis.id, sprache_id=german.id, kreisname=district, created_by=actor_id))
                    kreis_id = kreis.id
                    created = {"id": str(kreis.id), "name": district}
                ort = Ort(kreis_id=kreis_id, created_by=actor_id)
                db.add(ort)
                db.flush()
                db.add(Ortsname(ort_id=ort.id, sprache_id=german.id, ortsname=place, created_by=actor_id))
                db.add(MapReference(ort_id=ort.id, koordinate=coordinate, karte=KARTE, created_by=actor_id))
                db.flush()
            if created:
                districts[norm(district)] = kreis_id
                result.created_kreise.append(created)
            result.imported += 1
        except RowError as exc:
            result.errors.append({"line": line, "code": exc.code, "message": str(exc), "values": values})
        except Exception as exc:
            logger.exception("%s Zeile %s", KEY, line)
            result.errors.append(
                {"line": line, "code": "unexpected", "message": f"Unerwarteter Fehler ({type(exc).__name__})", "values": values}
            )
    for error in result.errors:
        logger.warning("%s Zeile %s: %s", KEY, error["line"], error["message"])
    return result
