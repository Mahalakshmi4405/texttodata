# Configuration and Database Setup

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as DBSession
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import logging
from logging.handlers import RotatingFileHandler


# Configure Logging
os.makedirs("logs", exist_ok=True)

# Create logger
logger = logging.getLogger("talktodata")
logger.setLevel(logging.INFO)

# File handler (detailed logs)
file_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(file_formatter)

# Console handler (only important messages)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Silence noisy loggers
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)


class Settings(BaseSettings):
    """Application settings from environment variables"""
    model_config = {"env_file": ".env", "case_sensitive": False}
    
    # Database (SQLite by default - no installation required!)
    database_url: str = "sqlite:///./talktodata.db"
    
    # LLM Configuration
    llm_provider: str = "gemini"  # Options: "gemini" or "ollama"
    gemini_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"  # Default Ollama model
    
    # File Upload Settingse
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 100
    
    # Application
    debug: bool = False


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


# Database engine and session
settings = get_settings()

# FORCE SQLite for local development - override any environment variables
SQLITE_URL = "sqlite:///./talktodata.db"
logger.info(f"[DATABASE] Using: {SQLITE_URL}")

engine = create_engine(
    SQLITE_URL,  # Hardcoded SQLite - ignores settings.database_url
    echo=False,  # Disable SQLAlchemy query logging
    connect_args={"check_same_thread": False}  # Required for SQLite
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
    logger.info("[SUCCESS] Database initialized")


# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
