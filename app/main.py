# import random
# import time
from contextlib import asynccontextmanager

import aiosqlite
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import app.crud as crud
from app.autocomplete import Trie, iter_levenshtein_distance
from app.constants import MAX_LIMIT, MAX_OFFSET
from app.indexer import Indexer, generate_inverted_index
from app.models.card import Card, CardField

lifespans = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = await aiosqlite.connect("./app/data/AllPrintings.sqlite")
    cards = await crud.get_unique_cards(db)

    card_name_to_upper = {
        card_name.lower(): (card_uuid, card_name) for card_uuid, card_name, _ in cards
    }

    cards_names_trie = Trie()
    cards_names_trie.append(card_data[1] for card_data in card_name_to_upper.values())

    inverted_index, cards_frequencies = await generate_inverted_index(
        [(card_uuid, card_text) for card_uuid, _, card_text in cards]
    )
    indexer = Indexer(inverted_index, cards_frequencies)

    lifespans["db"] = db
    lifespans["indexer"] = indexer
    lifespans["cards_names_trie"] = cards_names_trie
    lifespans["card_name_to_upper"] = card_name_to_upper
    yield
    await db.close()
    lifespans.clear()


origins = ["http://localhost:5173"]

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return None


@app.get("/cards/{uuid}")
async def get_card_by_uuid(uuid: str):
    card = await crud.get_card_by_uuid(lifespans["db"], uuid)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")

    return Card(*card).__dict__


@app.get("/cards/similar/{uuid}")
async def get_similar_cards_by_uuid(
    uuid: str,
    limit: int = 10,
    offset: int = 0,
    filter_color: bool = False,
    filter_colors: bool = False,
    filter_type: bool = False,
):
    print(filter_color, filter_colors, filter_type)
    if (
        (not isinstance(limit, int) or limit % 10 != 0 or limit > MAX_LIMIT)
        and (not isinstance(offset, int) or offset % 10 != 0 or offset > MAX_OFFSET)
        and not isinstance(filter_color, bool)
        and not isinstance(filter_type, bool)
    ):
        raise HTTPException(status_code=404, detail="Wrong pagination parameter")

    source_card = await crud.get_card_by_uuid(
        lifespans["db"],
        uuid,
        [
            CardField.UUID,
            CardField.TEXT,
            CardField.COLOR_IDENTITY,
            CardField.COLORS,
            CardField.TYPES,
        ],
    )

    if source_card is None:
        raise HTTPException(status_code=404, detail="Card not found")

    source_card = Card(**source_card)

    if (
        source_card.uuid is None
        or source_card.text is None
        or source_card.colorIdentity is None
        or source_card.colors is None
        or source_card.types is None
    ):
        raise HTTPException(status_code=404, detail="Missing card data")

    sim_scores = lifespans["indexer"].retrieve(source_card.text)

    params = (
        limit,
        offset,
    )

    similar_cards = await crud.get_similar_cards(
        lifespans["db"],
        filter_color,
        filter_colors,
        filter_type,
        source_card,
        params,
        sim_scores,
    )

    return {
        "data": [
            {"uuid": card[0], "scryfallId": card_scryfall_id}
            for card, card_scryfall_id, _ in similar_cards
        ],
        "limit": limit,
        "offset": offset,
        "total": 100,
    }


@app.get("/autocomplete/cards")
async def get_completations(q: str | None = None):
    if not q or len(q) < 2:
        return []

    search_query = q.lower()
    results = lifespans["cards_names_trie"].auto_complete(search_query)[:10]
    sorted_results = sorted(
        {result: iter_levenshtein_distance(result, q) for result in results}
    )
    return {
        str(lifespans["card_name_to_upper"][match][0]): lifespans["card_name_to_upper"][
            match
        ][1]
        for match in sorted_results
    }
