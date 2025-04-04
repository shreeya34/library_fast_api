# import logging
# from fastapi import Request, HTTPException
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.responses import JSONResponse
# from library_fast_api.logger import logger


# logger = logging.getLogger(__name__)

# class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         try:
#             response = await call_next(request)
#             return response
#         except HTTPException as exc:
#             logger.warning(f"HTTPException: {exc.detail}")
#             return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
#         except Exception as exc:
#             logger.error(f"Internal Server Error: {str(exc)}", exc_info=True)
#             return JSONResponse(status_code=500, content={"detail": "An internal error occurred."})
