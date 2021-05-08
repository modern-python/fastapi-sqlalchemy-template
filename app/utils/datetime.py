import datetime


def utcnow() -> datetime.datetime:
    """Generates timezone-aware UTC datetime."""
    return datetime.datetime.now(datetime.timezone.utc)
