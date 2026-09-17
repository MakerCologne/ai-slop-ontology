#!/usr/bin/env python3
"""
Issue #116 — Gate: signalReliability + UI-Tells-Register.

Validiert:
  - ontology.json enthaelt signalReliability mit schema/rules/entries
  - jedes Entry: reliability/status in Enum, last_verified ISO-Datum,
    false_positives Pflicht bei reliability == weak
  - lexikon/ui-tells.yaml: Attribution (CC BY-SA 4.0 + Quell-Repo)
    und gleiche Enum-/FP-Regeln je Eintrag

Run:  python3 scripts/check_signal_reliability.py
"""

import datetime
import json
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []

RELIABILITY = {"strong", "moderate", "weak"}
STATUS = {"current", "fading", "obsolete"}


def check(cond: bool, msg: str):
    if not cond:
        errors.append(msg)


def iso_date_ok(s: str) -> bool:
    try:
        datetime.date.fromisoformat(s)
        return True
    except (TypeError, ValueError):
        return False


def validate_entry(sid: str, e: dict, where: str):
    check(e.get("reliability") in RELIABILITY,
          f"{where}[{sid}]: reliability fehlt/ungueltig: {e.get('reliability')!r}")
    check(e.get("status") in STATUS,
          f"{where}[{sid}]: status fehlt/ungueltig: {e.get('status')!r}")
    check(iso_date_ok(e.get("last_verified")),
          f"{where}[{sid}]: last_verified kein ISO-Datum: {e.get('last_verified')!r}")
    if e.get("reliability") == "weak":
        check(bool(e.get("false_positives")),
              f"{where}[{sid}]: weak erfordert false_positives (Regel weakRequiresFP)")


def main() -> int:
    with open(os.path.join(ROOT, "ontology.json"), encoding="utf-8") as f:
        o = json.load(f)

    sr = o.get("signalReliability")
    check(isinstance(sr, dict), "ontology.json: signalReliability-Block fehlt (#116)")
    if isinstance(sr, dict):
        for key in ("schema", "rules", "entries"):
            check(key in sr, f"signalReliability.{key} fehlt")
        check(iso_date_ok(sr.get("lastUpdated")),
              "signalReliability.lastUpdated kein ISO-Datum")
        entries = sr.get("entries") or {}
        check(len(entries) > 0, "signalReliability.entries ist leer")
        for sid, e in entries.items():
            validate_entry(sid, e, "signalReliability.entries")

    ui_path = os.path.join(ROOT, "lexikon", "ui-tells.yaml")
    check(os.path.isfile(ui_path), "lexikon/ui-tells.yaml fehlt (#116 UI-Achse)")
    if os.path.isfile(ui_path):
        with open(ui_path, encoding="utf-8") as f:
            ui = yaml.safe_load(f)
        meta = (ui or {}).get("meta") or {}
        check("CC BY-SA 4.0" in str(meta.get("source_license", "")),
              "ui-tells.yaml: source_license muss CC BY-SA 4.0 nennen (Attribution)")
        check("signs-of-ai-design" in str(meta.get("source_repo", "")),
              "ui-tells.yaml: source_repo muss signs-of-ai-design nennen")
        entries = (ui or {}).get("entries") or []
        check(len(entries) > 0, "ui-tells.yaml: entries leer")
        for e in entries:
            validate_entry(e.get("id", "?"), e, "ui-tells.entries")

    if errors:
        print("CHECK SIGNAL RELIABILITY: FAIL")
        for e in errors:
            print("  -", e)
        return 1
    print("CHECK SIGNAL RELIABILITY: OK "
          f"(ontology {len(sr.get('entries', {})) if sr else 0}, "
          f"ui {len((ui or {}).get('entries', []) if isinstance(ui, dict) else 0)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
