from typing import Optional


class DatabaseException(Exception):
    pass


class DatabaseValidationError(DatabaseException):
    def __init__(self, message: str, field: Optional[str] = None) -> None:
        self.message = message
        self.field = field
