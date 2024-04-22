import json
import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

username = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
password = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
host = os.environ.get("MONGO_HOST")
port = os.environ.get("MONGO_PORT")

client = MongoClient("mongodb://{}:{}@{}:{}/".format(username, password, host, port))
database = client["mtg_cards"]
collection = database["cards"]

# Drop collection before populating
drop_info = database.drop_collection("cards")
print(f"Dropping collection: {drop_info}")


try:
    with open("AtomicCards.json", "r") as cards_file:
        data = cards_file.read()

    data_list = json.loads(data)
except FileNotFoundError:
    print("Error: JSON file not found!")
    exit(1)
except json.JSONDecodeError:
    print("Error: Invalid JSON format in the file!")
    exit(1)

for data in data_list["data"].values():
    for document in data:
        # Skip 'funny' unoficial realeses
        if ("isFunny" in document and document["isFunny"]) or (
            "printings" in document and "UNF" in document["printings"]
        ):
            continue

        try:
            collection.insert_one(document)
        except PyMongoError as error:
            print(f"Error while inserting document: {error}")

client.close()
