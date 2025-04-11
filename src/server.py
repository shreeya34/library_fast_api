from fastapi import FastAPI
from core.middleware import ExceptionHandlerMiddleware
from config.extension import init_db
from api.utils.logger import get_logger
from api.entrypoint.admin import routes as admin_routes
from api.entrypoint.member import routes as member_routes
from contextlib import asynccontextmanager

logger = get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(" Starting server...")
    init_db()  
    yield
    logger.info("Shutting down server...")

app=FastAPI(lifespan=lifespan)



def init_app()->FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.include_router(admin_routes.router)
    app.include_router(member_routes.router, tags=["member"])

    app.add_middleware(ExceptionHandlerMiddleware)

    return app

app = init_app()
