from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

SQLALCHEMY_DATABASE_URL = "postgresql://jarvis@localhost/jarvis_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=100,  # 동시 연결 수 증가
    max_overflow=10,  # 추가 연결 허용
    pool_timeout=30,  # 연결 대기 시간
    pool_recycle=1800  # 30분마다 연결 재생성
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 