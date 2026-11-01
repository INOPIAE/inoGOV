import pytest

from app.models import Sprache


@pytest.fixture
def de(db):
    s = Sprache(sprache="Deutsch", sprache_land="Deutsch", sprache2="de", sprache3="deu", sprache5="de-DE")
    db.add(s)
    db.commit()
    return s


SPRACHE = {"sprache": "Polnisch", "sprache_land": "Polski", "sprache2": "pl", "sprache3": "pol", "sprache5": "pl-PL"}


# Sprache
def test_sprache_read_is_public(client, de):
    response = client.get("/sprachen")
    assert response.status_code == 200
    assert [s["sprache2"] for s in response.json()] == ["de"]


def test_sprache_write_admin_only(client, admin_h, user_h):
    assert client.post("/sprachen", json=SPRACHE).status_code in (401, 403)
    assert client.post("/sprachen", json=SPRACHE, headers=user_h).status_code == 403
    created = client.post("/sprachen", json=SPRACHE, headers=admin_h)
    assert created.status_code == 201
    sid = created.json()["id"]
    assert client.patch(f"/sprachen/{sid}", json={"sprache": "Polish"}, headers=user_h).status_code == 403
    assert client.patch(f"/sprachen/{sid}", json={"sprache": "Polish"}, headers=admin_h).json()["sprache"] == "Polish"
    assert client.delete(f"/sprachen/{sid}", headers=user_h).status_code == 403
    assert client.delete(f"/sprachen/{sid}", headers=admin_h).status_code == 204
    assert client.get(f"/sprachen/{sid}").status_code == 404


def test_sprache_duplicate(client, admin_h):
    client.post("/sprachen", json=SPRACHE, headers=admin_h)
    assert client.post("/sprachen", json=SPRACHE, headers=admin_h).status_code == 409


def test_sprache_validation(client, admin_h):
    assert client.post("/sprachen", json={**SPRACHE, "sprache2": "pol"}, headers=admin_h).status_code == 422


# Kreis
def test_kreis_crud_by_user(client, user_h, de):
    assert client.post("/kreise", json={"gov_id": "K1"}).status_code in (401, 403)
    created = client.post(
        "/kreise",
        json={"gov_id": "K1", "namen": [{"sprache_id": str(de.id), "kreisname": "Lemberg"}]},
        headers=user_h,
    )
    assert created.status_code == 201
    kid = created.json()["id"]
    assert created.json()["namen"][0]["kreisname"] == "Lemberg"

    assert client.patch(f"/kreise/{kid}", json={"comment": "x"}, headers=user_h).json()["comment"] == "x"
    assert client.get(f"/kreise/{kid}").status_code == 200

    name = client.post(
        f"/kreise/{kid}/namen", json={"sprache_id": str(de.id), "kreisname": "Lwiw"}, headers=user_h
    )
    assert name.status_code == 201
    assert len(client.get(f"/kreise/{kid}").json()["namen"]) == 2
    assert client.delete(f"/kreise/{kid}/namen/{name.json()['id']}", headers=user_h).status_code == 204
    assert len(client.get(f"/kreise/{kid}").json()["namen"]) == 1

    assert client.delete(f"/kreise/{kid}", headers=user_h).status_code == 204
    assert client.get(f"/kreise/{kid}").status_code == 404


def test_kreis_search_and_unknown_sprache(client, user_h, de):
    client.post(
        "/kreise",
        json={"namen": [{"sprache_id": str(de.id), "kreisname": "Lemberg"}]},
        headers=user_h,
    )
    client.post("/kreise", json={"namen": [{"sprache_id": str(de.id), "kreisname": "Krakau"}]}, headers=user_h)
    assert len(client.get("/kreise").json()) == 2
    assert [k["namen"][0]["kreisname"] for k in client.get("/kreise", params={"q": "lemb"}).json()] == ["Lemberg"]
    bad = client.post(
        "/kreise",
        json={"namen": [{"sprache_id": "00000000-0000-0000-0000-000000000000", "kreisname": "X"}]},
        headers=user_h,
    )
    assert bad.status_code == 422


# Ort
ORT = {"gov_id": "O1", "lon": "22.858178", "lat": "49.525716"}


def test_ort_crud_with_names_and_maps(client, user_h, de):
    kreis = client.post("/kreise", json={"gov_id": "K1"}, headers=user_h).json()
    created = client.post(
        "/orte",
        json={
            **ORT,
            "kreis_id": kreis["id"],
            "namen": [{"sprache_id": str(de.id), "ortsname": "Przemyśl"}],
            "karten": [{"koordinate": "B5", "karte": "Lück"}],
        },
        headers=user_h,
    )
    assert created.status_code == 201
    body = created.json()
    assert body["namen"][0]["ortsname"] == "Przemyśl"
    assert body["karten"][0]["koordinate"] == "B5"
    assert float(body["lat"]) == 49.525716
    oid = body["id"]

    karte = client.post(f"/orte/{oid}/karten", json={"koordinate": "C7", "karte": "Stumpf"}, headers=user_h)
    assert karte.status_code == 201
    assert len(client.get(f"/orte/{oid}").json()["karten"]) == 2
    assert client.delete(f"/orte/{oid}/karten/{karte.json()['id']}", headers=user_h).status_code == 204
    assert len(client.get(f"/orte/{oid}").json()["karten"]) == 1

    assert client.patch(f"/orte/{oid}", json={"addition": "bei Lemberg"}, headers=user_h).json()["addition"] == "bei Lemberg"
    assert client.delete(f"/orte/{oid}", headers=user_h).status_code == 204
    assert client.get(f"/orte/{oid}").status_code == 404


def test_ort_filters(client, user_h, de):
    k1 = client.post("/kreise", json={}, headers=user_h).json()["id"]
    k2 = client.post("/kreise", json={}, headers=user_h).json()["id"]
    for kreis, name in [(k1, "Przemyśl"), (k1, "Jarosław"), (k2, "Lemberg")]:
        client.post(
            "/orte",
            json={"kreis_id": kreis, "namen": [{"sprache_id": str(de.id), "ortsname": name}]},
            headers=user_h,
        )
    assert len(client.get("/orte").json()) == 3
    assert len(client.get("/orte", params={"kreis_id": k1}).json()) == 2
    assert len(client.get("/orte", params={"q": "lemb"}).json()) == 1
    assert len(client.get("/orte", params={"q": "lemb", "sprache_id": str(de.id)}).json()) == 1
    assert len(client.get("/orte", params={"limit": 1}).json()) == 1


def test_ort_count_uses_search_filters_and_reports_global_total(client, user_h, de):
    kreis_id = client.post("/kreise", json={}, headers=user_h).json()["id"]
    other_kreis_id = client.post("/kreise", json={}, headers=user_h).json()["id"]
    for kreis, name in [(kreis_id, "Lemberg"), (kreis_id, "Lemberg Süd"), (other_kreis_id, "Krakau")]:
        client.post(
            "/orte",
            json={"kreis_id": kreis, "namen": [{"sprache_id": str(de.id), "ortsname": name}]},
            headers=user_h,
        )

    response = client.get("/orte/count", params={"q": "Lemberg", "kreis_id": kreis_id})

    assert response.status_code == 200
    assert response.json() == {"found": 2, "total": 3}


def test_ort_coordinate_and_link_filters_apply_to_list_and_count(client, user_h, de):
    places = [
        {"name": "empty", "gov_id": None, "coordinates_not_found": False},
        {"name": "not found", "gov_id": None, "coordinates_not_found": True},
        {"name": "with gov", "gov_id": "GOV1", "lat": "49.0", "lon": "22.0"},
        {"name": "without gov", "gov_id": None, "lat": "50.0", "lon": "23.0"},
        {"name": "gov only", "gov_id": "GOV2", "coordinates_not_found": False},
    ]
    for place in places:
        name = place.pop("name")
        response = client.post(
            "/orte",
            json={**place, "namen": [{"sprache_id": str(de.id), "ortsname": name}]},
            headers=user_h,
        )
        assert response.status_code == 201

    filters_and_expected_names = [
        ({"coordinate_status": "empty"}, {"empty", "gov only"}),
        ({"coordinate_status": "not_found"}, {"not found"}),
        ({"coordinate_status": "available"}, {"with gov", "without gov"}),
        ({"link_status": "empty"}, {"empty", "not found"}),
        ({"link_status": "gov"}, {"with gov", "gov only"}),
        ({"link_status": "without_gov"}, {"empty", "not found", "without gov"}),
        (
            {"coordinate_status": "available", "link_status": "without_gov"},
            {"without gov"},
        ),
    ]
    for params, expected_names in filters_and_expected_names:
        listed = client.get("/orte", params=params, headers=user_h)
        counted = client.get("/orte/count", params=params, headers=user_h)
        actual_names = {place["namen"][0]["ortsname"] for place in listed.json()}
        assert actual_names == expected_names
        assert counted.json() == {"found": len(expected_names), "total": len(places)}


def test_ort_sorting_applies_before_pagination(client, user_h, de):
    for gov_id, name in [("O1", "Zamość"), ("O2", "Alwernia"), ("O3", "Przemyśl")]:
        client.post(
            "/orte",
            json={"gov_id": gov_id, "namen": [{"sprache_id": str(de.id), "ortsname": name}]},
            headers=user_h,
        )

    first_page = client.get(
        "/orte",
        params={"sort_by": "name", "sort_sprache_id": str(de.id), "limit": 1},
    )
    second_page = client.get(
        "/orte",
        params={"sort_by": "name", "sort_sprache_id": str(de.id), "limit": 1, "offset": 1},
    )
    descending = client.get(
        "/orte",
        params={"sort_by": "name", "sort_sprache_id": str(de.id), "sort_order": "desc"},
    )

    assert first_page.json()[0]["namen"][0]["ortsname"] == "Alwernia"
    assert second_page.json()[0]["namen"][0]["ortsname"] == "Przemyśl"
    assert descending.json()[0]["namen"][0]["ortsname"] == "Zamość"


def test_ort_validation(client, user_h):
    assert client.post("/orte", json={"lat": "91"}, headers=user_h).status_code == 422
    assert client.post("/orte", json={"kreis_id": "00000000-0000-0000-0000-000000000000"}, headers=user_h).status_code == 422
    assert client.post("/orte", json={"karten": [{"koordinate": "ABC"}]}, headers=user_h).status_code == 422
    assert client.post("/orte", json=ORT).status_code in (401, 403)


def test_name_of_other_ort_not_deletable(client, user_h, de):
    names = {"namen": [{"sprache_id": str(de.id), "ortsname": "A"}]}
    a = client.post("/orte", json=names, headers=user_h).json()
    b = client.post("/orte", json={}, headers=user_h).json()
    assert client.delete(f"/orte/{b['id']}/namen/{a['namen'][0]['id']}", headers=user_h).status_code == 404
