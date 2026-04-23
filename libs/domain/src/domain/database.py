import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]  # fails fast if missing

# pool_size and max_overflow are PostgreSQL-specific — SQLite (unit tests) does not support them
_pool_kwargs = {"pool_size": 5, "max_overflow": 10} if DATABASE_URL.startswith("postgresql") else {}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # validate connections before use (detects stale connections)
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    **_pool_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
