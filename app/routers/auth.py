from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..schemas.user import UserCreate, User, LoginRequest, LoginResponse, RegisterResponse
from ..database import get_db
from ..models.user import User as UserModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from typing import Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = "your-secret-key"  # 실제 운영 환경에서는 환경 변수로 관리해야 합니다
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_token(token: str = Depends(oauth2_scheme)):
    logger.debug(f"Received token in OAuth2 scheme: {token[:10]}...")
    return token

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.debug(f"Attempting to decode token: {token[:10]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.error("Username not found in token payload")
            raise credentials_exception
        
        logger.debug(f"Looking up user in database: {username}")
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user is None:
            logger.error(f"User not found in database: {username}")
            raise credentials_exception
        
        logger.debug(f"Successfully authenticated user: {username}")
        return user
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}, Token: {token[:10]}...")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}, Token: {token[:10]}...")
        raise credentials_exception

@router.post("/register", response_model=RegisterResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 사용자 이름 중복 체크
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 새 사용자 생성
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"New user registered: {user.username}")
    
    return RegisterResponse(
        message="User registered successfully",
        username=user.username
    )

@router.post("/login", response_model=LoginResponse)
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {form_data.username}")
    
    return LoginResponse(access_token=access_token) 