"""Application entrypoint for the Sonaris FastAPI service.

Run locally:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, calculations, materials, projects
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description="API base para proyectos y calculos acusticos.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(calculations.router, prefix="/api/calculations", tags=["calculations"])
app.include_router(materials.router, prefix="/api/materiales", tags=["materiales"])


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a minimal health response for Docker and uptime checks."""
    return {"status": "ok", "service": "backend"}
