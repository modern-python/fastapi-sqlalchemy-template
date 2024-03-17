class DatabaseError(Exception):
    pass


class DatabaseValidationError(DatabaseError):
    def __init__(self, message: str, field: str | None = None) -> None:
        self.message = message
        self.field = field
