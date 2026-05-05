"""Main acoustic calculation engine.

Public facade for the backend:

    from engine.acoustic_engine import AcousticEngine

The API layer does not need to know about catalog lookup, Sharp formulas or
ISO 717-1 weighting internals.
"""

from __future__ import annotations

from typing import Any

from engine.calculations.double_leaf import TIPOS_UNION_VALIDOS, calcular_r_doble_hoja
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

    Supports two calculation modes:

    * **Single-wall / multi-layer bonded** (``separacion_m`` not set or zero):
      Each layer is calculated with the Sharp formula and contributions are
      summed (independent-barrier approximation).

    * **Double-leaf cavity wall** (``separacion_m > 0``, exactly 2 layers):
      Uses the mass-air-mass model (double_leaf module) with selectable
      union type and optional porous cavity fill.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.libreria = LibreriaMatariales()

        for material_data in self.config.get("materiales", []):
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

    # ── Public API ────────────────────────────────────────────────────────────

    def calcular_aislamiento(
        self,
        materiales: list[MaterialInput],
        frecuencias: list[float] | None = None,
        separacion_m: float | None = None,
        tipo_union: str = "montantes_metal",
        tiene_relleno: bool = False,
    ) -> dict[float, float]:
        """Calculate total airborne sound reduction R(f).

        Args:
            materiales: Layer list, each entry with ``nombre`` and
                ``espesor`` (metres).
            frecuencias: Optional frequency bands in Hz.  Defaults to the
                standard one-third octave bands 100 Hz – 5000 Hz.
            separacion_m: Cavity depth in metres.  When provided and > 0 with
                exactly 2 layers, the double-leaf model is used instead of the
                independent-barrier sum.
            tipo_union: Union type for the double-leaf model.  One of
                ``rigida``, ``montantes_metal``, ``montantes_madera``,
                ``canal_resiliente``, ``aire``.  Ignored for single-wall mode.
            tiene_relleno: ``True`` when the cavity contains porous fill
                (mineral wool / glass wool).  Only used in double-leaf mode.

        Returns:
            Mapping ``{frecuencia_Hz: R_dB}``.

        Raises:
            MaterialNotFoundError: If a layer name is not in the library.
            CalculationError: On invalid input or formula error.
        """
        try:
            if not materiales:
                raise CalculationError("Debe proporcionar al menos un material.")

            bandas = self._validar_frecuencias(frecuencias or generar_frecuencias_estandar())
            capas = [self._crear_capa(m) for m in materiales]

            # ── Double-leaf mode ─────────────────────────────────────────────
            usa_doble_hoja = (
                separacion_m is not None
                and separacion_m > 0
                and len(capas) == 2
                and tipo_union in TIPOS_UNION_VALIDOS
            )

            if usa_doble_hoja:
                assert separacion_m is not None  # narrowing for type checker
                return {
                    f: calcular_r_doble_hoja(
                        capas[0], capas[1],
                        separacion_m, tipo_union, tiene_relleno, f,
                    )
                    for f in bandas
                }

            # ── Single-wall / independent-barrier sum ────────────────────────
            return {
                f: round(sum(calcular_r_sharp(capa, f) for capa in capas), 1)
                for f in bandas
            }

        except MaterialNotFoundError:
            raise
        except (CalculationError, SharpCalculationError) as exc:
            raise CalculationError(str(exc)) from exc
        except Exception as exc:
            raise CalculationError(f"Error calculando aislamiento: {exc}") from exc

    def ponderacion_iso717_1(self, R_frecuencias: dict[float, float]) -> dict[str, Any]:
        """Apply ISO 717-1 weighting to an R(f) spectrum."""
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
        """Find material properties in the library."""
        try:
            return self.libreria.buscar_por_nombre(nombre).to_dict()
        except KeyError as exc:
            raise MaterialNotFoundError(str(exc)) from exc

    def calculate_transmission_loss(
        self, material: str, thickness_mm: float
    ) -> dict[str, float | str | list[float]]:
        """Compatibility helper for the old API placeholder."""
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

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _crear_capa(self, material_input: MaterialInput) -> Material:
        nombre = str(material_input.get("nombre", "")).strip()
        if not nombre:
            raise CalculationError("Cada material debe incluir un nombre.")

        espesor = float(material_input.get("espesor", 0.0))
        if espesor <= 0:
            raise CalculationError(f"El espesor de '{nombre}' debe ser mayor que cero.")

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
            modulo_young=base.modulo_young,
            coef_poisson=base.coef_poisson,
        )

    def _validar_frecuencias(self, frecuencias: list[float]) -> list[float]:
        if not frecuencias:
            raise CalculationError("Debe proporcionar al menos una frecuencia.")
        bandas = [float(f) for f in frecuencias]
        if any(f <= 0 for f in bandas):
            raise CalculationError("Todas las frecuencias deben ser mayores que cero.")
        return bandas


if __name__ == "__main__":
    engine = AcousticEngine()

    # Single concrete wall
    R_f = engine.calcular_aislamiento([{"nombre": "Hormigon 200mm", "espesor": 0.2}])
    resultado = engine.ponderacion_iso717_1(R_f)
    print(f"Hormigon 200mm  Rw={resultado['Rw']} C={resultado['C']} Ctr={resultado['Ctr']}")

    # Double-leaf: 15 mm gypsum / 90 mm Metalcon / 15 mm gypsum, no fill
    R_dh = engine.calcular_aislamiento(
        [{"nombre": "Placa yeso 15mm", "espesor": 0.015},
         {"nombre": "Placa yeso 15mm", "espesor": 0.015}],
        separacion_m=0.09,
        tipo_union="montantes_metal",
        tiene_relleno=False,
    )
    res_dh = engine.ponderacion_iso717_1(R_dh)
    print(f"Yeso/Metalcon90/Yeso  Rw={res_dh['Rw']} C={res_dh['C']} Ctr={res_dh['Ctr']}")
