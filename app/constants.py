import os
from dotenv import load_dotenv

# Get envs
load_dotenv()

MONGO_ROOT_USERNAME = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
MONGO_ROOT_PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
MONGO_HOST = os.environ.get("MONGO_HOST")
MONGO_PORT = os.environ.get("MONGO_PORT")

MONGO_URL = "mongodb://{}:{}@{}:{}/".format(
    MONGO_ROOT_USERNAME, MONGO_ROOT_PASSWORD, MONGO_HOST, MONGO_PORT
)

DB_NAME = "mtg_cards"
CARDS_COLLECTION_NAME = "cards"
