"""#98-Zielstand — Runner + Korpus-Disziplin für eval/human_ideological.jsonl."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, "eval", "run_human_ideological.py")
CORPUS = os.path.join(ROOT, "eval", "human_ideological.jsonl")


def _load():
    with open(CORPUS, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def test_runner_passes_on_target_corpus():
    proc = subprocess.run(
        [sys.executable, RUNNER, "--json"], capture_output=True, text=True)
    assert proc.returncode == 0, f"Runner rot:\n{proc.stdout}\n{proc.stderr}"
    report = json.loads(proc.stdout)
    assert report["integrity"] == "PASS"
    assert report["leak_check"] == "PASS"
    assert report["rhetoric"]["pass"] is True
    assert report["pos"] >= 40 and report["neg"] >= 40


def test_corpus_target_40_40_and_segments():
    rows = _load()
    pos = [r for r in rows if r["label"] == "slop"]
    neg = [r for r in rows if r["label"] == "hard_negative"]
    assert len(pos) >= 40 and len(neg) >= 40
    segments = {
        "Ritual-Brandmauer": {"RitualFirewall"},
        "Kollektivframe": {"CollectiveOther", "ReplacementKicker"},
        "Purity-Kette": {"PurityBan", "VibeScapegoat"},
        "Salvation-Kette": {"SalvationModel", "MartyrCartel"},
        "Ethnopluralismus-Rebrand": {"EthnopluralistRebrand"},
    }
    for name, sigs in segments.items():
        n = sum(1 for r in pos if r["signal"] in sigs)
        assert n >= 8, f"Segment {name}: nur {n} < 8"


def test_corpus_discipline_no_third_party_texts():
    for r in _load():
        assert r["source"] == "own:handwritten", r["id"]
        assert r["text"].strip() == r["text"], r["id"]


def test_leak_check_every_positive_has_structure_feature():
    for r in _load():
        if r["label"] == "slop":
            feats = r.get("features") or []
            assert any(f.startswith("structure:") for f in feats), (
                f"{r['id']}: positives Merkmal darf nicht allein eine Phrase sein (#98)")
