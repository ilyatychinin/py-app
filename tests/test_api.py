import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root_endpoint():
    """Тест главной страницы"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data

def test_health_check():
    """Тест проверки здоровья"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data

def test_get_all_users():
    """Тест получения всех пользователей"""
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)

def test_get_all_todos():
    """Тест получения всех задач"""
    response = client.get("/todos")
    assert response.status_code == 200
    todos = response.json()
    assert isinstance(todos, list)

def test_get_stats():
    """Тест получения статистики"""
    response = client.get("/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total" in stats
    assert "completed" in stats
    assert "pending" in stats

def test_get_user_stats():
    """Тест получения статистики по пользователям"""
    response = client.get("/stats/users")
    assert response.status_code == 200
    stats = response.json()
    assert isinstance(stats, list)
