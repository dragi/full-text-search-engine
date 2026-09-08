"""In-memory inverted index.

Maps each term to a postings list: for every document that contains the term, the
list of positions where it occurs. The term frequency in a document is simply the
length of its position list. The index also tracks per-document lengths and the set
of indexed document IDs, which ranking and the stats endpoint build on.

The structures are plain dicts and are never persisted; the index is rebuilt from the
document collection on startup.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, KeysView

from searchengine.tokenizer import Token

Postings = dict[int, list[int]]


class InvertedIndex:
    def __init__(self) -> None:
        self._postings: dict[str, Postings] = {}
        self._doc_lengths: dict[int, int] = {}
        self._norms: dict[int, float] | None = None

    def add_document(self, doc_id: int, tokens: Iterable[Token]) -> None:
        """Add a document's tokens to the index.

        Raises ``ValueError`` if ``doc_id`` was already indexed; documents are
        immutable once added.
        """
        if doc_id in self._doc_lengths:
            raise ValueError(f"document {doc_id} is already indexed")

        self._norms = None
        length = 0
        for token in tokens:
            length += 1
            term_postings = self._postings.setdefault(token.term, {})
            term_postings.setdefault(doc_id, []).append(token.position)
        self._doc_lengths[doc_id] = length

    def postings(self, term: str) -> Postings:
        """Return ``{doc_id: [positions]}`` for ``term`` (empty if unknown).

        The returned dict is the index's own storage; callers must not mutate it.
        """
        return self._postings.get(term, {})

    def document_frequency(self, term: str) -> int:
        """Number of documents containing ``term``."""
        return len(self._postings.get(term, {}))

    def term_frequency(self, term: str, doc_id: int) -> int:
        """Number of occurrences of ``term`` in ``doc_id``."""
        return len(self._postings.get(term, {}).get(doc_id, ()))

    def doc_length(self, doc_id: int) -> int:
        """Token count of ``doc_id`` (0 if unknown)."""
        return self._doc_lengths.get(doc_id, 0)

    def document_norm(self, doc_id: int) -> float:
        """L2 norm of the document's log-term-frequency vector.

        Used by the ranker to cosine-normalize scores. Computed in one pass over
        the postings the first time it is needed and cached until a new document
        is added.
        """
        if self._norms is None:
            self._compute_norms()
        return self._norms.get(doc_id, 0.0)

    def _compute_norms(self) -> None:
        sums: dict[int, float] = {}
        for docs in self._postings.values():
            for doc_id, positions in docs.items():
                weight = 1.0 + math.log10(len(positions))
                sums[doc_id] = sums.get(doc_id, 0.0) + weight * weight
        self._norms = {doc_id: math.sqrt(value) for doc_id, value in sums.items()}

    def has_document(self, doc_id: int) -> bool:
        return doc_id in self._doc_lengths

    def terms(self) -> KeysView[str]:
        return self._postings.keys()

    def document_ids(self) -> KeysView[int]:
        return self._doc_lengths.keys()

    @property
    def document_count(self) -> int:
        return len(self._doc_lengths)

    @property
    def vocabulary_size(self) -> int:
        return len(self._postings)

    @property
    def total_postings(self) -> int:
        """Total number of (term, document) pairs in the index."""
        return sum(len(docs) for docs in self._postings.values())

    @property
    def average_doc_length(self) -> float:
        if not self._doc_lengths:
            return 0.0
        return sum(self._doc_lengths.values()) / len(self._doc_lengths)
