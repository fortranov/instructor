"""
Простые тесты для проверки работоспособности сервиса
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
import os

# Удаляем тестовую базу данных, если она существует
if os.path.exists("./triplan.db"):
    os.remove("./triplan.db")

from main import app

client = TestClient(app)

def test_health_check():
    """Тест проверки здоровья сервиса"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Triplan Backend Service" in response.json()["message"]

def test_get_competition_types():
    """Тест получения типов соревнований"""
    response = client.get("/api/v1/competition-types")
    assert response.status_code == 200
    data = response.json()
    assert "running" in data
    assert "cycling" in data
    assert "swimming" in data
    assert "triathlon" in data

def test_create_running_plan():
    """Тест создания плана для бега"""
    plan_data = {
        "uin": "test_runner",
        "complexity": 500,
        "competition_date": (date.today() + timedelta(days=90)).isoformat(),
        "competition_type": "run_marathon"
    }
    
    response = client.post("/api/v1/plans/create", json=plan_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["complexity"] == 500
    assert data["competition_type"] == "run_marathon"
    assert len(data["workouts"]) > 0

def test_create_triathlon_plan():
    """Тест создания плана для триатлона"""
    plan_data = {
        "uin": "test_triathlete",
        "complexity": 700,
        "competition_date": (date.today() + timedelta(days=120)).isoformat(),
        "competition_type": "triathlon_olympic"
    }
    
    response = client.post("/api/v1/plans/create", json=plan_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["complexity"] == 700
    assert data["competition_type"] == "triathlon_olympic"
    
    # Проверяем, что есть тренировки всех трех видов спорта
    sport_types = set([workout["sport_type"] for workout in data["workouts"]])
    assert "running" in sport_types
    assert "cycling" in sport_types
    assert "swimming" in sport_types

def test_get_plan():
    """Тест получения плана"""
    response = client.get("/api/v1/plans/test_runner")
    assert response.status_code == 200
    
    data = response.json()
    assert data["complexity"] == 500

def test_get_workouts_by_date():
    """Тест получения тренировок по датам"""
    start_date = date.today().isoformat()
    end_date = (date.today() + timedelta(days=14)).isoformat()
    
    response = client.get(
        f"/api/v1/plans/test_runner/workouts",
        params={"start_date": start_date, "end_date": end_date}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["uin"] == "test_runner"
    assert isinstance(data["workouts"], list)

def test_replace_existing_plan():
    """Тест замены существующего плана"""
    # Создаем первый план
    plan_data = {
        "uin": "test_replace",
        "complexity": 300,
        "competition_date": (date.today() + timedelta(days=60)).isoformat(),
        "competition_type": "run_10k"
    }
    
    response1 = client.post("/api/v1/plans/create", json=plan_data)
    assert response1.status_code == 201
    plan1_id = response1.json()["id"]
    
    # Создаем второй план для того же пользователя
    plan_data["complexity"] = 600
    plan_data["competition_type"] = "run_half_marathon"
    
    response2 = client.post("/api/v1/plans/create", json=plan_data)
    assert response2.status_code == 201
    plan2_id = response2.json()["id"]
    
    # ID должны отличаться (новый план заменил старый)
    assert plan1_id != plan2_id
    
    # Проверяем, что остался только новый план
    response = client.get("/api/v1/plans/test_replace")
    assert response.status_code == 200
    assert response.json()["complexity"] == 600

def test_delete_plan():
    """Тест удаления плана"""
    response = client.delete("/api/v1/plans/test_replace")
    assert response.status_code == 204
    
    # Проверяем, что план удален
    response = client.get("/api/v1/plans/test_replace")
    assert response.status_code == 404

def test_get_nonexistent_plan():
    """Тест получения несуществующего плана"""
    response = client.get("/api/v1/plans/nonexistent_user")
    assert response.status_code == 404

def test_delete_nonexistent_plan():
    """Тест удаления несуществующего плана"""
    response = client.delete("/api/v1/plans/nonexistent_user")
    assert response.status_code == 404

def test_invalid_date_range():
    """Тест с некорректным диапазоном дат"""
    start_date = (date.today() + timedelta(days=10)).isoformat()
    end_date = date.today().isoformat()
    
    response = client.get(
        f"/api/v1/plans/test_runner/workouts",
        params={"start_date": start_date, "end_date": end_date}
    )
    assert response.status_code == 400

def test_cycling_with_distance():
    """Тест создания плана для велосипеда с указанием дистанции"""
    plan_data = {
        "uin": "test_cyclist",
        "complexity": 400,
        "competition_date": (date.today() + timedelta(days=75)).isoformat(),
        "competition_type": "cycling",
        "competition_distance": 150.0  # 150 км
    }
    
    response = client.post("/api/v1/plans/create", json=plan_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["competition_distance"] == 150.0
    assert data["competition_type"] == "cycling"

if __name__ == "__main__":
    # Запуск тестов
    print("Запуск тестов...")
    
    # Можно запустить отдельные тесты
    test_health_check()
    print("✓ Health check test passed")
    
    test_root_endpoint()
    print("✓ Root endpoint test passed")
    
    test_get_competition_types()
    print("✓ Competition types test passed")
    
    test_create_running_plan()
    print("✓ Create running plan test passed")
    
    test_create_triathlon_plan()
    print("✓ Create triathlon plan test passed")
    
    test_get_plan()
    print("✓ Get plan test passed")
    
    test_get_workouts_by_date()
    print("✓ Get workouts by date test passed")
    
    test_replace_existing_plan()
    print("✓ Replace existing plan test passed")
    
    test_delete_plan()
    print("✓ Delete plan test passed")
    
    test_cycling_with_distance()
    print("✓ Cycling with distance test passed")
    
    print("\nВсе тесты прошли успешно! ✅")
