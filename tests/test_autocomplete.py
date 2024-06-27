import pytest

from app.autocomplete import levenshtein_distance, iter_levenshtein_distance


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    (
        (
            "kitten",
            "sitting",
            3,
        ),
    ),
)
def test_iter_levenshtein_distance(first, second, expected):
    assert iter_levenshtein_distance(first, second) == expected


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    (
        (
            "kitten",
            "sitting",
            3,
        ),
    ),
)
def test_levenshtein_distance(first, second, expected):
    assert levenshtein_distance(first, second) == expected
