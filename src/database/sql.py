from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from database.settings import settings

Base = declarative_base()

DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"

engine = create_engine(DATABASE_URL)

Sessionlocal = sessionmaker(bind=engine)


def init_db():
    from models.db_admin import Admin, AdminLogin

    Base.metadata.create_all(engine)
    print("Tables created successfully!")


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()
