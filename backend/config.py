# Configuration and Database Setup

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as DBSession
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database (SQLite by default - no installation required!)
    database_url: str = "sqlite:///./talktodata.db"
    
    # LLM
    gemini_api_key: str
    
    # File Storage
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 100
    
    # Application
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


# Database engine and session
settings = get_settings()
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> DBSession:
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database tables"""
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
