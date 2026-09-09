"""Load a JSONL(.gz) document collection into a search engine.

Each line is a JSON object with at least ``title`` and ``body`` fields; any ``id``
in the file is ignored, since the engine assigns its own sequential IDs as it
indexes. Files ending in ``.gz`` are read with gzip, everything else as plain text.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

from searchengine.engine import SearchEngine


def load_into(engine: SearchEngine, path: str | Path) -> int:
    """Index every document in ``path`` and return the number loaded."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    loaded = 0
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            engine.add_document(record["title"], record["body"])
            loaded += 1
    return loaded
