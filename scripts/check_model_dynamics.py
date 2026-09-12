#!/usr/bin/env python3
"""
Issue #36 — Modell-Dynamik-Gate: signalModelDynamics in ontology.json.

Offline gate (no network, no API). Fails with exit 1 on any violation:

  M1  Block existiert und hat version/lastUpdated/source/note/schema/
      rules/modelNotes/halfLives.

  M2  modelNotes-Eintraege: model ist nicht-leerer String, effect in
      {weaker, stronger, absent, only_model}, evidence nicht-leer (Pflicht),
      asOf matcht YYYY-Q[1-4].

  M3  halfLives-Eintraege: quarters ist int > 0, rationale nicht-leer,
      reviewed_on ist ISO-8601 Datum.

  M4  Jeder Signalname in modelNotes/halfLives ist ein bekanntes Signal:
      er muss in signalSeverity.tiers, collisionMatrix oder den
      signals-Registern (signals.*) vorkommen.

  M5  Signals mit model_notes effect in {weaker, absent, only_model}
      brauchen einen halfLives-Eintrag (Review-Kadenz ist der Punkt des
      Registers — ohne Halbwertszeit keine Befristung).

Run:  python3 scripts/check_model_dynamics.py
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = Path(os.environ.get("ONT_MODEL_DYNAMICS_ONTOLOGY",
                               ROOT / "ontology.json"))

EFFECTS = {"weaker", "stronger", "absent", "only_model"}
AS_OF = re.compile(r"^\d{4}-Q[1-4]$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_KEYS = ["version", "lastUpdated", "source", "note", "schema",
                 "rules", "modelNotes", "halfLives"]


def known_signal_names(data: dict) -> set:
    names = set()

    sev = data.get("signalSeverity", {})
    tiers = sev.get("tiers", {}) if isinstance(sev, dict) else {}
    if isinstance(tiers, dict):
        for tier in tiers.values():
            if isinstance(tier, dict):
                names.update(tier.get("signals", []))

    coll = data.get("collisionMatrix", {})
    if isinstance(coll, dict):
        matrix = coll.get("matrix", coll)
        if isinstance(matrix, dict):
            for k, v in matrix.items():
                names.add(k)
                if isinstance(v, dict):
                    names.update(v.get("collidesWith", []))
                    names.update(v.get("priority", []) if isinstance(v.get("priority"), list) else [])

    signals = data.get("signals", {})
    if isinstance(signals, dict):
        for medium in signals.values():
            if isinstance(medium, dict):
                for sig in medium.keys():
                    if sig not in {"description", "note"}:
                        names.add(sig)
                # nested signal objects may list individual indicators
                for entry in medium.values():
                    if isinstance(entry, dict) and "telltale" in entry:
                        pass  # concept names live in tier lists, not here
    return names


def main() -> int:
    failures = []
    data = json.loads(ONTOLOGY.read_text(encoding="utf-8"))

    md = data.get("signalModelDynamics")
    if not isinstance(md, dict):
        print("M1 FAIL: signalModelDynamics fehlt in ontology.json")
        return 1
    for key in REQUIRED_KEYS:
        if key not in md:
            failures.append(f"M1: Schlüssel '{key}' fehlt")

    known = known_signal_names(data)

    for signal, entries in md.get("modelNotes", {}).items():
        if signal not in known:
            failures.append(f"M4: unbekanntes Signal '{signal}' in modelNotes")
        if not isinstance(entries, list) or not entries:
            failures.append(f"M2: modelNotes['{signal}'] muss nicht-leere Liste sein")
            continue
        for e in entries:
            model = e.get("model", "")
            effect = e.get("effect", "")
            evidence = e.get("evidence", "")
            as_of = e.get("asOf", "")
            if not isinstance(model, str) or not model.strip():
                failures.append(f"M2: modelNotes['{signal}'] model leer")
            if effect not in EFFECTS:
                failures.append(f"M2: modelNotes['{signal}'] effect '{effect}' nicht in {sorted(EFFECTS)}")
            if not isinstance(evidence, str) or not evidence.strip():
                failures.append(f"M2: modelNotes['{signal}'] evidence fehlt (Pflicht)")
            if not AS_OF.match(as_of or ""):
                failures.append(f"M2: modelNotes['{signal}'] asOf '{as_of}' matcht nicht YYYY-Q[1-4]")

    for signal, entry in md.get("halfLives", {}).items():
        if signal not in known:
            failures.append(f"M4: unbekanntes Signal '{signal}' in halfLives")
        quarters = entry.get("quarters")
        if not isinstance(quarters, int) or isinstance(quarters, bool) or quarters <= 0:
            failures.append(f"M3: halfLives['{signal}'] quarters muss int > 0 sein (ist {quarters!r})")
        rationale = entry.get("rationale", "")
        if not isinstance(rationale, str) or not rationale.strip():
            failures.append(f"M3: halfLives['{signal}'] rationale fehlt")
        reviewed = entry.get("reviewed_on", "")
        if not ISO_DATE.match(reviewed or ""):
            failures.append(f"M3: halfLives['{signal}'] reviewed_on '{reviewed}' ist kein ISO-8601 Datum")

    hot_effects = {"weaker", "absent", "only_model"}
    for signal, entries in md.get("modelNotes", {}).items():
        effects = {e.get("effect") for e in entries if isinstance(e, dict)}
        if effects & hot_effects and signal not in md.get("halfLives", {}):
            failures.append(f"M5: '{signal}' hat volatile model_notes (weaker/absent/only_model) "
                            f"aber keinen halfLives-Eintrag")

    if failures:
        for f in failures:
            print(f"FAIL {f}")
        return 1
    n_notes = sum(len(v) for v in md.get("modelNotes", {}).values())
    print(f"signalModelDynamics ok: {n_notes} model_notes / "
          f"{len(md.get('halfLives', {}))} halfLives geprüft")
    return 0


if __name__ == "__main__":
    sys.exit(main())
