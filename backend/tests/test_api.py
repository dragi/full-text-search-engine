import pytest
from fastapi.testclient import TestClient

from searchengine import api
from searchengine.engine import SearchEngine


@pytest.fixture
def client():
    api.app.state.engine = SearchEngine()
    with TestClient(api.app) as test_client:
        yield test_client


def add(client, title, body):
    response = client.post("/documents", json={"title": title, "body": body})
    assert response.status_code == 201
    return response.json()["id"]


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_add_document_returns_created_id(client):
    first = client.post("/documents", json={"title": "A", "body": "first body"})
    assert first.status_code == 201
    assert first.json() == {"id": 0}
    second = client.post("/documents", json={"title": "B", "body": "second body"})
    assert second.json() == {"id": 1}


def test_add_document_rejects_missing_fields(client):
    assert client.post("/documents", json={"title": "no body"}).status_code == 422


def test_get_document_roundtrip(client):
    doc_id = add(client, "Whales", "Whales are large marine mammals.")
    body = client.get(f"/documents/{doc_id}").json()
    assert body == {
        "id": doc_id,
        "title": "Whales",
        "body": "Whales are large marine mammals.",
    }


def test_get_missing_document_is_404(client):
    response = client.get("/documents/999")
    assert response.status_code == 404
    assert "999" in response.json()["detail"]


def test_search_finds_an_indexed_document_with_score_and_snippet(client):
    add(client, "Solar System", "The Sun and the planets that orbit it.")
    add(client, "Cooking", "A recipe for braised beef and root vegetables.")
    add(client, "Astronomy", "Astronomers observe planets, moons and distant stars.")

    body = client.get("/search", params={"q": "planets"}).json()
    assert body["query"] == "planets"
    assert body["count"] >= 1
    assert "elapsed_ms" in body
    top = body["results"][0]
    assert top["title"] in {"Solar System", "Astronomy"}
    assert top["score"] > 0
    assert "<mark>planets</mark>" in top["snippet"]


def test_search_respects_the_limit(client):
    for i in range(5):
        add(client, f"doc {i}", "shared keyword here")
    add(client, "outlier", "nothing in common with the rest")
    body = client.get("/search", params={"q": "keyword", "limit": 2}).json()
    assert len(body["results"]) == 2
    assert body["count"] == 2


def test_search_rejects_a_non_positive_limit(client):
    assert client.get("/search", params={"q": "x", "limit": 0}).status_code == 422


def test_empty_query_returns_no_results(client):
    add(client, "Topic", "some indexed content")
    body = client.get("/search", params={"q": ""}).json()
    assert body["count"] == 0
    assert body["results"] == []


def test_stats_reflect_additions(client):
    empty = client.get("/stats").json()
    assert empty["documents"] == 0

    add(client, "Alpha", "alpha beta gamma")
    add(client, "Delta", "delta beta gamma")
    stats = client.get("/stats").json()
    assert stats["documents"] == 2
    assert stats["unique_terms"] == 4  # alpha beta gamma delta (titles lowercase alike)
    assert stats["postings"] == 6  # alpha:1 delta:1 beta:2 gamma:2
    assert stats["avg_doc_length"] == 4.0  # title + body tokens per document
