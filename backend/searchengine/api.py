"""FastAPI application exposing the search engine over HTTP.

A single in-memory :class:`SearchEngine` lives on ``app.state.engine``. It starts
empty; ``POST /documents`` adds to it at runtime but nothing is persisted across
restarts. Allowed CORS origins come from the ``ALLOWED_ORIGINS`` environment
variable (comma-separated, default ``*``).
"""

from __future__ import annotations

import os
import time

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from searchengine.engine import SearchEngine
from searchengine.models import (
    DocumentIn,
    DocumentOut,
    SearchResponse,
    SearchResultOut,
    StatsOut,
)

app = FastAPI(title="Full-Text Search Engine")

_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
