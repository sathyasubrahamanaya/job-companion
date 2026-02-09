from sqlmodel import create_engine,Session
from sqlalchemy.orm import sessionmaker
from typing import Generator
from app.db.datamodels import SQLModel

DATABASE_URL = "sqlite:///./jobcompanion.db"


engine = create_engine(
    DATABASE_URL,
    echo=True,        # set False in production
    pool_pre_ping=True
)


def create_db_and_tables():
    """Initializes the database and creates all tables defined via SQLModel."""
    # Ensure all your models are imported before calling this
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency to yield a database session and close it after use."""
    with Session(engine) as session:
        yield session    