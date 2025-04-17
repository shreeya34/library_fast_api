from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from config.config import settings

Base = declarative_base()


def create_db_engine():
    engine = create_engine(
        f"postgresql://{settings.database_username}:{settings.database_password.get_secret_value()}"
        f"@{settings.database_host}:{settings.database_port}/{settings.database_name}"
    )
    return engine

def init_db(engine):
    Base.metadata.create_all(bind=engine)


def get_db(engine):
    with Session(engine) as session:
        yield session