import datetime


def generate_utc_dt() -> datetime.datetime:
    """Generate timezone-aware UTC datetime."""
    return datetime.datetime.now(datetime.UTC)
