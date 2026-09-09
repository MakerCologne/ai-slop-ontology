"""Tests for scripts/calibration_drift.py (issue #47).

Covers: reference build, clean self-check, each drift type
(percotted shift, signal-rate shift, fixture missing/unknown/text
changed), and threshold passthrough via CLI defaults.
"""

import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "calibration_drift.py")


def _write_corpus(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


def _run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args],
                          capture_output=True, text=True)


SLOP_TEXT = ("In today's rapidly evolving digital landscape, it's important "
             "to note that the rich tapestry of AI tools serves as a "
             "testament to innovation — let's dive in and delve into the "
             "nuances that game-changers bring to the table.")
SLOP_TEXT_2 = ("Whether you're a seasoned developer or just starting out, "
               "this comprehensive guide delves into the realm of "
               "cutting-edge solutions — a testament to innovation.")


def _corpus_items():
    return [
        {"id": "s1", "label": "slop", "text": SLOP_TEXT},
        {"id": "s2", "label": "slop", "text": SLOP_TEXT_2},
        {"id": "c1", "label": "clean",
         "text": "The meeting ran long. We fixed two bugs and shipped."},
        {"id": "c2", "label": "clean",
         "text": "Ich habe gestern das Fahrrad repariert und Brot gekauft."},
    ]


@pytest.fixture()
def workspace(tmp_path):
    corpus = tmp_path / "corpus.jsonl"
    _write_corpus(corpus, _corpus_items())
    ref = tmp_path / "ref.json"
    r = _run("--init", "--corpus", str(corpus), "--reference", str(ref))
    assert r.returncode == 0, r.stderr
    return tmp_path, corpus, ref


def test_init_writes_reference(workspace):
    _, corpus, ref = workspace
    data = json.loads(ref.read_text())
    assert data["schema"] == 1
    assert set(data["fixtures"]) == {"s1", "s2", "c1", "c2"}
    assert data["labels"]["slop"]["distribution"]["n"] == 2
    assert data["labels"]["clean"]["distribution"]["n"] == 2
    assert "text_sha256" in data["fixtures"]["s1"]
    assert data["thresholds"]["score_percentile_shift"] == 0.05
    assert data["thresholds"]["signal_rate_shift"] == 0.10


def test_check_passes_without_drift(workspace):
    _, corpus, ref = workspace
    r = _run("--check", "--corpus", str(corpus), "--reference", str(ref))
    assert r.returncode == 0
    assert "passed" in r.stdout


def test_score_percentile_shift_alerts(workspace):
    _, corpus, ref = workspace
    data = json.loads(ref.read_text())
    for fid, f in data["fixtures"].items():
        if f["label"] == "slop":
            f["slop_score"] = max(0.0, f["slop_score"] - 0.2)
    # committed percentiles must follow the fixture scores
    ref.write_text(json.dumps(data))
    r = _run("--check", "--corpus", str(corpus), "--reference", str(ref))
    # reference fixture scores moved; current re-score unmoved → shift
    assert r.returncode == 1
    assert any("score_percentile_shift" in line or "score_drift" in line
               or "percentile" in line
               for line in r.stdout.splitlines()), r.stdout


def test_signal_rate_shift_alerts(workspace):
    _, corpus, ref = workspace
    data = json.loads(ref.read_text())
    # drop a signal from the slop hit-rate table → current has it → delta
    rates = data["labels"]["slop"]["signal_hit_rates"]
    assert rates, "reference should contain slop signal rates"
    victim = max(rates, key=rates.get)
    del rates[victim]
    ref.write_text(json.dumps(data))
    r = _run("--check", "--corpus", str(corpus), "--reference", str(ref))
    assert r.returncode == 1
    assert any("signal_rate_shift" in line for line in r.stdout.splitlines())


def test_fixture_missing_alerts(workspace):
    _, corpus, ref = workspace
    items = _corpus_items()[:-1]  # remove c2
    _write_corpus(corpus, items)
    r = _run("--check", "--corpus", str(corpus), "--reference", str(ref))
    assert r.returncode == 1
    assert any("fixture_missing" in line for line in r.stdout.splitlines())


def test_fixture_unknown_alerts(workspace):
    _, corpus, ref = workspace
    items = _corpus_items() + [{
        "id": "new-1", "label": "clean", "text": "Neuer Satz ohne Bezug."}]
    _write_corpus(corpus, items)
    r = _run("--check", "--corpus", str(corpus), "--reference", str(ref))
    assert r.returncode == 1
    assert any("fixture_unknown" in line for line in r.stdout.splitlines())


def test_fixture_text_changed_alerts(workspace):
    _, corpus, ref = workspace
    items = _corpus_items()
    items[0]["text"] = SLOP_TEXT + " Edited."
    _write_corpus(corpus, items)
    r = _run("--check", "--corpus", str(corpus), "--reference", str(ref))
    assert r.returncode == 1
    assert any("fixture_text_changed" in line
               for line in r.stdout.splitlines())


def test_no_auto_tuning_note(workspace):
    """Alert is a review trigger, not auto-tuning — stated in the note."""
    _, _, ref = workspace
    data = json.loads(ref.read_text())
    assert "NOT auto-tuning" in data["note"]
