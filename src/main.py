from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from .controllers.error_controller import (
    app_error_controller,
    http_exception_controller,
    validation_exception_controller,
)
from .core.config import settings
from .utils.db import close_pool, create_pool, get_conn
from .utils.logging import setup_logging

# Configure logging
logger = setup_logging()


async def lifespan(app: FastAPI):
    """
    Lifespan function to manage application startup and shutdown events.

    :param app: FastAPI application instance
    :type app: FastAPI
    """
    app.state.pool = await create_pool()

    yield

    await close_pool(app.state.pool)


app = FastAPI(lifespan=lifespan)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_controller)
app.add_exception_handler(RequestValidationError, validation_exception_controller)
app.add_exception_handler(Exception, app_error_controller)


class Dummy(BaseModel):
    id: int
    name: str


@app.get("/")
async def read_root(db=Depends(get_conn)):
    """
    Health check endpoint to verify the application is running.

    :return: Health status message
    :rtype: dict
    """
    return {"status": "200", "message": "API is running", "environment": settings.env}


@app.post("/dummys")
async def create_dummy(dummy: Dummy, db=Depends(get_conn)):
    """
    Dummy endpoint to test database connection.

    :return: Dummy data
    :rtype: Dummy
    """
    return dummy
