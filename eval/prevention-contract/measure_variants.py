#!/usr/bin/env python3
"""L2 'Prevention Contract' (#232 / P5): Strukturvarianten-Messung.

Misst je Variante (Text je Gattung/Anlass) die Pruefkriterien C1-C7 und
berechnet paarweise Musterabstaende fuer C8 (strukturelle vs. lexikalische
Varianz). Nutzbar als Erstmessung und als Quartals-L3-Re-Score-Harness.

Input:  JSONL mit {"genre": ..., "variant": ..., "text": ...}
Output: je Variante Kriterienvektor + je Gattung paarweise Distanzen (stdout/JSON)

C8-Regel: Distanz unter Schwelle (default 1.0 Einheiten) = 'nur lexikalisch
variiert' -> FAIL der Variante (E6).
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "skills" / "ai-slop-detection" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from rhetorical_patterns import find_rhetorical_patterns  # noqa: E402
from rhythm_openers import rhythm_metrics  # noqa: E402

_ANNOUNCE = ("OpenerAnnouncement",)
_TRIADS = ("ForcedTriad", "DecorativeSeparatorTriad")
_ENGAGEMENT = ("engagement_comment_default",)

_ICH_APPROACH = ("ich moechte", "ich möchte", "ich wollte", "ich denke",
                 "ich finde", "ich glaube", "ich ", "ich-")
# Haltungs-Verben sind Inhalt, kein Anlauf (Arjan: 'Ich' erlaubt, wenn Haltung relevant)
_STANCE_OK = ("widerspreche", "bezweifle", "empfehle", "halte", "lehne", "stehe")
_JUSTIFICATION = ("weil", "denn", "grund", "belegt", "belegen", "laut", "deshalb")


def _sentences(text: str) -> list[str]:
    import re
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def criteria_vector(text: str) -> dict:
    sents = _sentences(text)
    first = (sents[0] or "").lower() if sents else ""
    rhy = rhythm_metrics(text)
    pats = {p["id"] for p in find_rhetorical_patterns(text)}
    paragraphs = [p for p in text.split("\n\n") if p.strip()]

    c1 = (first.startswith(_ICH_APPROACH) and not any(m in first for m in _JUSTIFICATION)
          and not any(v in first for v in _STANCE_OK))
    c2 = any(p in pats for p in _ANNOUNCE) and first.startswith(("spannender", "interessanter", "wichtiger beitrag", "danke"))
    c3 = " paraphrase" in "" or any(p in pats for p in _ENGAGEMENT)
    c4 = any(p in pats for p in _ANNOUNCE)
    c5 = any(p in pats for p in _TRIADS) or "RoboticRhythm" in pats
    c6 = rhy.get("paragraph_connector_rate", 0.0) > 0.5
    questions = [s for s in sents if s.rstrip().endswith("?")]
    c7 = len(questions) > 1 and not questions[-1].rstrip().endswith(("?", "!"))
    c7 = len(questions) > 2  # mehr als zwei Fragen je Text gilt als Hook-Verdacht (heuristisch)
    return {
        "C1_ich_opener": c1, "C2_lob_first": c2, "C3_engagement_seq": c3,
        "C4_announce_frame": c4, "C5_triad": c5, "C6_connector_rate": c6,
        "C7_question_hook": c7,
        "isometry_run": rhy.get("max_uniform_length_run", 0),
        "opener_share": rhy.get("top_opener_share", 0.0),
        "connector_rate": rhy.get("paragraph_connector_rate", 0.0),
        "signals": sorted(pats),
    }


def distance(a: dict, b: dict) -> float:
    keys = ("C1_ich_opener", "C2_lob_first", "C3_engagement_seq", "C4_announce_frame",
            "C5_triad", "C6_connector_rate", "C7_question_hook")
    d = sum(1 for k in keys if a[k] != b[k])
    d += abs(a["opener_share"] - b["opener_share"]) >= 0.15
    d += abs(a["connector_rate"] - b["connector_rate"]) >= 0.2
    return float(d)


def measure(jsonl_path: Path, c8_threshold: float = 1.0) -> dict:
    entries = [json.loads(l) for l in jsonl_path.read_text().splitlines() if l.strip()]
    by_genre: dict[str, list[dict]] = {}
    for e in entries:
        vec = criteria_vector(e["text"])
        vec.update({"genre": e["genre"], "variant": e["variant"], "text_len": len(e["text"])})
        by_genre.setdefault(e["genre"], []).append(vec)
    pairs = {}
    for genre, vecs in by_genre.items():
        for (i, a), (j, b) in itertools.combinations(enumerate(vecs), 2):
            d = distance(a, b)
            pairs[f"{genre}:{a['variant']}-{b['variant']}"] = {
                "distance": d,
                "verdict": "OK" if d >= c8_threshold else "E6_LEXICAL_VARIANT",
            }
    return {"variants": {f"{v['genre']}:{v['variant']}": v for vs in by_genre.values() for v in vs}, "pairs": pairs}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", type=Path)
    ap.add_argument("--c8-threshold", type=float, default=1.0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = measure(args.jsonl, args.c8_threshold)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for key, v in result["variants"].items():
            flags = [k for k in v if k.startswith("C") and v[k] is True]
            print(f"{key}: {'FEHLER:' + ','.join(flags) if flags else 'OK'}  signals={v['signals'] or '-'}")
        for key, p in result["pairs"].items():
            print(f"  paar {key}: distanz={p['distance']} {p['verdict']}")


if __name__ == "__main__":
    main()
