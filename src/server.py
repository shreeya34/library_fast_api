
from fastapi import FastAPI
from core.handlers.exception_handlers.middleware import ExceptionHandlerMiddleware
from database.sql import init_db
from library_fast_api.logger.logger import get_logger
from api.entrypoint.admin import routes as admin_routes
from api.entrypoint.member import routes as member_routes

logger = get_logger()

app = FastAPI()

init_db()

app.add_middleware(ExceptionHandlerMiddleware)

app.include_router(admin_routes.router,tags=["admin"])
app.include_router(member_routes.router, tags=["member"])
