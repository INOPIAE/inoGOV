from fastapi import FastAPI

from app.routers import auth, kreise, orte, sprachen, users

app = FastAPI(title="inoGOV")
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(sprachen.router)
app.include_router(kreise.router)
app.include_router(orte.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
