from fastapi import APIRouter, Depends, HTTPException, Query

from app.deps import get_current_user
from app.routers.gov_suche import GovResult, fetch_gov, normalize_gov_results

router = APIRouter(
    prefix="/gov_suche_nearby",
    tags=["GOV-Suche"],
    dependencies=[Depends(get_current_user)],
)

GOV_BOUNDING_BOX_URL = "https://gov.genealogy.net/api/searchByBoundingBox"


@router.get("", response_model=list[GovResult])
async def suche_orte_nearby(
    latitude0: float = Query(..., ge=-90, le=90),
    latitude1: float = Query(..., ge=-90, le=90),
    longitude0: float = Query(..., ge=-180, le=180),
    longitude1: float = Query(..., ge=-180, le=180),
):
    if latitude0 > latitude1 or longitude0 > longitude1:
        raise HTTPException(
            status_code=400,
            detail="Der Suchbereich ist ungültig.",
        )

    data = await fetch_gov(
        GOV_BOUNDING_BOX_URL,
        {
            "latitude0": latitude0,
            "latitude1": latitude1,
            "longitude0": longitude0,
            "longitude1": longitude1,
        },
    )
    return normalize_gov_results(data)
