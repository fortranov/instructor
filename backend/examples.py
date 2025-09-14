"""
Примеры использования Triplan Backend Service API
"""

import requests
import json
from datetime import date, timedelta

# Базовый URL сервиса
BASE_URL = "http://localhost:8000/api/v1"

def example_create_running_plan():
    """Пример создания плана для бега на марафон"""
    
    plan_data = {
        "uin": "user123",
        "complexity": 600,  # Средне-высокая сложность
        "competition_date": (date.today() + timedelta(days=90)).isoformat(),  # Соревнование через 90 дней
        "competition_type": "run_marathon",
        "competition_distance": None  # Не нужно для марафона
    }
    
    response = requests.post(f"{BASE_URL}/plans/create", json=plan_data)
    print("Создание плана для марафона:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()

def example_create_triathlon_plan():
    """Пример создания плана для триатлона"""
    
    plan_data = {
        "uin": "triathlete456",
        "complexity": 800,  # Высокая сложность
        "competition_date": (date.today() + timedelta(days=120)).isoformat(),  # Соревнование через 120 дней
        "competition_type": "triathlon_olympic",
        "competition_distance": None  # Не нужно для олимпийского триатлона
    }
    
    response = requests.post(f"{BASE_URL}/plans/create", json=plan_data)
    print("\nСоздание плана для олимпийского триатлона:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()

def example_create_cycling_plan():
    """Пример создания плана для велосипеда"""
    
    plan_data = {
        "uin": "cyclist789",
        "complexity": 400,  # Средняя сложность
        "competition_date": (date.today() + timedelta(days=60)).isoformat(),  # Соревнование через 60 дней
        "competition_type": "cycling",
        "competition_distance": 100  # 100 км
    }
    
    response = requests.post(f"{BASE_URL}/plans/create", json=plan_data)
    print("\nСоздание плана для велосипеда на 100км:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()

def example_get_plan(uin: str):
    """Пример получения плана пользователя"""
    
    response = requests.get(f"{BASE_URL}/plans/{uin}")
    print(f"\nПолучение плана для пользователя {uin}:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()

def example_get_workouts_by_date(uin: str):
    """Пример получения тренировок по датам"""
    
    start_date = date.today().isoformat()
    end_date = (date.today() + timedelta(days=14)).isoformat()  # Следующие 2 недели
    
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    
    response = requests.get(f"{BASE_URL}/plans/{uin}/workouts", params=params)
    print(f"\nТренировки для пользователя {uin} на следующие 2 недели:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()

def example_delete_plan(uin: str):
    """Пример удаления плана"""
    
    response = requests.delete(f"{BASE_URL}/plans/{uin}")
    print(f"\nУдаление плана для пользователя {uin}:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 204:
        print("План успешно удален")
    else:
        print(response.text)

def example_get_competition_types():
    """Пример получения типов соревнований"""
    
    response = requests.get(f"{BASE_URL}/competition-types")
    print("\nДоступные типы соревнований:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()

def example_health_check():
    """Пример проверки здоровья сервиса"""
    
    response = requests.get(f"{BASE_URL}/health")
    print("\nПроверка здоровья сервиса:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()

if __name__ == "__main__":
    print("=== Примеры использования Triplan Backend Service ===")
    
    try:
        # Проверка здоровья сервиса
        example_health_check()
        
        # Получение типов соревнований
        example_get_competition_types()
        
        # Создание планов
        example_create_running_plan()
        example_create_triathlon_plan() 
        example_create_cycling_plan()
        
        # Получение планов
        example_get_plan("user123")
        example_get_plan("triathlete456")
        
        # Получение тренировок по датам
        example_get_workouts_by_date("user123")
        example_get_workouts_by_date("triathlete456")
        
        # Удаление планов (раскомментируйте при необходимости)
        # example_delete_plan("user123")
        # example_delete_plan("triathlete456")
        # example_delete_plan("cyclist789")
        
    except requests.exceptions.ConnectionError:
        print("Ошибка: Не удается подключиться к серверу.")
        print("Убедитесь, что сервер запущен: uvicorn main:app --reload")
    except Exception as e:
        print(f"Ошибка: {e}")
