import json

from pprint import pprint
from contextlib import asynccontextmanager
from Levenshtein import distance

import aiosqlite

# from typing_extensions import Annotated
# # from bson import json_util, ObjectId
from autocomplete import Trie, levenshtein_distance
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from indexer import Indexer, generate_inverted_index

lifespans = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = await aiosqlite.connect("data/AllPrintings.sqlite")
    # sql_query = """SELECT cards.name, identifier.scryfallId FROM cardIdentifiers as identifier INNER JOIN cards ON identifier.uuid = cards.uuid GROUP BY cards.name;"""
    sql_query = """SELECT uuid, name, text FROM cards GROUP BY name"""
    # query_card_identifiers_info = """PRAGMA table_info(cardIdentifiers);"""
    query_cards_info = """PRAGMA table_info(cards)"""
    cards_table_info_cursor = await db.execute(query_cards_info)
    cards_table_info = await cards_table_info_cursor.fetchall()
    pprint(cards_table_info)
    cards_cursor = await db.execute(sql_query)
    cards = await cards_cursor.fetchall()
    # pprint(cards[:10])

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


class PaginationQueryParameters:
    def __init__(self, page: int = 1, skip: int = 0, limit: int = 10):
        self.page = page
        self.skip = skip
        self.limit = limit


@app.get("/")
async def root():
    # card = await lifespans["db_client"][DB_NAME][CARDS_COLLECTION_NAME].find_one(
    #     {"name": "Shu Yun, the Silent Tempest"},
    #     {
    #         "colors": 1,
    #         "colorIdentity": 1,
    #         "text": 1,
    #         "convertedManaCost": 1,
    #         "types": 1,
    #     },
    # )

    # sim_scores = lifespans["indexer"].retrieve(card)
    # pipeline = [
    #     {
    #         "$match": {
    #             "_id": {"$in": list(sim_scores.keys())},
    #             "colorIdentity": {"$in": card["colorIdentity"]},
    #         },
    #     },
    #     {
    #         "$project": {
    #             "colors": 1,
    #             "colorIdentity": 1,
    #             "text": 1,
    #             "convertedManaCost": 1,
    #             "types": 1,
    #         },
    #     },
    # ]

    # cards_cursor = lifespans["db_client"][DB_NAME][CARDS_COLLECTION_NAME].aggregate(
    #     pipeline
    # )
    # cards = await cards_cursor.to_list(length=None)
    # return json.loads(json_util.dumps(cards))

    return None


# @app.get("/cards")
# async def get_cards(
#     db: Annotated[AsyncIOMotorClient, Depends(get_database)],
#     pagination_parameters: Annotated[
#         PaginationQueryParameters, Depends(PaginationQueryParameters)
#     ],
# ):


#     pipeline = [
#         {
#             "$facet": {
#                 "metadata": [{"$count": "totalCount"}],
#                 "data": [
#                     {
#                         "$skip": (pagination_parameters.page - 1)
#                         * pagination_parameters.limit
#                     },
#                     {"$limit": pagination_parameters.limit},
#                     {"$project": {"_id": 0}},
#                 ],
#             }
#         }
#     ]

#     cards = (
#         await db[DB_NAME][CARDS_COLLECTION_NAME]
#         .aggregate(pipeline)
#         .to_list(length=None)
#     )

#     return cards


@app.get("/cards/similar/{card_uuid}")
async def get_similar_cards_by_id(card_uuid: str):
    card_by_id_query = """SELECT uuid, text, colorIdentity FROM cards WHERE uuid = ?"""
    card_cursor = await lifespans["db"].execute(card_by_id_query, (card_uuid,))
    card = await card_cursor.fetchone()

    if card is None:
        return []

    card_uuid, card_text, card_color_identity = card

    print(card_color_identity)

    # card = await lifespans["db_client"][DB_NAME][CARDS_COLLECTION_NAME].find_one(
    #     {"_id": ObjectId(card_id)},
    #     {
    #         "colors": 1,
    #         "colorIdentity": 1,
    #         "text": 1,
    #         "convertedManaCost": 1,
    #         "types": 1,
    #     },
    # )

    sim_scores = lifespans["indexer"].retrieve(card_text)
    print(sim_scores)

    db_cursor = await lifespans["db"].cursor()
    await db_cursor.execute("""
                                CREATE TEMPORARY TABLE temp_similar_cards (uuid TEXT)
                            """)
    for similar_card_uuid in sim_scores:
        await db_cursor.execute(
            """
                              INSERT INTO temp_similar_cards VALUES (?)
                          """,
            (similar_card_uuid,),
        )

    similar_cards_query = """
        SELECT card.uuid, identifier.scryfallId
        FROM cards AS card
        INNER JOIN temp_similar_cards AS temp_card
        ON card.uuid = temp_card.uuid
        INNER JOIN cardIdentifiers AS identifier
        ON card.uuid = identifier.uuid
        WHERE card.colorIdentity = ?
        GROUP BY card.name
    """
    similar_cards_cursor = await lifespans["db"].execute(
        similar_cards_query, (card_color_identity,)
    )
    cards = await similar_cards_cursor.fetchall()

    print(cards)

    await db_cursor.execute("DROP TABLE temp_similar_cards")
    await lifespans["db"].commit()
    # pipeline = [
    #     {
    #         "$match": {
    #             "_id": {"$in": list(sim_scores.keys())},
    #             "colorIdentity": {"$in": card["colorIdentity"]}
    #             if card["colorIdentity"]
    #             else [],
    #         },
    #     },
    #     {
    #         "$project": {
    #             "colors": 1,
    #             "colorIdentity": 1,
    #             "text": 1,
    #             "convertedManaCost": 1,
    #             "types": 1,
    #         },
    #     },
    # ]

    return [
        {"uuid": card_uuid, "scryfallId": card_scryfall_id}
        for card_uuid, card_scryfall_id in cards
    ]


@app.get("/autocomplete/cards")
async def get_completations(q: str | None = None):
    if not q or len(q) < 2:
        return []

    search_query = q.lower()
    print("before trie")
    results = lifespans["cards_names_trie"].auto_complete(search_query)[:10]
    print("after trie")
    print(results)
    sorted_results = sorted({result: distance(result, q) for result in results})
    print("after lev")
    return {
        str(lifespans["card_name_to_upper"][match][0]): lifespans["card_name_to_upper"][
            match
        ][1]
        for match in sorted_results
    }
