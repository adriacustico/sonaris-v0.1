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


def _estimar_propiedades_elasticas(densidad: float, tipo: str) -> tuple[float, float]:
    """Estimate (Young's modulus Pa, Poisson's ratio) from density and material type.

    Used as a fallback when explicit values are not provided. The estimates
    are conservative mid-range values for each material family.
    """
    if tipo == "poroso":
        return (1e6, 0.25)  # very soft; coincidence is irrelevant
    if densidad >= 7000:          # metals: steel, iron
        return (200e9, 0.30)
    if densidad >= 2450:          # glass, dense minerals
        return (70e9, 0.23)
    if densidad >= 2200:          # regular concrete, dense masonry
        return (30e9, 0.20)
    if densidad >= 1600:          # brick, hollow block, heavy ceramic
        return (12e9, 0.20)
    if densidad >= 1200:          # fiber cement, dense gypsum plaster
        return (18e9, 0.22)
    if densidad >= 700:           # gypsum board, lightweight composites
        return (2_500_000_000.0, 0.25)
    if densidad >= 450:           # wood (pine, spruce), OSB
        return (10e9, 0.35)
    return (5e9, 0.30)            # lightweight composites, MDF


class Material:
    """Acoustic material with physical and elastic properties.

    Args:
        nombre: Human-readable material name.
        densidad: Material density in kg/m3.
        factor_perdida: Dimensionless loss factor between 0 and 1.
        tipo: Material family: ``poroso``, ``rigido`` or ``composite``.
        espesor: Optional thickness in meters. When omitted, it is inferred
            from the first ``NNmm`` fragment in the name, if present.
        modulo_young: Optional Young's modulus in Pa. Auto-estimated when None.
        coef_poisson: Optional Poisson's ratio (0–0.5). Auto-estimated when None.

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
        modulo_young: float | None = None,
        coef_poisson: float | None = None,
        **extra: Any,
    ) -> None:
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

        e_est, nu_est = _estimar_propiedades_elasticas(densidad, tipo_normalizado)
        self.nombre = nombre_limpio
        self.densidad = float(densidad)
        self.espesor = float(espesor_calculado)
        self.factor_perdida = float(factor_perdida)
        self.tipo = tipo_normalizado
        self.modulo_young: float = float(modulo_young) if modulo_young is not None else e_est
        self.coef_poisson: float = float(coef_poisson) if coef_poisson is not None else nu_est

    def __repr__(self) -> str:
        return f"Material(nombre='{self.nombre}', ρ={self.densidad:g} kg/m³)"

    @property
    def categoria(self) -> str:
        """UI category: 'filling' for cavity absorbers, 'rigid' for structural panels."""
        return "filling" if self.tipo == "poroso" else "rigid"

    def to_dict(self) -> MaterialDict:
        """Serialize material properties for API responses or UI lists."""
        return {
            "nombre": self.nombre,
            "densidad": self.densidad,
            "espesor": self.espesor,
            "factor_perdida": self.factor_perdida,
            "tipo": self.tipo,
            "categoria": self.categoria,
        }

    @staticmethod
    def _inferir_espesor(nombre: str) -> float:
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*mm", nombre, flags=re.IGNORECASE)
        if not match:
            return 0.0
        return float(match.group(1).replace(",", ".")) / 1000.0


class LibreriaMatariales:
    """In-memory catalog of standard acoustic materials."""

    def __init__(self) -> None:
        self._materiales: dict[str, Material] = {}
        for material in self._materiales_estandar():
            self.agregar_material(material)

    def agregar_material(self, material: Material) -> None:
        clave = _normalizar_nombre(material.nombre)
        if clave in self._materiales:
            raise ValueError(f"Material duplicado: {material.nombre}")
        self._materiales[clave] = material

    def buscar_por_nombre(self, nombre: str) -> Material:
        clave = _normalizar_nombre(nombre)
        try:
            return self._materiales[clave]
        except KeyError as exc:
            raise KeyError(f"Material no encontrado: {nombre}") from exc

    def buscar_por_tipo(self, tipo: str) -> list[Material]:
        tipo_normalizado = _normalizar_tipo(tipo)
        if tipo_normalizado not in Material.TIPOS_VALIDOS:
            raise ValueError(f"Tipo de material no soportado: {tipo}")
        return [m for m in self._materiales.values() if m.tipo == tipo_normalizado]

    def listar_todos(self) -> list[MaterialDict]:
        return [m.to_dict() for m in self._materiales.values()]

    def _materiales_estandar(self) -> list[Material]:
        """Standard catalog with explicit E and ν for materials where
        the density-based estimate would be inaccurate."""
        def m(nombre: str, densidad: float, fp: float, tipo: str,
              E: float | None = None, nu: float | None = None) -> Material:
            return Material(nombre, densidad, fp, tipo, modulo_young=E, coef_poisson=nu)

        return [
            # ── Porosos ─────────────────────────────────────────────────────
            m("Lana mineral 50mm",          30,   0.10, "poroso"),
            m("Espuma acustica 25mm",        40,   0.15, "poroso"),
            m("Corcho natural 30mm",        120,   0.08, "poroso"),
            m("Lana de vidrio 50mm",         25,   0.12, "poroso"),
            m("Lana de roca 70mm",           70,   0.10, "poroso"),
            m("Fibra de poliester 50mm",     35,   0.11, "poroso"),
            m("Espuma melamina 40mm",        11,   0.18, "poroso"),
            m("Espuma poliuretano 30mm",     28,   0.14, "poroso"),
            m("Fieltro acustico 10mm",      180,   0.09, "poroso"),
            m("Panel fibra madera 25mm",    250,   0.07, "poroso"),
            m("Celulosa insuflada 80mm",     55,   0.10, "poroso"),
            m("Algodon reciclado 50mm",      45,   0.12, "poroso"),
            m("Fibra coco 30mm",            110,   0.08, "poroso"),
            m("Perlita expandida 50mm",      90,   0.06, "poroso"),
            m("Vermiculita 50mm",           100,   0.06, "poroso"),

            # ── Rígidos ─────────────────────────────────────────────────────
            # Hormigón: E = 30 GPa, ν = 0.20
            m("Hormigon 200mm",            2400, 0.02, "rigido", E=30e9, nu=0.20),
            m("Hormigon armado 150mm",     2500, 0.02, "rigido", E=32e9, nu=0.20),
            m("Hormigon liviano 150mm",    1800, 0.03, "rigido", E=18e9, nu=0.20),
            m("Bloque hormigon 150mm",     1400, 0.03, "rigido", E=10e9, nu=0.20),
            # Mampostería
            m("Ladrillo ceramico 120mm",   1800, 0.03, "rigido", E=12e9, nu=0.20),
            m("Ladrillo hueco 120mm",      1000, 0.04, "rigido", E=5e9,  nu=0.20),
            # Yeso y placas
            m("Yeso + papel 13mm",          900, 0.01, "rigido", E=2e9,  nu=0.25),
            m("Placa yeso 15mm",            850, 0.02, "rigido", E=2e9,  nu=0.25),
            # Fibrocemento y mortero
            m("Fibrocemento 10mm",         1350, 0.02, "rigido", E=18e9, nu=0.22),
            m("Mortero cemento 20mm",      2000, 0.02, "rigido", E=20e9, nu=0.20),
            # Vidrio: E = 70 GPa, ν = 0.23  →  c_L ≈ 5400 m/s  →  f_c(6mm) ≈ 2000 Hz
            m("Vidrio 4mm",                2500, 0.005, "rigido", E=70e9, nu=0.23),
            m("Vidrio 6mm",                2500, 0.005, "rigido", E=70e9, nu=0.23),
            m("Vidrio 10mm",               2500, 0.005, "rigido", E=70e9, nu=0.23),
            # Metales
            m("Acero 3mm",                 7850, 0.002, "rigido", E=200e9, nu=0.30),
            m("Aluminio 3mm",              2700, 0.003, "rigido", E=70e9,  nu=0.33),
            # Madera y derivados: E ~10 GPa (parallel to grain), ν = 0.35
            m("Madera pino 18mm",           520, 0.04, "rigido", E=10e9, nu=0.35),
            m("MDF 18mm",                   720, 0.04, "rigido", E=5e9,  nu=0.30),
            m("OSB 15mm",                   620, 0.04, "rigido", E=5e9,  nu=0.30),
            m("Contrachapado 18mm",         600, 0.04, "rigido", E=6e9,  nu=0.30),
            m("Baldosa ceramica 10mm",     2000, 0.02, "rigido", E=50e9, nu=0.25),

            # ── Composites ──────────────────────────────────────────────────
            m("Doble vidrio 4-12-4",        800, 0.06, "composite"),
            m("Ladrillo 120 + lana 50",     900, 0.05, "composite"),
            m("Yeso doble + lana 50",       450, 0.07, "composite"),
            m("Hormigon 150 + lana 50",    1250, 0.05, "composite"),
            m("Vidrio laminado 3+3",       2500, 0.04, "composite", E=70e9, nu=0.23),
            m("Panel sandwich acero 80mm", 1200, 0.04, "composite"),
            m("Panel SIP 114mm",            520, 0.04, "composite"),
            m("Puerta madera maciza 45mm",  650, 0.04, "composite"),
            m("Puerta metalica aislada 50mm", 900, 0.05, "composite"),
            m("Piso flotante madera + manta", 500, 0.08, "composite"),
            m("Cielo yeso + lana 100",      300, 0.08, "composite"),
            m("Tabique metalcon doble placa", 520, 0.06, "composite"),
            m("Muro cortina vidrio camara", 900, 0.05, "composite"),
            m("Cubierta chapa + aislante",  650, 0.06, "composite"),
            m("Membrana vinilica cargada 3mm", 1900, 0.08, "composite"),
        ]


LibreriaMateriales = LibreriaMatariales


def _normalizar_nombre(nombre: str) -> str:
    ascii_name = normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_name.lower().replace("-", " ").replace("_", " ").split())


def _normalizar_tipo(tipo: str) -> str:
    normalizado = _normalizar_nombre(tipo)
    if normalizado == "rigido":
        return "rigido"
    return normalizado


_DEFAULT_LIBRARY = LibreriaMatariales()


def get_material(key: str) -> Material:
    """Backward-compatible helper for older imports."""
    return _DEFAULT_LIBRARY.buscar_por_nombre(key)


MATERIALS: dict[str, Material] = {}
for _tipo in ("poroso", "rigido", "composite"):
    MATERIALS.update({_normalizar_nombre(mat.nombre): mat for mat in _DEFAULT_LIBRARY.buscar_por_tipo(_tipo)})


if __name__ == "__main__":
    libreria = LibreriaMatariales()
    material = libreria.buscar_por_nombre("Hormigon 200mm")
    print(material.densidad, material.modulo_young)
    todos = libreria.listar_todos()
    for mat in todos[:5]:
        print(mat)
