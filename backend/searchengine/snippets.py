"""Snippet extraction with query-term highlighting.

Picks the passage of a document body with the highest concentration of distinct
query terms, trims it to roughly ``max_chars`` characters on word boundaries, and
returns it as an HTML fragment with matches wrapped in ``<mark>`` tags. All text is
HTML-escaped; the only markup in the result is ``<mark>`` and ``</mark>``. Leading
and trailing ellipses mark where the body was cut.
"""

from __future__ import annotations

import re
from html import escape

from searchengine.tokenizer import normalize

_WORD_RE = re.compile(r"[^\W_]+(?:['’ʼ][^\W_]+)*", re.UNICODE)
_WHITESPACE_RE = re.compile(r"\s+")
_ELLIPSIS = "…"


def _match_spans(body: str, query: set[str]) -> list[tuple[int, int, str]]:
    spans = []
    for match in _WORD_RE.finditer(body):
        term = normalize(match.group())
        if term in query:
            spans.append((match.start(), match.end(), term))
    return spans


def _best_cluster(spans: list[tuple[int, int, str]], max_chars: int) -> tuple[int, int]:
    """Return the (first, last) span indices of the strongest cluster."""
    best_range = (0, 0)
    best_key = (-1, -1, 1)
    for i in range(len(spans)):
        seen: set[str] = set()
        for j in range(i, len(spans)):
            if spans[j][0] - spans[i][0] > max_chars:
                break
            seen.add(spans[j][2])
            key = (len(seen), j - i + 1, -(spans[j][1] - spans[i][0]))
            if key > best_key:
                best_key = key
                best_range = (i, j)
    return best_range


def _grow_left(body: str, index: int) -> int:
    while index > 0 and not body[index - 1].isspace():
        index -= 1
    return index


def _grow_right(body: str, index: int) -> int:
    while index < len(body) and not body[index].isspace():
        index += 1
    return index


def _render(body: str, start: int, end: int, spans: list[tuple[int, int, str]]) -> str:
    out: list[str] = []
    cursor = start
    for span_start, span_end, _ in spans:
        if span_start < start or span_end > end:
            continue
        out.append(escape(body[cursor:span_start], quote=False))
        out.append(f"<mark>{escape(body[span_start:span_end], quote=False)}</mark>")
        cursor = span_end
    out.append(escape(body[cursor:end], quote=False))
    return "".join(out)


def make_snippet(body: str, query_terms: list[str], max_chars: int = 240) -> str:
    body = body.strip()
    if not body:
        return ""

    spans = _match_spans(body, set(query_terms))

    if not spans:
        end = min(len(body), max_chars)
        if end < len(body):
            end = _grow_left(body, end)
        text = escape(body[:end], quote=False)
        text = _WHITESPACE_RE.sub(" ", text).strip()
        return f"{text} {_ELLIPSIS}" if end < len(body) else text

    first, last = _best_cluster(spans, max_chars)
    window_start, window_end = spans[first][0], spans[last][1]

    padding = max(0, (max_chars - (window_end - window_start)) // 2)
    start = _grow_left(body, max(0, window_start - padding))
    end = _grow_right(body, min(len(body), window_end + padding))

    text = _render(body, start, end, spans)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    if start > 0:
        text = f"{_ELLIPSIS} {text}"
    if end < len(body):
        text = f"{text} {_ELLIPSIS}"
    return text
