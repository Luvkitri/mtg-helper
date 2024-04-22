import os
import re
from pprint import pprint

from dotenv import load_dotenv
from nltk.tokenize import RegexpTokenizer, word_tokenize
from pymongo import MongoClient


class Termset:
    def __init__(self, term):
        self.term = term
        self.set_of_terms = set()
        self.cards = set()


def tokenize(text: str):
    # porter2 = SnowballStemmer(language="english", ignore_stopwords=False)
    # tokenizer = RegexpTokenizer(r"(\b[^\s{}()]+)\b|({[^}]+})")
    pattern = r"\b[^\s{}()]+\b|{\w+}"
    return re.findall(pattern, text)
    # return text.split(" ")


def main():
    # Get envs
    load_dotenv()

    username = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
    password = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
    host = os.environ.get("MONGO_HOST")
    port = os.environ.get("MONGO_PORT")

    # Connect to MongoDB
    mongo_client = MongoClient(
        "mongodb://{}:{}@{}:{}/".format(username, password, host, port)
    )
    database = mongo_client.get_database("mtg_cards")
    collection = database.get_collection("cards")

    # card_texts_cursor = collection.find({}, {"text": 1})
    # mtg_helper = MTGHelper()
    # mtg_helper.get_card_text_similarity(
    #     source_text="{T}: {1}{1}", cursor=card_texts_cursor
    # )
    # create_word2vec_model(card_texts_cursor, "text")

    sol_ring = collection.find_one({"name": "Sol Ring"})

    # for sol_ring in sol_rings:
    #     pprint.pprint(sol_ring)
    print(tokenize(sol_ring["text"]))

    # Test data
    cards_cursor = collection.find({}, {"text": 1}).limit(10)

    termsets = []
    for card in cards_cursor:
        card_id = card["_id"]
        terms = tokenize(card["text"])
        for term in terms:
            print(term)

    mongo_client.close()


if __name__ == "__main__":
    main()
