from searchengine.snippets import make_snippet


def test_empty_body_gives_empty_snippet():
    assert make_snippet("", ["anything"]) == ""


def test_highlights_query_terms():
    body = "The Eiffel Tower is a wrought-iron lattice tower in Paris."
    out = make_snippet(body, ["eiffel", "paris"])
    assert "<mark>Eiffel</mark>" in out
    assert "<mark>Paris</mark>" in out


def test_highlighting_is_case_insensitive():
    out = make_snippet("Python is a programming language.", ["python"])
    assert "<mark>Python</mark>" in out


def test_non_matching_query_falls_back_to_the_start():
    body = "one two three four five six seven eight nine ten " * 5
    out = make_snippet(body, ["absent"], max_chars=40)
    assert "<mark>" not in out
    assert out.startswith("one two")
    assert out.endswith("…")


def test_short_body_is_returned_whole_without_ellipsis():
    out = make_snippet("A tiny document.", ["absent"])
    assert out == "A tiny document."


def test_html_in_body_is_escaped():
    body = "Use <script>alert(1)</script> carefully when handling markup input."
    out = make_snippet(body, ["script"])
    assert "<script>" not in out
    assert "</script>" not in out
    assert "&lt;" in out and "&gt;" in out
    assert "<mark>script</mark>" in out


def test_window_prefers_the_densest_cluster_of_distinct_terms():
    body = (
        "alpha appears here alone near the beginning. "
        + "padding " * 40
        + "then alpha and beta and gamma all appear together at the end."
    )
    out = make_snippet(body, ["alpha", "beta", "gamma"], max_chars=120)
    assert "<mark>beta</mark>" in out
    assert "<mark>gamma</mark>" in out
    assert out.startswith("…")


def test_snippet_length_is_bounded():
    body = "word " * 500
    body = body.replace("word ", "needle ", 1) + "needle at the very end."
    out = make_snippet(body, ["needle"], max_chars=100)
    # allow for tags, ellipses and boundary expansion, but keep it in the ballpark
    assert len(out) < 220


def test_whitespace_is_collapsed():
    body = "start\n\n  keyword   spread\tacross\n lines and  more  words here"
    out = make_snippet(body, ["keyword"])
    assert "  " not in out.replace("…", "")
    assert "\n" not in out
