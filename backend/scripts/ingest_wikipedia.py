"""Download a Simple English Wikipedia subset and write it as a JSONL.gz corpus.

Pulls rows from the Hugging Face datasets-server (JSON, no extra dependencies),
keeps the first articles with a body of at least ``MIN_BODY_CHARS`` characters,
lightly cleans the text, caps each body at ``MAX_BODY_CHARS`` on a paragraph or
sentence boundary, and writes ``data/wikipedia_sample.jsonl.gz`` with one
``{"id", "title", "body"}`` object per line. Ordering follows the dataset, so runs
are deterministic.

Run from the backend directory:

    python scripts/ingest_wikipedia.py [target_docs]
"""

from __future__ import annotations

import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DATASET = "wikimedia/wikipedia"
CONFIG = "20231101.simple"
SPLIT = "train"
ROWS_URL = "https://datasets-server.huggingface.co/rows"
PAGE_SIZE = 100  # datasets-server hard limit per request

TARGET_DOCS = 5000
MIN_BODY_CHARS = 200
MAX_BODY_CHARS = 1500

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "wikipedia_sample.jsonl.gz"

_INLINE_WS_RE = re.compile(r"[^\S\n]+")
_BLANK_LINES_RE = re.compile(r"\n\s*\n\s*")
_SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s")


def _clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\xa0", " ")
    text = _INLINE_WS_RE.sub(" ", text)
    text = _BLANK_LINES_RE.sub("\n\n", text)
    return text.strip()


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    head = text[:limit]
    para = head.rfind("\n\n")
    if para >= MIN_BODY_CHARS:
        return head[:para].strip()
    sentences = list(_SENTENCE_END_RE.finditer(head))
    if sentences and sentences[-1].start() >= MIN_BODY_CHARS:
        return head[: sentences[-1].start() + 1].strip()
    return head[: head.rfind(" ")].strip()


def _fetch_page(offset: int, length: int, *, retries: int = 6) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "dataset": DATASET,
            "config": CONFIG,
            "split": SPLIT,
            "offset": offset,
            "length": length,
        }
    )
    request = urllib.request.Request(
        f"{ROWS_URL}?{query}",
        headers={"User-Agent": "searchengine-ingest/1.0"},
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.load(response)
            return [item["row"] for item in payload["rows"]]
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == retries - 1:
                raise
            wait = float(error.headers.get("Retry-After") or 5 * (2**attempt))
            print(f"  rate limited, retrying in {wait:.0f}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("unreachable")


def main(target: int = TARGET_DOCS) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    kept = 0
    offset = 0

    with gzip.open(OUT_PATH, "wt", encoding="utf-8") as out:
        while kept < target:
            rows = _fetch_page(offset, PAGE_SIZE)
            if not rows:
                break
            offset += len(rows)
            for row in rows:
                body = _truncate(_clean(row["text"]), MAX_BODY_CHARS)
                if len(body) < MIN_BODY_CHARS:
                    continue
                record = {"id": row["id"], "title": row["title"], "body": body}
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                kept += 1
                if kept >= target:
                    break
            print(f"  scanned {offset}, kept {kept}", file=sys.stderr)
            time.sleep(1.0)

    size_mb = OUT_PATH.stat().st_size / 1_000_000
    elapsed = time.perf_counter() - started
    print(
        f"wrote {kept} documents to {OUT_PATH} ({size_mb:.1f} MB) in {elapsed:.0f}s",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else TARGET_DOCS)
