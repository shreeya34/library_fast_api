from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

DB_URL = 'postgresql://postgres:password@localhost:5432/library_db'

engine = create_engine(DB_URL)

Sessionlocal = sessionmaker(bind=engine)

def init_db():
    from models import Admin,AdminLogin
    Base.metadata.create_all(engine)  
    print("Tables created successfully!")

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()
