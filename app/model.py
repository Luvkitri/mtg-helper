# import os
# from pprint import pprint

# from dotenv import load_dotenv
# from pymongo import MongoClient

# from indexer import Indexer, generate_inverted_index
from autocomplete import Trie


def main():
    # Get envs
    # load_dotenv()
    # username = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
    # password = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
    # host = os.environ.get("MONGO_HOST")
    # port = os.environ.get("MONGO_PORT")

    # # Connect to MongoDB
    # mongo_client = MongoClient(
    #     "mongodb://{}:{}@{}:{}/".format(username, password, host, port)
    # )
    # database = mongo_client.get_database("mtg_cards")
    # collection = database.get_collection("cards")
    # # indexer.retrieve()
    # # card_texts_cursor = collection.find({}, {"text": 1})
    # # mtg_helper = MTGHelper()
    # # mtg_helper.get_card_text_similarity(
    # #     source_text="{T}: {1}{1}", cursor=card_texts_cursor
    # # )
    # # create_word2vec_model(card_texts_cursor, "text")

    # # sol_ring = collection.find_one({"name": "Sol Ring"})

    # # for sol_ring in sol_rings:
    # #     pprint.pprint(sol_ring)
    # # print(tokenize(sol_ring["text"]))

    # # Test
    # # cards_cursor = collection.find({}, {"text": 1})

    # # inverted_index, cards_frequencies = generate_inverted_index(cards_cursor)
    # # indexer = Indexer(inverted_index, cards_frequencies)

    # # Source
    # sol_ring = collection.find_one(
    #     {"name": "Shu Yun, the Silent Tempest"},
    #     {
    #         "colors": 1,
    #         "colorIdentity": 1,
    #         "text": 1,
    #         "convertedManaCost": 1,
    #         "types": 1,
    #     },
    # )
    # pprint(sol_ring)
    # # sim_scores = indexer.retrieve(sol_ring)
    # # results = collection.find(
    # #     {"_id": {"$in": [result for (result, _) in sim_scores]}}, {"name": 1, "text": 1}
    # # )
    # # for result in results:
    # #     pprint(result)
    # mongo_client.close()

    trie = Trie()
    trie.append("Ala ma kota, a kot ma Ale".split(" "))
    print(trie.root)
    print(trie.auto_complete("a"))


if __name__ == "__main__":
    main()
