"""
Тестовый скрипт для проверки работы мастера создания планов
"""

import requests
import json
from datetime import date, timedelta

# Базовый URL API
BASE_URL = "http://localhost:8000/api/v1"

def test_wizard_endpoint():
    """Тестирует endpoint мастера создания планов"""
    
    print("🧪 Тестирование мастера создания планов...")
    
    # Сначала нужно зарегистрироваться и войти
    print("1. Регистрация тестового пользователя...")
    
    # Данные для регистрации
    register_data = {
        "email": "test_wizard@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        # Регистрация
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("✅ Пользователь зарегистрирован")
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️  Пользователь уже существует")
        else:
            print(f"❌ Ошибка регистрации: {response.status_code} - {response.text}")
            return
        
        # Вход в систему
        print("2. Вход в систему...")
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Ошибка входа: {response.status_code} - {response.text}")
            return
        
        token_data = response.json()
        access_token = token_data["access_token"]
        print("✅ Успешный вход в систему")
        
        # Заголовки с токеном
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Тестирование мастера планов
        print("3. Тестирование мастера планов...")
        
        # Дата соревнования через 3 месяца
        competition_date = (date.today() + timedelta(days=90)).isoformat()
        
        wizard_data = {
            "weekly_distance": "10-30",
            "comfortable_pace": "6-7",
            "target_distance": "21k",
            "competition_date": competition_date,
            "has_specific_goal": True
        }
        
        response = requests.post(f"{BASE_URL}/plans/wizard", json=wizard_data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ План успешно создан через мастер!")
            print(f"   📊 Сложность: {result['complexity']}")
            print(f"   🏃 Тип соревнования: {result['competition_type']}")
            print(f"   📅 Дата соревнования: {result['competition_date']}")
            print(f"   🆔 ID плана: {result['plan_id']}")
        else:
            print(f"❌ Ошибка создания плана: {response.status_code}")
            print(f"   Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу. Убедитесь, что backend запущен на http://localhost:8000")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")

if __name__ == "__main__":
    test_wizard_endpoint()
