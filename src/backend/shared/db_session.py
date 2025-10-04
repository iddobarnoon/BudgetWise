"""
Database Session Management with SQLAlchemy
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build PostgreSQL connection string from Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Extract project ID from Supabase URL
# Format: https://mjwuxawseluajqduwuru.supabase.co
if SUPABASE_URL:
    project_id = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
else:
    project_id = ""

# PostgreSQL connection string
# Format: postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://postgres:YOUR_PASSWORD@db.{project_id}.supabase.co:5432/postgres"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Get database session (for FastAPI Depends)

    Usage:
    ```python
    from fastapi import Depends
    from shared.db_session import get_db

    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        users = db.query(User).all()
        return users
    ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Get database session as context manager

    Usage:
    ```python
    from shared.db_session import get_db_context

    with get_db_context() as db:
        user = db.query(User).first()
        print(user.email)
    ```
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    """
    from shared.db_models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def drop_db():
    """
    Drop all tables (use with caution!)
    """
    from shared.db_models import Base
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All tables dropped!")
