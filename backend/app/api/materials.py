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
    categoria: str   # "rigid" | "filling"


@router.get("/", response_model=list[MaterialResponse])
def list_materiales(search: str = "", categoria: str | None = None) -> list[MaterialResponse]:
    """Return catalog materials, optionally filtered by name or categoria.

    - ``?categoria=rigid``   — structural panels (hormigon, yeso, OSB …)
    - ``?categoria=filling`` — cavity fill materials (lana, espuma …)
    - ``?search=lana``       — substring match on name (case-insensitive)
    """
    todos = _libreria.listar_todos()
    if search:
        q = search.lower()
        todos = [m for m in todos if q in str(m.get("nombre", "")).lower()]
    if categoria:
        todos = [m for m in todos if m.get("categoria") == categoria]
    return [MaterialResponse(**m) for m in todos]  # type: ignore[arg-type]
