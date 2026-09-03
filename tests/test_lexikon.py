"""Tests for the Lexikon pilot (issue #50): schema-first SSOT + build.

SSOT rule: only lexikon/entries/*.yaml is hand-edited; everything under
lexikon/dist/ is a build artifact (tests enforce dist == rebuild).
"""

import json
import os
import subprocess
import sys
import tempfile

import pytest
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEXIKON = os.path.join(ROOT, "lexikon")
ENTRIES_DIR = os.path.join(LEXIKON, "entries")
DIST = os.path.join(LEXIKON, "dist")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_lexikon  # noqa: E402


def load_entries():
    out = {}
    for fn in sorted(os.listdir(ENTRIES_DIR)):
        if fn.endswith(".yaml"):
            with open(os.path.join(ENTRIES_DIR, fn)) as f:
                out[fn] = yaml.safe_load(f)
    return out


def build_to(tmpdir):
    rc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "build_lexikon.py"),
         "--out", tmpdir],
        capture_output=True, text=True)
    assert rc.returncode == 0, rc.stderr
    return tmpdir


def read_dist(filename):
    with open(os.path.join(DIST, filename)) as f:
        return f.read()


def test_entry_count():
    """#50 Pilot startete mit 5 Einträgen; #126/#128 erweiterten auf 8
    (human-slop, ideological-slop, ethnopluralism)."""
    entries = load_entries()
    assert len(entries) == 8
    assert all(isinstance(v, dict) for v in entries.values())


def test_all_entries_valid_schema():
    schema = json.load(open(os.path.join(LEXIKON, "schema", "entry.schema.json")))
    for fn, entry in load_entries().items():
        errors = build_lexikon.validate_entry(entry, schema)
        assert errors == [], f"{fn}: {errors}"


def test_every_claim_has_source_with_url_quote_and_accessed():
    for fn, entry in load_entries().items():
        claims = entry.get("claims", [])
        assert claims, f"{fn}: entry without claims"
        for claim in claims:
            sources = claim.get("sources", [])
            assert sources, f"{fn}: claim without sources: {claim.get('statement', '')[:50]}"
            for src in sources:
                assert src.get("url", "").startswith("http"), f"{fn}: source without url"
                assert src.get("quote", "").strip(), f"{fn}: source without quote"
                assert src.get("accessed"), f"{fn}: source without accessed date"


def test_status_lifecycle_consistent_with_methodology():
    text = open(os.path.join(ROOT, "docs", "METHODOLOGY.md")).read()
    entries = load_entries()
    for fn, entry in entries.items():
        assert entry["status"] in ("nursery", "beta", "stable"), fn
        assert entry["status"] in text  # lifecycle documented in METHODOLOGY.md


def test_build_deterministic():
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        build_to(a)
        build_to(b)
        fa = sorted(os.listdir(a))
        fb = sorted(os.listdir(b))
        assert fa == fb
        for fn in fa:
            assert open(os.path.join(a, fn)).read() == open(os.path.join(b, fn)).read()


def test_dist_is_in_sync_with_entries():  # Sync-Gate
    assert os.path.isdir(DIST), "dist/ missing — run scripts/build_lexikon.py"
    with tempfile.TemporaryDirectory() as tmp:
        build_to(tmp)
        for fn in sorted(os.listdir(tmp)):
            got = open(os.path.join(tmp, fn)).read()
            assert got == read_dist(fn), f"dist/{fn} is stale — rebuild required"


def test_llms_txt_structure():
    txt = read_dist("llms.txt")
    lines = txt.splitlines()
    assert lines[0].startswith("# ")
    assert any(l.startswith(">") for l in lines)
    entries = load_entries()
    for fn, e in entries.items():
        assert f"[{e['term']}]" in txt, f"llms.txt missing link for {e['term']}"


def test_llms_full_txt_contains_every_claim_quote():
    full = read_dist("llms-full.txt")
    entries = load_entries()
    for fn, e in entries.items():
        assert e["term"] in full
        for claim in e["claims"]:
            for src in claim["sources"]:
                assert src["quote"][:40] in full, f"{fn}: quote missing in llms-full.txt"


def test_content_hash_in_both_views():
    index = read_dist("index.md")
    data = json.loads(read_dist("lexikon.json"))
    hashes = {e["id"]: e["content_hash"] for e in data["entries"]}
    assert len(hashes) == 8  # #50 Pilot (5) + #126/#128 Erweiterung (3)
    for h in hashes.values():
        assert h in index, "content_hash missing from human view (index.md)"


def test_index_md_alphabetical_and_narrative():
    index = read_dist("index.md")
    entries = load_entries()
    terms = [e["term"] for e in entries.values()]
    # section headers, not bare substring (see_also references would match early)
    positions = [index.find("\n## " + t + "\n") for t in sorted(terms)]
    assert all(p >= 0 for p in positions)
    assert positions == sorted(positions), "index.md not alphabetical"
