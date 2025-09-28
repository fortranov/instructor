#!/usr/bin/env python3
"""
Скрипт для тестирования исправления в Docker окружении
"""

import os
import sys
import requests
import time
import json

def test_docker_deployment():
    """Тестировать развертывание в Docker"""
    
    print("🐳 Testing Docker deployment...")
    
    # URL для тестирования (предполагаем, что приложение запущено на порту 8000)
    base_url = "http://localhost:8000"
    
    # Ждем запуска приложения
    print("Waiting for application to start...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/api/v1/health", timeout=5)
            if response.status_code == 200:
                print("✅ Application is running")
                break
        except requests.exceptions.RequestException:
            pass
        
        if i == max_retries - 1:
            print("❌ Application failed to start")
            return False
        
        time.sleep(2)
    
    try:
        # Тест 1: Регистрация пользователя (это вызывало ошибку)
        print("\n=== TEST 1: User Registration ===")
        registration_data = {
            "email": "docker_test@example.com",
            "password": "testpassword123",
            "first_name": "Docker",
            "last_name": "Test"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ User registration successful")
            user_data = response.json()
            print(f"Created user: {user_data['email']}")
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Тест 2: Вход пользователя
        print("\n=== TEST 2: User Login ===")
        login_data = {
            "email": "docker_test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ User login successful")
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"Got access token: {access_token[:20]}...")
        else:
            print(f"❌ User login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Тест 3: Получение информации о пользователе
        print("\n=== TEST 3: Get User Info ===")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{base_url}/api/v1/auth/me",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Get user info successful")
            user_info = response.json()
            print(f"User info: {user_info['email']}")
        else:
            print(f"❌ Get user info failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Тест 4: Создание плана тренировок
        print("\n=== TEST 4: Create Training Plan ===")
        plan_data = {
            "uin": user_info["uin"],
            "complexity": 500,
            "competition_date": "2024-06-15",
            "competition_type": "run_marathon"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/plans/create",
            json=plan_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ Training plan creation successful")
            plan_info = response.json()
            print(f"Created plan with ID: {plan_info['id']}")
        else:
            print(f"❌ Training plan creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print("\n🎉 All Docker tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_docker_deployment()
    sys.exit(0 if success else 1)
