import gzip
import json

import pytest

from searchengine.corpus import load_into
from searchengine.engine import SearchEngine

RECORDS = [
    {"id": 10, "title": "Whales", "body": "Whales are large marine mammals."},
    {"id": 11, "title": "Bicycle", "body": "A bicycle is a pedal-driven vehicle."},
    {"id": 12, "title": "Basalt", "body": "Basalt is a common volcanic rock."},
]


def write_jsonl(path, records, blank_lines=False):
    lines = []
    for record in records:
        lines.append(json.dumps(record))
        if blank_lines:
            lines.append("")
    text = "\n".join(lines) + "\n"
    if str(path).endswith(".gz"):
        with gzip.open(path, "wt", encoding="utf-8") as handle:
            handle.write(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path


def test_loads_plain_jsonl(tmp_path):
    path = write_jsonl(tmp_path / "corpus.jsonl", RECORDS)
    engine = SearchEngine()
    assert load_into(engine, path) == 3
    assert engine.stats()["documents"] == 3


def test_loads_gzipped_jsonl(tmp_path):
    path = write_jsonl(tmp_path / "corpus.jsonl.gz", RECORDS)
    engine = SearchEngine()
    assert load_into(engine, path) == 3


def test_blank_lines_are_skipped(tmp_path):
    path = write_jsonl(tmp_path / "corpus.jsonl", RECORDS, blank_lines=True)
    engine = SearchEngine()
    assert load_into(engine, path) == 3


def test_documents_are_searchable_after_loading(tmp_path):
    path = write_jsonl(tmp_path / "corpus.jsonl.gz", RECORDS)
    engine = SearchEngine()
    load_into(engine, path)
    results = engine.search("volcanic rock")
    assert results
    assert results[0].title == "Basalt"


def test_engine_assigns_its_own_sequential_ids(tmp_path):
    path = write_jsonl(tmp_path / "corpus.jsonl", RECORDS)
    engine = SearchEngine()
    load_into(engine, path)
    # file ids are 10..12; the engine numbers from zero
    assert engine.get_document(0).title == "Whales"
    assert engine.get_document(2).title == "Basalt"
    assert engine.get_document(10) is None


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_into(SearchEngine(), tmp_path / "nope.jsonl.gz")
