import asyncio
from fastapi import FastAPI
from core.middleware import ExceptionHandlerMiddleware
from config.extension import create_db_engine, init_db
from api.utils.logger import get_logger
from api.entrypoint.admin import routes as admin_routes
from api.entrypoint.member import routes as member_routes
from contextlib import asynccontextmanager

logger = get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(" Starting server...")  
    engine = await asyncio.to_thread(create_db_engine)
    await asyncio.to_thread(init_db, engine)
    app.state.db_engine = engine
    yield
    logger.info("Shutting down server...")

app=FastAPI(lifespan=lifespan)

def init_app()->FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.include_router(admin_routes.router, tags=["admin"])
    app.include_router(member_routes.router, tags=["member"])

    app.add_middleware(ExceptionHandlerMiddleware)

    return app

app = init_app()
