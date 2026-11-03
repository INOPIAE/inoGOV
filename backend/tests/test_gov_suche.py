import httpx
import pytest

from app.routers import gov_suche, gov_suche_nearby


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


def mock_gov_client(monkeypatch, *, response=None, error=None):
    calls = []

    class FakeAsyncClient:
        def __init__(self, timeout):
            assert timeout == 20.0

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def get(self, url, *, params, headers):
            calls.append((url, params, headers))
            if error:
                raise error
            return response

    monkeypatch.setattr(gov_suche.httpx, "AsyncClient", FakeAsyncClient)
    return calls


def test_gov_search_trims_query_and_normalizes_results(client, monkeypatch):
    calls = mock_gov_client(
        monkeypatch,
        response=FakeResponse(
            [
                {
                    "id": "object_1",
                    "position": {"lon": 22.5, "lat": 49.8, "type": "point"},
                    "name": [
                        {"lang": "pol", "value": "Przemyśl"},
                        {"lang": "deu", "value": "Premissel"},
                        None,
                    ],
                    "ignored": "value",
                },
                {"id": "object_2", "position": {"lat": 50}, "name": []},
            ]
        ),
    )

    response = client.get("/gov_suche", params={"placename": "  Przemyśl  "}, headers={"Host": "localhost"})

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "object_1",
            "position": {"lon": 22.5, "lat": 49.8, "type": "point"},
            "name": [
                {"lang": "pol", "value": "Przemyśl"},
                {"lang": "deu", "value": "Premissel"},
            ],
        },
        {"id": "object_2", "position": None, "name": []},
    ]
    assert calls == [
        (gov_suche.GOV_API_URL, {"placename": "Przemyśl"}, {"Accept": "application/json"})
    ]


NEARBY_PARAMS = {"latitude0": 50.6, "latitude1": 50.65, "longitude0": 25.2, "longitude1": 25.25}


def test_gov_nearby_requires_login(client):
    response = client.get("/gov_suche_nearby", params=NEARBY_PARAMS, headers={"Host": "localhost"})
    assert response.status_code in (401, 403)


def test_gov_nearby_returns_id_position_and_names(client, monkeypatch, user_h):
    calls = mock_gov_client(
        monkeypatch,
        response=FakeResponse(
            [
                {
                    "id": "LAWROWKO20OP",
                    "position": {"lon": 25.2099, "lat": 50.6257, "type": "p"},
                    "name": [{"lang": "deu", "value": "Lawriw"}],
                    "population": [{"value": "1294"}],
                }
            ]
        ),
    )

    response = client.get("/gov_suche_nearby", params=NEARBY_PARAMS, headers={**user_h, "Host": "localhost"})

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "LAWROWKO20OP",
            "position": {"lon": 25.2099, "lat": 50.6257, "type": "p"},
            "name": [{"lang": "deu", "value": "Lawriw"}],
        }
    ]
    assert calls == [
        (gov_suche_nearby.GOV_BOUNDING_BOX_URL, NEARBY_PARAMS, {"Accept": "application/json"})
    ]


def test_gov_nearby_rejects_inverted_area(client, monkeypatch, user_h):
    calls = mock_gov_client(monkeypatch, response=FakeResponse([]))
    params = {**NEARBY_PARAMS, "latitude0": 51}

    response = client.get("/gov_suche_nearby", params=params, headers={**user_h, "Host": "localhost"})

    assert response.status_code == 400
    assert calls == []


def test_gov_nearby_maps_request_failure(client, monkeypatch, user_h):
    mock_gov_client(monkeypatch, error=httpx.TimeoutException("timeout"))

    response = client.get("/gov_suche_nearby", params=NEARBY_PARAMS, headers={**user_h, "Host": "localhost"})

    assert response.status_code == 504


def test_gov_search_rejects_whitespace_only_query(client, monkeypatch):
    calls = mock_gov_client(monkeypatch, response=FakeResponse([]))

    response = client.get("/gov_suche", params={"placename": "   "}, headers={"Host": "localhost"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Der Ortsname darf nicht leer sein."
    assert calls == []


@pytest.mark.parametrize(
    "error, status, detail",
    [
        (httpx.TimeoutException("timeout"), 504, "Zeitüberschreitung bei der GOV-API."),
        (
            httpx.HTTPStatusError(
                "bad status",
                request=httpx.Request("GET", gov_suche.GOV_API_URL),
                response=httpx.Response(503, request=httpx.Request("GET", gov_suche.GOV_API_URL)),
            ),
            502,
            "GOV-API lieferte HTTP 503.",
        ),
        (
            httpx.RequestError("network error", request=httpx.Request("GET", gov_suche.GOV_API_URL)),
            502,
            "GOV-API ist nicht erreichbar.",
        ),
    ],
)
def test_gov_search_maps_request_failures(client, monkeypatch, error, status, detail):
    mock_gov_client(monkeypatch, error=error)

    response = client.get("/gov_suche", params={"placename": "Przemyśl"}, headers={"Host": "localhost"})

    assert response.status_code == status
    assert response.json()["detail"] == detail


def test_gov_search_rejects_invalid_json_and_response_shape(client, monkeypatch):
    mock_gov_client(monkeypatch, response=FakeResponse(ValueError("invalid json")))
    invalid_json = client.get("/gov_suche", params={"placename": "x"}, headers={"Host": "localhost"})
    assert invalid_json.status_code == 502
    assert invalid_json.json()["detail"] == "GOV-API lieferte kein gültiges JSON."

    mock_gov_client(monkeypatch, response=FakeResponse({"results": []}))
    invalid_shape = client.get("/gov_suche", params={"placename": "x"}, headers={"Host": "localhost"})
    assert invalid_shape.status_code == 502
    assert invalid_shape.json()["detail"] == "Unerwartetes Antwortformat der GOV-API."