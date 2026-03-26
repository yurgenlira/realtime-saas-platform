import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
# Raises at startup if DATABASE_URL is not set

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Validate connections before use (detects stale connections)
    pool_size=5,  # Max persistent connections per worker process
    max_overflow=10,  # Max additional connections under peak load
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
