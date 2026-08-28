#!/usr/bin/env python3
"""
Issue #104, Slice A — Doku<->SSOT-Gate (Gate 3 in scripts/verify.sh).

Der SSOT ist ontology.json. Die Detection-Referenz des Skills
(skills/ai-slop-detection/references/detection-signals.md) fasst die
Text-Signale fuer den LLM-Pfad zusammen — wenn sie vom SSOT abdriftet,
beschreibt sie Signale, die die Engine gar nicht kennt (oder umgekehrt).
Der Parity-Gedanke aus #49/#88, hier fuer die Dokumentation:

  D1  Jede Phrase, die die Doku in den Abschnitten "Buzzword Detection"
      und "Template Phrases" nennt, muss im SSOT existieren
      (Buzzword-Tiers, Phrase-Kategorien oder TypePattern-Muster —
      Normalisierung: kleingeschrieben, [X] -> [x]).

  D2  Rueckrichtung: Jede gepinnte SSOT-Kategorie muss in der Doku
      vertreten sein — mindestens ein Item der Kategorie muss in der
      Doku nennet werden. Gepinnt sind die Kategorien, die der
      Template-Phrases-Abschnitt der Doku konzeptuell abdeckt
      (hedging_qualifiers, generic_transitions, opening_formulas) und
      die vier Buzzword-Tiers.

Bewusst NICHT im Gate (dokumentierte Abweichungen, siehe
SSOT_REGISTER/ALLOWLIST in scripts/check_ssot.py): die korpus-
kalibrierten Batch-F-Listen der Skill-Skripte und die
engine-seitigen MORAL_PATTERNS — sie sind als deviation registriert
und leben absichtlich nicht im SSOT.

Offline, kein Netzwerk. Exit 1 bei Drift.
Run:  python3 scripts/check_doc_signals.py
"""

import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DOC = os.path.join(ROOT, "skills", "ai-slop-detection",
                   "references", "detection-signals.md")
ONTOLOGY = os.path.join(ROOT, "ontology.json")

# D2: SSOT-Kategorien, die die Doku abdecken muss (mind. 1 Item nennet).
PINNED_PHRASE_CATEGORIES = [
    "hedging_qualifiers",
    "generic_transitions",
    "opening_formulas",
]
PINNED_BUZZWORD_TIERS = [
    "tier1_critical",
    "tier2_high",
    "tier3_moderate",
    "tier4_weak",
]


def _norm(phrase: str) -> str:
    return phrase.strip().lower().replace("[x]", "[x]")


def _doc_section(text: str, heading: str, stop_headings: list) -> str:
    """Rohtext einer '### <heading>'-Sektion bis zur naechsten ueberschrift."""
    m = re.search(rf"^### {re.escape(heading)}[^\n]*\s*$", text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    stop = re.compile(r"^###+ ", re.M)
    nxt = stop.search(rest)
    return rest[:nxt.start()] if nxt else rest


def _extract_doc_terms() -> dict:
    """{abschnitt: [terme]} aus der Detection-Referenz."""
    with open(DOC, encoding="utf-8") as fh:
        text = fh.read()
    terms = {"buzzwords": [], "template_phrases": []}

    buzz = _doc_section(text, "Buzzword Detection", [])
    # Tier-Zeilen: "**Tier N** (...): w1, w2, w3" — Komma-Liste bis
    # Zeilenende; Bindestrich-Formen bleiben ganz.
    for line in buzz.splitlines():
        m = re.match(r"\*\*Tier \d+\*\*\s*\(.*?\):\s*(.+)$", line.strip())
        if m:
            terms["buzzwords"] += [
                t.strip() for t in m.group(1).split(",") if t.strip()]

    tpl = _doc_section(text, "Template Phrases", [])
    m = re.search(r'^"(.+?)"\s*$', tpl, re.M | re.S)
    if m:
        terms["template_phrases"] = [
            t.strip() for t in m.group(1).split('", "') if t.strip()]
    return terms


def _ssot_universe(ontology: dict) -> dict:
    text = ontology["signals"]["text"]
    buzzwords = set()
    for tier in text["buzzwords"]["tiers"].values():
        buzzwords |= {_norm(w) for w in tier["words"]}
    phrases = set()
    by_category = {}
    for cat, data in text["phrases"]["categories"].items():
        items = {_norm(p) for p in data.get("items", [])}
        phrases |= items
        by_category[cat] = items
    type_patterns = set()
    for tdef in text.get("typePatterns", {}).get("types", {}).values():
        type_patterns |= {_norm(p) for p in tdef.get("patterns", [])}
    return {
        "buzzwords": buzzwords,
        "phrases": phrases,
        "phrases_by_category": by_category,
        "type_patterns": type_patterns,
        "tiers": {name: {_norm(w) for w in tier["words"]}
                  for name, tier in text["buzzwords"]["tiers"].items()},
    }


def main() -> int:
    with open(ONTOLOGY, encoding="utf-8") as fh:
        ontology = json.load(fh)
    ssot = _ssot_universe(ontology)
    doc_terms = _extract_doc_terms()
    doc_all = {_norm(t) for terms in doc_terms.values() for t in terms}
    doc_text_blob = " ".join(doc_all)

    errors = []
    checked_d1 = 0

    # --- D1: jede Doku-Phrase muss im SSOT existieren ------------------
    for section, universe in (
            ("buzzwords", ssot["buzzwords"]),
            ("template_phrases", ssot["phrases"] | ssot["type_patterns"])):
        for term in doc_terms[section]:
            checked_d1 += 1
            if _norm(term) not in universe:
                errors.append(
                    f"D1 FAIL: '{term}' ({section}) steht in der Doku, "
                    "fehlt aber im SSOT (ontology.json: Buzzword-Tiers, "
                    "Phrase-Kategorien, TypePatterns) — Phrase im SSOT "
                    "nachziehen oder aus der Doku entfernen.")

    # --- D2: jede gepinnte Kategorie muss in der Doku vertreten sein ---
    for cat in PINNED_PHRASE_CATEGORIES:
        items = ssot["phrases_by_category"].get(cat, set())
        represented = items & doc_all
        if not represented:
            errors.append(
                f"D2 FAIL: SSOT-Kategorie '{cat}' hat kein einziges in der "
                "Doku vertretenes Item — Doku (Template Phrases) oder Pin "
                "in scripts/check_doc_signals.py pflegen.")
    for tier in PINNED_BUZZWORD_TIERS:
        items = ssot["tiers"].get(tier, set())
        represented = items & doc_all
        if not represented:
            errors.append(
                f"D2 FAIL: Buzzword-Tier '{tier}' hat kein einziges in der "
                "Doku (Buzzword Detection) vertretenes Item.")

    # Self-Check: das Gate hat wirklich etwas geprueft (kein stiller
    # No-Op, falls sich die Doku-Struktur aendert).
    if checked_d1 < 10:
        errors.append(
            f"GATE FAIL: nur {checked_d1} Doku-Terme extrahiert — "
            "Abschnitts-Parser in _extract_doc_terms pruefen (Struktur "
            "der detection-signals.md hat sich geaendert?).")

    if errors:
        print("Doc-SSOT check FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"Doc-SSOT check passed (D1: {checked_d1} Doku-Terme im SSOT "
          f"gegegenprueft; D2: {len(PINNED_PHRASE_CATEGORIES)} Phrase-"
          f"Kategorien + {len(PINNED_BUZZWORD_TIERS)} Buzzword-Tiers in "
          "der Doku vertreten).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
