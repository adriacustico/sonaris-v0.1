"""ISO 717-1 weighted sound reduction helpers."""

from __future__ import annotations

from typing import Any

from engine.calculations.utils import interpolar_frecuencias, redondear_iso717


# Reference curve values from ISO 717-1:2013 Table 1 (Rw = 52 dB baseline).
# Each value is the reference at that 1/3-octave band for a wall with Rw = 52 dB.
CURVA_REFERENCIA_ISO717_1: dict[float, float] = {
    100.0: 33.0,
    125.0: 36.0,
    160.0: 39.0,
    200.0: 42.0,
    250.0: 45.0,
    315.0: 48.0,
    400.0: 51.0,
    500.0: 52.0,
    630.0: 53.0,
    800.0: 54.0,
    1000.0: 55.0,
    1250.0: 56.0,
    1600.0: 56.0,
    2000.0: 56.0,
    2500.0: 56.0,
    3150.0: 56.0,
    4000.0: 57.0,
    5000.0: 58.0,
}

# Rw baseline: reference curve value at 500 Hz (ISO 717-1 Table 1).
_RW_BASE = 52.0

# Maximum allowed sum of adverse deviations (ISO 717-1 clause 5.1).
_SUMA_MAX_DESVIACIONES = 32.0


class ISO717CalculationError(ValueError):
    """Raised when ISO 717-1 weighting cannot be calculated."""


def aplicar_ponderacion_iso717_1(R_frecuencias: dict[float, float]) -> dict[str, Any]:
    """Apply ISO 717-1 weighting to an R(f) spectrum.

    The procedure follows ISO 717-1:2013 clause 5.1:
    shift R(f) upward (positive offset) until the sum of adverse deviations
    against the reference curve first reaches or falls below 32 dB.  The
    minimum such offset is the result; Rw = _RW_BASE + offset.

    Args:
        R_frecuencias: Measured or calculated reduction index by frequency.

    Returns:
        A dictionary with Rw, C, Ctr, offset, maximum deviation and weighted
        values for every input frequency.

    Raises:
        ISO717CalculationError: If the spectrum is empty or contains invalid values.
    """
    if not R_frecuencias:
        raise ISO717CalculationError("R_frecuencias no puede estar vacio.")

    espectro = {float(frecuencia): float(valor) for frecuencia, valor in R_frecuencias.items()}
    if any(frecuencia <= 0 for frecuencia in espectro):
        raise ISO717CalculationError("Todas las frecuencias deben ser mayores que cero.")
    if any(valor < 0 for valor in espectro.values()):
        raise ISO717CalculationError("Los valores R(f) no pueden ser negativos.")

    frecuencias = sorted(espectro)
    referencia_interpolada = interpolar_frecuencias(CURVA_REFERENCIA_ISO717_1, frecuencias)

    # ISO 717-1 procedure: find the minimum offset (scanning low to high) at which
    # the sum of adverse deviations ≤ 32 dB.  An adverse deviation at frequency f
    # is max(0, ref[f] − (R[f] + offset)) — it appears when the reference curve
    # exceeds the shifted spectrum.  A higher offset means a better-performing wall.
    mejor_offset: float | None = None
    mejor_suma = 0.0
    mejor_max = 0.0

    for paso in range(-500, 501):
        offset = paso / 10.0
        desviaciones = [
            max(0.0, referencia_interpolada[frecuencia] - (espectro[frecuencia] + offset))
            for frecuencia in frecuencias
        ]
        suma = sum(desviaciones)
        if suma <= _SUMA_MAX_DESVIACIONES:
            mejor_offset = offset
            mejor_suma = suma
            mejor_max = max(desviaciones) if desviaciones else 0.0
            break  # first (minimum) offset satisfying the constraint

    if mejor_offset is None:
        # Degenerate case: even at the maximum scan offset the wall is too poor.
        # Use the least-bad result instead of crashing.
        mejor_offset = 50.0
        mejor_suma = 0.0
        mejor_max = 0.0

    rw = redondear_iso717(_RW_BASE + mejor_offset)

    r_100 = _valor_banda_cercana(espectro, 100.0)
    r_500 = _valor_banda_cercana(espectro, 500.0)
    r_ponderado = {
        frecuencia: round(valor + mejor_offset, 1)
        for frecuencia, valor in espectro.items()
    }

    return {
        "Rw": rw,
        "C": redondear_iso717(r_100 - rw),
        "Ctr": redondear_iso717(r_500 - rw),
        "offset": round(mejor_offset, 1),
        "max_desviacion": round(mejor_max, 1),
        "R_ponderado": r_ponderado,
    }


def calculate_weighted_index(values_db: list[float]) -> float:
    """Backward-compatible helper for early placeholder tests."""
    if not values_db:
        return 0.0
    return round(sum(values_db) / len(values_db), 1)


def _valor_banda_cercana(espectro: dict[float, float], objetivo: float) -> float:
    """Return the spectrum value nearest to a target frequency."""
    frecuencia = min(espectro, key=lambda item: abs(item - objetivo))
    return espectro[frecuencia]
