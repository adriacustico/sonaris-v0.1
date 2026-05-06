"""Double-leaf (doble hoja) acoustic model.

Implements a simplified Sharp / Hopkins mass-air-mass model for two panels
separated by an air cavity, with optional porous fill and mechanical coupling
through different types of structural connections (unions/studs).

References:
    Sharp, B.H. (1978). Prediction methods for the sound transmission of
        building elements. Noise Control Engineering, 11(2), 53–63.
    Hopkins, C. (2007). Sound Insulation. Butterworth-Heinemann.
    Davy, J.L. (2009). The prediction of the sound insulation of walls with
        stud connections. Applied Acoustics, 71(9), 829–834.
"""

from __future__ import annotations

from math import sqrt

from engine.calculations.sharp import calcular_r_sharp
from engine.calculations.utils import log10_seguro
from engine.materials import Material


_C_AIRE = 343.0
_ESPACIADO_STUD_M = 0.6   # 600 mm — typical stud spacing

# Stud-path constants — Davy mass-dependent formula:
#   R_stud = 20·log10(f · S · m1 · m2) + C_abs
#
# Including panel masses (m1·m2 term) ensures that heavier walls give better
# stud resistance, avoiding the artefact where R_stud ≤ R_single-wall when
# both sides carry multiple boards.
#
# Calibrated so that 1×Placa-yeso-15mm each side + 90 mm Metalcon gives
# Rw ≈ 40–43 dB, matching typical field measurements.
_C_STUD_ABS: dict[str, float] = {
    "montantes_metal":   -58.0,   # light-gauge steel C-stud (Metalcon)
    "montantes_madera":  -65.0,   # 38×90 mm wood stud (more coupling)
}

TIPOS_UNION_VALIDOS = frozenset({
    "rigida",
    "montantes_metal",
    "montantes_madera",
    "canal_resiliente",
    "aire",
})


class DobleHojaError(ValueError):
    """Raised when the double-leaf calculation receives invalid input."""


def calcular_r_doble_hoja(
    capa1: Material,
    capa2: Material,
    separacion_m: float,
    tipo_union: str,
    tiene_relleno: bool,
    frecuencia: float,
) -> float:
    """Compute sound reduction R(f) for a double-leaf cavity partition.

    Physical model
    ──────────────
    1. **Rigid union** (``rigida``): cavity is short-circuited by direct
       structural coupling.  Both panels behave as a single wall with
       combined surface mass m₁+m₂.

    2. **Below mass-air-mass resonance** (f ≤ f_mam): the system behaves as
       a single wall with combined mass.

    3. **Above f_mam** (f > f_mam): two parallel transmission paths:

       * *Air path* (cavity isolation):
         R_air = R₁ + R₂ + max(0, 20·log10(f/f_mam) − 6)
         (+6 dB bonus when cavity has porous fill)

       * *Stud path* (mechanical bridge through studs):
         R_stud = 20·log10(f · S) + C_stud   (Sharp stud formula)

       Combined transmission:  τ_total = τ_air + τ_stud
       R_total = −10·log10(τ_total)

       For ``canal_resiliente`` and ``aire`` the stud path is negligible
       (mechanical decoupling), so R → R_air.

    Mass-air-mass resonance (Sharp 1978):
        f_mam = 60 · √[(m₁+m₂) / (d · m₁ · m₂)]
    where d is cavity depth in metres and m in kg/m².

    Args:
        capa1: First panel (must have espesor > 0).
        capa2: Second panel (must have espesor > 0).
        separacion_m: Cavity depth in metres (> 0).
        tipo_union: One of ``rigida``, ``montantes_metal``,
            ``montantes_madera``, ``canal_resiliente``, ``aire``.
        tiene_relleno: True when the cavity contains porous fill (mineral
            wool, glass wool, etc.).  Adds ≈ 6 dB to the air-path gain.
        frecuencia: Frequency in Hz.

    Returns:
        Sound reduction index R in dB (≥ 0).

    Raises:
        DobleHojaError: On invalid input values.
    """
    if frecuencia <= 0:
        raise DobleHojaError("La frecuencia debe ser mayor que cero.")
    if separacion_m <= 0:
        raise DobleHojaError("La separacion debe ser mayor que cero.")
    if capa1.espesor <= 0 or capa2.espesor <= 0:
        raise DobleHojaError("El espesor de cada capa debe ser mayor que cero.")

    tipo = tipo_union.strip().lower()
    if tipo not in TIPOS_UNION_VALIDOS:
        raise DobleHojaError(
            f"Tipo de union no soportado: '{tipo_union}'. "
            f"Valores validos: {sorted(TIPOS_UNION_VALIDOS)}"
        )

    m1 = capa1.densidad * capa1.espesor   # surface mass (kg/m²)
    m2 = capa2.densidad * capa2.espesor

    # ── Rigid union: no cavity benefit ──────────────────────────────────────
    if tipo == "rigida":
        r_sw = 20.0 * log10_seguro((m1 + m2) * frecuencia) - 52.0
        return round(max(0.0, r_sw), 1)

    # ── Mass-air-mass resonance frequency ───────────────────────────────────
    # Sharp (1978): f_mam = 60·√[(m1+m2)/(d·m1·m2)]
    f_mam = 60.0 * sqrt((m1 + m2) / (separacion_m * m1 * m2))

    # Single-wall equivalent with combined mass (lower bound)
    r_sw = max(0.0, 20.0 * log10_seguro((m1 + m2) * frecuencia) - 52.0)

    # ── Below resonance: single-wall regime ─────────────────────────────────
    if frecuencia <= f_mam:
        return round(r_sw, 1)

    # ── Above resonance: double-wall regime ─────────────────────────────────
    R1 = calcular_r_sharp(capa1, frecuencia)
    R2 = calcular_r_sharp(capa2, frecuencia)

    # Cavity isolation gain: 6 dB/octave above f_mam, offset by −6 dB at
    # the crossover (onset of double-wall behaviour).
    delta = max(0.0, 20.0 * log10_seguro(frecuencia / f_mam) - 6.0)
    R_air = R1 + R2 + delta

    # Porous fill improves cavity absorption (≈ +6 dB, Guigou-Carter 2006)
    if tiene_relleno:
        R_air += 6.0

    # ── Fully decoupled paths (no stud bridge) ───────────────────────────────
    if tipo in {"canal_resiliente", "aire"}:
        return round(max(r_sw, R_air), 1)

    # ── Stud path (Davy mass-dependent formula) ──────────────────────────────
    # R_stud = 20·log10(f · S · m1 · m2) + C_abs
    # Panel mass product ensures heavier assemblies get better stud resistance,
    # preventing the single-wall shortcut from dominating on multi-board walls.
    C_stud = _C_STUD_ABS.get(tipo, -58.0)
    R_stud = 20.0 * log10_seguro(frecuencia * _ESPACIADO_STUD_M * m1 * m2) + C_stud

    # Combine air and stud transmission paths in parallel
    tau_air  = 10.0 ** (-R_air  / 10.0)
    tau_stud = 10.0 ** (-R_stud / 10.0)
    R_total  = -10.0 * log10_seguro(tau_air + tau_stud)

    return round(max(r_sw, R_total), 1)
