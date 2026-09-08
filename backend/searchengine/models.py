"""Pydantic request and response schemas for the REST API."""

from __future__ import annotations

from pydantic import BaseModel


class DocumentIn(BaseModel):
    title: str
    body: str


class DocumentOut(BaseModel):
    id: int
    title: str
    body: str


class SearchResultOut(BaseModel):
    id: int
    title: str
    score: float
    snippet: str


class SearchResponse(BaseModel):
    query: str
    count: int
    elapsed_ms: float
    results: list[SearchResultOut]


class StatsOut(BaseModel):
    documents: int
    unique_terms: int
    postings: int
    avg_doc_length: float
