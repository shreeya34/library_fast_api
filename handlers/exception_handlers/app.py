from fastapi import FastAPI
from handlers.exception_handlers.middleware import ExceptionHandlerMiddleware  # Import the middleware

def register_middleware(app: FastAPI):
    """
    Register custom exception handler middleware with the FastAPI app.
    """
    app.add_middleware(ExceptionHandlerMiddleware)
