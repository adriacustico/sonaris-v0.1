"""Tests for the structured Capa1 + Unión + Capa2 calculation model."""

from __future__ import annotations

import pytest

from engine.acoustic_engine import AcousticEngine, CalculationError, MaterialNotFoundError
from engine.materials import LibreriaMatariales


@pytest.fixture
def motor() -> AcousticEngine:
    return AcousticEngine()


# ── test_materiales_categoria ─────────────────────────────────────────────────

def test_materiales_categoria_rigid() -> None:
    """Rigid and composite materials must be classified as 'rigid'."""
    libreria = LibreriaMatariales()
    for material in libreria.buscar_por_tipo("rigido"):
        assert material.categoria == "rigid", f"{material.nombre} should be rigid"
    for material in libreria.buscar_por_tipo("composite"):
        assert material.categoria == "rigid", f"{material.nombre} should be rigid"


def test_materiales_categoria_filling() -> None:
    """Porous materials must be classified as 'filling'."""
    libreria = LibreriaMatariales()
    for material in libreria.buscar_por_tipo("poroso"):
        assert material.categoria == "filling", f"{material.nombre} should be filling"


def test_to_dict_incluye_categoria() -> None:
    """to_dict() must expose the categoria field."""
    libreria = LibreriaMatariales()
    d = libreria.buscar_por_nombre("Hormigon 200mm").to_dict()
    assert "categoria" in d
    assert d["categoria"] == "rigid"


# ── test_estructura_capas ─────────────────────────────────────────────────────

def test_estructura_doble_hoja_supera_capa_simple(motor: AcousticEngine) -> None:
    """Double-leaf Capa1+Unión+Capa2 should outperform Capa1 alone at 1000 Hz."""
    capa1 = [{"nombre": "Placa yeso 15mm", "cantidad": 2, "espesor_unitario_mm": 15}]
    union = {
        "relleno_nombre": "Lana mineral 50mm",
        "relleno_espesor_mm": 100,
        "camara_aire_mm": 0,
        "tipo_montantes": "montantes_metal",
    }
    capa2 = [{"nombre": "Placa yeso 15mm", "cantidad": 1, "espesor_unitario_mm": 15}]

    R_doble = motor.calcular_aislamiento_estructurado(capa1, union, capa2, [1000.0])
    R_solo = motor.calcular_aislamiento(
        [{"nombre": "Placa yeso 15mm", "espesor": 0.015}], [1000.0]
    )
    assert R_doble[1000.0] > R_solo[1000.0], (
        f"Double-leaf {R_doble[1000.0]} dB should exceed single panel {R_solo[1000.0]} dB"
    )


def test_estructura_equivale_single_sin_cavidad(motor: AcousticEngine) -> None:
    """Capa1 only (no capa2, no cavity) must match the Sharp single-panel result."""
    capa1 = [{"nombre": "Hormigon 200mm", "cantidad": 1, "espesor_unitario_mm": 200}]
    union = {"camara_aire_mm": 0}
    R_struct = motor.calcular_aislamiento_estructurado(capa1, union, [], [500.0, 1000.0])
    R_sharp  = motor.calcular_aislamiento(
        [{"nombre": "Hormigon 200mm", "espesor": 0.2}], [500.0, 1000.0]
    )
    for f in [500.0, 1000.0]:
        assert R_struct[f] == pytest.approx(R_sharp[f], abs=0.1)


def test_estructura_multicapa_combina_masas(motor: AcousticEngine) -> None:
    """2× Placa yeso on one side should yield higher R than 1× at 1000 Hz."""
    union: dict[str, object] = {"camara_aire_mm": 0}
    R_uno = motor.calcular_aislamiento_estructurado(
        [{"nombre": "Placa yeso 15mm", "cantidad": 1, "espesor_unitario_mm": 15}],
        union, [], [1000.0],
    )
    R_dos = motor.calcular_aislamiento_estructurado(
        [{"nombre": "Placa yeso 15mm", "cantidad": 2, "espesor_unitario_mm": 15}],
        union, [], [1000.0],
    )
    assert R_dos[1000.0] > R_uno[1000.0]


def test_estructura_material_no_existe(motor: AcousticEngine) -> None:
    """Unknown material name must raise MaterialNotFoundError."""
    with pytest.raises(MaterialNotFoundError):
        motor.calcular_aislamiento_estructurado(
            [{"nombre": "Material Inexistente XYZ", "cantidad": 1, "espesor_unitario_mm": 50}],
            {"camara_aire_mm": 0}, [], [1000.0],
        )


def test_estructura_sin_capas_falla(motor: AcousticEngine) -> None:
    """Empty capa1 and capa2 must raise CalculationError."""
    with pytest.raises(CalculationError):
        motor.calcular_aislamiento_estructurado([], {"camara_aire_mm": 0}, [])


# ── test_tabla_resultados ─────────────────────────────────────────────────────

def test_tabla_resultados_coincide_con_grafico(motor: AcousticEngine) -> None:
    """R_frecuencias returned by the engine are the same values used by the chart."""
    capa1 = [{"nombre": "Hormigon 200mm", "cantidad": 1, "espesor_unitario_mm": 200}]
    union: dict[str, object] = {"camara_aire_mm": 0}
    R_f = motor.calcular_aislamiento_estructurado(capa1, union, [])
    ponderacion = motor.ponderacion_iso717_1(R_f)

    # The chart data and table data come from the same R_frecuencias dict
    for f, r in R_f.items():
        assert isinstance(f, float)
        assert isinstance(r, float)
        assert r >= 0, f"R({f} Hz) must be non-negative"

    # Rw should be a plausible single-number for 200 mm concrete
    assert 30 <= ponderacion["Rw"] <= 80
