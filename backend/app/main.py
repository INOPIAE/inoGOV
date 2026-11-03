from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import account, auth, gov_suche, imports, kreise, maps, online_maps, orte, sprachen, users

app = FastAPI(
    title="inoGOV",
    description="RESTful API for inoGOV",
    version="1.0.0",
    terms_of_service=f"{settings.frontend_url.rstrip('/')}/terms",
    servers=[
        {"url": settings.api_server_url, "description": "inoGOV API"}
    ],
    openapi_tags=[
        {"name": "auth", "description": "Authentication and user management"},
        {"name": "users", "description": "User management and profile"},
        {"name": "sprachen", "description": "Language management"},
        {"name": "kreise", "description": "District management"},
        {"name": "orte", "description": "Place management"},
        {"name": "imports", "description": "Data import management"},
        {"name": "maps", "description": "Map management"},
        {"name": "online maps", "description": "Online map providers and regional assignments"},
        {"name": "GOV-Suche", "description": "GOV search functionality"},
    ]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(account.router)
app.include_router(users.router)
app.include_router(sprachen.router)
app.include_router(kreise.router)
app.include_router(orte.router)
app.include_router(imports.router)
app.include_router(maps.router)
app.include_router(online_maps.router)
app.include_router(gov_suche.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/settings")
def public_settings() -> dict[str, str | bool]:
    return {
        "app_name": settings.app_name,
        "copyright_name": settings.copyright_name,
        "public_search": settings.public_search,
    }
