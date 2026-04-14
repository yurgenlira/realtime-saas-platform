import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
# Raises at startup if DATABASE_URL is not set

# pool_size and max_overflow are PostgreSQL-specific — SQLite (unit tests) does not support them
_pool_kwargs = (
    {"pool_size": 5, "max_overflow": 10}
    if DATABASE_URL and DATABASE_URL.startswith("postgresql")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Validate connections before use (detects stale connections)
    **_pool_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
