from contextlib import asynccontextmanager

import aiosqlite
import time
import random
from app.autocomplete import Trie, iter_levenshtein_distance
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.indexer import Indexer, generate_inverted_index
from app.models.card import Card

lifespans = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = await aiosqlite.connect("./app/data/AllPrintings.sqlite")
    sql_query = """
        SELECT uuid, name, text FROM cards 
        WHERE (isFunny = 0 OR isFunny IS NULL) 
        AND (isOversized = 0 OR isOversized IS NULL) 
        AND (isOnlineOnly = 0 OR isOnlineOnly IS NULL) 
        AND (isFullArt = 0 OR isFullArt IS NULL) 
        AND (isAlternative = 0 or isAlternative IS NULL) 
        AND (setCode != "REX" AND setCode != "SLD" AND setCode != "40K") 
        GROUP BY name
    """

    cards_cursor = await db.execute(sql_query)
    cards = await cards_cursor.fetchall()

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


origins = ["*"]

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


@app.get("/cards/{card_uuid}")
async def get_card_by_uuid(card_uuid: str):
    card_by_id_query = """SELECT * FROM cards WHERE uuid = ?"""
    card_cursor = await lifespans["db"].execute(card_by_id_query, (card_uuid,))
    card = await card_cursor.fetchone()

    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")

    return Card(*card).__dict__


@app.get("/cards/similar/{card_uuid}")
async def get_similar_cards_by_uuid(card_uuid: str, limit: int = 10, offset: int = 0):
    if not isinstance(offset, int) or offset % 10 != 0:
        raise HTTPException(status_code=404, detail="Wrong pagination parameter")

    card_by_id_query = (
        """SELECT uuid, text, colorIdentity, colors, types FROM cards WHERE uuid = ?"""
    )
    card_cursor = await lifespans["db"].execute(card_by_id_query, (card_uuid,))
    card = await card_cursor.fetchone()

    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")

    card_uuid, card_text, card_color_identity, card_colors, card_types = card

    sim_scores = lifespans["indexer"].retrieve(card_text)

    temp_table_name = f"temp_{int(time.time() + (random.random() * 100_000))}"

    db_cursor = await lifespans["db"].cursor()
    await db_cursor.execute(
        f"""
                                CREATE TEMPORARY TABLE {temp_table_name} (uuid TEXT, sim_score REAL)
                            """,
    )
    for uuid, sim_score in sim_scores.items():
        await db_cursor.execute(
            f"""
                              INSERT INTO {temp_table_name} (uuid, sim_score) VALUES (?, ?)
                          """,
            (
                uuid,
                sim_score,
            ),
        )

    similar_cards_query = f"""
        SELECT card.uuid, identifier.scryfallId, temp_card.sim_score
        FROM cards AS card
        INNER JOIN {temp_table_name} AS temp_card
        ON card.uuid = temp_card.uuid
        INNER JOIN cardIdentifiers AS identifier
        ON card.uuid = identifier.uuid
        WHERE (card.colorIdentity = ? OR card.colors = ?) AND card.types = ?
        ORDER BY temp_card.sim_score DESC
        LIMIT ?
        OFFSET ?
    """
    similar_cards_cursor = await lifespans["db"].execute(
        similar_cards_query,
        (
            card_color_identity,
            card_colors,
            card_types,
            limit,
            offset,
        ),
    )
    similar_cards = await similar_cards_cursor.fetchall()

    await db_cursor.execute(f"DROP TABLE {temp_table_name}")
    await lifespans["db"].commit()

    return {
        "data": [
            {"uuid": card[0], "scryfallId": card_scryfall_id}
            for card, card_scryfall_id, _ in similar_cards
        ],
        "limit": limit,
        "offset": offset,
        "total": 50,
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
