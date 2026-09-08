from searchengine.engine import SearchEngine

# Unrelated documents that share no vocabulary with the tests' target documents.
# Adding them keeps a searched term's document frequency below the corpus size, so
# its idf stays non-zero (a term that appears in *every* document is ignored).
FILLER = [
    ("Cooking", "A recipe for slow-braised beef with root vegetables."),
    ("Weather", "Coastal fog forms when warm air moves over a cold current."),
    ("Music", "The string quartet rehearsed the second movement all afternoon."),
]


def make_engine(*docs):
    engine = SearchEngine()
    for title, body in docs:
        engine.add_document(title, body)
    return engine


def make_engine_with_filler(*docs):
    return make_engine(*docs, *FILLER)


def test_add_document_assigns_sequential_ids():
    engine = SearchEngine()
    assert engine.add_document("first", "some body") == 0
    assert engine.add_document("second", "another body") == 1


def test_get_document_returns_stored_fields():
    engine = SearchEngine()
    doc_id = engine.add_document("Whales", "Whales are large marine mammals.")
    doc = engine.get_document(doc_id)
    assert doc is not None
    assert doc.title == "Whales"
    assert doc.body == "Whales are large marine mammals."


def test_get_unknown_document_is_none():
    assert SearchEngine().get_document(3) is None


def test_search_ranks_relevant_document_first():
    engine = make_engine(
        ("Solar System", "The Sun and the planets orbiting it form the solar system."),
        ("Gardening", "Tips for growing tomatoes and herbs at home."),
        ("Astronomy", "Telescopes let astronomers study distant planets and stars."),
    )
    results = engine.search("planets")
    assert results
    assert results[0].id in (0, 2)
    assert all(r.score > 0 for r in results)


def test_search_result_carries_a_highlighted_snippet():
    engine = make_engine_with_filler(
        ("Eiffel Tower", "The Eiffel Tower is a wrought-iron lattice tower in Paris."),
    )
    (result,) = engine.search("eiffel paris")
    assert result.id == 0
    assert "<mark>Eiffel</mark>" in result.snippet
    assert "<mark>Paris</mark>" in result.snippet


def test_title_terms_are_searchable():
    engine = make_engine_with_filler(
        ("Photosynthesis", "Plants convert light into chemical energy."),
    )
    results = engine.search("photosynthesis")
    assert [r.id for r in results] == [0]


def test_search_respects_the_limit():
    engine = make_engine_with_filler(
        *[(f"doc {i}", "shared keyword here") for i in range(5)]
    )
    assert len(engine.search("keyword", limit=2)) == 2


def test_search_with_no_match_returns_empty():
    engine = make_engine(("Topic", "entirely unrelated content"))
    assert engine.search("absent") == []


def test_empty_query_returns_empty():
    engine = make_engine(("Topic", "some content"))
    assert engine.search("") == []


def test_stats_reflect_indexed_documents():
    engine = make_engine(
        ("Minerals", "alpha beta gamma"),
        ("Physics", "delta beta gamma"),
    )
    stats = engine.stats()
    assert stats["documents"] == 2
    # bodies: alpha beta gamma delta; titles add minerals, physics
    assert stats["unique_terms"] == 6
    assert stats["avg_doc_length"] > 0
