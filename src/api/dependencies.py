from config.extension import get_db
from typing import Annotated
from fastapi import Depends, Request
from sqlalchemy.orm import Session


db_dependency = Annotated[Session, Depends(get_db)]

def get_db_from_app(request: Request):
    engine = request.app.state.db_engine
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()