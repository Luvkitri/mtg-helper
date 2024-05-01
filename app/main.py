from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from typing_extensions import Annotated
from bson import json_util
import json

from constants import DB_NAME, CARDS_COLLECTION_NAME, MONGO_URL
from db.client import get_database
from indexer import Indexer, generate_inverted_index

lifespans = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_client = AsyncIOMotorClient(MONGO_URL)
    cards_cursor = db_client[DB_NAME][CARDS_COLLECTION_NAME].find({}, {"text": 1})
    cards = await cards_cursor.to_list(length=None)
    inverted_index, cards_frequencies = await generate_inverted_index(cards)
    indexer = Indexer(inverted_index, cards_frequencies)
    lifespans["db_client"] = db_client
    lifespans["indexer"] = indexer
    yield
    lifespan["db_client"].close()
    lifespans.clear()


app = FastAPI(lifespan=lifespan)

# app.add_event_handler("startup", connect_to_mongodb)
# app.add_event_handler("shutdown", close_mongodb_connection)


class PaginationQueryParameters:
    def __init__(self, page: int = 1, skip: int = 0, limit: int = 10):
        self.page = page
        self.skip = skip
        self.limit = limit


@app.get("/")
async def root():
    sample = {"_id": "id", "text": "{T}: Add {1}{1}"}
    sim_scores = lifespans["indexer"].retrieve(sample)
    return {"sim_scores": json.loads(json_util.dumps(sim_scores))}


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
