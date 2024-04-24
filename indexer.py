import math
import re

from typing import List, Tuple
from dataclasses import dataclass
from bson.objectid import ObjectId


@dataclass
class Terms:
    term: List[str]


# @dataclass
# class Posting:
#     card_id: ObjectId
#     term_frequency: int


@dataclass
class CardIndex:
    term: str
    posting: Tuple[ObjectId, int]  # Posting


@dataclass
class Card:
    _id: ObjectId
    text: str


def tokenize(text: str) -> List[str]:
    pattern = r"\b[^\s{}()]+\b|{\w+}"
    return re.findall(pattern, text)


def parse_card_text(text: str) -> Terms:
    tokens = tokenize(text)
    terms = {}

    for index, token in enumerate(tokens):
        if token in terms:
            terms[token].append(index)
            continue

        terms[token] = [index]


def generate_card_index(card_id: ObjectId, terms: Terms) -> CardIndex:
    card_index = {}

    for term, positions in terms.items():
        posting = (card_id, len(positions))

        card_index[term] = posting

    return card_index


def mapper(card: Card):
    try:
        terms = parse_card_text(card.text)
        card_info = (card._id, len(terms))
        card_index = generate_card_index(card._id, terms)
        return (card_info, card_index)
    except Exception as error:
        # just in case i guess
        print(error)
        return None


class Indexer:
    def __init__(self, inverted_index, cards_info):
        self.inverted_index = inverted_index
        self.cards_info = cards_info
        self.total_number_of_cards = 20_000

    def calculate_TFIDF_weight(self, term_frequency, card_frequency):
        return 1 + math.log(term_frequency) * math.log(
            self.total_number_of_cards / card_frequency
        )

    def retrieve(self, source_card: Card):
        source_card_terms = parse_card_text(source_card.text)

        degrees_of_similarity = {}

        for source_card_term in source_card_terms:
            if source_card_term not in self.inverted_index:
                print("Somehow card term is not in inverted index")

            term_postings = self.inverted_index[source_card_term]

            for post in term_postings:
                pass
