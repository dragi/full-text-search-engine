from searchengine.index import InvertedIndex
from searchengine.ranking import rank
from searchengine.tokenizer import tokenize


def build(*docs):
    index = InvertedIndex()
    for doc_id, text in enumerate(docs):
        index.add_document(doc_id, tokenize(text))
    return index


def ranked_ids(query, index, limit=10):
    return [doc_id for doc_id, _ in rank(query.split(), index, limit)]


def test_empty_query_returns_nothing():
    assert rank([], build("some content here"), 10) == []


def test_zero_limit_returns_nothing():
    assert rank(["content"], build("some content here"), 0) == []


def test_empty_index_returns_nothing():
    assert rank(["content"], InvertedIndex(), 10) == []


def test_unknown_terms_return_nothing():
    assert rank(["zeta", "eta"], build("alpha beta gamma"), 10) == []


def test_document_with_more_query_terms_ranks_higher():
    index = build(
        "machine learning tutorial",
        "machine learning and deep learning models",
        "gardening tips for spring",
    )
    result = ranked_ids("machine learning", index)
    assert result[0] in (0, 1)
    assert 2 not in result


def test_rare_term_outweighs_common_term():
    index = build(
        "data data data",
        "data pipeline",
        "data warehouse",
        "data streaming with kafka",
        "data lake",
        "unrelated topic entirely",
    )
    assert ranked_ids("data kafka", index)[0] == 3


def test_term_frequency_effect_is_sublinear():
    index = build(
        "target " + "filler " * 9,
        "target " * 10,
        "nothing relevant in here at all",
    )
    scored = dict(rank(["target"], index, 10))
    assert scored[1] > scored[0]
    assert scored[1] < 3 * scored[0]  # nowhere near the 10x term-frequency ratio


def test_shorter_document_is_not_penalised_by_a_long_rival():
    index = build(
        "penguin",
        "penguin " + "antarctica ice snow colony " * 30,
        "a document about something else",
    )
    assert ranked_ids("penguin", index)[0] == 0


def test_ties_break_on_document_id():
    index = build("identical text body", "identical text body", "a different thing")
    assert [doc_id for doc_id, _ in rank(["identical", "text"], index, 10)] == [0, 1]


def test_limit_caps_result_count():
    index = build(*[f"alpha item{i}" for i in range(10)], "beta gamma")
    assert len(rank(["alpha"], index, 3)) == 3


def test_term_in_every_document_has_no_effect():
    index = build("common alpha", "common beta", "common gamma")
    assert rank(["common"], index, 10) == []
    assert ranked_ids("common alpha", index)[0] == 0


def test_scores_are_positive_and_sorted():
    index = build("red green blue", "green blue yellow", "blue yellow orange", "plain")
    scores = [score for _, score in rank(["green", "yellow"], index, 10)]
    assert scores and all(s > 0 for s in scores)
    assert scores == sorted(scores, reverse=True)
