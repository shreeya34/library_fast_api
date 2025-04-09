from fastapi import FastAPI
from core.handlers.exception_handlers.middleware import ExceptionHandlerMiddleware
from config.extension import init_db
from api.utils.logger import get_logger
from api.entrypoint.admin import routes as admin_routes
from api.entrypoint.member import routes as member_routes
from contextlib import asynccontextmanager

logger = get_logger()

# @asynccontextmanager
# async def lifespan(app: FastAPI):  
#     logger.info("Starting server")
#     app.state.db = 
#     yield 
app = FastAPI()

init_db()

app.add_middleware(ExceptionHandlerMiddleware)

app.include_router(admin_routes.router, tags=["admin"])
app.include_router(member_routes.router, tags=["member"])
