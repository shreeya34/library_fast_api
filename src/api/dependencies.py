from config.extension import get_db
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session


db_dependency = Annotated[Session, Depends(get_db)]