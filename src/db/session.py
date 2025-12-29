"""Session Manager For Application DB."""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


# NOTE: Aurora DSQL handles connection pooling automatically (no proxy needed)
# IAM auth tokens auto-refresh, so no credential rotation issues
# In case I go back to RDS, I need to use RDS proxy for connections pooling
@contextmanager
def get_db_session():  # noqa
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
