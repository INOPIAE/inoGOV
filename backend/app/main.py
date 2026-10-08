from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import account, auth, kreise, orte, sprachen, users

app = FastAPI(title="inoGOV")
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
