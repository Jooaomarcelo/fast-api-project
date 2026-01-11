from fastapi import Depends, FastAPI

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


@app.get("/")
async def read_root(db=Depends(get_conn)):
    """
    Health check endpoint to verify the application is running.

    :return: Health status message
    :rtype: dict
    """
    return {"status": "200", "message": "API is running", "environment": settings.env}
