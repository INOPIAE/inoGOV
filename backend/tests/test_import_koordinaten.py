import io

import pytest
from openpyxl import Workbook

from app.config import settings
from app.models import MapGrid, MapImage


@pytest.fixture(autouse=True)
def archive_dir(monkeypatch, tmp_path):
    path = tmp_path / "archive"
    monkeypatch.setattr(settings, "import_archive_dir", str(path))
    return path


KEY = "ImportLueckKoordinaten"
HEADER = ["Koordinate", "X1", "Y1", "X2", "Y2", "Breite_px", "Hoehe_px", "Laenge_von", "Laenge_bis", "Breite_von", "Breite_bis"]
A1 = ["A1", 36, 35, 357, 248, 321, 213, 42, 42.5, 51, 50]
B1 = ["B1", 357, 35, 677, 248, 320, 213, 42.5, 43, 51, 50]


def sheet(rows, width=2000, height=1362):
    """Aufbau wie in der Originaldatei: Bildgröße, Leerzeile, Kopfzeile, Daten."""
    return [["Bildbreite_px", width], ["Bildhoehe_px", height], [], HEADER, *rows]


def xlsx(rows):
    workbook = Workbook()
    worksheet = workbook.active
    for row in rows:
        worksheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def text(rows, sep="\t", encoding="utf-8"):
    return ("\n".join(sep.join("" if c is None else str(c) for c in row) for row in rows) + "\n").encode(encoding)


def upload(client, headers, content, name="koordinaten.xlsx"):
    return client.post(f"/imports/{KEY}", files={"file": (name, content)}, headers=headers)


def grid(db):
    return {g.koordinate: g for g in db.query(MapGrid).all()}


def test_imports_excel_file(client, admin_h, db, admin):
    report = upload(client, admin_h, xlsx(sheet([A1, B1]))).json()
    assert (report["total"], report["imported"], report["failed"]) == (2, 2, 0)

    (image,) = db.query(MapImage).all()
    assert (image.karte, image.filename, image.width_px, image.height_px) == ("Lück", "Lueck1927_gr.jpg", 2000, 1362)
    squares = grid(db)
    a1 = squares["A1"]
    assert (a1.karte, a1.x1, a1.y1, a1.x2, a1.y2, a1.breite_px, a1.hoehe_px) == ("Lück", 36, 35, 357, 248, 321, 213)
    assert [float(v) for v in (a1.laenge_von, a1.laenge_bis, a1.breite_von, a1.breite_bis)] == [42, 42.5, 51, 50]
    assert float(squares["B1"].laenge_bis) == 43
    assert a1.created_by == admin.id and image.created_by == admin.id


def test_text_paste_with_decimal_commas(client, admin_h, db):
    rows = sheet([["A1", 36, 35, 357, 248, 321, 213, "42", "42,5", "51", "50"]])
    report = upload(client, admin_h, text(rows), name="koordinaten.txt").json()
    assert report["imported"] == 1
    assert float(grid(db)["A1"].laenge_bis) == 42.5


def test_csv_with_semicolons_and_cp1250(client, admin_h, db):
    rows = sheet([["A1", 36, 35, 357, 248, 321, 213, "42", "42,5", "51", "50"]])
    assert upload(client, admin_h, text(rows, sep=";", encoding="cp1250"), name="k.csv").json()["imported"] == 1


def test_excel_numbers_stored_as_text_are_accepted(client, admin_h, db):
    rows = sheet([["A1", "36", "35", "357", "248", "321", "213", "42", "42,5", "51", "50"]])
    assert upload(client, admin_h, xlsx(rows)).json()["imported"] == 1
    assert float(grid(db)["A1"].laenge_bis) == 42.5


def test_columns_may_be_in_any_order(client, admin_h, db):
    order = list(reversed(range(len(HEADER))))
    rows = [["Bildbreite_px", 2000], ["Bildhoehe_px", 1362], [], [HEADER[i] for i in order], [A1[i] for i in order]]
    assert upload(client, admin_h, xlsx(rows)).json()["imported"] == 1
    assert grid(db)["A1"].x2 == 357


def test_image_size_is_stored_once_per_map_and_updated(client, admin_h, db):
    upload(client, admin_h, xlsx(sheet([A1])))
    upload(client, admin_h, xlsx(sheet([A1], width=3000, height=2000)))
    (image,) = db.query(MapImage).all()
    assert (image.width_px, image.height_px) == (3000, 2000)
    assert db.query(MapGrid).count() == 2  # Duplikate werden nicht geprüft


def test_row_errors_are_reported_and_valid_rows_still_import(client, admin_h, db):
    rows = sheet(
        [
            A1,
            ["", 1, 1, 2, 2, 1, 1, 1, 2, 3, 4],  # Koordinate fehlt
            ["C1", "x", 1, 2, 2, 1, 1, 1, 2, 3, 4],  # keine Zahl
            ["C2", 1.5, 1, 2, 2, 1, 1, 1, 2, 3, 4],  # Pixel nicht ganzzahlig
            ["C3", 10, 10, 10, 20, 0, 10, 1, 2, 3, 4],  # leerer Bereich
            ["C4", 10, 10, 5, 20, 0, 10, 1, 2, 3, 4],  # umgekehrt
            ["C5", 10, 10, 2001, 20, 1991, 10, 1, 2, 3, 4],  # außerhalb
            ["C6", -1, 10, 20, 20, 21, 10, 1, 2, 3, 4],  # negativ
            ["C7", 10, 10, 20, 20, 10, 10, 1, 2, 3, 400],  # Grad unplausibel
            ["C8", 10, 10, 20, 20, 10, 10, 1, 2, 3, "NaN"],  # NaN
            ["ZZZZZZZZZZZ", 10, 10, 20, 20, 10, 10, 1, 2, 3, 4],  # zu lang
            B1,
        ]
    )
    report = upload(client, admin_h, xlsx(rows)).json()
    assert (report["total"], report["imported"], report["failed"]) == (12, 2, 10)
    codes = [e["code"] for e in report["errors"]]
    assert codes == [
        "empty_coordinate", "bad_number", "bad_number", "invalid_area", "invalid_area",
        "outside_image", "outside_image", "bad_number", "bad_number", "coordinate_too_long",
    ]
    assert [e["line"] for e in report["errors"]][:2] == [6, 7]  # echte Excel-Zeilennummern
    assert set(grid(db)) == {"A1", "B1"}


def test_short_rows_are_reported(client, admin_h, db):
    report = upload(client, admin_h, xlsx(sheet([["A1", 1, 2]]))).json()
    assert report["failed"] == 1 and report["errors"][0]["code"] == "bad_number"


@pytest.mark.parametrize(
    "rows, code",
    [
        ([["Bildhoehe_px", 10], HEADER], "no_image_size"),
        ([["Bildbreite_px", 10], HEADER], "no_image_size"),
        ([["Bildbreite_px", "breit"], ["Bildhoehe_px", 10], HEADER], "no_image_size"),
        ([["Bildbreite_px", 0], ["Bildhoehe_px", 10], HEADER], "no_image_size"),
        ([["Bildbreite_px", 10], ["Bildhoehe_px", 10]], "no_header"),
        ([["Bildbreite_px", 10], ["Bildhoehe_px", 10], HEADER[:-1]], "missing_columns"),
    ],
)
def test_structural_problems_abort_without_changes(client, admin_h, db, archive_dir, rows, code):
    response = upload(client, admin_h, xlsx(rows))
    assert response.status_code == 422 and response.json()["detail"] == code
    assert db.query(MapImage).count() == 0 and db.query(MapGrid).count() == 0
    assert not archive_dir.exists()


def test_unreadable_files(client, admin_h):
    assert upload(client, admin_h, b"PK\x03\x04kaputt", name="x.xlsx").json()["detail"] == "unreadable"
    assert upload(client, admin_h, b"\x81\x8d\x8f\x90", name="x.csv").json()["detail"] == "unreadable"


def test_empty_file(client, admin_h):
    assert upload(client, admin_h, b"", name="x.csv").json()["detail"] == "no_header"


def test_file_and_protocol_are_archived(client, admin_h, archive_dir):
    content = xlsx(sheet([A1, ["", 1, 1, 2, 2, 1, 1, 1, 2, 3, 4]]))
    report = upload(client, admin_h, content, name="Lück Koordinaten.xlsx").json()
    name = report["archived_as"]
    assert KEY in name and name.endswith(".xlsx")
    assert (archive_dir / name).read_bytes() == content
    protocol = (archive_dir / f"{name}.log").read_text(encoding="utf-8")
    assert "Zeilen: 2, importiert: 1, Fehler: 1" in protocol and "Koordinate fehlt" in protocol


def test_admin_only(client, user_h, admin_h):
    assert upload(client, user_h, xlsx(sheet([A1]))).status_code == 403
    assert client.post(f"/imports/{KEY}", files={"file": ("x.xlsx", xlsx(sheet([A1])))}).status_code in (401, 403)


# Abfrage für die Anzeige
def seed(client, admin_h, rows=None):
    upload(client, admin_h, xlsx(sheet(rows or [A1, B1])))


def test_square_lookup(client, admin_h):
    seed(client, admin_h)
    body = client.get("/maps/Lück/B1").json()
    assert body == {
        "karte": "Lück",
        "koordinate": "B1",
        "image": {"filename": "Lueck1927_gr.jpg", "width_px": 2000, "height_px": 1362},
        "area": {"x1": 357, "y1": 35, "x2": 677, "y2": 248},
        "extent": {"lon_from": 42.5, "lon_to": 43.0, "lat_from": 51.0, "lat_to": 50.0},
    }


@pytest.mark.parametrize("path", ["/maps/l%C3%BCck/b1", "/maps/L%C3%9CCK/B1"])
def test_lookup_ignores_case(client, admin_h, path):
    seed(client, admin_h)
    assert client.get(path).json()["koordinate"] == "B1"


def test_unknown_square_or_map(client, admin_h):
    seed(client, admin_h)
    assert client.get("/maps/Lück/Z9").status_code == 404
    assert client.get("/maps/Stumpf/A1").status_code == 404
    assert client.get("/maps/Lück/A1").status_code == 200


def test_newest_row_wins_when_a_square_was_imported_twice(client, admin_h, db):
    seed(client, admin_h, [A1])
    import time

    time.sleep(1.1)
    seed(client, admin_h, [["A1", 40, 40, 300, 200, 260, 160, 42, 42.5, 51, 50]])
    assert client.get("/maps/Lück/A1").json()["area"]["x1"] == 40


def test_inactive_rows_are_ignored(client, admin_h, db):
    seed(client, admin_h, [A1])
    for g in db.query(MapGrid).all():
        g.active = False
    db.commit()
    assert client.get("/maps/Lück/A1").status_code == 404


def test_lookup_follows_the_search_access_setting(client, admin_h, user_h, monkeypatch):
    seed(client, admin_h)
    monkeypatch.setattr(settings, "public_search", False)
    assert client.get("/maps/Lück/A1").status_code == 401
    assert client.get("/maps/Lück/A1", headers=user_h).status_code == 200


def test_square_matches_the_map_reference_of_a_place(client, admin_h, db):
    """Verknüpfung: map_reference.karte/koordinate entspricht map_grid.karte/koordinate."""
    from app.models import Ort, MapReference

    seed(client, admin_h)
    ort = Ort()
    db.add(ort)
    db.flush()
    db.add(MapReference(ort_id=ort.id, karte="Lück", koordinate="B1"))
    db.commit()
    place = client.get(f"/orte/{ort.id}").json()
    ref = place["karten"][0]
    assert client.get(f"/maps/{ref['karte']}/{ref['koordinate']}").status_code == 200
