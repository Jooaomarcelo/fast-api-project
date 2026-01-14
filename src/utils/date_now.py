from datetime import datetime, timezone


def get_utc_now() -> datetime:
    """Get the current date and time in UTC timezone."""
    return datetime.now(timezone.utc)
