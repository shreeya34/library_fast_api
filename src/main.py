from fastapi import FastAPI
from handlers.exception_handlers.middleware import ExceptionHandlerMiddleware
from database.sql import init_db
from library_fast_api.logger.logger import get_logger
from api.routes import admin, member

logger = get_logger()

app = FastAPI()

init_db()

app.add_middleware(ExceptionHandlerMiddleware)

app.include_router(admin.router,  tags=["admin"])
app.include_router(member.router, tags=["member"])
