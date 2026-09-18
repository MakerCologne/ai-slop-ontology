"""Tests for hard gates (Issue #118: Gates statt Score für Binärsignale).

Gates are binary: FAIL = hard marking, PASS = nothing. They never
contribute to slop_score and never fire fp-guards.
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"))

import gates  # noqa: E402

CODE = """\
import os
API_KEY = "your-api-key"
def run():
    data = load()
    # ... rest of implementation
    return data
"""

HTML = """\
<!DOCTYPE html>
<html><body>
<h1>Lorem ipsum dolor sit amet</h1>
<a href="#">Click here</a>
<img src="https://via.placeholder.com/600x400" alt="hero">
</body></html>
"""

PROSE_CLEAN = (
    "Der Bericht wurde im Mai fertiggestellt und geprüft. "
    "Zwölf Personen nahmen an der Studie teil. "
    "Die Ergebnisse sind in Tabelle 3 zusammengefasst."
)


def test_placeholder_credentials_fails_on_code():
    r = gates.run_gates(CODE, force=True)
    by_id = {g["id"]: g["status"] for g in r["gates"]}
    assert by_id.get("placeholder_credentials") == "fail"
    assert r["failed"] >= 1


def test_elision_comment_fails():
    r = gates.run_gates(CODE, force=True)
    by_id = {g["id"]: g["status"] for g in r["gates"]}
    assert by_id.get("elision_comments") == "fail"


def test_markup_gates_fire_on_html():
    r = gates.run_gates(HTML)  # auto: markup detected
    by_id = {g["id"]: g["status"] for g in r["gates"]}
    assert by_id.get("lorem_ipsum") == "fail"
    assert by_id.get("dead_anchor") == "fail"
    assert by_id.get("placeholder_image") == "fail"


def test_code_gates_autorun_on_code_like_input():
    r = gates.run_gates(CODE)  # no force; code detected
    ids = {g["id"] for g in r["gates"]}
    assert "placeholder_credentials" in ids


def test_prose_passes_all_text_scope_gates():
    r = gates.run_gates(PROSE_CLEAN)  # text-scope gates only
    assert r["failed"] == 0


def test_prose_no_code_gates_without_force():
    r = gates.run_gates(PROSE_CLEAN)
    ids = {g["id"] for g in r["gates"]}
    assert "placeholder_credentials" not in ids
    # force exposes them as pass
    r2 = gates.run_gates(PROSE_CLEAN, force=True)
    assert all(g["status"] == "pass" for g in r2["gates"])


def test_gate_fail_carry_evidence():
    r = gates.run_gates(CODE, force=True)
    for g in r["gates"]:
        if g["status"] == "fail":
            assert g["evidence"]
            assert g["hits"] >= 1


def test_scorer_cli_json_contains_gates_no_score_change(tmp_path):
    f = tmp_path / "sample.py"
    f.write_text(CODE)
    out = subprocess.run(
        [sys.executable, os.path.join(
            os.path.dirname(__file__), "..", "skills",
            "ai-slop-detection", "scripts", "slop_scorer.py"),
         "--json", "--file", str(f)],
        capture_output=True, text=True, check=True)
    result = json.loads(out.stdout)
    assert "gates" in result
    by_id = {g["id"]: g["status"] for g in result["gates"]["gates"]}
    assert by_id.get("placeholder_credentials") == "fail"
    # gates are not a dimension: no dimension key may reference them
    assert "gates" not in result["dimension_scores"]


def test_gates_never_change_slop_score(tmp_path):
    """Gates must be score-neutral: same text, --gates on/off."""
    scorer = os.path.join(
        os.path.dirname(__file__), "..", "skills",
        "ai-slop-detection", "scripts", "slop_scorer.py")
    f = tmp_path / "sample.py"
    f.write_text(CODE)
    s1 = json.loads(subprocess.run(
        [sys.executable, scorer, "--json", "--file", str(f)],
        capture_output=True, text=True, check=True).stdout)
    s2 = json.loads(subprocess.run(
        [sys.executable, scorer, "--json", "--gates", "--file", str(f)],
        capture_output=True, text=True, check=True).stdout)
    assert s1["slop_score"] == s2["slop_score"]
