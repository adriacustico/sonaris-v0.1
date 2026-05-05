"""ISO 717-1 weighted sound reduction helpers."""

from __future__ import annotations

from typing import Any

from engine.calculations.utils import interpolar_frecuencias, log10_seguro, redondear_iso717


# ── Reference curve ISO 717-1:2013 Table 1 (Rw = 52 dB baseline) ──────────────

CURVA_REFERENCIA_ISO717_1: dict[float, float] = {
    100.0: 33.0, 125.0: 36.0, 160.0: 39.0, 200.0: 42.0,
    250.0: 45.0, 315.0: 48.0, 400.0: 51.0, 500.0: 52.0,
    630.0: 53.0, 800.0: 54.0, 1000.0: 55.0, 1250.0: 56.0,
    1600.0: 56.0, 2000.0: 56.0, 2500.0: 56.0, 3150.0: 56.0,
    4000.0: 57.0, 5000.0: 58.0,
}

_RW_BASE = 52.0
_SUMA_MAX_DESVIACIONES = 32.0

# ── ISO 717-1:2013 Annex A — Spectrum adaptation terms ────────────────────────
#
# Type I (C)  — indoor activities / pink-noise-weighted source.
# Type II (Ctr) — urban road / railway traffic spectrum.
# Values in dB, normalised so that 10·log10(Σ 10^(L/10)) = 0 dB per band set.
# Band range for both terms: 100 Hz – 3150 Hz (16 one-third-octave bands).

_ESPECTRO_C: dict[float, float] = {
    100.0: -29.0, 125.0: -26.0, 160.0: -23.0, 200.0: -21.0,
    250.0: -19.0, 315.0: -17.0, 400.0: -15.0, 500.0: -13.0,
    630.0: -12.0, 800.0: -11.0, 1000.0: -10.0, 1250.0: -9.0,
    1600.0: -9.0, 2000.0: -9.0, 2500.0: -9.0, 3150.0: -9.0,
}

_ESPECTRO_CTR: dict[float, float] = {
    100.0: -20.0, 125.0: -20.0, 160.0: -18.0, 200.0: -16.0,
    250.0: -15.0, 315.0: -14.0, 400.0: -13.0, 500.0: -12.0,
    630.0: -11.0,  800.0:  -9.0, 1000.0: -8.0, 1250.0: -9.0,
    1600.0: -10.0, 2000.0: -11.0, 2500.0: -13.0, 3150.0: -15.0,
}


class ISO717CalculationError(ValueError):
    """Raised when ISO 717-1 weighting cannot be calculated."""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _termino_adaptacion(
    espectro_R: dict[float, float],
    espectro_Li: dict[float, float],
    rw: int,
) -> int:
    """Compute an ISO 717-1 spectrum adaptation term (C or Ctr).

    Implements clause 5.2 of ISO 717-1:2013:
        X = −10 · log10( Σ_j 10^((L_j − R_j) / 10) ) − Rw

    where L_j are the normalised reference spectrum values and R_j are the
    sound reduction values at each one-third-octave band.  Interpolation
    (log-linear) is used to map R to the 16 reference bands.

    Typical results: C ∈ [−4, 0] dB,  Ctr ∈ [−15, −4] dB.
    """
    bandas_ref = sorted(espectro_Li)
    R_interp = interpolar_frecuencias(espectro_R, bandas_ref)

    suma = sum(
        10.0 ** ((espectro_Li[f] - R_interp[f]) / 10.0)
        for f in bandas_ref
        if f in R_interp
    )
    r_eficaz = -10.0 * log10_seguro(suma)
    return redondear_iso717(r_eficaz - rw)


# ── Main function ─────────────────────────────────────────────────────────────

def aplicar_ponderacion_iso717_1(R_frecuencias: dict[float, float]) -> dict[str, Any]:
    """Apply ISO 717-1 weighting to an R(f) spectrum.

    Procedure (ISO 717-1:2013 clause 5.1):
    Shift the reference curve upward (positive offset) until the sum of
    adverse deviations against the shifted curve first reaches or falls
    below 32 dB.  The first (minimum) such offset determines Rw.

    Adaptation terms C and Ctr are computed per Annex A (clause 5.2) using
    the normalised Type-I and Type-II reference spectra.

    Args:
        R_frecuencias: Measured / calculated reduction index by frequency (Hz → dB).

    Returns:
        Dictionary with keys: Rw, C, Ctr, offset, max_desviacion, R_ponderado.

    Raises:
        ISO717CalculationError: If the spectrum is empty or invalid.
    """
    if not R_frecuencias:
        raise ISO717CalculationError("R_frecuencias no puede estar vacio.")

    espectro = {float(f): float(v) for f, v in R_frecuencias.items()}
    if any(f <= 0 for f in espectro):
        raise ISO717CalculationError("Todas las frecuencias deben ser mayores que cero.")
    if any(v < 0 for v in espectro.values()):
        raise ISO717CalculationError("Los valores R(f) no pueden ser negativos.")

    frecuencias = sorted(espectro)
    referencia_interpolada = interpolar_frecuencias(CURVA_REFERENCIA_ISO717_1, frecuencias)

    mejor_offset: float | None = None
    mejor_suma = 0.0
    mejor_max = 0.0

    for paso in range(-500, 501):
        offset = paso / 10.0
        desviaciones = [
            max(0.0, referencia_interpolada[f] - (espectro[f] + offset))
            for f in frecuencias
        ]
        suma = sum(desviaciones)
        if suma <= _SUMA_MAX_DESVIACIONES:
            mejor_offset = offset
            mejor_suma = suma
            mejor_max = max(desviaciones) if desviaciones else 0.0
            break

    if mejor_offset is None:
        mejor_offset = 50.0
        mejor_suma = 0.0
        mejor_max = 0.0

    rw = redondear_iso717(_RW_BASE + mejor_offset)

    r_ponderado = {f: round(v + mejor_offset, 1) for f, v in espectro.items()}

    # Adaptation terms per ISO 717-1:2013 Annex A
    c_term = _termino_adaptacion(espectro, _ESPECTRO_C, rw)
    ctr_term = _termino_adaptacion(espectro, _ESPECTRO_CTR, rw)

    return {
        "Rw": rw,
        "C": c_term,
        "Ctr": ctr_term,
        "offset": round(mejor_offset, 1),
        "max_desviacion": round(mejor_max, 1),
        "R_ponderado": r_ponderado,
    }


def calculate_weighted_index(values_db: list[float]) -> float:
    """Backward-compatible helper for early placeholder tests."""
    if not values_db:
        return 0.0
    return round(sum(values_db) / len(values_db), 1)
