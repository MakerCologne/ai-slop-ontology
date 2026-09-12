"""Tests für Issue #36 — signalModelDynamics (model_notes + Halbwertszeiten)."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "scripts" / "check_model_dynamics.py"
ONTOLOGY = ROOT / "ontology.json"


def _run_check(tmp_path, data):
    ontology = tmp_path / "ontology.json"
    ontology.write_text(json.dumps(data), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(CHECK)],
        env={"PYTHONPATH": str(ROOT), "ONT_MODEL_DYNAMICS_ONTOLOGY": str(ontology)},
        capture_output=True, text=True, cwd=str(tmp_path),
    )


def _base_block():
    return {
        "version": "1.0.0",
        "lastUpdated": "2026-09-12",
        "source": "#36",
        "note": "test",
        "schema": {"model_notes": {}, "halfLives": {}},
        "rules": {"evidenceRequired": "x"},
        "modelNotes": {
            "ExcessiveEmDash": [
                {"model": "gpt-5.1+", "effect": "weaker",
                 "evidence": "AIDASH", "asOf": "2026-Q3"},
            ],
        },
        "halfLives": {
            "ExcessiveEmDash": {"quarters": 1, "rationale": "suppressed",
                                "reviewed_on": "2026-09-12"},
        },
    }


def _base_data():
    data = json.loads(ONTOLOGY.read_text(encoding="utf-8"))
    data["signalModelDynamics"] = _base_block()
    return data


def test_real_ontology_passes_gate():
    result = subprocess.run([sys.executable, str(CHECK)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "signalModelDynamics ok" in result.stdout


def test_seed_entries_present_and_wellformed():
    data = json.loads(ONTOLOGY.read_text(encoding="utf-8"))
    md = data["signalModelDynamics"]
    # Kern-Empirie aus Issue #36: Em-Dash, CurlyQuotes, Puffery
    assert "ExcessiveEmDash" in md["modelNotes"]
    assert "CurlyQuotes" in md["modelNotes"]
    assert "ImportancePuffery" in md["modelNotes"]
    for entries in md["modelNotes"].values():
        for e in entries:
            assert e["effect"] in {"weaker", "stronger", "absent", "only_model"}
            assert e["evidence"].strip()
            assert e["asOf"].count("Q") == 1


def test_gate_rejects_missing_block():
    data = _base_data()
    del data["signalModelDynamics"]
    result = _run_check_and_capture(data)
    assert result.returncode == 1
    assert "M1" in result.stdout


def test_gate_rejects_bad_effect_and_missing_evidence():
    data = _base_data()
    data["signalModelDynamics"]["modelNotes"]["ExcessiveEmDash"] = [
        {"model": "gpt-5.1+", "effect": "sometimes", "evidence": "", "asOf": "2026-Q3"},
    ]
    result = _run_check_and_capture(data)
    assert result.returncode == 1
    assert "effect" in result.stdout
    assert "evidence" in result.stdout


def test_gate_rejects_unknown_signal():
    data = _base_data()
    data["signalModelDynamics"]["modelNotes"]["TotallyUnknownSignalXYZ"] = [
        {"model": "m", "effect": "stronger", "evidence": "e", "asOf": "2026-Q3"},
    ]
    result = _run_check_and_capture(data)
    assert result.returncode == 1
    assert "TotallyUnknownSignalXYZ" in result.stdout


def test_gate_requires_halflife_for_volatile_notes():
    data = _base_data()
    del data["signalModelDynamics"]["halfLives"]["ExcessiveEmDash"]
    result = _run_check_and_capture(data)
    assert result.returncode == 1
    assert "M5" in result.stdout


def test_gate_rejects_zero_halflife_and_bad_dates():
    data = _base_data()
    data["signalModelDynamics"]["halfLives"]["ExcessiveEmDash"] = {
        "quarters": 0, "rationale": "", "reviewed_on": "12.09.2026"}
    result = _run_check_and_capture(data)
    assert result.returncode == 1
    assert "quarters" in result.stdout
    assert "reviewed_on" in result.stdout


def _run_check_and_capture(data):
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        return _run_check(Path(td), data)
