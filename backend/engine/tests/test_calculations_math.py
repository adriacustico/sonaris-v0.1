"""Tests for low-level acoustic calculation functions."""

from __future__ import annotations

import pytest

from engine.calculations.iso717_1 import aplicar_ponderacion_iso717_1
from engine.calculations.sharp import SharpCalculationError, calcular_r_sharp
from engine.calculations.utils import generar_frecuencias_estandar, interpolar_frecuencias, log10_seguro
from engine.materials import Material


def test_calcular_r_sharp_rigido() -> None:
    """Rigid materials should return positive R values for valid bands."""
    material = Material("Hormigon 200mm", 2400, 0.02, "rigido", espesor=0.2)
    assert calcular_r_sharp(material, 1000.0) > 40


def test_calcular_r_sharp_poroso() -> None:
    """Porous materials should use the porous Sharp branch."""
    material = Material("Lana mineral 50mm", 30, 0.1, "poroso", espesor=0.05)
    assert calcular_r_sharp(material, 1000.0) > 0


def test_calcular_r_sharp_valida_frecuencia() -> None:
    """Zero or negative frequencies should be rejected."""
    material = Material("Hormigon 200mm", 2400, 0.02, "rigido", espesor=0.2)
    with pytest.raises(SharpCalculationError):
        calcular_r_sharp(material, 0)


def test_aplicar_ponderacion_iso717_1() -> None:
    """ISO weighting should return Rw and adaptation terms."""
    spectrum = {frequency: 45.0 + index for index, frequency in enumerate(generar_frecuencias_estandar())}
    result = aplicar_ponderacion_iso717_1(spectrum)
    assert {"Rw", "C", "Ctr", "offset", "max_desviacion", "R_ponderado"} <= set(result)


def test_interpolar_frecuencias() -> None:
    """Frequency interpolation should fill target bands."""
    result = interpolar_frecuencias({100.0: 30.0, 1000.0: 50.0}, [100.0, 500.0, 1000.0])
    assert set(result) == {100.0, 500.0, 1000.0}


def test_log10_seguro() -> None:
    """Safe logarithm should avoid math domain errors."""
    assert log10_seguro(0) < 0
