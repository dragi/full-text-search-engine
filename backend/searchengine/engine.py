"""Search engine facade.

Owns the stored documents and the inverted index, and ties together tokenization,
ranking, and snippet generation. Document IDs are assigned sequentially starting at
zero. Everything lives in memory.
"""

from __future__ import annotations

from dataclasses import dataclass

from searchengine.index import InvertedIndex
from searchengine.ranking import rank
from searchengine.snippets import make_snippet
from searchengine.tokenizer import tokenize


@dataclass(frozen=True)
class Document:
    id: int
    title: str
    body: str


@dataclass(frozen=True)
class SearchResult:
    id: int
    title: str
    score: float
    snippet: str


class SearchEngine:
    def __init__(self) -> None:
        self._index = InvertedIndex()
        self._docs: dict[int, Document] = {}
        self._next_id = 0

    def add_document(self, title: str, body: str) -> int:
        doc_id = self._next_id
        self._next_id += 1
        self._docs[doc_id] = Document(doc_id, title, body)
        self._index.add_document(doc_id, tokenize(f"{title}\n{body}"))
        return doc_id

    def get_document(self, doc_id: int) -> Document | None:
        return self._docs.get(doc_id)

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        terms = [token.term for token in tokenize(query)]
        results = []
        for doc_id, score in rank(terms, self._index, limit):
            doc = self._docs[doc_id]
            results.append(
                SearchResult(doc.id, doc.title, score, make_snippet(doc.body, terms))
            )
        return results

    def stats(self) -> dict[str, float | int]:
        return {
            "documents": self._index.document_count,
            "unique_terms": self._index.vocabulary_size,
            "postings": self._index.total_postings,
            "avg_doc_length": round(self._index.average_doc_length, 2),
        }
