"""Backend-level unit tests for the acoustic engine and material library."""

from __future__ import annotations

import pytest

from engine.acoustic_engine import AcousticEngine, MaterialNotFoundError
from engine.materials import LibreriaMatariales, Material


class TestAcousticEngine:
    """Acoustic engine behavior tests."""

    @pytest.mark.unit
    def test_init(self, engine: AcousticEngine) -> None:
        """The engine should initialize with a material library."""
        assert engine.libreria.listar_todos()

    @pytest.mark.unit
    def test_calcular_simple(self, engine: AcousticEngine) -> None:
        """A concrete wall should produce a complete R(f) spectrum."""
        result = engine.calcular_aislamiento([{"nombre": "Hormigon 200mm", "espesor": 0.2}])
        assert result[1000.0] > 40

    @pytest.mark.unit
    def test_calcular_multiples_capas(self, engine: AcousticEngine) -> None:
        """Multiple layers should increase the total insulation."""
        simple = engine.calcular_aislamiento([{"nombre": "Hormigon 200mm", "espesor": 0.2}], [1000])
        multiple = engine.calcular_aislamiento(
            [
                {"nombre": "Hormigon 200mm", "espesor": 0.2},
                {"nombre": "Lana mineral 50mm", "espesor": 0.05},
            ],
            [1000],
        )
        assert multiple[1000.0] > simple[1000.0]

    @pytest.mark.unit
    def test_calcular_frecuencias_custom(self, engine: AcousticEngine) -> None:
        """Custom frequency bands should be respected."""
        result = engine.calcular_aislamiento([{"nombre": "Vidrio 6mm", "espesor": 0.006}], [125, 500])
        assert list(result) == [125.0, 500.0]

    @pytest.mark.unit
    def test_ponderacion_iso717(self, engine: AcousticEngine) -> None:
        """ISO weighting should return a reasonable Rw value."""
        spectrum = engine.calcular_aislamiento([{"nombre": "Hormigon 200mm", "espesor": 0.2}])
        result = engine.ponderacion_iso717_1(spectrum)
        assert 30 <= result["Rw"] <= 70

    @pytest.mark.unit
    def test_error_material_inexistente(self, engine: AcousticEngine) -> None:
        """Unknown materials should raise MaterialNotFoundError."""
        with pytest.raises(MaterialNotFoundError):
            engine.calcular_aislamiento([{"nombre": "No existe", "espesor": 0.2}])


class TestMateriales:
    """Material catalog tests."""

    @pytest.mark.unit
    def test_buscar_por_nombre(self) -> None:
        """The catalog should find concrete by normalized name."""
        libreria = LibreriaMatariales()
        assert libreria.buscar_por_nombre("Hormigón 200mm").densidad == 2400

    @pytest.mark.unit
    def test_lista_vacia(self) -> None:
        """The standard catalog should not be empty."""
        assert LibreriaMatariales().listar_todos()

    @pytest.mark.unit
    def test_agregar_material_duplicado(self) -> None:
        """Duplicate additions should fail."""
        libreria = LibreriaMatariales()
        material = Material("Duplicado 10mm", 100, 0.1, "poroso")
        libreria.agregar_material(material)
        with pytest.raises(ValueError):
            libreria.agregar_material(material)
