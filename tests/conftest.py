import pytest

@pytest.fixture
def client():
    """Фикстура для тестового клиента FastAPI"""
    from fastapi.testclient import TestClient
    from app import app
    with TestClient(app) as client:
        yield client
