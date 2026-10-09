import pytest

from app.config import settings
from app.models import Kreis, Kreisname, MapReference, Ort, Ortsname, Sprache, User


@pytest.fixture(autouse=True)
def archive_dir(monkeypatch, tmp_path):
    path = tmp_path / "archive"
    monkeypatch.setattr(settings, "import_archive_dir", str(path))
    return path


@pytest.fixture
def pl(db):
    s = Sprache(sprache="Polnisch", sprache_land="Polski", sprache2="pl", sprache3="pol", sprache5="pl-PL")
    db.add(s)
    db.commit()
    return s


@pytest.fixture
def de(db):
    s = Sprache(sprache="Deutsch", sprache_land="Deutsch", sprache2="de", sprache3="deu", sprache5="de-DE")
    db.add(s)
    db.commit()
    return s


def make_kreis(db, sprache, name, active=True):
    kreis = Kreis(active=active)
    db.add(kreis)
    db.flush()
    db.add(Kreisname(kreis_id=kreis.id, sprache_id=sprache.id, kreisname=name))
    db.commit()
    return kreis


def csv_bytes(rows, header=True, sep=";", encoding="utf-8"):
    lines = [sep.join(["Ort", "Kreis", "Koordinate"])] if header else []
    lines += [sep.join(r) for r in rows]
    return ("\n".join(lines) + "\n").encode(encoding)


def upload(client, headers, content, key="ImportLueck", name="lueck.csv"):
    return client.post(f"/imports/{key}", files={"file": (name, content, "text/csv")}, headers=headers)


def places(db):
    return {
        n.ortsname: db.get(Ort, n.ort_id)
        for n in db.query(Ortsname).all()
    }


# Zugriff
def test_import_list_is_admin_only(client, admin_h, user_h):
    assert client.get("/imports").status_code in (401, 403)
    assert client.get("/imports", headers=user_h).status_code == 403
    body = client.get("/imports", headers=admin_h).json()
    assert body == [
        {"key": "ImportLueck", "columns": ["place_name_pl", "district_name_pl", "coordinate"], "accepts": [".csv"]},
        {
            "key": "ImportLueckKoordinaten",
            "columns": [
                "Koordinate", "X1", "Y1", "X2", "Y2", "Breite_px", "Hoehe_px",
                "Laenge_von", "Laenge_bis", "Breite_von", "Breite_bis",
            ],
            "accepts": [".xlsx", ".csv"],
        },
    ]


def test_upload_is_admin_only(client, user_h, pl):
    content = csv_bytes([("A", "B", "C3")])
    assert client.post("/imports/ImportLueck", files={"file": ("x.csv", content)}).status_code in (401, 403)
    assert upload(client, user_h, content).status_code == 403


def test_unknown_import(client, admin_h):
    assert upload(client, admin_h, b"a;b;c\n", key="ImportXyz").status_code == 404


# Grundfunktion
def test_imports_place_with_existing_district(client, admin_h, db, pl, admin):
    kreis = make_kreis(db, pl, "Przemyśl")
    response = upload(client, admin_h, csv_bytes([("Krasiczyn", "Przemyśl", "B5")]))
    assert response.status_code == 200
    report = response.json()
    assert (report["total"], report["imported"], report["failed"]) == (1, 1, 0)
    assert report["created_kreise"] == []

    ort = places(db)["Krasiczyn"]
    assert ort.kreis_id == kreis.id
    (name,) = db.query(Ortsname).all()
    assert name.sprache_id == pl.id
    (ref,) = db.query(MapReference).all()
    assert (ref.ort_id, ref.koordinate, ref.karte) == (ort.id, "B5", "Lück")
    assert db.query(Kreis).count() == 1
    assert ort.created_by == admin.id and ref.created_by == admin.id


def test_header_row_is_skipped(client, admin_h, db, pl):
    make_kreis(db, pl, "K")
    report = upload(client, admin_h, csv_bytes([("A", "K", "B5")])).json()
    assert report["total"] == 1
    assert "Ort" not in places(db)


def test_missing_district_is_created_in_polish_and_reported(client, admin_h, db, pl, admin):
    report = upload(client, admin_h, csv_bytes([("Krasiczyn", "Nowy Kreis", "B5")])).json()
    assert report["imported"] == 1
    assert [k["name"] for k in report["created_kreise"]] == ["Nowy Kreis"]

    (kreis,) = db.query(Kreis).all()
    assert report["created_kreise"][0]["id"] == str(kreis.id)
    (kname,) = db.query(Kreisname).all()
    assert (kname.kreis_id, kname.sprache_id, kname.kreisname) == (kreis.id, pl.id, "Nowy Kreis")
    assert kreis.created_by == admin.id
    assert places(db)["Krasiczyn"].kreis_id == kreis.id


def test_new_district_is_reused_within_the_same_import(client, admin_h, db, pl):
    rows = [("A", "Nowy", "B5"), ("B", "Nowy", "C6"), ("C", "Inny", "D7")]
    report = upload(client, admin_h, csv_bytes(rows)).json()
    assert report["imported"] == 3
    assert sorted(k["name"] for k in report["created_kreise"]) == ["Inny", "Nowy"]
    assert db.query(Kreis).count() == 2
    p = places(db)
    assert p["A"].kreis_id == p["B"].kreis_id != p["C"].kreis_id


def test_district_created_by_first_import_is_found_by_the_second(client, admin_h, db, pl):
    upload(client, admin_h, csv_bytes([("A", "Nowy", "B5")]))
    report = upload(client, admin_h, csv_bytes([("B", "Nowy", "B6")])).json()
    assert report["created_kreise"] == []
    assert db.query(Kreis).count() == 1


@pytest.mark.parametrize("written", ["przemyśl", "  Przemyśl  ", "PRZEMYŚL", "Przemyśl\u00a0"])
def test_district_matching_ignores_case_and_whitespace(client, admin_h, db, pl, written):
    make_kreis(db, pl, "Przemyśl")
    report = upload(client, admin_h, csv_bytes([("A", written, "B5")])).json()
    assert report["created_kreise"] == []
    assert db.query(Kreis).count() == 1


def test_only_polish_district_names_are_matched(client, admin_h, db, pl, de):
    make_kreis(db, de, "Przemyśl")
    report = upload(client, admin_h, csv_bytes([("A", "Przemyśl", "B5")])).json()
    assert [k["name"] for k in report["created_kreise"]] == ["Przemyśl"]
    assert db.query(Kreis).count() == 2


def test_inactive_district_is_not_reused(client, admin_h, db, pl):
    make_kreis(db, pl, "Przemyśl", active=False)
    report = upload(client, admin_h, csv_bytes([("A", "Przemyśl", "B5")])).json()
    assert len(report["created_kreise"]) == 1


def test_duplicates_are_not_checked(client, admin_h, db, pl):
    make_kreis(db, pl, "K")
    rows = [("Krasiczyn", "K", "B5")] * 3
    assert upload(client, admin_h, csv_bytes(rows)).json()["imported"] == 3
    assert db.query(Ort).count() == 3
    assert db.query(MapReference).count() == 3
    # auch ein zweiter Import derselben Datei legt erneut an
    upload(client, admin_h, csv_bytes(rows))
    assert db.query(Ort).count() == 6


# CSV-Formate
@pytest.mark.parametrize("sep", [";", ",", "\t"])
def test_delimiters(client, admin_h, db, pl, sep):
    make_kreis(db, pl, "K")
    report = upload(client, admin_h, csv_bytes([("Krasiczyn", "K", "B5")], sep=sep)).json()
    assert report["imported"] == 1


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig", "cp1250"])
def test_encodings_keep_polish_characters(client, admin_h, db, pl, encoding):
    make_kreis(db, pl, "Łańcut")
    report = upload(client, admin_h, csv_bytes([("Żółkiew", "Łańcut", "B5")], encoding=encoding)).json()
    assert report["imported"] == 1 and report["created_kreise"] == []
    assert "Żółkiew" in places(db)


def test_quoted_values_and_windows_line_endings(client, admin_h, db, pl):
    make_kreis(db, pl, "K")
    content = 'Ort;Kreis;Koordinate\r\n"Ort; mit Semikolon";K;B5\r\n'.encode()
    assert upload(client, admin_h, content).json()["imported"] == 1
    assert "Ort; mit Semikolon" in places(db)


def test_blank_lines_and_extra_columns(client, admin_h, db, pl):
    make_kreis(db, pl, "K")
    content = b"Ort;Kreis;Koordinate;Bemerkung\n\nA;K;B5;egal\n;;;\n\nB;K;B6\n"
    report = upload(client, admin_h, content).json()
    assert (report["total"], report["imported"], report["failed"]) == (2, 2, 0)


def test_empty_file_and_header_only(client, admin_h, pl):
    assert upload(client, admin_h, b"").json()["total"] == 0
    assert upload(client, admin_h, csv_bytes([])).json()["total"] == 0


# Fehler
def test_errors_are_reported_with_line_and_code_and_valid_rows_still_import(client, admin_h, db, pl):
    make_kreis(db, pl, "K")
    rows = [
        ("Gut1", "K", "B5"),
        ("", "K", "B5"),
        ("Ohne Kreis", "", "B5"),
        ("Ohne Koordinate", "K", ""),
        ("Zu lang", "K", "B55"),
        ("X" * 256, "K", "B5"),
        ("Kreis zu lang", "K" * 51, "B5"),
        ("Gut2", "K", "C6"),
    ]
    report = upload(client, admin_h, csv_bytes(rows)).json()
    assert (report["total"], report["imported"], report["failed"]) == (8, 2, 6)
    by_line = {e["line"]: e for e in report["errors"]}
    assert {line: e["code"] for line, e in by_line.items()} == {
        3: "empty_place",
        4: "empty_district",
        5: "empty_coordinate",
        6: "coordinate_too_long",
        7: "place_too_long",
        8: "district_too_long",
    }
    assert by_line[3]["values"] == ["", "K", "B5"]
    assert set(places(db)) == {"Gut1", "Gut2"}
    assert db.query(Ort).count() == 2


def test_too_few_columns(client, admin_h, db, pl):
    report = upload(client, admin_h, b"Ort;Kreis;Koordinate\nNur Ort;K\n").json()
    assert report["errors"][0]["code"] == "columns" and report["errors"][0]["line"] == 2


def test_failed_rows_do_not_leave_districts_behind(client, admin_h, db, pl):
    report = upload(client, admin_h, csv_bytes([("A", "Nowy", "")])).json()
    assert report["failed"] == 1 and report["created_kreise"] == []
    assert db.query(Kreis).count() == 0


def test_database_error_in_a_row_does_not_stop_the_import(client, admin_h, db, pl, monkeypatch):
    from app.imports import lueck

    make_kreis(db, pl, "K")
    original = lueck.MapReference
    calls = {"n": 0}

    def flaky(**kwargs):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("kaputt")
        return original(**kwargs)

    monkeypatch.setattr(lueck, "MapReference", flaky)
    rows = [("A", "K", "B1"), ("B", "K", "B2"), ("C", "K", "B3")]
    report = upload(client, admin_h, csv_bytes(rows)).json()
    assert (report["imported"], report["failed"]) == (2, 1)
    assert report["errors"][0]["code"] == "unexpected" and report["errors"][0]["line"] == 3
    assert set(places(db)) == {"A", "C"}  # B wurde vollständig zurückgerollt


def test_missing_polish_language_aborts_everything(client, admin_h, db, archive_dir):
    response = upload(client, admin_h, csv_bytes([("A", "K", "B5")]))
    assert response.status_code == 422 and response.json()["detail"] == "no_polish"
    assert db.query(Ort).count() == 0
    assert not archive_dir.exists()


def test_oversized_file(client, admin_h, pl, monkeypatch):
    monkeypatch.setattr(settings, "import_max_mb", 0)
    assert upload(client, admin_h, b"x" * 10).status_code == 413


def test_missing_file(client, admin_h):
    assert client.post("/imports/ImportLueck", headers=admin_h).status_code == 422


# Ablage und Protokoll
def test_file_and_protocol_are_archived_after_processing(client, admin_h, db, pl, archive_dir):
    make_kreis(db, pl, "K")
    content = csv_bytes([("Gut", "K", "B5"), ("", "K", "B5"), ("Neu", "Nowy", "C6")])
    report = upload(client, admin_h, content, name="meine datei (1).csv").json()

    name = report["archived_as"]
    assert name and name.endswith("meine_datei__1_.csv") and "ImportLueck" in name
    assert (archive_dir / name).read_bytes() == content
    protocol = (archive_dir / f"{name}.log").read_text(encoding="utf-8")
    assert "Zeilen: 3, importiert: 2, Fehler: 1" in protocol
    assert "Zeile 3: Ortsname fehlt" in protocol
    assert "Nowy" in protocol
    assert report["archive_failed"] is False


def test_failed_rows_are_archived_too(client, admin_h, db, pl, archive_dir):
    report = upload(client, admin_h, csv_bytes([("", "K", "B5")])).json()
    assert report["imported"] == 0 and report["archived_as"]
    assert (archive_dir / report["archived_as"]).exists()


def test_archive_names_do_not_collide_and_cannot_escape(client, admin_h, db, pl, archive_dir):
    a = upload(client, admin_h, csv_bytes([("A", "K", "B5")]), name="../../evil.csv").json()["archived_as"]
    b = upload(client, admin_h, csv_bytes([("A", "K", "B5")]), name="../../evil.csv").json()["archived_as"]
    assert a != b
    assert "/" not in a and "\\" not in a
    assert {p.name for p in archive_dir.iterdir()} == {a, f"{a}.log", b, f"{b}.log"}


def test_import_succeeds_when_archiving_fails(client, admin_h, db, pl, monkeypatch, tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("datei statt ordner")
    monkeypatch.setattr(settings, "import_archive_dir", str(blocker / "sub"))
    report = upload(client, admin_h, csv_bytes([("A", "K", "B5")])).json()
    assert report["imported"] == 1
    assert report["archived_as"] is None and report["archive_failed"] is True
    assert db.query(Ort).count() == 1


def test_imported_places_are_searchable(client, admin_h, db, pl):
    upload(client, admin_h, csv_bytes([("Krasiczyn", "Przemyśl", "B5")]))
    found = client.get("/orte", params={"q": "krasic"}).json()
    assert len(found) == 1
    assert found[0]["namen"][0]["ortsname"] == "Krasiczyn"
    assert found[0]["karten"][0]["karte"] == "Lück" and found[0]["karten"][0]["koordinate"] == "B5"
    kreise = client.get("/kreise", params={"q": "przemy"}).json()
    assert kreise[0]["namen"][0]["kreisname"] == "Przemyśl"


def test_admin_otp_requirement_applies(client, admin, pl, monkeypatch):
    from app.security import create_access_token

    monkeypatch.setattr(settings, "admin_otp_required", True)
    headers = {"Authorization": f"Bearer {create_access_token(str(admin.id))}"}
    assert upload(client, headers, csv_bytes([("A", "K", "B5")])).status_code == 403
