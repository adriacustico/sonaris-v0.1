"""Sharp-style airborne sound reduction calculations."""

from __future__ import annotations

from math import sqrt

from engine.calculations.utils import log10_seguro
from engine.materials import Material


class SharpCalculationError(ValueError):
    """Raised when the Sharp calculation receives invalid input."""


_C_AIRE = 343.0


def _velocidad_longitudinal(material: Material) -> float:
    """Plate longitudinal wave speed (m/s) for critical-frequency computation.

    Uses the exact formula  c_L = sqrt(E / (rho*(1-nu²)))  when the material
    has explicit elastic constants.  Falls back to a density-based estimate
    for materials that were not given explicit modulo_young values.
    """
    E = material.modulo_young
    rho = material.densidad
    nu = material.coef_poisson
    if E > 1e6 and rho > 0:          # guard against default poroso value (1 MPa)
        denom = rho * (1.0 - nu ** 2)
        if denom > 0:
            return sqrt(E / denom)
    # Density-only fallback
    if rho >= 4000:
        return 5000.0   # steel, aluminium
    if rho >= 1500:
        return 3500.0   # concrete, brick, ceramic
    if rho >= 600:
        return 2000.0   # wood, gypsum, dense composites
    return 1200.0        # lightweight boards


def calcular_r_sharp(material: Material, frecuencia: float) -> float:
    """Calculate sound reduction index R(f) for a single material layer.

    Model:
    * Porous absorbers: empirical formula based on surface mass × frequency.
    * Rigid / composite panels: field-incidence mass law (constant −52 dB)
      with a Sharp coincidence correction at and above the critical frequency
      f_c = c² / (1.8 · c_L · h).  The correction term 10·log10(2η) is
      negative for η < 0.5, representing the coincidence dip.  For glass and
      other stiff thin panels, f_c falls inside the audible band, producing
      a visible dip in the spectrum.

    Args:
        material: Material with density, thickness, loss factor, and elastic
            constants.  Elastic constants (modulo_young, coef_poisson) are
            used to compute f_c accurately; a density fallback is used when
            they are not set.
        frecuencia: Frequency in Hz.

    Returns:
        Reduction index in dB (≥ 0).

    Raises:
        SharpCalculationError: On invalid input.
    """
    if frecuencia <= 0:
        raise SharpCalculationError("La frecuencia debe ser mayor que cero.")
    if material.espesor <= 0:
        raise SharpCalculationError("El espesor del material debe ser mayor que cero.")

    tipo = material.tipo
    m_s = material.densidad * material.espesor  # surface mass (kg/m²)

    if tipo == "poroso":
        r_db = 0.0571 * log10_seguro(m_s * frecuencia) + 10.0

    elif tipo in {"rigido", "composite"}:
        r_mass = 20.0 * log10_seguro(m_s * frecuencia) - 52.0

        c_L = _velocidad_longitudinal(material)
        f_c = (_C_AIRE ** 2) / (1.8 * c_L * material.espesor)

        if frecuencia >= f_c:
            # Sharp coincidence formula: mass law + damping term.
            # 10·log10(2η) < 0 for η < 0.5, reducing R at and above f_c.
            r_db = r_mass + 10.0 * log10_seguro(2.0 * material.factor_perdida)
        else:
            r_db = r_mass

        if tipo == "composite":
            r_db += 10.0 * material.factor_perdida

    else:
        raise SharpCalculationError(f"Tipo de material no soportado: {material.tipo}")

    return round(max(0.0, r_db), 1)


def estimate_transmission_loss(
    material_data: Material, thickness_mm: float
) -> dict[str, float | str | list[float]]:
    """Compatibility wrapper for older API code paths."""
    material = Material(
        nombre=material_data.nombre,
        densidad=material_data.densidad,
        factor_perdida=material_data.factor_perdida,
        tipo=material_data.tipo,
        espesor=thickness_mm / 1000.0,
        modulo_young=material_data.modulo_young,
        coef_poisson=material_data.coef_poisson,
    )
    frequencies = [125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0]
    losses = [calcular_r_sharp(material, f) for f in frequencies]
    return {
        "method": "sharp",
        "material": material.nombre,
        "surface_mass_kg_m2": round(material.densidad * material.espesor, 2),
        "frequencies_hz": frequencies,
        "transmission_loss_db": losses,
    }
