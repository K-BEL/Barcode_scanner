"""Custom middleware for the application."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.exceptions import AppException, handle_app_exception
from app.core.logging import logger


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle custom application exceptions."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and handle exceptions."""
        try:
            response = await call_next(request)
            return response
        except AppException as e:
            logger.error(f"Application exception: {e}")
            http_exception = handle_app_exception(e)
            return JSONResponse(
                status_code=http_exception.status_code,
                content={"detail": http_exception.detail}
            )
        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )

