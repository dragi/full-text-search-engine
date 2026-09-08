from searchengine.tokenizer import Token, analyze, normalize, tokenize


def terms(text):
    return [t.term for t in tokenize(text)]


def test_lowercases():
    assert terms("The QUICK Brown FOX") == ["quick", "brown", "fox"]


def test_strips_punctuation():
    assert terms("Hello, world! (Really?) -- yes.") == ["hello", "world", "really", "yes"]


def test_splits_on_hyphens_and_slashes():
    assert terms("state-of-the-art TCP/IP stack") == ["state", "art", "tcp", "ip", "stack"]


def test_collapses_apostrophes():
    assert terms("It's Dragan's résumé") == ["dragans", "résumé"]
    # curly apostrophe is handled the same way
    assert terms("can’t won’t") == []


def test_removes_stop_words():
    assert terms("the cat sat on a mat and it was warm") == ["cat", "sat", "mat", "warm"]


def test_keeps_digits():
    assert terms("iPhone 15 released in 2023") == ["iphone", "15", "released", "2023"]


def test_unicode_letters_survive():
    assert terms("Zürich Malmö São Paulo") == ["zürich", "malmö", "são", "paulo"]


def test_empty_and_whitespace_input():
    assert tokenize("") == []
    assert tokenize("   \n\t  ") == []
    assert tokenize("!!! ??? ...") == []


def test_positions_count_from_original_stream():
    tokens = tokenize("the quick brown fox jumps")
    assert tokens == [
        Token("quick", 1),
        Token("brown", 2),
        Token("fox", 3),
        Token("jumps", 4),
    ]


def test_positions_preserve_gaps_from_removed_stop_words():
    # "a b c" where b is a stop word -> positions 0 and 2, gap at 1
    tokens = tokenize("cat the dog")
    assert [(t.term, t.position) for t in tokens] == [("cat", 0), ("dog", 2)]


def test_analyze_keeps_stop_words_but_normalizes():
    assert analyze("The Cat's Hat") == ["the", "cats", "hat"]


def test_normalize():
    assert normalize("DON'T STOP") == "dont stop"
