from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from config.settings import settings

Base = declarative_base()

# DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"

_engine = create_engine(f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"
)

def init_db():
    Base.metadata.create_all(bind=_engine)


def get_db():
    with Session(_engine) as session:
        yield session

