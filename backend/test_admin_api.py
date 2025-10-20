#!/usr/bin/env python3
"""
Тестирование админ API
"""

import requests
import json

def test_admin_api():
    """Тестируем админ API"""
    try:
        # Сначала получаем токен для администратора
        login_data = {
            'username': 'abramov.yu.v@gmail.com',
            'password': 'admin123'
        }
        
        # Попробуем получить токен через эндпоинт логина
        print("🔐 Попытка логина администратора...")
        response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
        print(f'Статус логина: {response.status_code}')
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print(f'Токен получен: {token[:20]}...')
            
            # Теперь тестируем админ API
            print("👥 Тестирование админ API...")
            headers = {'Authorization': f'Bearer {token}'}
            admin_response = requests.get('http://localhost:8000/api/v1/admin/users', headers=headers)
            print(f'Статус админ API: {admin_response.status_code}')
            
            if admin_response.status_code == 200:
                users = admin_response.json()
                print(f'✅ Получено пользователей: {len(users)}')
                for user in users[:3]:  # Показываем первых 3
                    print(f'  - {user["email"]} (активен: {user["is_active"]})')
                return True
            else:
                print(f'❌ Ошибка админ API: {admin_response.text}')
                return False
        else:
            print(f'❌ Ошибка логина: {response.text}')
            return False
            
    except requests.exceptions.ConnectionError:
        print('❌ Сервер не запущен. Запустите сервер командой: python main.py')
        return False
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        return False

if __name__ == "__main__":
    success = test_admin_api()
    if success:
        print("🎉 Админ API работает корректно!")
    else:
        print("💥 Админ API не работает")
