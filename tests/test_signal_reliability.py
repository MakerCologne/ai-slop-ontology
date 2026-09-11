"""Issue #116 — Tests: signalReliability-Block + UI-Tells-Register."""

import datetime
import json
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RELIABILITY = {"strong", "moderate", "weak"}
STATUS = {"current", "fading", "obsolete"}


def ontology():
    with open(os.path.join(ROOT, "ontology.json"), encoding="utf-8") as f:
        return json.load(f)


def ui_tells():
    with open(os.path.join(ROOT, "lexikon", "ui-tells.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_signal_reliability_block_exists():
    sr = ontology()["signalReliability"]
    assert sr["source"].startswith("#116")
    for key in ("schema", "rules", "entries"):
        assert key in sr


def test_entries_validate_schema():
    sr = ontology()["signalReliability"]
    assert sr["entries"], "Starter-Einträge fehlen"
    for sid, e in sr["entries"].items():
        assert e["reliability"] in RELIABILITY, sid
        assert e["status"] in STATUS, sid
        datetime.date.fromisoformat(e["last_verified"])  # wirft bei Verstoß
        if e["reliability"] == "weak":
            assert e.get("false_positives"), f"{sid}: weak ohne false_positives"


def test_confidence_mapping_rule_is_documented():
    sr = ontology()["signalReliability"]
    m = sr["reliabilityFromConfidence"]["mapping"]
    assert "0.85" in m and "0.6" in m


def test_ui_tells_attribution():
    ui = ui_tells()
    meta = ui["meta"]
    assert "CC BY-SA 4.0" in meta["source_license"]
    assert "signs-of-ai-design" in meta["source_repo"]


def test_ui_tells_entries_validate():
    entries = ui_tells()["entries"]
    assert len(entries) >= 10
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids)), "dupe IDs"
    for e in entries:
        assert e["reliability"] in RELIABILITY, e["id"]
        assert e["status"] in STATUS, e["id"]
        if e["reliability"] == "weak":
            assert e.get("false_positives"), f"{e['id']}: weak ohne false_positives"


def test_ui_tells_exclude_image_artifacts_scope():
    """UI-Tells sind Design-Defaults, keine Bild-Artefakte (Abgrenzung signals.image)."""
    ids = [e["id"] for e in ui_tells()["entries"]]
    assert not any(i.startswith("Extra") or "Limbs" in i for i in ids)
