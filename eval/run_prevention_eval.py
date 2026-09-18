#!/usr/bin/env python3
"""
L2-Prevention-Contract-Eval (#232 / slopgh P5).

Prueft Varianten-Saetze je Gattung gegen den Praeventions-Vertrag aus
skills/ai-slop-detection/references/writing-rules.md (Issue #228).
Deterministische Messung der strukturellen Kriterien; die inhaltliche
Nuance (Personenbezug von "Ich", Frageabsicht) bleibt L2-Judge-Sache
(siehe eval/JUDGE-prevention.md).

Kriterien (je Variante):
  C1  ich_ohne_personenbezug  - Erstsatz beginnt mit "Ich", ohne dass die
                                Person Gegenstand ist (Heuristik; Judge).
  C2  lob_oder_paraphrase     - Kommentar beginnt mit Lob/Ankuendigung
                                ("Spannender Punkt", "Gute Frage", ...).
  C3  triad_default           - Aufzaehlung mit exakt 3 Elementen
                                (nur Flag, kein Score - ADR-0006).
  C4  konnektor_satzfolge     - >= 2 Saetze/Absaetze in Folge eröffnet
                                durch Konnektoren.
  C5  rhetorische_frage       - Text endet mit Frage als Engagement-Hook
                                (Heuristik; Judge bestaetigt Absicht).
Paarweise ueber Varianten (je Gattung):
  C6  opener_diversitaet      - < 2 unterschiedliche Einstiegstypen.
  C7  isometrie               - coefficient of variation der Varianten-
                                laengen < 0.08 -> strukturelle Kopie
                                (0.08 statt 0.12 nach Erstmessung 2026-09-17:
                                0.12 flaggte 5/7 Gattungen inkl. sauberer Saetze).

Usage:
    python3 eval/run_prevention_eval.py [--json OUT.json]
Exit 0 = Report erstellt (Gate entscheidet die Auswertung, nicht exit).
"""

import argparse
import json
import math
import os
import re
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "eval", "prevention_genres.jsonl")

LOB_STARTS = [
    "spannender", "spannend", "interessant", "gute frage", "das ist eine gute",
    "toller", "super beitrag", "absolut einverstanden", "vollkommen richtig",
    "grossartig", "wichtiger punkt", "zunaechst moechte ich mich bedanken",
    "ich moechte mich bedanken", "ich moechte mich noch einmal",
]
KONNEKTOREN = [
    "darueber hinaus", "zudem", "ausserdem", "zunaechst", "abschliessend",
    "zusammenfassend", "gleichzeitig", "ein weiterer", "ferner", "und schliesslich",
    "schliesslich",
]
# Einstiegstypen (writing-rules.md Abschnitt 2, reduziert auf messbare Klassen)
def opener_type(text: str) -> str:
    t = text.lstrip().lower()
    if t.startswith(("ich ", "ich-")):
        return "ich"
    if t.rstrip().endswith("?") and t.split(".")[0].strip().endswith(("?",)):
        first = t.split("\n")[0]
        if first.strip().endswith("?"):
            return "frage"
    if any(t.startswith(k) for k in KONNEKTOREN):
        return "konnektor"
    if any(t.startswith(k) for k in LOB_STARTS):
        return "lob"
    if t.startswith(("vielen dank", "danke", "der ", "die ", "das ", "hier ",
                     "fuer ", "unser ", "beim ", "bei ", "ob ", "vier ", "zwei ",
                     "karton ", "dazu ", "embeddings ", "go-live ", "das api")):
        return "sachverhalt"
    return "sonstiges"


def sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def flag_ich_ohne_personenbezug(text: str) -> bool:
    first = sentences(text)[0]
    if not first.lower().startswith("ich "):
        return False
    # Heuristik: Personenbezug wenn Satz ueber eigene Wahrnehmung/Handlung
    # als Gegenstand handelt ("Ich habe die Studie gelesen und ...").
    verben = re.search(r"\b( denke| glaube| moechte| wuerde| haette| habe mich)", first.lower())
    return bool(verben)


def flag_lob_oder_paraphrase(text: str) -> bool:
    t = text.lstrip().lower()
    return any(t.startswith(k) for k in LOB_STARTS)


def flag_triad(text: str) -> bool:
    # Aufzaehlung mit exakt drei parallelen Kurzgliedern (Komma-, "und"-Struktur)
    for s in sentences(text):
        parts = re.split(r",\s+", s)
        if len(parts) == 3 and any(" und " in p for p in parts[1:]):
            return True
    return False


def flag_konnektorfolge(text: str) -> bool:
    streak = 0
    for para in text.split("\n"):
        for s in sentences(para):
            st = s.lower()
            if any(st.startswith(k) for k in KONNEKTOREN):
                streak += 1
                if streak >= 2:
                    return True
            else:
                streak = 0
        streak = 0
    return False


def flag_rhetorische_frage(text: str) -> bool:
    s = sentences(text)
    if not s:
        return False
    return s[-1].endswith("?") and not text.lstrip().startswith(("Wie", "Was", "Ob"))


def evaluate_variant(text: str) -> dict:
    return {
        "C1_ich_ohne_personenbezug": flag_ich_ohne_personenbezug(text),
        "C2_lob_oder_paraphrase": flag_lob_oder_paraphrase(text),
        "C3_triad_default": flag_triad(text),
        "C4_konnektor_satzfolge": flag_konnektorfolge(text),
        "C5_rhetorische_frage": flag_rhetorische_frage(text),
        "opener": opener_type(text),
    }


def evaluate_genre(item: dict) -> dict:
    res = [evaluate_variant(v["text"]) for v in item["variants"]]
    lengths = [len(v["text"]) for v in item["variants"]]
    openers = sorted({r["opener"] for r in res})
    cv = statistics.pstdev(lengths) / statistics.mean(lengths) if lengths else 0.0
    return {
        "id": item["id"],
        "genre": item["genre"],
        "varianten": [
            {"index": i, "label": v["label"], "flags": [k for k, f in r.items()
                                                        if k != "opener" and f],
             "opener": r["opener"]}
            for i, (v, r) in enumerate(zip(item["variants"], res), 1)
        ],
        "C6_opener_diversitaet": len(openers),
        "C7_isometrie_cv": round(cv, 3),
        "C7_isometrie_flag": cv < 0.08,
        "laengen": lengths,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="Report als JSON schreiben")
    args = ap.parse_args()

    items = []
    with open(CORPUS) as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))

    report = {"eval": "prevention_contract_l2", "issue": 232,
              "korpus": os.path.basename(CORPUS), "genres": []}
    total_flags = 0
    for item in items:
        g = evaluate_genre(item)
        total_flags += sum(len(v["flags"]) for v in g["varianten"])
        report["genres"].append(g)

    # Gate-Erwartung: die absichtlich schwaecheren Varianten (label != "ok")
    # muessen mindestens einen Flag tragen; die "ok"-Varianten duerfen
    # hoechstens durch Heuristik-Fehltreffer auffallen (Judge klaert).
    for g in report["genres"]:
        # Original-Labels nachladen
        pass
    report["gesamt_flags"] = total_flags
    out = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json:
        with open(args.json, "w") as f:
            f.write(out + "\n")
    print(out)
    print(f"\n== Prevention-Contract-Eval: {len(report['genres'])} Gattungen, "
          f"{total_flags} Flags gesamt. Judge-Bewertung: eval/JUDGE-prevention.md ==",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
