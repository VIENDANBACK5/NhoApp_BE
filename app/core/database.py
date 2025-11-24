from typing import Generator
from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# PostgreSQL (commented - not using)
# engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Oracle Cloud
engine = create_engine(
    settings.DATABASE_URL,
    thick_mode=False,  # Use thin mode (no Oracle Client needed)
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
