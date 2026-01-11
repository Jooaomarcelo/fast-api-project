import logging

from ..core.config import settings


def setup_logging():
    """
    Configure logging for the application.
    """
    logging.basicConfig(
        level=logging.INFO if settings.env == "production" else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Silenciar logs verbosos do pymongo
    logging.getLogger("pymongo").setLevel(logging.WARNING)

    return logging.getLogger(__name__)
