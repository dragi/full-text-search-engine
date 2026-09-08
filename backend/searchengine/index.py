"""In-memory inverted index.

Maps each term to a postings list of document IDs, with the term frequency and the
list of positions within each document. Also tracks per-document lengths and
per-term document frequencies for ranking.
"""

from __future__ import annotations

from searchengine.tokenizer import Token


class InvertedIndex:
    def __init__(self) -> None:
        raise NotImplementedError

    def add_document(self, doc_id: int, tokens: list[Token]) -> None:
        raise NotImplementedError

    def postings(self, term: str) -> dict[int, list[int]]:
        raise NotImplementedError

    def document_frequency(self, term: str) -> int:
        raise NotImplementedError

    def doc_length(self, doc_id: int) -> int:
        raise NotImplementedError

    @property
    def document_count(self) -> int:
        raise NotImplementedError

    @property
    def vocabulary_size(self) -> int:
        raise NotImplementedError
