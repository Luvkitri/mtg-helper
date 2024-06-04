from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from typing_extensions import Annotated
from bson import json_util, ObjectId
import json

from autocomplete import Trie, levenshtein_distance
from constants import DB_NAME, CARDS_COLLECTION_NAME, MONGO_URL
from db.client import get_database
from indexer import Indexer, generate_inverted_index

lifespans = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_client = AsyncIOMotorClient(MONGO_URL)

    db_client[DB_NAME][CARDS_COLLECTION_NAME].create_index([("name", "text")])

    cards_cursor = db_client[DB_NAME][CARDS_COLLECTION_NAME].find(
        {}, {"name": 1, "text": 1}
    )
    cards = await cards_cursor.to_list(length=None)

    card_name_to_upper = {
        card["name"].lower(): (card["_id"], card["name"]) for card in cards
    }
    cards_names_trie = Trie()
    cards_names_trie.append(card_data[1] for card_data in card_name_to_upper.values())

    inverted_index, cards_frequencies = await generate_inverted_index(cards)
    indexer = Indexer(inverted_index, cards_frequencies)

    lifespans["db_client"] = db_client
    lifespans["indexer"] = indexer
    lifespans["cards_names_trie"] = cards_names_trie
    lifespans["card_name_to_upper"] = card_name_to_upper
    yield
    db_client.close()
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
    card = await lifespans["db_client"][DB_NAME][CARDS_COLLECTION_NAME].find_one(
        {"name": "Shu Yun, the Silent Tempest"},
        {
            "colors": 1,
            "colorIdentity": 1,
            "text": 1,
            "convertedManaCost": 1,
            "types": 1,
        },
    )

    sim_scores = lifespans["indexer"].retrieve(card)
    pipeline = [
        {
            "$match": {
                "_id": {"$in": list(sim_scores.keys())},
                "colorIdentity": {"$in": card["colorIdentity"]},
            },
        },
        {
            "$project": {
                "colors": 1,
                "colorIdentity": 1,
                "text": 1,
                "convertedManaCost": 1,
                "types": 1,
            },
        },
    ]

    cards_cursor = lifespans["db_client"][DB_NAME][CARDS_COLLECTION_NAME].aggregate(
        pipeline
    )
    cards = await cards_cursor.to_list(length=None)
    return json.loads(json_util.dumps(cards))


@app.get("/cards")
async def get_cards(
    db: Annotated[AsyncIOMotorClient, Depends(get_database)],
    pagination_parameters: Annotated[
        PaginationQueryParameters, Depends(PaginationQueryParameters)
    ],
):
    pipeline = [
        {
            "$facet": {
                "metadata": [{"$count": "totalCount"}],
                "data": [
                    {
                        "$skip": (pagination_parameters.page - 1)
                        * pagination_parameters.limit
                    },
                    {"$limit": pagination_parameters.limit},
                    {"$project": {"_id": 0}},
                ],
            }
        }
    ]

    cards = (
        await db[DB_NAME][CARDS_COLLECTION_NAME]
        .aggregate(pipeline)
        .to_list(length=None)
    )

    return cards


@app.get("/cards/{card_id}")
async def get_card_by_id(card_id: str):
    card = await lifespans["db_client"][DB_NAME][CARDS_COLLECTION_NAME].find_one(
        {"_id": ObjectId(card_id)},
        {
            "colors": 1,
            "colorIdentity": 1,
            "text": 1,
            "convertedManaCost": 1,
            "types": 1,
        },
    )

    print(card["colorIdentity"])

    if card is None:
        return []

    sim_scores = lifespans["indexer"].retrieve(card)
    print(sim_scores)
    pipeline = [
        {
            "$match": {
                "_id": {"$in": list(sim_scores.keys())},
                "colorIdentity": {"$in": card["colorIdentity"]}
                if card["colorIdentity"]
                else [],
            },
        },
        {
            "$project": {
                "colors": 1,
                "colorIdentity": 1,
                "text": 1,
                "convertedManaCost": 1,
                "types": 1,
            },
        },
    ]

    cards_cursor = lifespans["db_client"][DB_NAME][CARDS_COLLECTION_NAME].aggregate(
        pipeline
    )
    cards = await cards_cursor.to_list(length=None)
    print(cards)
    return json.loads(json_util.dumps(cards))


@app.get("/autocomplete/cards")
async def get_completations(q: str | None = None):
    if not q or len(q) < 2:
        return []

    search_query = q.lower()

    results = lifespans["cards_names_trie"].auto_complete(search_query)[:10]
    sorted_results = sorted(
        {result: levenshtein_distance(result, q) for result in results}
    )
    return json.loads(
        json_util.dumps(
            {
                str(lifespans["card_name_to_upper"][match][0]): lifespans[
                    "card_name_to_upper"
                ][match][1]
                for match in sorted_results
            }
        )
    )
