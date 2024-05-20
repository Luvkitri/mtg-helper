from typing import List


def tail(s: str):
    return s[1:]


def head(s: str):
    return s[0]


def levenshtein_distance(first: str, second: str):
    if len(first) == 0:
        return len(second)

    if len(second) == 0:
        return len(first)

    if head(first) == head(second):
        return levenshtein_distance(tail(first), tail(second))

    return 1 + min(
        levenshtein_distance(tail(first), second),
        levenshtein_distance(first, tail(second)),
        levenshtein_distance(tail(first), tail(second)),
    )


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_terminal = False

    def __str__(self):
        return f"{self.children}"

    def __repr__(self):
        return f"{self.children}"


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def append(self, words: List[str]):
        for word in words:
            self.insert(word.lower())

    def insert(self, word):
        node = self.root
        for character in word:
            if character not in node.children:
                node.children[character] = TrieNode()

            node = node.children[character]

        node.is_terminal = True
