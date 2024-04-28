import pytest

from app.indexer import (
    generate_card_index,
    tokenize,
    parse_card_text,
    generate_inverted_index,
    Indexer,
)
from bson.objectid import ObjectId

GENERIC_TEST_DATA = [
    {
        "_id": "d1",
        "text": "To do is to be.\nTo be is to do.",
    },
    {
        "_id": "d2",
        "text": "To be or not to be.\nI am what I am",
    },
    {
        "_id": "d3",
        "text": "I think therefore I am.\nDo be do be do.",
    },
    {
        "_id": "d4",
        "text": "Do do do, da da da.\nLet it be, let it be.",
    },
]


CARD_TEST_DATA = [{"_id": ObjectId(), "text": "{T}: Add {1}{1}"}]


@pytest.mark.parametrize(
    ("text_input", "expected"),
    (
        (
            GENERIC_TEST_DATA[0]["text"],
            ["to", "do", "is", "to", "be", "to", "be", "is", "to", "do"],
        ),
        (
            GENERIC_TEST_DATA[1]["text"],
            ["to", "be", "or", "not", "to", "be", "i", "am", "what", "i", "am"],
        ),
        (
            GENERIC_TEST_DATA[2]["text"],
            ["i", "think", "therefore", "i", "am", "do", "be", "do", "be", "do"],
        ),
        (
            GENERIC_TEST_DATA[3]["text"],
            ["do", "do", "do", "da", "da", "da", "let", "it", "be", "let", "it", "be"],
        ),
        (CARD_TEST_DATA[0]["text"], ["{t}", "add", "{1}", "{1}"]),
    ),
)
def test_tokenize(text_input, expected):
    assert tokenize(text_input) == expected


@pytest.mark.parametrize(
    ("text_input", "expected"),
    (
        (
            GENERIC_TEST_DATA[0]["text"],
            {
                "to": [0, 3, 5, 8],
                "do": [1, 9],
                "is": [2, 7],
                "be": [4, 6],
            },
        ),
        (CARD_TEST_DATA[0]["text"], {"{t}": [0], "add": [1], "{1}": [2, 3]}),
    ),
)
def test_parse_card_text(text_input, expected):
    assert parse_card_text(text_input) == expected


@pytest.mark.parametrize(
    ("card_id", "terms", "expected"),
    (
        (
            "some_id",
            {
                "to": [0, 3, 5, 8],
                "do": [1, 9],
                "is": [2, 7],
                "be": [4, 6],
            },
            {
                "to": ("some_id", 4),
                "do": ("some_id", 2),
                "is": ("some_id", 2),
                "be": ("some_id", 2),
            },
        ),
        (
            "some_id",
            {"{t}": [0], "add": [1], "{1}": [2, 3]},
            {"{t}": ("some_id", 1), "add": ("some_id", 1), "{1}": ("some_id", 2)},
        ),
    ),
)
def test_generate_card_index(card_id, terms, expected):
    assert generate_card_index(card_id, terms) == expected


@pytest.mark.parametrize(
    ("data_iter", "expected"),
    (
        (
            GENERIC_TEST_DATA,
            (
                {
                    "to": [("d1", 4), ("d2", 2)],
                    "do": [("d1", 2), ("d3", 3), ("d4", 3)],
                    "is": [("d1", 2)],
                    "be": [("d1", 2), ("d2", 2), ("d3", 2), ("d4", 2)],
                    "or": [("d2", 1)],
                    "not": [("d2", 1)],
                    "i": [("d2", 2), ("d3", 2)],
                    "am": [("d2", 2), ("d3", 1)],
                    "what": [("d2", 1)],
                    "think": [("d3", 1)],
                    "therefore": [("d3", 1)],
                    "da": [("d4", 3)],
                    "let": [("d4", 2)],
                    "it": [("d4", 2)],
                }
            ),
        ),
    ),
)
def test_generate_inverted_index(data_iter, expected):
    assert generate_inverted_index(data_iter) == expected


@pytest.mark.parametrize(
    ("query", "expected"),
    (
        (
            {"_id": "some_id", "text": "to do"},
            (
                {
                    "d1": 0.660,
                    "d2": 0.408,
                    "d3": 0.118,
                    "d4": 0.058,
                }
            ),
        ),
    ),
)
def test_retrieval(query, expected):
    inverted_index = generate_inverted_index(GENERIC_TEST_DATA)
    indexer = Indexer(inverted_index)
    assert indexer.retrieve(query) == expected
