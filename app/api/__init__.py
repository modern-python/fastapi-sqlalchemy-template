import typing

import fastapi

from app import schemas


PathId = typing.Annotated[int, fastapi.Path(gt=0, le=schemas.MAX_ID)]
