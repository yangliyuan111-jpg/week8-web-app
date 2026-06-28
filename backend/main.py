import os
from typing import List
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# ==================== 1. 数据库配置 ====================
# 建议在 Cloud Run 的环境变量中配置以下信息
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password123")
HOST_NAME = os.getenv("HOST_NAME", "127.0.0.1")
HOST_PORT = os.getenv("HOST_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "demo_db")

# 生产环境建议使用私有 IP 或 Cloud SQL Auth Proxy
# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{HOST_NAME}:{HOST_PORT}/{DB_NAME}"
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?unix_socket=/cloudsql/{HOST_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

print(HOST_NAME)
print(DATABASE_URL)

# ==================== 2. 数据库模型 ====================
class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ==================== 3. Pydantic 模型 ====================
class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    class Config:
        from_attributes = True

# ==================== 4. 核心路由配置 ====================
app = FastAPI(title="GCP Full-Stack API")

# 创建带有 /api 前缀的路由组
api_router = APIRouter(prefix="/api")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@api_router.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = DBUser(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@api_router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(DBUser).all()

@api_router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None

# 将带前缀的路由注册到 app
app.include_router(api_router)
