"""Search engine facade.

Ties together the tokenizer, inverted index, ranking, and snippet generation, and
owns the stored raw documents.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    id: int
    title: str
    score: float
    snippet: str


@dataclass(frozen=True)
class Document:
    id: int
    title: str
    body: str


class SearchEngine:
    def __init__(self) -> None:
        raise NotImplementedError

    def add_document(self, title: str, body: str) -> int:
        raise NotImplementedError

    def get_document(self, doc_id: int) -> Document | None:
        raise NotImplementedError

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        raise NotImplementedError

    def stats(self) -> dict[str, float | int]:
        raise NotImplementedError
