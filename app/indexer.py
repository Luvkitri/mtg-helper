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
        card_index[term] = posting

    return card_index


def generate_card_frequencies(card_id: ObjectId, terms):
    card_frequencies = {}

    for term, positions in terms.items():
        card_frequencies[term] = len(positions)

    return (card_id, card_frequencies)


def mapper(card: Card):
    try:
        terms = parse_card_text(card["text"])
        card_frequencies = generate_card_frequencies(card["_id"], terms)
        card_index = generate_card_index(card["_id"], terms)
        return (card_index, card_frequencies)
    except Exception as error:
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


async def generate_inverted_index(data_iter):
    cores = cpu_count() - 1
    print(f"Running on {cores} processes...")

    with Pool(processes=cores) as pool:
        results = pool.map_async(func=mapper, iterable=data_iter).get()
        inverted_index = reducer(
            card_indices=[result[0] for result in results if result]
        )
        cards_frequencies = {result[1][0]: result[1][1] for result in results if result}

        pool.close()
        pool.join()

    return inverted_index, cards_frequencies


class Indexer:
    def __init__(self, inverted_index, cards_frequencies):
        self.inverted_index = inverted_index
        self.total_number_of_cards = 4
        self.cards_frequencies = cards_frequencies

    def calculate_TFIDF_weight(self, term_frequency: int, card_frequency: int):
        return (1 + math.log2(term_frequency)) * math.log2(
            self.total_number_of_cards / card_frequency
        )

    def calculate_card_norm(self, card_id):
        card_norm = 0

        for term, term_frequency in self.cards_frequencies[card_id].items():
            card_norm += (
                self.calculate_TFIDF_weight(
                    term_frequency, len(self.inverted_index[term])
                )
                ** 2
            )

        return math.sqrt(card_norm)

    def calculate_similarity_scores(self, cards_data):
        similarity_scores = {}
        for card_id, card_weights in cards_data.items():
            similarity_scores[card_id] = round(
                sum(
                    source_term_weight * card_term_weight
                    for source_term_weight, card_term_weight in card_weights
                )
                / self.calculate_card_norm(card_id),
                ndigits=3,
            )

        return similarity_scores

    def retrieve(self, source_card: Card):
        source_card_terms = parse_card_text(source_card["text"])

        cards_data = {}

        for source_card_term, indicies in source_card_terms.items():
            if source_card_term not in self.inverted_index:
                print(f"Missing {source_card_term}")
                continue
            term_postings = self.inverted_index[source_card_term]
            card_frequency = len(term_postings)

            source_term_weight = self.calculate_TFIDF_weight(
                len(indicies), card_frequency
            )

            for term_posting in term_postings:
                card_id, term_frequency = term_posting

                card_term_weight = self.calculate_TFIDF_weight(
                    term_frequency, card_frequency
                )

                if card_id in cards_data:
                    cards_data[card_id].append((source_term_weight, card_term_weight))
                    continue

                cards_data[card_id] = [(source_term_weight, card_term_weight)]

        similarity_scores = self.calculate_similarity_scores(cards_data)
        return dict(
            sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        )
