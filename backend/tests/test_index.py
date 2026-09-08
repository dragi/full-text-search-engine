import pytest

from searchengine.index import InvertedIndex
from searchengine.tokenizer import Token, tokenize


def build(*docs):
    index = InvertedIndex()
    for doc_id, text in enumerate(docs):
        index.add_document(doc_id, tokenize(text))
    return index


def test_single_document_postings_and_positions():
    index = build("the quick brown fox")
    # "the" is a stop word; positions come from the original stream
    assert index.postings("quick") == {0: [1]}
    assert index.postings("brown") == {0: [2]}
    assert index.postings("fox") == {0: [3]}


def test_repeated_term_records_frequency_and_every_position():
    index = build("cat dog cat bird cat")
    assert index.postings("cat") == {0: [0, 2, 4]}
    assert index.term_frequency("cat", 0) == 3
    assert index.term_frequency("dog", 0) == 1


def test_document_frequency_counts_distinct_documents():
    index = build("apple banana", "apple cherry", "cherry cherry")
    assert index.document_frequency("apple") == 2
    assert index.document_frequency("cherry") == 2
    assert index.document_frequency("banana") == 1


def test_postings_span_multiple_documents():
    index = build("shared term here", "another shared line")
    assert index.postings("shared") == {0: [0], 1: [1]}


def test_unknown_term_is_empty():
    index = build("hello world")
    assert index.postings("missing") == {}
    assert index.document_frequency("missing") == 0
    assert index.term_frequency("missing", 0) == 0


def test_counts_and_sizes():
    index = build("alpha beta gamma", "beta gamma delta")
    assert index.document_count == 2
    assert index.vocabulary_size == 4  # alpha beta gamma delta
    assert index.total_postings == 2 + 2 + 1 + 1  # per-term document counts


def test_doc_length_is_token_count_after_stop_word_removal():
    index = build("the cat sat on the mat")  # -> cat sat mat
    assert index.doc_length(0) == 3
    assert index.doc_length(99) == 0


def test_average_doc_length():
    index = InvertedIndex()
    assert index.average_doc_length == 0.0
    index.add_document(0, tokenize("one two three"))
    index.add_document(1, tokenize("four five"))
    assert index.average_doc_length == pytest.approx(2.5)


def test_adding_same_document_id_twice_is_rejected():
    index = InvertedIndex()
    index.add_document(1, tokenize("first"))
    with pytest.raises(ValueError):
        index.add_document(1, tokenize("second"))
    # the failed add left nothing behind
    assert index.postings("second") == {}


def test_accepts_raw_tokens():
    index = InvertedIndex()
    index.add_document(7, [Token("lorem", 0), Token("ipsum", 1), Token("lorem", 2)])
    assert index.postings("lorem") == {7: [0, 2]}
    assert index.has_document(7)
    assert set(index.document_ids()) == {7}
    assert set(index.terms()) == {"lorem", "ipsum"}
