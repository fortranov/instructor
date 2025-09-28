"""
Тест для проверки регистрации пользователей
"""

import requests
import json

def test_registration():
    """Тестируем регистрацию нового пользователя"""
    
    url = "http://localhost:8000/api/v1/auth/register"
    
    test_user = {
        "email": "test_user_123@example.com",
        "password": "testpassword123",
        "first_name": "Тест",
        "last_name": "Пользователь"
    }
    
    try:
        response = requests.post(url, json=test_user)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Регистрация прошла успешно!")
            user_data = response.json()
            print(f"Создан пользователь: {user_data.get('email')}")
        else:
            print("❌ Ошибка регистрации")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу. Убедитесь, что бэкенд запущен.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_registration()
