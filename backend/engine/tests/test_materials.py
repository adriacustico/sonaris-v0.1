"""Tests for the acoustic material library."""

from __future__ import annotations

import pytest

from engine.materials import LibreriaMatariales, Material


def test_buscar_por_nombre() -> None:
    """The library should resolve names regardless of accents."""
    libreria = LibreriaMatariales()
    material = libreria.buscar_por_nombre("Hormigón 200mm")
    assert material.densidad == 2400
    assert material.espesor == 0.2


def test_buscar_por_tipo() -> None:
    """Type searches should return only materials from that family."""
    libreria = LibreriaMatariales()
    porosos = libreria.buscar_por_tipo("poroso")
    assert porosos
    assert all(material.tipo == "poroso" for material in porosos)


def test_agregar_material_duplicado() -> None:
    """Duplicated normalized names should be rejected."""
    libreria = LibreriaMatariales()
    material = Material("Material test 10mm", 100, 0.1, "poroso")
    libreria.agregar_material(material)
    with pytest.raises(ValueError):
        libreria.agregar_material(material)
