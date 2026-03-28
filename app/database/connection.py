from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

settings = Settings()

if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgresql"):
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
else:
    engine = create_engine("sqlite:///./webhook.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models.webhook_event import WebhookEvent
    Base.metadata.create_all(bind=engine)
