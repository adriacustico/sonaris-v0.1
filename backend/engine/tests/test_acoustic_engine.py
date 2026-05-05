"""Unit tests for the acoustic engine facade."""

from __future__ import annotations

import pytest

from engine.acoustic_engine import AcousticEngine, CalculationError, MaterialNotFoundError


@pytest.fixture
def motor() -> AcousticEngine:
    """Return a ready-to-use acoustic engine."""
    return AcousticEngine()


@pytest.fixture
def material_hormigon() -> list[dict[str, float | str]]:
    """Return a concrete layer fixture."""
    return [{"nombre": "Hormigon 200mm", "espesor": 0.2}]


@pytest.fixture
def material_lana() -> list[dict[str, float | str]]:
    """Return a mineral wool layer fixture."""
    return [{"nombre": "Lana mineral 50mm", "espesor": 0.05}]


@pytest.fixture
def R_frecuencias_muestra(motor: AcousticEngine, material_hormigon: list[dict[str, float | str]]) -> dict[float, float]:
    """Return a representative R(f) spectrum."""
    return motor.calcular_aislamiento(material_hormigon)


def test_material_simple(motor: AcousticEngine, material_hormigon: list[dict[str, float | str]]) -> None:
    """Concrete at 200 mm should provide strong and increasing insulation."""
    R_f = motor.calcular_aislamiento(material_hormigon)
    assert R_f[1000.0] > 40
    assert R_f[2000.0] > R_f[1000.0] > R_f[500.0]


def test_material_no_existe(motor: AcousticEngine) -> None:
    """Unknown materials should raise the public engine error."""
    with pytest.raises(MaterialNotFoundError):
        motor.calcular_aislamiento([{"nombre": "Material imposible", "espesor": 0.1}])


def test_ponderacion_iso717(motor: AcousticEngine, R_frecuencias_muestra: dict[float, float]) -> None:
    """The ISO 717-1 weighting should return a reasonable single-number index."""
    resultado = motor.ponderacion_iso717_1(R_frecuencias_muestra)
    assert 30 <= resultado["Rw"] <= 70
    assert "R_ponderado" in resultado


def test_multiples_capas(
    motor: AcousticEngine,
    material_hormigon: list[dict[str, float | str]],
    material_lana: list[dict[str, float | str]],
) -> None:
    """A multi-layer assembly should exceed each single-layer spectrum."""
    vidrio = [{"nombre": "Vidrio 6mm", "espesor": 0.006}]
    R_total = motor.calcular_aislamiento(material_hormigon + material_lana + vidrio, [1000.0])
    R_individual = motor.calcular_aislamiento(material_hormigon, [1000.0])
    assert R_total[1000.0] > R_individual[1000.0]


def test_validaciones(motor: AcousticEngine) -> None:
    """Invalid thickness, frequency and empty material lists should fail."""
    with pytest.raises(CalculationError):
        motor.calcular_aislamiento([{"nombre": "Hormigon 200mm", "espesor": -0.2}])
    with pytest.raises(CalculationError):
        motor.calcular_aislamiento([{"nombre": "Hormigon 200mm", "espesor": 0.2}], [0])
    with pytest.raises(CalculationError):
        motor.calcular_aislamiento([])
