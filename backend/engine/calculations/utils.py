"""Mathematical helpers shared by acoustic calculations."""

from __future__ import annotations

from math import floor, log10


def log10_seguro(valor: float) -> float:
    """Return base-10 logarithm while avoiding log of zero or negatives."""
    return log10(max(valor, 1e-12))


def redondear_iso717(valor: float) -> int:
    """Round a value using the integer convention used for ISO single numbers."""
    return int(floor(valor + 0.5))


def generar_frecuencias_estandar() -> list[float]:
    """Return one-third octave bands from 100 Hz to 5000 Hz."""
    return [
        100.0,
        125.0,
        160.0,
        200.0,
        250.0,
        315.0,
        400.0,
        500.0,
        630.0,
        800.0,
        1000.0,
        1250.0,
        1600.0,
        2000.0,
        2500.0,
        3150.0,
        4000.0,
        5000.0,
    ]


def interpolar_frecuencias(R_dict: dict[float, float], frecuencias_target: list[float]) -> dict[float, float]:
    """Interpolate acoustic values to target frequency bands.

    Interpolation is linear over log-frequency, which is appropriate for
    octave and one-third-octave acoustic spectra.
    """
    if not R_dict:
        raise ValueError("R_dict no puede estar vacio.")
    if not frecuencias_target:
        raise ValueError("frecuencias_target no puede estar vacio.")

    puntos = sorted((float(frecuencia), float(valor)) for frecuencia, valor in R_dict.items())
    resultado: dict[float, float] = {}

    for target in [float(frecuencia) for frecuencia in frecuencias_target]:
        if target <= puntos[0][0]:
            resultado[target] = puntos[0][1]
            continue
        if target >= puntos[-1][0]:
            resultado[target] = puntos[-1][1]
            continue

        for izquierda, derecha in zip(puntos, puntos[1:]):
            f1, r1 = izquierda
            f2, r2 = derecha
            if f1 <= target <= f2:
                posicion = (log10_seguro(target) - log10_seguro(f1)) / (log10_seguro(f2) - log10_seguro(f1))
                resultado[target] = round(r1 + posicion * (r2 - r1), 3)
                break

    return resultado


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a numeric value into an inclusive range."""
    return max(minimum, min(value, maximum))
