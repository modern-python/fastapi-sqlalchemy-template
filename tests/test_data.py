from app import schemas


deck = schemas.Deck(
    **{"name": "test deck", "description": "test deck description"}
)


deck2 = schemas.Deck(
    **{"name": "test deck2", "description": "test deck description2"}
)
