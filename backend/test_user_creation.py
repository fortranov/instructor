"""
Тест создания пользователя напрямую через базу данных
"""

from database import SessionLocal, User
from auth import get_password_hash
import uuid

def test_user_creation():
    """Тестируем создание пользователя напрямую"""
    
    db = SessionLocal()
    try:
        # Проверяем, что пользователь с таким email не существует
        test_email = "test_user_direct@example.com"
        existing_user = db.query(User).filter(User.email == test_email).first()
        
        if existing_user:
            print(f"Пользователь {test_email} уже существует, удаляем...")
            db.delete(existing_user)
            db.commit()
        
        # Создаем нового пользователя
        uin = str(uuid.uuid4())
        hashed_password = get_password_hash("testpassword123")
        
        new_user = User(
            uin=uin,
            email=test_email,
            hashed_password=hashed_password,
            first_name="Тест",
            last_name="Пользователь",
            is_active=1
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Пользователь создан успешно:")
        print(f"   ID: {new_user.id}")
        print(f"   UIN: {new_user.uin}")
        print(f"   Email: {new_user.email}")
        print(f"   Имя: {new_user.first_name} {new_user.last_name}")
        print(f"   Тариф ID: {new_user.tariff_id}")
        
        # Проверяем, что можем найти пользователя
        found_user = db.query(User).filter(User.email == test_email).first()
        if found_user:
            print("✅ Пользователь найден в базе данных")
        else:
            print("❌ Пользователь не найден в базе данных")
        
    except Exception as e:
        print(f"❌ Ошибка при создании пользователя: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_user_creation()
