"""Snippet extraction with query-term highlighting.

Finds the passage of a document body with the highest concentration of query terms
and returns it with matches wrapped in ``<mark>`` tags. Non-match text is
HTML-escaped.
"""

from __future__ import annotations


def make_snippet(body: str, query_terms: list[str], max_chars: int = 240) -> str:
    """Return a highlighted snippet of at most roughly ``max_chars`` characters."""
    raise NotImplementedError
