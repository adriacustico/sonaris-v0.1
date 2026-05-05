"""Tests for acoustic calculation endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _payload(nombre: str = "Muro principal") -> dict:
    """Return a valid calculation payload."""
    return {
        "proyecto_id": 1,
        "nombre": nombre,
        "materiales": [{"nombre": "Hormigon 200mm", "espesor": 0.2}],
        "frecuencias": [125, 250, 500, 1000, 2000, 4000],
    }


def test_post_calculation_201(client: TestClient) -> None:
    """POST should create and return a persisted calculation."""
    response = client.post("/api/calculations/", json=_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert "Rw" in body["salida"]


def test_post_invalid_material_400(client: TestClient) -> None:
    """Invalid materials should return a client error."""
    payload = _payload()
    payload["materiales"] = [{"nombre": "Material invalido", "espesor": 0.2}]
    response = client.post("/api/calculations/", json=payload)
    assert response.status_code == 400


def test_get_calculation_200(client: TestClient) -> None:
    """GET by ID should return a created calculation."""
    created = client.post("/api/calculations/", json=_payload()).json()
    response = client.get(f"/api/calculations/{created['id']}")
    assert response.status_code == 200
    assert response.json()["nombre"] == "Muro principal"


def test_get_nonexistent_404(client: TestClient) -> None:
    """GET by missing ID should return 404."""
    response = client.get("/api/calculations/999")
    assert response.status_code == 404


def test_get_calculations_por_proyecto(client: TestClient) -> None:
    """Project listing should include project calculations."""
    client.post("/api/calculations/", json=_payload("Muro A"))
    client.post("/api/calculations/", json=_payload("Muro B"))
    response = client.get("/api/calculations/proyecto/1?limit=10&offset=0")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_calculation(client: TestClient) -> None:
    """DELETE should soft-delete and hide a calculation."""
    created = client.post("/api/calculations/", json=_payload()).json()
    response = client.delete(f"/api/calculations/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/calculations/{created['id']}").status_code == 404
