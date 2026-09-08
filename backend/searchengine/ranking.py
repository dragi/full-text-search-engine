"""TF-IDF ranking.

Scores documents against a query with the classic lnc.ltc scheme:

* document term weight: ``1 + log10(tf)``, no idf, cosine-normalized by the
  document's vector norm (see ``InvertedIndex.document_norm``)
* query term weight: ``(1 + log10(tf)) * idf`` where ``idf = log10(N / df)``

A term that appears in every document has ``idf == 0`` and does not affect the
ranking. The query vector is not cosine-normalized: its norm is the same for every
document, so it changes the absolute scores but not their order. Documents are
ordered by score descending, ties broken by document ID.
"""

from __future__ import annotations

import math
from collections import Counter

from searchengine.index import InvertedIndex


def rank(
    query_terms: list[str], index: InvertedIndex, limit: int
) -> list[tuple[int, float]]:
    if not query_terms or limit <= 0:
        return []

    n = index.document_count
    if n == 0:
        return []

    scores: dict[int, float] = {}
    for term, query_tf in Counter(query_terms).items():
        postings = index.postings(term)
        df = len(postings)
        if df == 0:
            continue
        idf = math.log10(n / df)
        if idf <= 0.0:
            continue
        query_weight = (1.0 + math.log10(query_tf)) * idf
        for doc_id, positions in postings.items():
            doc_weight = 1.0 + math.log10(len(positions))
            scores[doc_id] = scores.get(doc_id, 0.0) + doc_weight * query_weight

    ranked = [
        (doc_id, raw / (index.document_norm(doc_id) or 1.0))
        for doc_id, raw in scores.items()
    ]
    ranked.sort(key=lambda pair: (-pair[1], pair[0]))
    return ranked[:limit]
