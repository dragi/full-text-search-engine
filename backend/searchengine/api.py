"""FastAPI application exposing the search engine over HTTP.

A single in-memory :class:`SearchEngine` lives on ``app.state.engine``. On startup
the bundled Simple English Wikipedia sample is indexed into it; set ``SKIP_CORPUS=1``
to start empty (used by the tests) or ``CORPUS_PATH`` to point at another JSONL(.gz)
file. ``POST /documents`` adds to the index at runtime but nothing is persisted
across restarts. Allowed CORS origins come from the ``ALLOWED_ORIGINS`` environment
variable (comma-separated, default ``*``).
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from searchengine.corpus import load_into
from searchengine.engine import SearchEngine
from searchengine.models import (
    DocumentIn,
    DocumentOut,
    SearchResponse,
    SearchResultOut,
    StatsOut,
)

logger = logging.getLogger("searchengine")

_DEFAULT_CORPUS = Path(__file__).resolve().parent.parent / "data" / "wikipedia_sample.jsonl.gz"


def _load_corpus(engine: SearchEngine) -> None:
    if os.getenv("SKIP_CORPUS") == "1":
        return
    path = Path(os.getenv("CORPUS_PATH", _DEFAULT_CORPUS))
    if not path.exists():
        logger.warning("corpus file %s not found; starting with an empty index", path)
        return
    started = time.perf_counter()
    count = load_into(engine, path)
    logger.info("indexed %d documents from %s in %.2fs", count, path.name, time.perf_counter() - started)


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = SearchEngine()
    _load_corpus(engine)
    app.state.engine = engine
    yield


app = FastAPI(title="Full-Text Search Engine", lifespan=lifespan)

_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fallback so the app is usable even if the ASGI lifespan is not run (e.g. a bare
# TestClient without a context manager); the lifespan replaces this on startup.
app.state.engine = SearchEngine()


def _engine() -> SearchEngine:
    return app.state.engine


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents", status_code=status.HTTP_201_CREATED)
def add_document(document: DocumentIn) -> dict[str, int]:
    return {"id": _engine().add_document(document.title, document.body)}


@app.get("/documents/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: int) -> DocumentOut:
    document = _engine().get_document(doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail=f"document {doc_id} not found")
    return DocumentOut(id=document.id, title=document.title, body=document.body)


@app.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(default="", description="query string"),
    limit: int = Query(default=10, ge=1, le=100),
) -> SearchResponse:
    start = time.perf_counter()
    results = _engine().search(q, limit)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return SearchResponse(
        query=q,
        count=len(results),
        elapsed_ms=round(elapsed_ms, 3),
        results=[
            SearchResultOut(
                id=result.id,
                title=result.title,
                score=result.score,
                snippet=result.snippet,
            )
            for result in results
        ],
    )


@app.get("/stats", response_model=StatsOut)
def stats() -> StatsOut:
    return StatsOut(**_engine().stats())
