from app import schemas


deck = schemas.DeckCreate(
    **{"name": "test deck", "description": "test deck description"}
)


card = schemas.CardCreate(
    front="card front",
    back="card back",
    hint="card hint",
)

card2 = schemas.CardCreate(
    front="card front2",
    back="card back2",
    hint="card hint2",
)
