"""Acoustic material library for the calculation engine.

The module keeps an in-memory catalog of common porous, rigid and composite
materials used by the acoustic engine. It is intentionally framework-agnostic:
no FastAPI, database, or frontend imports live here.
"""

from __future__ import annotations

import re
from typing import Any
from unicodedata import normalize


MaterialDict = dict[str, str | float]


class Material:
    """Acoustic material with physical properties.

    Args:
        nombre: Human-readable material name.
        densidad: Material density in kg/m3.
        factor_perdida: Dimensionless loss factor between 0 and 1.
        tipo: Material family: ``poroso``, ``rigido`` or ``composite``.
        espesor: Optional thickness in meters. When omitted, it is inferred
            from the first ``NNmm`` fragment in the name, if present.

    Raises:
        ValueError: If density, loss factor, name, or type are invalid.
    """

    TIPOS_VALIDOS = {"poroso", "rigido", "composite"}

    def __init__(
        self,
        nombre: str,
        densidad: float,
        factor_perdida: float | None = None,
        tipo: str = "rigido",
        espesor: float | None = None,
        **extra: Any,
    ) -> None:
        """Initialize and validate a material."""
        if factor_perdida is None:
            factor_perdida = extra.pop("factor_pérdida", None)
        if factor_perdida is None:
            raise ValueError("El factor de perdida es obligatorio.")

        nombre_limpio = nombre.strip()
        tipo_normalizado = _normalizar_tipo(tipo)

        if not nombre_limpio:
            raise ValueError("El nombre del material no puede estar vacio.")
        if densidad <= 0:
            raise ValueError("La densidad debe ser mayor que cero.")
        if not 0 <= factor_perdida <= 1:
            raise ValueError("El factor de perdida debe estar entre 0 y 1.")
        if tipo_normalizado not in self.TIPOS_VALIDOS:
            raise ValueError(f"Tipo de material no soportado: {tipo}")

        espesor_calculado = self._inferir_espesor(nombre_limpio) if espesor is None else espesor
        if espesor_calculado < 0:
            raise ValueError("El espesor no puede ser negativo.")

        self.nombre = nombre_limpio
        self.densidad = float(densidad)
        self.espesor = float(espesor_calculado)
        self.factor_perdida = float(factor_perdida)
        self.tipo = tipo_normalizado

    def __repr__(self) -> str:
        """Return a compact developer-friendly representation."""
        return f"Material(nombre='{self.nombre}', ρ={self.densidad:g} kg/m³)"

    def to_dict(self) -> MaterialDict:
        """Serialize material properties for API responses or UI lists."""
        return {
            "nombre": self.nombre,
            "densidad": self.densidad,
            "espesor": self.espesor,
            "factor_perdida": self.factor_perdida,
            "tipo": self.tipo,
        }

    @staticmethod
    def _inferir_espesor(nombre: str) -> float:
        """Infer thickness in meters from names containing values like 50mm."""
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*mm", nombre, flags=re.IGNORECASE)
        if not match:
            return 0.0
        return float(match.group(1).replace(",", ".")) / 1000.0


class LibreriaMatariales:
    """In-memory catalog of standard acoustic materials."""

    def __init__(self) -> None:
        """Initialize the catalog with standard construction materials."""
        self._materiales: dict[str, Material] = {}
        for material in self._materiales_estandar():
            self.agregar_material(material)

    def agregar_material(self, material: Material) -> None:
        """Add a material to the catalog.

        Args:
            material: Material instance to store.

        Raises:
            ValueError: If another material with the same normalized name exists.
        """
        clave = _normalizar_nombre(material.nombre)
        if clave in self._materiales:
            raise ValueError(f"Material duplicado: {material.nombre}")
        self._materiales[clave] = material

    def buscar_por_nombre(self, nombre: str) -> Material:
        """Find a material by exact normalized name.

        Args:
            nombre: Material name, accent-insensitive and case-insensitive.

        Returns:
            Matching material.

        Raises:
            KeyError: If the material does not exist.
        """
        clave = _normalizar_nombre(nombre)
        try:
            return self._materiales[clave]
        except KeyError as exc:
            raise KeyError(f"Material no encontrado: {nombre}") from exc

    def buscar_por_tipo(self, tipo: str) -> list[Material]:
        """Return all materials for a given family type."""
        tipo_normalizado = _normalizar_tipo(tipo)
        if tipo_normalizado not in Material.TIPOS_VALIDOS:
            raise ValueError(f"Tipo de material no soportado: {tipo}")
        return [material for material in self._materiales.values() if material.tipo == tipo_normalizado]

    def listar_todos(self) -> list[MaterialDict]:
        """Return every catalog material as dictionaries."""
        return [material.to_dict() for material in self._materiales.values()]

    def _materiales_estandar(self) -> list[Material]:
        """Build the standard catalog used during initialization."""
        return [
            Material("Lana mineral 50mm", 30, 0.10, "poroso"),
            Material("Espuma acustica 25mm", 40, 0.15, "poroso"),
            Material("Corcho natural 30mm", 120, 0.08, "poroso"),
            Material("Lana de vidrio 50mm", 25, 0.12, "poroso"),
            Material("Lana de roca 70mm", 70, 0.10, "poroso"),
            Material("Fibra de poliester 50mm", 35, 0.11, "poroso"),
            Material("Espuma melamina 40mm", 11, 0.18, "poroso"),
            Material("Espuma poliuretano 30mm", 28, 0.14, "poroso"),
            Material("Fieltro acustico 10mm", 180, 0.09, "poroso"),
            Material("Panel fibra madera 25mm", 250, 0.07, "poroso"),
            Material("Celulosa insuflada 80mm", 55, 0.10, "poroso"),
            Material("Algodon reciclado 50mm", 45, 0.12, "poroso"),
            Material("Fibra coco 30mm", 110, 0.08, "poroso"),
            Material("Perlita expandida 50mm", 90, 0.06, "poroso"),
            Material("Vermiculita 50mm", 100, 0.06, "poroso"),
            Material("Hormigon 200mm", 2400, 0.02, "rigido"),
            Material("Ladrillo ceramico 120mm", 1800, 0.03, "rigido"),
            Material("Yeso + papel 13mm", 900, 0.01, "rigido"),
            Material("Hormigon armado 150mm", 2500, 0.02, "rigido"),
            Material("Hormigon liviano 150mm", 1800, 0.03, "rigido"),
            Material("Bloque hormigon 150mm", 1400, 0.03, "rigido"),
            Material("Ladrillo hueco 120mm", 1000, 0.04, "rigido"),
            Material("Placa yeso 15mm", 850, 0.02, "rigido"),
            Material("Fibrocemento 10mm", 1350, 0.02, "rigido"),
            Material("Vidrio 4mm", 2500, 0.005, "rigido"),
            Material("Vidrio 6mm", 2500, 0.005, "rigido"),
            Material("Vidrio 10mm", 2500, 0.005, "rigido"),
            Material("Acero 3mm", 7850, 0.002, "rigido"),
            Material("Aluminio 3mm", 2700, 0.003, "rigido"),
            Material("Madera pino 18mm", 520, 0.04, "rigido"),
            Material("MDF 18mm", 720, 0.04, "rigido"),
            Material("OSB 15mm", 620, 0.04, "rigido"),
            Material("Contrachapado 18mm", 600, 0.04, "rigido"),
            Material("Baldosa ceramica 10mm", 2000, 0.02, "rigido"),
            Material("Mortero cemento 20mm", 2000, 0.02, "rigido"),
            Material("Doble vidrio 4-12-4", 800, 0.06, "composite"),
            Material("Ladrillo 120 + lana 50", 900, 0.05, "composite"),
            Material("Yeso doble + lana 50", 450, 0.07, "composite"),
            Material("Hormigon 150 + lana 50", 1250, 0.05, "composite"),
            Material("Vidrio laminado 3+3", 2500, 0.04, "composite"),
            Material("Panel sandwich acero 80mm", 1200, 0.04, "composite"),
            Material("Panel SIP 114mm", 520, 0.04, "composite"),
            Material("Puerta madera maciza 45mm", 650, 0.04, "composite"),
            Material("Puerta metalica aislada 50mm", 900, 0.05, "composite"),
            Material("Piso flotante madera + manta", 500, 0.08, "composite"),
            Material("Cielo yeso + lana 100", 300, 0.08, "composite"),
            Material("Tabique metalcon doble placa", 520, 0.06, "composite"),
            Material("Muro cortina vidrio camara", 900, 0.05, "composite"),
            Material("Cubierta chapa + aislante", 650, 0.06, "composite"),
            Material("Membrana vinilica cargada 3mm", 1900, 0.08, "composite"),
        ]


LibreriaMateriales = LibreriaMatariales


def _normalizar_nombre(nombre: str) -> str:
    """Normalize names for accent-insensitive dictionary lookup."""
    ascii_name = normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_name.lower().replace("-", " ").replace("_", " ").split())


def _normalizar_tipo(tipo: str) -> str:
    """Normalize type names and accept accented input."""
    normalizado = _normalizar_nombre(tipo)
    if normalizado == "rigido":
        return "rigido"
    return normalizado


_DEFAULT_LIBRARY = LibreriaMatariales()


def get_material(key: str) -> Material:
    """Backward-compatible helper for older imports."""
    return _DEFAULT_LIBRARY.buscar_por_nombre(key)


MATERIALS: dict[str, Material] = {
    _normalizar_nombre(material.nombre): material for material in _DEFAULT_LIBRARY.buscar_por_tipo("poroso")
}
MATERIALS.update(
    {_normalizar_nombre(material.nombre): material for material in _DEFAULT_LIBRARY.buscar_por_tipo("rigido")}
)
MATERIALS.update(
    {_normalizar_nombre(material.nombre): material for material in _DEFAULT_LIBRARY.buscar_por_tipo("composite")}
)


if __name__ == "__main__":
    libreria = LibreriaMatariales()

    material = libreria.buscar_por_nombre("Hormigon 200mm")
    print(material.densidad)

    todos = libreria.listar_todos()
    for mat in todos[:5]:
        print(mat)
