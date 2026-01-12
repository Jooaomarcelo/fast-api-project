import logging
import traceback

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.config import settings
from src.core.errors import AppError

logger = logging.getLogger("error_controller")


def send_error_dev(exc: AppError) -> JSONResponse:
    """Send detailed error response in development environment."""
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "status": exc.status,
                "message": exc.message,
                "error": str(exc),
                "stack_trace": traceback.format_exc(),
            }
        ),
    )


def send_error_prod(exc: AppError) -> JSONResponse:
    """Send sanitized error response in production environment."""
    if exc.is_operational:
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(
                {
                    "status": exc.status,
                    "message": exc.message,
                }
            ),
        )
    else:
        logger.error(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {
                    "status": "error",
                    "message": "An unexpected error occurred. Please try again later.",
                }
            ),
        )


async def app_error_controller(request: Request, exc: Exception):
    """
    Controller to handle application-specific errors.

    :param request: Incoming request object
    :type request: Request
    :param exc: Application error exception
    :type exc: Exception
    :return: JSON response with error details
    :rtype: JSONResponse
    """
    exc.status_code = getattr(exc, "status_code", 500)
    exc.status = getattr(exc, "status", "error")
    exc.message = getattr(exc, "message", "An unexpected error occurred.")
    logger.error(str(exc))

    if settings.env == "development":
        return send_error_dev(exc)
    else:
        return send_error_prod(exc)


async def http_exception_controller(
    request: Request, exc: HTTPException | StarletteHTTPException
):
    """
    Controller to handle HTTP exceptions.

    :param request: Incoming request object
    :type request: Request
    :param exc: HTTP exception
    :type exc: Exception
    :return: JSON response with error details
    :rtype: JSONResponse
    """
    exc.status_code = getattr(exc, "status_code", 500)
    exc.status = "error"
    exc.message = getattr(exc, "detail", "An unexpected HTTP error occurred.")
    exc.is_operational = True

    if settings.env == "development":
        return send_error_dev(exc)
    else:
        return send_error_prod(exc)


async def validation_exception_controller(
    request: Request, exc: RequestValidationError
):
    """
    Controller to handle validation exceptions.

    :param request: Incoming request object
    :type request: Request
    :param exc: Validation exception
    :type exc: Exception
    :return: JSON response with error details
    :rtype: JSONResponse
    """
    exc.status_code = 400
    exc.status = "error"
    exc.is_operational = True

    errors = exc.errors()
    exc.message = f"{len(errors)} validation error(s).\n"
    for error in errors:
        exc.message += f"Field '{error['loc'][-1]}': {error['msg']}\n"

    if settings.env == "development":
        return send_error_dev(exc)
    else:
        return send_error_prod(exc)
