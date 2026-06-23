from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.base import Base


def _ensure_database_exists() -> None:
    engine = create_engine(settings.database_url_without_db)
    with engine.connect() as conn:
        conn.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS {settings.db_name} "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        conn.commit()
    engine.dispose()


def init_db() -> None:
    _ensure_database_exists()
    Base.metadata.create_all(bind=engine)


engine = create_engine(
    settings.database_url,
    pool_size=25,
    max_overflow=0,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
