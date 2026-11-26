"""Tests para autenticación."""

import pytest
from fastapi.testclient import TestClient
from ganimedes.server import app

client = TestClient(app)


def test_health_check():
    """Test del endpoint de health check."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] in ("healthy", "degraded", "testing")


@pytest.mark.skip(reason="Requiere configuración de Supabase")
def test_signup():
    """Test de registro de usuario."""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201


@pytest.mark.skip(reason="Requiere configuración de Supabase")
def test_signin():
    """Test de inicio de sesión."""
    response = client.post(
        "/api/auth/signin",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    assert "session" in response.json()
