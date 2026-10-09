"""ImportLueckKoordinaten: Planquadrate der Karte Lück mit Pixelbereich und Gradangaben (Excel oder CSV).

Aufbau der Datei:
  Bildbreite_px <Zahl>
  Bildhoehe_px  <Zahl>
  (Leerzeile)
  Koordinate X1 Y1 X2 Y2 Breite_px Hoehe_px Laenge_von Laenge_bis Breite_von Breite_bis
  A1 36 35 357 248 321 213 42 42,5 51 50
"""
import logging
import uuid
from decimal import Decimal, InvalidOperation

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.imports.common import ImportAborted, ImportResult, RowError
from app.models import MapGrid, MapImage

logger = logging.getLogger(__name__)

KEY = "ImportLueckKoordinaten"
KARTE = "Lück"
IMAGE_FILE = "Lueck1927_gr.jpg"
COLUMNS = [
    "Koordinate", "X1", "Y1", "X2", "Y2", "Breite_px", "Hoehe_px",
    "Laenge_von", "Laenge_bis", "Breite_von", "Breite_bis",
]
INT_COLUMNS = ["X1", "Y1", "X2", "Y2", "Breite_px", "Hoehe_px"]
DEGREE_COLUMNS = ["Laenge_von", "Laenge_bis", "Breite_von", "Breite_bis"]
MAX_COORDINATE = 10


def to_decimal(text: str) -> Decimal:
    try:
        value = Decimal(text.strip().replace(",", "."))
    except InvalidOperation:
        raise ValueError(text)
    if not value.is_finite():
        raise ValueError(text)
    return value


def to_int(text: str) -> int:
    value = to_decimal(text)
    if value != value.to_integral_value():
        raise ValueError(text)
    return int(value)


def find_layout(rows):
    """Bildgröße aus den Zeilen vor der Tabelle und Spaltenpositionen der Kopfzeile."""
    sizes: dict[str, str] = {}
    for position, (_, cells) in enumerate(rows):
        first = cells[0].strip().casefold() if cells else ""
        if "koordinate" in (c.strip().casefold() for c in cells):
            break
        if first in ("bildbreite_px", "bildhoehe_px") and len(cells) > 1:
            sizes[first] = cells[1]
    else:
        raise ImportAborted("no_header", "Kopfzeile mit 'Koordinate' fehlt")

    try:
        width, height = to_int(sizes["bildbreite_px"]), to_int(sizes["bildhoehe_px"])
        if width <= 0 or height <= 0:
            raise ValueError
    except (KeyError, ValueError):
        raise ImportAborted("no_image_size", "Bildbreite_px / Bildhoehe_px fehlen oder sind ungültig")

    header = [c.strip().casefold() for c in rows[position][1]]
    try:
        columns = {name: header.index(name.casefold()) for name in COLUMNS}
    except ValueError:
        raise ImportAborted("missing_columns", "Pflichtspalten fehlen")
    return width, height, columns, rows[position + 1 :]


def validate(cells: list[str], columns: dict[str, int], width: int, height: int) -> dict:
    def cell(name):
        index = columns[name]
        return cells[index].strip() if index < len(cells) else ""

    coordinate = cell("Koordinate")
    if not coordinate:
        raise RowError("empty_coordinate", "Koordinate fehlt")
    if len(coordinate) > MAX_COORDINATE:
        raise RowError("coordinate_too_long", f"Koordinate länger als {MAX_COORDINATE} Zeichen")

    values: dict = {"koordinate": coordinate}
    try:
        for name in INT_COLUMNS:
            values[name.lower()] = to_int(cell(name))
        for name in DEGREE_COLUMNS:
            number = to_decimal(cell(name))
            if abs(number) > 180:
                raise ValueError(name)
            values[name.lower()] = number
    except ValueError as exc:
        raise RowError("bad_number", f"Ungültige Zahl: {exc}")

    if values["x2"] <= values["x1"] or values["y2"] <= values["y1"]:
        raise RowError("invalid_area", "Bereich ist leer oder X2/Y2 nicht größer als X1/Y1")
    if min(values["x1"], values["y1"]) < 0 or values["x2"] > width or values["y2"] > height:
        raise RowError("outside_image", "Bereich liegt außerhalb des Bildes")
    return values


def run(db: Session, rows: list[tuple[int, list[str]]], actor_id: uuid.UUID) -> ImportResult:
    width, height, columns, data_rows = find_layout(rows)

    image = db.scalar(select(MapImage).where(MapImage.karte == KARTE))
    if image is None:
        db.add(MapImage(karte=KARTE, filename=IMAGE_FILE, width_px=width, height_px=height, created_by=actor_id))
    else:
        image.filename, image.width_px, image.height_px = IMAGE_FILE, width, height
        image.active = True
        image.last_modified_by = actor_id
    db.flush()

    result = ImportResult()
    for line, cells in data_rows:
        result.total += 1
        try:
            values = validate(cells, columns, width, height)
            updated = False
            with db.begin_nested():
                existing = db.scalar(
                    select(MapGrid)
                    .where(
                        MapGrid.karte == KARTE,
                        func.lower(MapGrid.koordinate) == values["koordinate"].lower(),
                        MapGrid.active,
                    )
                    .order_by(MapGrid.created_on.desc())
                    .limit(1)
                )
                if existing is None:
                    db.add(MapGrid(karte=KARTE, created_by=actor_id, **values))
                else:
                    for field, value in values.items():
                        setattr(existing, field, value)
                    existing.last_modified_by = actor_id
                    updated = True
                db.flush()
            result.imported += 1
            result.updated += updated
        except RowError as exc:
            result.errors.append({"line": line, "code": exc.code, "message": str(exc), "values": cells})
        except Exception as exc:
            logger.exception("%s Zeile %s", KEY, line)
            result.errors.append(
                {"line": line, "code": "unexpected", "message": f"Unerwarteter Fehler ({type(exc).__name__})", "values": cells}
            )
    for error in result.errors:
        logger.warning("%s Zeile %s: %s", KEY, error["line"], error["message"])
    return result
