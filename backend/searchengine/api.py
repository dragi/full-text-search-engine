"""FastAPI application exposing the search engine over HTTP."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Full-Text Search Engine")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
