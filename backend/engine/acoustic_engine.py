"""Main acoustic calculation engine.

This module is the public facade for the backend:

    from engine.acoustic_engine import AcousticEngine

The API layer does not need to know about catalog lookup, Sharp formulas or
ISO 717-1 weighting internals.
"""

from __future__ import annotations

from typing import Any

from engine.calculations.iso717_1 import ISO717CalculationError, aplicar_ponderacion_iso717_1
from engine.calculations.sharp import SharpCalculationError, calcular_r_sharp
from engine.calculations.utils import generar_frecuencias_estandar
from engine.materials import LibreriaMatariales, Material


MaterialInput = dict[str, float | str]
MaterialProperties = dict[str, float | str]


class AcousticEngineError(Exception):
    """Base exception for acoustic engine errors."""


class MaterialNotFoundError(AcousticEngineError):
    """Raised when a material does not exist in the engine library."""


class CalculationError(AcousticEngineError):
    """Raised when an acoustic calculation cannot be completed."""


class AcousticEngine:
    """Engine for acoustic insulation calculations.

    The engine computes R(f) using the Sharp calculation implemented in
    ``engine.calculations.sharp`` and applies ISO 717-1 style weighting through
    ``engine.calculations.iso717_1``.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the acoustic engine.

        Args:
            config: Optional configuration dictionary. Supported key:
                ``materiales`` as a list of custom material dictionaries with
                ``nombre``, ``densidad``, ``factor_perdida`` and ``tipo``.
        """
        self.config = config or {}
        self.libreria = LibreriaMatariales()

        materiales_extra = self.config.get("materiales", [])
        if isinstance(materiales_extra, list):
            for material_data in materiales_extra:
                if isinstance(material_data, dict):
                    self.libreria.agregar_material(
                        Material(
                            nombre=str(material_data["nombre"]),
                            densidad=float(material_data["densidad"]),
                            factor_perdida=float(material_data["factor_perdida"]),
                            tipo=str(material_data.get("tipo", "rigido")),
                            espesor=float(material_data.get("espesor", 0.0)),
                        )
                    )

    def calcular_aislamiento(
        self,
        materiales: list[MaterialInput],
        frecuencias: list[float] | None = None,
    ) -> dict[float, float]:
        """Calculate total airborne sound reduction R(f).

        Args:
            materiales: Layers with ``nombre`` and ``espesor`` in meters.
            frecuencias: Optional frequency bands in Hz. Defaults to one-third
                octave bands from 100 Hz to 5000 Hz.

        Returns:
            Mapping ``{frecuencia: R_dB}``.

        Raises:
            MaterialNotFoundError: If a layer name is not in the material library.
            CalculationError: If thickness, frequency or formula input is invalid.
        """
        try:
            if not materiales:
                raise CalculationError("Debe proporcionar al menos un material.")

            bandas = self._validar_frecuencias(frecuencias or generar_frecuencias_estandar())
            capas = [self._crear_capa(material) for material in materiales]

            return {
                frecuencia: round(sum(calcular_r_sharp(capa, frecuencia) for capa in capas), 1)
                for frecuencia in bandas
            }
        except MaterialNotFoundError:
            raise
        except (CalculationError, SharpCalculationError) as exc:
            raise CalculationError(str(exc)) from exc
        except Exception as exc:
            raise CalculationError(f"Error calculando aislamiento: {exc}") from exc

    def ponderacion_iso717_1(self, R_frecuencias: dict[float, float]) -> dict[str, Any]:
        """Apply ISO 717-1 weighting to an R(f) spectrum.

        Args:
            R_frecuencias: Reduction index by frequency in dB.

        Returns:
            Dictionary with ``Rw``, ``C``, ``Ctr``, ``offset``,
            ``max_desviacion`` and ``R_ponderado``.

        Raises:
            CalculationError: If weighting cannot be calculated.
        """
        try:
            return aplicar_ponderacion_iso717_1(R_frecuencias)
        except ISO717CalculationError as exc:
            raise CalculationError(str(exc)) from exc
        except Exception as exc:
            raise CalculationError(f"Error aplicando ISO 717-1: {exc}") from exc

    def aplicar_iso717_1(self, R_frecuencias: dict[float, float]) -> dict[str, Any]:
        """Backward-compatible alias for ISO 717-1 weighting."""
        return self.ponderacion_iso717_1(R_frecuencias)

    def obtener_material(self, nombre: str) -> MaterialProperties:
        """Find material properties in the library.

        Args:
            nombre: Material name.

        Returns:
            Material properties as a dictionary.

        Raises:
            MaterialNotFoundError: If no matching material exists.
        """
        try:
            return self.libreria.buscar_por_nombre(nombre).to_dict()
        except KeyError as exc:
            raise MaterialNotFoundError(str(exc)) from exc

    def calculate_transmission_loss(self, material: str, thickness_mm: float) -> dict[str, float | str | list[float]]:
        """Compatibility helper for the current API placeholder.

        Args:
            material: Material name.
            thickness_mm: Thickness in millimeters.

        Returns:
            Frequencies and transmission loss arrays for UI wiring.
        """
        espesor_m = thickness_mm / 1000.0
        material_data = self.obtener_material(material)
        R_f = self.calcular_aislamiento(
            [{"nombre": material, "espesor": espesor_m}],
            [125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0],
        )
        return {
            "method": "sharp",
            "material": str(material_data["nombre"]),
            "surface_mass_kg_m2": round(float(material_data["densidad"]) * espesor_m, 2),
            "frequencies_hz": list(R_f.keys()),
            "transmission_loss_db": list(R_f.values()),
        }

    def _crear_capa(self, material_input: MaterialInput) -> Material:
        """Create a layer material by combining catalog data with input thickness."""
        nombre = str(material_input.get("nombre", "")).strip()
        if not nombre:
            raise CalculationError("Cada material debe incluir un nombre.")

        espesor = float(material_input.get("espesor", 0.0))
        if espesor <= 0:
            raise CalculationError(f"El espesor de {nombre} debe ser mayor que cero.")

        try:
            base = self.libreria.buscar_por_nombre(nombre)
        except KeyError as exc:
            raise MaterialNotFoundError(f"Material no encontrado: {nombre}") from exc

        return Material(
            nombre=base.nombre,
            densidad=base.densidad,
            factor_perdida=base.factor_perdida,
            tipo=base.tipo,
            espesor=espesor,
        )

    def _validar_frecuencias(self, frecuencias: list[float]) -> list[float]:
        """Validate and normalize frequency bands."""
        if not frecuencias:
            raise CalculationError("Debe proporcionar al menos una frecuencia.")

        bandas = [float(frecuencia) for frecuencia in frecuencias]
        if any(frecuencia <= 0 for frecuencia in bandas):
            raise CalculationError("Todas las frecuencias deben ser mayores que cero.")
        return bandas


if __name__ == "__main__":
    engine = AcousticEngine()

    muro = [{"nombre": "Hormigon 200mm", "espesor": 0.2}]
    R_f = engine.calcular_aislamiento(muro)
    print(f"R(f): {R_f}")

    resultado = engine.ponderacion_iso717_1(R_f)
    print(f"Rw: {resultado['Rw']} dB")
    print(f"C: {resultado['C']} dB")
