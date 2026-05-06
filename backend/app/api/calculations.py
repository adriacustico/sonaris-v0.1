"""Calculation endpoints backed by the acoustic engine."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.calculation import Calculation
from engine.acoustic_engine import AcousticEngine, CalculationError, MaterialNotFoundError


logger = logging.getLogger(__name__)
router = APIRouter()
engine = AcousticEngine()


# ── Structured (Capa1 + Unión + Capa2) schemas ────────────────────────────────

class CapaMaterialStructInput(BaseModel):
    """One material entry inside a structural panel layer."""

    nombre: str
    cantidad: int = Field(1, ge=1, le=20, description="Number of identical boards stacked")
    espesor_unitario_mm: float = Field(..., gt=0, description="Thickness of each board in mm")


class UnionStructInput(BaseModel):
    """Cavity / union between both panels."""

    relleno_nombre: str | None = Field(None, description="Filling material name (poroso)")
    relleno_espesor_mm: float | None = Field(None, gt=0)
    camara_aire_mm: float = Field(0, ge=0, description="Additional air-gap depth in mm")
    tipo_montantes: str = Field("montantes_metal", description="Stud coupling type")


class StructuredCalculationRequest(BaseModel):
    """Full structured Capa1 + Unión + Capa2 request."""

    proyecto_id: int
    nombre: str
    capa1: list[CapaMaterialStructInput] = []
    union: UnionStructInput = UnionStructInput()
    capa2: list[CapaMaterialStructInput] = []
    frecuencias: list[float] | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "proyecto_id": 1,
                "nombre": "Tabique Metalcon ejemplo",
                "capa1": [
                    {"nombre": "Placa yeso 15mm", "cantidad": 2, "espesor_unitario_mm": 15},
                    {"nombre": "OSB 15mm", "cantidad": 1, "espesor_unitario_mm": 15},
                ],
                "union": {
                    "relleno_nombre": "Lana mineral 50mm",
                    "relleno_espesor_mm": 100,
                    "camara_aire_mm": 0,
                    "tipo_montantes": "montantes_metal",
                },
                "capa2": [
                    {"nombre": "OSB 15mm", "cantidad": 1, "espesor_unitario_mm": 15},
                ],
            }
        }
    }


# ── Legacy flat-list schemas ───────────────────────────────────────────────────

class MaterialInput(BaseModel):
    """Material layer sent by the client."""

    nombre: str
    espesor: float = Field(..., gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {"nombre": "Hormigon 200mm", "espesor": 0.2},
        }
    }


class CalculationRequest(BaseModel):
    """Calculation request payload."""

    proyecto_id: int
    nombre: str
    materiales: list[MaterialInput]
    frecuencias: list[float] | None = None
    # Double-leaf parameters (optional; ignored for single-wall calculations)
    separacion_mm: float | None = Field(None, ge=0, description="Cavity depth in mm (double-leaf mode)")
    tipo_union: str = Field("montantes_metal", description="Union type: rigida | montantes_metal | montantes_madera | canal_resiliente | aire")
    tiene_relleno: bool = Field(False, description="True when the cavity contains porous fill")

    model_config = {
        "json_schema_extra": {
            "example": {
                "proyecto_id": 1,
                "nombre": "Tabique Metalcon doble hoja",
                "materiales": [
                    {"nombre": "Placa yeso 15mm", "espesor": 0.015},
                    {"nombre": "Placa yeso 15mm", "espesor": 0.015},
                ],
                "separacion_mm": 90,
                "tipo_union": "montantes_metal",
                "tiene_relleno": True,
            }
        }
    }


class CalculationResponse(BaseModel):
    """Calculation response returned by the API."""

    id: int
    proyecto_id: int
    nombre: str
    entrada: CalculationRequest
    salida: dict[str, Any]
    timestamp: datetime

    model_config = {"from_attributes": True}


@router.post("/", response_model=CalculationResponse, status_code=status.HTTP_201_CREATED)
def create_calculation(req: CalculationRequest, db: Session = Depends(get_db)) -> CalculationResponse:
    """Create, persist and return an acoustic calculation."""
    logger.info("POST /calculations: %s", req.nombre)
    try:
        separacion_m = req.separacion_mm / 1000.0 if req.separacion_mm else None
        R_frecuencias = engine.calcular_aislamiento(
            materiales=[material.model_dump() for material in req.materiales],
            frecuencias=req.frecuencias,
            separacion_m=separacion_m,
            tipo_union=req.tipo_union,
            tiene_relleno=req.tiene_relleno,
        )
        ponderacion = engine.ponderacion_iso717_1(R_frecuencias)
        resultado = {
            **ponderacion,
            "R_frecuencias": R_frecuencias,
        }

        calc = Calculation(
            proyecto_id=req.proyecto_id,
            nombre=req.nombre,
            entrada_json=json.dumps(req.model_dump(), ensure_ascii=False),
            resultado_json=json.dumps(resultado, ensure_ascii=False),
            timestamp=datetime.utcnow(),
        )
        db.add(calc)
        db.commit()
        db.refresh(calc)
        return _to_response(calc)
    except MaterialNotFoundError as exc:
        logger.error("Calculo fallido por material invalido: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CalculationError as exc:
        logger.error("Calculo fallido: %s", exc)
        raise HTTPException(status_code=500, detail="Error en calculo") from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error inesperado: %s", exc)
        raise HTTPException(status_code=500, detail="Error interno") from exc


@router.get("/proyecto/{proyecto_id}", response_model=list[CalculationResponse])
def list_calculations_by_project(
    proyecto_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[CalculationResponse]:
    """List calculations for one project with pagination."""
    logger.info("GET /calculations/proyecto/%s", proyecto_id)
    calculations = (
        db.query(Calculation)
        .filter(Calculation.proyecto_id == proyecto_id, Calculation.eliminado.is_(False))
        .order_by(Calculation.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_to_response(calc) for calc in calculations]


@router.get("/{calculation_id}", response_model=CalculationResponse)
def get_calculation(calculation_id: int, db: Session = Depends(get_db)) -> CalculationResponse:
    """Return one calculation by ID."""
    logger.info("GET /calculations/%s", calculation_id)
    calc = db.get(Calculation, calculation_id)
    if calc is None or calc.eliminado:
        raise HTTPException(status_code=404, detail="Calculo no encontrado")
    return _to_response(calc)


@router.delete("/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calculation_id: int, db: Session = Depends(get_db)) -> Response:
    """Soft-delete one calculation by ID."""
    logger.info("DELETE /calculations/%s", calculation_id)
    calc = db.get(Calculation, calculation_id)
    if calc is None or calc.eliminado:
        raise HTTPException(status_code=404, detail="Calculo no encontrado")

    calc.eliminado = True
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/structured/", response_model=CalculationResponse, status_code=status.HTTP_201_CREATED)
def create_structured_calculation(
    req: StructuredCalculationRequest, db: Session = Depends(get_db)
) -> CalculationResponse:
    """Create a calculation using the Capa1 + Unión + Capa2 model."""
    logger.info("POST /calculations/structured: %s", req.nombre)
    try:
        capa1 = [c.model_dump() for c in req.capa1]
        union = req.union.model_dump()
        capa2 = [c.model_dump() for c in req.capa2]

        R_frecuencias = engine.calcular_aislamiento_estructurado(
            capa1=capa1,
            union=union,
            capa2=capa2,
            frecuencias=req.frecuencias,
        )
        ponderacion = engine.ponderacion_iso717_1(R_frecuencias)
        resultado = {**ponderacion, "R_frecuencias": R_frecuencias}

        entrada_json = json.dumps(
            {"structured": True, **req.model_dump()}, ensure_ascii=False
        )
        calc = Calculation(
            proyecto_id=req.proyecto_id,
            nombre=req.nombre,
            entrada_json=entrada_json,
            resultado_json=json.dumps(resultado, ensure_ascii=False),
            timestamp=datetime.utcnow(),
        )
        db.add(calc)
        db.commit()
        db.refresh(calc)

        # Re-use the flat CalculationRequest wrapper for the response schema
        entrada_flat = CalculationRequest(
            proyecto_id=req.proyecto_id,
            nombre=req.nombre,
            materiales=[],
        )
        return CalculationResponse(
            id=calc.id,
            proyecto_id=calc.proyecto_id,
            nombre=calc.nombre,
            entrada=entrada_flat,
            salida=resultado,
            timestamp=calc.timestamp,
        )
    except MaterialNotFoundError as exc:
        logger.error("Material invalido: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CalculationError as exc:
        logger.error("Calculo estructurado fallido: %s", exc)
        raise HTTPException(status_code=500, detail="Error en calculo") from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error inesperado structured: %s", exc)
        raise HTTPException(status_code=500, detail="Error interno") from exc


def _to_response(calc: Calculation) -> CalculationResponse:
    """Convert a SQLAlchemy model into the API response schema."""
    entrada = CalculationRequest(**json.loads(calc.entrada_json))
    salida = json.loads(calc.resultado_json)
    return CalculationResponse(
        id=calc.id,
        proyecto_id=calc.proyecto_id,
        nombre=calc.nombre,
        entrada=entrada,
        salida=salida,
        timestamp=calc.timestamp,
    )
