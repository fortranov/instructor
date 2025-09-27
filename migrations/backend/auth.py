"""
Модуль аутентификации и авторизации пользователей
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid
import os

from database import get_db, User

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка Bearer токена
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Получить хеш пароля"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создать JWT токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Проверить JWT токен и вернуть email пользователя"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Аутентифицировать пользователя"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(db: Session, email: str, password: str, first_name: str = None, last_name: str = None) -> User:
    """Создать нового пользователя"""
    # Проверить, что пользователь с таким email не существует
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создать уникальный UIN
    uin = str(uuid.uuid4())
    while db.query(User).filter(User.uin == uin).first():
        uin = str(uuid.uuid4())
    
    # Создать пользователя
    hashed_password = get_password_hash(password)
    user = User(
        uin=uin,
        email=email,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        is_active=1
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Получить текущего пользователя из JWT токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Получить текущего активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Неактивный пользователь"
        )
    return current_user
