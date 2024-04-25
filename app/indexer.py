import math
import re

from multiprocessing import cpu_count, Pool
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
    posting: List[Tuple[ObjectId, int]]  # Posting


@dataclass
class Card:
    _id: ObjectId
    text: str


def tokenize(text: str) -> List[str]:
    pattern = r"\b[^\s{}()]+\b|{\w+}"
    return re.findall(pattern, text.lower())


def parse_card_text(text: str) -> Terms:
    tokens = tokenize(text)
    terms = {}

    for index, token in enumerate(tokens):
        if token in terms:
            terms[token].append(index)
            continue

        terms[token] = [index]

    return terms


def generate_card_index(card_id: ObjectId, terms: Terms) -> CardIndex:
    card_index = {}

    for term, positions in terms.items():
        posting = (card_id, len(positions))

        card_index[term].append(posting)

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


def reducer(card_indices):
    inverted_index = {}

    for card_index in card_indices:
        for term, postings in card_index.items():
            if term in inverted_index:
                inverted_index[term].append(postings)
                continue

            inverted_index[term] = [postings]

    return inverted_index


def generate(data_iter):
    cores = cpu_count() - 1

    with Pool(processes=cores) as pool:
        results = pool.map_async(func=mapper, iterable=data_iter).get()
        inverted_index = reducer(documents_indices=[result[0] for result in results])
        cards_info = {result[1][0]: result[1][1] for result in results}
        pool.close()
        pool.join()

    return inverted_index, cards_info


class Indexer:
    def __init__(self, inverted_index, cards_info):
        self.inverted_index = inverted_index
        self.cards_info = cards_info
        self.total_number_of_cards = 4

    def calculate_TFIDF_weight(self, term_frequency: int, card_frequency: int):
        return (1 + math.log2(term_frequency)) * math.log2(
            self.total_number_of_cards / card_frequency
        )

    def retrieve(self, source_card: Card):
        source_card_terms = parse_card_text(source_card.text)

        card_weights = {}

        # TODO ADD (source_term_weight, 0) if some card_id is missing it or figure out how to do it better

        for source_card_term, indicies in source_card_terms.items():
            if source_card_term not in self.inverted_index:
                print("Somehow card term is not in inverted index")

            term_postings = self.inverted_index[source_card_term]
            card_frequency = len(term_postings)

            source_term_weight = self.calculate_TFIDF_weight(
                len(indicies), card_frequency
            )

            for posting in term_postings:
                card_id, term_frequency = posting
                card_term_weight = self.calculate_TFIDF_weight(
                    term_frequency, len(term_postings), self.total_number_of_cards
                )

                if card_id in card_weights:
                    card_weights[card_id].append((source_term_weight, card_term_weight))
                    continue

                card_weights[card_id] = [(source_term_weight, card_term_weight)]

        similarity_scores = {}
        for card_id, card_weights in card_weights.items():
            sum1 = 0
            sum2 = 0
            sum3 = 0

            for source_weight, card_weight in card_weights:
                sum1 += source_weight * card_weight
                sum2 += source_weight**2
                sum3 += card_weight**2

            similarity_scores[card_id] = sum1 / math.sqrt(sum2) * math.sqrt(sum3)
