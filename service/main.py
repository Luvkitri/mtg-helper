from fastapi import Depends, FastAPI
from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient
from typing_extensions import Annotated

from constants import DB_NAME, CARDS_COLLECTION_NAME
from db.utils import connect_to_mongodb, close_mongodb_connection
from db.client import get_database

mtg_helper_service = FastAPI()

mtg_helper_service.add_event_handler("startup", connect_to_mongodb)
mtg_helper_service.add_event_handler("shutdown", close_mongodb_connection)

# Get envs
load_dotenv()


class PaginationQueryParameters:
    def __init__(self, page: int = 1, skip: int = 0, limit: int = 10):
        self.page = page
        self.skip = skip
        self.limit = limit


@mtg_helper_service.get("/")
async def root():
    return {"message": "Hello World"}


@mtg_helper_service.get("/cards")
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
