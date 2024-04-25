import pytest

from app.indexer import Indexer, generate, tokenize, parse_card_text
from bson.objectid import ObjectId

GENERIC_TEST_DATA = [
    {
        "_id": ObjectId(),
        "text": "To do is to be.\nTo be is to do.",
    },
    {
        "_id": ObjectId(),
        "text": "To be or not to be.\nI am what I am",
    },
    {
        "_id": ObjectId(),
        "text": "I think therfore I am.\nDo be do be do.",
    },
    {
        "_id": ObjectId(),
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
            ["i", "think", "therfore", "i", "am", "do", "be", "do", "be", "do"],
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


def test_generate_card_index()
