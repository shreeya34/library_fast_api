from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


DB_URL = 'postgresql://postgres:password@localhost:5432/library_db'

engine = create_engine(DB_URL)
connection = engine.connect()

Sessionlocal= sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()
    