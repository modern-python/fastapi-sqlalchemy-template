from typing import Optional


class DatabaseValidationError(Exception):
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        object_id: Optional[int] = None,
    ) -> None:
        self.message = message
        self.field = field
        self.object = object_id
