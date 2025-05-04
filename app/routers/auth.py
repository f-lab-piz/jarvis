from fastapi import APIRouter, HTTPException, Depends
from ..models import UserCreate, User, RegisterResponse
from passlib.context import CryptContext
from typing import List

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 임시로 메모리에 사용자 정보를 저장합니다 (실제로는 데이터베이스를 사용해야 합니다)
fake_users_db = {}

def get_password_hash(password: str):
    return pwd_context.hash(password)

@router.post("/register", response_model=RegisterResponse)
async def register_user(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    user_id = len(fake_users_db) + 1
    
    fake_users_db[user.username] = {
        "id": user_id,
        "username": user.username,
        "hashed_password": hashed_password,
        "is_active": True
    }
    
    return RegisterResponse(
        message="회원가입이 성공적으로 완료되었습니다",
        username=user.username
    ) 