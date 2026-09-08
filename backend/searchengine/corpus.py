"""Load a JSONL(.gz) document collection into a search engine."""

from __future__ import annotations

from pathlib import Path

from searchengine.engine import SearchEngine


def load_into(engine: SearchEngine, path: str | Path) -> int:
    """Index every document in ``path`` and return the number loaded."""
    raise NotImplementedError
