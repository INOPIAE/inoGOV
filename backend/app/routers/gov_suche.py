
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(
    prefix="/gov_suche",
    tags=["GOV-Suche"]
)

GOV_API_URL = (
    "https://gov.genealogy.net/api/searchByNameAndType"
)


class GovPosition(BaseModel):
    lon: float
    lat: float
    type: str


class GovName(BaseModel):
    lang: Optional[str] = None
    value: Optional[str] = None


class GovResult(BaseModel):
    id: str
    position: Optional[GovPosition] = None
    name: list[GovName] = []


@router.get("", response_model=list[GovResult])
async def suche_orte(
    placename: str = Query(
        ...,
        min_length=1,
        description="Zu suchender Ortsname"
    )
):
    placename = placename.strip()

    if not placename:
        raise HTTPException(
            status_code=400,
            detail="Der Ortsname darf nicht leer sein."
        )

    data = await fetch_gov(GOV_API_URL, {"placename": placename})
    return normalize_gov_results(data)


async def fetch_gov(url: str, params: dict) -> list:
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                url,
                params=params,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            data = response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Zeitüberschreitung bei der GOV-API."
        )

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"GOV-API lieferte HTTP {exc.response.status_code}."
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="GOV-API ist nicht erreichbar."
        )

    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="GOV-API lieferte kein gültiges JSON."
        )

    if not isinstance(data, list):
        raise HTTPException(
            status_code=502,
            detail="Unerwartetes Antwortformat der GOV-API."
        )

    return data


def normalize_gov_results(data: list) -> list[GovResult]:
    results = []

    for item in data:
        position = item.get("position")

        # Namen aller vorhandenen Sprachen übernehmen
        names = [
            GovName(
                lang=name.get("lang"),
                value=name.get("value")
            )
            for name in item.get("name", [])
            if isinstance(name, dict)
        ]

        # Position ist nicht bei jedem GOV-Eintrag vorhanden
        gov_position = None

        if (
            isinstance(position, dict)
            and all(
                key in position
                for key in ("lon", "lat", "type")
            )
        ):
            gov_position = GovPosition(
                lon=position["lon"],
                lat=position["lat"],
                type=position["type"]
            )

        results.append(
            GovResult(
                id=item["id"],
                position=gov_position,
                name=names
            )
        )

    return results
