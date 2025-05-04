from fastapi import APIRouter, HTTPException, Depends
from ..models import UserCreate, User, RegisterResponse, LoginRequest, LoginResponse
from passlib.context import CryptContext
from typing import List
from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = "your-secret-key-keep-it-secret"  # 실제 운영 환경에서는 환경 변수로 관리해야 합니다
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 임시로 메모리에 사용자 정보를 저장합니다 (실제로는 데이터베이스를 사용해야 합니다)
fake_users_db = {}

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    user = fake_users_db.get(login_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(
        data={"sub": user["username"]}
    )
    
    return LoginResponse(access_token=access_token) 