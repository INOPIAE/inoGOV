import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base, MapGrid, MapImage, MapOnline, MapReference, Ort, RegionalMap


def test_map_online_requires_editor_for_writes(client, user_h):
    payload = {
        "mapname": "Test map",
        "map_short": "TST",
        "map_url_basis": "https://maps.example/",
        "map_url_pattern": "?lat={lat}&lon={lon}",
        "global": False,
    }
    assert client.post("/map-online", json=payload).status_code in (401, 403)
    assert client.post("/map-online", json=payload, headers=user_h).status_code == 201


def test_map_online_crud_and_regional_assignment(client, user_h, db):
    ort = Ort(gov_id="GOV1", lat="49.5", lon="22.5")
    db.add(ort)
    db.commit()
    payload = {
        "mapname": "Ukraine 75000",
        "map_short": "U75",
        "map_url_basis": "https://maps.example/",
        "map_url_pattern": "?lat={lat}&lon={lon}",
        "global": False,
    }
    created = client.post("/map-online", json=payload, headers=user_h)
    assert created.status_code == 201
    map_data = created.json()
    assert map_data["global"] is False

    updated = client.patch(
        f"/map-online/{map_data['id']}",
        json={"mapname": "Ukraine 1:75000", "global": True},
        headers=user_h,
    )
    assert updated.status_code == 200
    assert updated.json()["mapname"] == "Ukraine 1:75000"
    assert updated.json()["global"] is True

    assignment = client.get("/regional-maps", params={"ort_id": str(ort.id)}).json()[0]
    assert assignment["map_online"]["map_short"] == "U75"
    assert assignment["map_online"]["global"] is True
    place_response = client.get(f"/orte/{ort.id}", headers=user_h)
    assert place_response.json()["regional_maps"][0]["map_online"]["map_short"] == "U75"
    assert client.post(
        "/regional-maps",
        json={"ort_id": str(ort.id), "map_online_id": map_data["id"]},
        headers=user_h,
    ).status_code == 409
    assert client.delete(f"/map-online/{map_data['id']}", headers=user_h).status_code == 409
    assert client.delete(f"/regional-maps/{assignment['id']}", headers=user_h).status_code == 204
    restored = client.post(
        "/regional-maps",
        json={"ort_id": str(ort.id), "map_online_id": map_data["id"]},
        headers=user_h,
    )
    assert restored.status_code == 201 and restored.json()["id"] == assignment["id"]
    assert client.delete(f"/regional-maps/{assignment['id']}", headers=user_h).status_code == 204
    assert client.delete(f"/map-online/{map_data['id']}", headers=user_h).status_code == 204
    assert client.post(
        "/map-online",
        json={**payload, "mapname": "Replacement", "map_short": "U75"},
        headers=user_h,
    ).status_code == 409
    assert client.get("/map-online", params={"global_only": "true"}).json() == []
    assert db.query(RegionalMap).count() == 1
    assert db.query(MapOnline).one().active is False


def test_new_coordinate_place_gets_global_map_assignments(client, user_h, db):
    for short in ("OSM", "GM"):
        db.add(
            MapOnline(
                mapname=short,
                map_short=short,
                map_url_basis="https://maps.example/",
                map_url_pattern="?lat={lat}&lon={lon}",
                global_map=True,
            )
        )
    db.commit()

    created = client.post(
        "/orte",
        json={"lat": "49.5", "lon": "22.5", "gov_id": "GOV1"},
        headers=user_h,
    )

    assert created.status_code == 201
    assert [item["map_online"]["map_short"] for item in created.json()["regional_maps"]] == ["OSM", "GM"]


def test_place_response_orders_regional_maps_by_requested_priority(client, db):
    ort = Ort(lat="49.5", lon="22.5")
    priority = ["U75", "U100", "OSM", "GM"]
    maps = [
        MapOnline(
            mapname=short,
            map_short=short,
            map_url_basis="https://maps.example/",
            map_url_pattern="?lat={lat}&lon={lon}",
            global_map=short in {"OSM", "GM"},
        )
        for short in priority
    ]
    db.add_all([ort, *maps])
    db.flush()
    db.add_all(
        RegionalMap(ort_id=ort.id, map_online_id=online_map.id)
        for online_map in reversed(maps)
    )
    db.commit()

    response = client.get(f"/orte/{ort.id}", headers={"Host": "localhost"})

    assert response.status_code == 200
    assert [item["map_online"]["map_short"] for item in response.json()["regional_maps"]] == priority


def test_migration_seeds_online_maps_and_regional_assignments():
    engine = create_engine("sqlite://")
    legacy_tables = [
        table
        for table in Base.metadata.sorted_tables
        if table.name not in {"map_online", "regional_map"}
    ]
    Base.metadata.create_all(engine, tables=legacy_tables)
    with Session(engine) as db:
        lueck_exception = Ort(lat="50", lon="23")
        lueck_regular = Ort(lat="50", lon="23")
        stumpp_place = Ort()
        coordinate_only = Ort(lat="51", lon="24")
        db.add_all([lueck_exception, lueck_regular, stumpp_place, coordinate_only])
        db.flush()
        db.add_all(
            [
                MapReference(ort_id=lueck_exception.id, karte="Lück", koordinate="A1"),
                MapReference(ort_id=lueck_regular.id, karte="Lück", koordinate="H2"),
                MapReference(ort_id=stumpp_place.id, karte="Stumpp", koordinate="G1"),
            ]
        )
        db.commit()
        ids = {
            "lueck_exception": lueck_exception.id,
            "lueck_regular": lueck_regular.id,
            "stumpp": stumpp_place.id,
            "coordinate_only": coordinate_only.id,
        }

    migration_path = Path(__file__).parents[1] / "alembic" / "versions" / "0006_map_online.py"
    spec = importlib.util.spec_from_file_location("migration_0006_map_online", migration_path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    with engine.begin() as connection:
        context = MigrationContext.configure(connection)
        with Operations.context(context):
            migration.upgrade()

    with Session(engine) as db:
        online_maps = {item.map_short: item for item in db.query(MapOnline).all()}
        assignments = {
            place_id: {mapping.map_online.map_short for mapping in db.query(RegionalMap).filter_by(ort_id=place_id)}
            for place_id in ids.values()
        }

    assert set(online_maps) == {"U75", "U100", "OSM", "GM"}
    assert assignments[ids["lueck_exception"]] == {"U100", "OSM", "GM"}
    assert assignments[ids["lueck_regular"]] == {"U75", "U100", "OSM", "GM"}
    assert assignments[ids["stumpp"]] == {"U100"}
    assert assignments[ids["coordinate_only"]] == {"OSM", "GM"}
    engine.dispose()
