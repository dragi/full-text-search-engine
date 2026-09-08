"""TF-IDF ranking.

Scores documents against a query using logarithmic term frequency, inverse document
frequency, and cosine normalization of the document vectors.
"""

from __future__ import annotations

from searchengine.index import InvertedIndex


def rank(
    query_terms: list[str], index: InvertedIndex, limit: int
) -> list[tuple[int, float]]:
    """Return up to ``limit`` ``(doc_id, score)`` pairs, most relevant first."""
    raise NotImplementedError
