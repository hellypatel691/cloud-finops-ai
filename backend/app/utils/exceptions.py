from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.logger import get_logger

logger = get_logger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning("HTTP %s: %s", exc.status_code, request.url)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    logger.warning("Validation error: %s", str(exc))
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )
