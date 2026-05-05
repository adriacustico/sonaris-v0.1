"""Sharp-style airborne sound reduction calculations."""

from __future__ import annotations

from engine.calculations.utils import log10_seguro
from engine.materials import Material


class SharpCalculationError(ValueError):
    """Raised when the Sharp calculation receives invalid input."""


# Speed of sound in air at 20°C (m/s)
_C_AIRE = 343.0


def _estimar_velocidad_longitudinal(densidad: float) -> float:
    """Estimate longitudinal plate wave speed from bulk density (m/s).

    This is used only to estimate the critical frequency for the coincidence
    correction; exact values are not required for a reasonable prediction.
    """
    if densidad >= 4000:
        return 5000.0  # metals: steel, aluminum
    if densidad >= 1500:
        return 3500.0  # concrete, brick, ceramic, glass
    if densidad >= 600:
        return 2000.0  # wood, gypsum, dense composites
    return 1200.0       # lightweight porous boards


def calcular_r_sharp(material: Material, frecuencia: float) -> float:
    """Calculate sound reduction index R(f) for one material layer.

    Uses the field-incidence mass law below the critical frequency and the
    Sharp above-coincidence formula (mass law + damping correction) at and
    above the critical frequency.

    Args:
        material: Acoustic material with density, thickness and type.
        frecuencia: Frequency in Hz.

    Returns:
        Reduction index in dB. Negative values are clipped to 0 dB.

    Raises:
        SharpCalculationError: If frequency, material type or thickness is invalid.
    """
    if frecuencia <= 0:
        raise SharpCalculationError("La frecuencia debe ser mayor que cero.")
    if material.espesor <= 0:
        raise SharpCalculationError("El espesor del material debe ser mayor que cero.")

    tipo = material.tipo
    m_s = material.densidad * material.espesor  # surface mass density (kg/m²)

    if tipo == "poroso":
        # Porous absorbers: simplified empirical law for sound reduction.
        r_db = 0.0571 * log10_seguro(m_s * frecuencia) + 10.0

    elif tipo in {"rigido", "composite"}:
        # Field-incidence mass law (constant −52 dB is the −47 dB normal-incidence
        # value minus the standard 5 dB field-incidence correction).
        r_mass = 20.0 * log10_seguro(m_s * frecuencia) - 52.0

        c_L = _estimar_velocidad_longitudinal(material.densidad)
        f_c = (_C_AIRE ** 2) / (1.8 * c_L * material.espesor)

        if frecuencia >= f_c:
            # Sharp above-coincidence formula: mass law + damping term.
            # 10·log10(2·η) is negative for η < 0.5, reducing R relative to mass law.
            r_db = r_mass + 10.0 * log10_seguro(2.0 * material.factor_perdida)
        else:
            r_db = r_mass

        if tipo == "composite":
            # Composite assemblies benefit from additional stiffness-decoupling.
            r_db += 10.0 * material.factor_perdida

    else:
        raise SharpCalculationError(f"Tipo de material no soportado: {material.tipo}")

    return round(max(0.0, r_db), 1)


def estimate_transmission_loss(material_data: Material, thickness_mm: float) -> dict[str, float | str | list[float]]:
    """Compatibility wrapper for older API code paths."""
    material = Material(
        nombre=material_data.nombre,
        densidad=material_data.densidad,
        factor_perdida=material_data.factor_perdida,
        tipo=material_data.tipo,
        espesor=thickness_mm / 1000.0,
    )
    frequencies = [125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0]
    losses = [calcular_r_sharp(material, frequency) for frequency in frequencies]
    return {
        "method": "sharp",
        "material": material.nombre,
        "surface_mass_kg_m2": round(material.densidad * material.espesor, 2),
        "frequencies_hz": frequencies,
        "transmission_loss_db": losses,
    }
