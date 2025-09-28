"""
Тест API регистрации
"""

import requests
import json
import time

def test_api_registration():
    """Тестируем API регистрации"""
    
    # Ждем запуска сервера
    time.sleep(2)
    
    url = "http://localhost:8000/api/v1/auth/register"
    
    test_user = {
        "email": "api_test_user@example.com",
        "password": "testpassword123",
        "first_name": "API",
        "last_name": "Тест"
    }
    
    try:
        print("Отправляем запрос на регистрацию...")
        response = requests.post(url, json=test_user, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Регистрация через API прошла успешно!")
            try:
                user_data = response.json()
                print(f"Создан пользователь: {user_data.get('email')}")
            except:
                print("Ответ не в формате JSON")
        else:
            print("❌ Ошибка регистрации через API")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу на localhost:8000")
        print("Проверьте, что сервер запущен командой: python main.py")
    except requests.exceptions.Timeout:
        print("❌ Таймаут при подключении к серверу")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_api_registration()
