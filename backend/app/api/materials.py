"""Material catalog endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from engine.materials import LibreriaMatariales


router = APIRouter()
_libreria = LibreriaMatariales()


class MaterialResponse(BaseModel):
    nombre: str
    densidad: float
    espesor: float
    factor_perdida: float
    tipo: str


@router.get("/", response_model=list[MaterialResponse])
def list_materiales(search: str = "") -> list[MaterialResponse]:
    """Return all catalog materials, optionally filtered by name."""
    todos = _libreria.listar_todos()
    if search:
        query = search.lower()
        todos = [m for m in todos if query in m["nombre"].lower()]  # type: ignore[index]
    return [MaterialResponse(**m) for m in todos]  # type: ignore[arg-type]
