#!/usr/bin/env python3
"""
Diskurs-Metriken (issue #72, explorativ, detect-only).

Explorative Signale auf Diskursartefakte aus dem Markt-Kontext
(research/slop-ontology-gap-2026-08-24/deep/10 + deep/06):

  RankWithoutCriterion   Rangliste mit >= 3 nummerierten Positionen, die
                         KEIN einziges Bewertungskriterium nennt (kein
                         "Grund", "weil", "Kriterium", "because" …).
  IdenticalEnumeration   >= 3 Saetze mit identischem Anfangs-Frame
                         ("No more X. No more Y. No more Z." / "Kein …
                         mehr.") — Aufzaehung als rhetorische Staffage.

EXPLORATIV: beide Signale sind bewusst als explorativ markiert
(``exploratory: True``), Konfidenz <= 0.35, niemals Teil des numerischen
Slop-Scores. Referenzkorpus: eval/discourse_ref.jsonl (versioniert, L4).

Lizenz-Schutz: Konzepte selbst abgeleitet aus den eigenen Deep-Dive-
Notizen (deep/10, deep/06); kurze oeffentliche Zitate nur attribuiert im
Referenzkorpus. Kein Pattern-Material aus CC BY-SA-Katalogen kopiert.

Public surface:
    rank_without_criterion(text) -> finding | None
    identical_enumeration(text) -> finding | None
    find_discourse_findings(text) -> list[finding]
"""

import re

import tokenizer

# Rang-Marker: Zeilen, die mit "1." / "2)" / "3." beginnen.
RANKED_LINE_RE = re.compile(r"(?m)^\s*\d{1,2}[.)]\s+\S")
MIN_RANKED_ITEMS = 3

# Bewertungskriterium-Marker (EN+DE) — wenn mindestens EINES vorkommt,
# ist die Rangliste begruendet und kein Artefakt.
CRITERION_MARKERS = [
    "weil", "grund", "gründe", "kriterium", "kriterien", "begruendet",
    "begründet", "gemessen an", "sortiert nach", "massstab", "maßstab",
    "weil", "because", "reason", "criterion", "criteria", "rationale",
    "metric", "measured by", "ranked by", "sorted by", "justification",
    "basis:",
]

MIN_ENUM_ITEMS = 3      # zwei parallele Saetze sind noch normale Rhetorik
MAX_ENUM_CONFIDENCE = 0.35


def rank_without_criterion(text: str):
    ranked = RANKED_LINE_RE.findall(text)
    if len(ranked) < MIN_RANKED_ITEMS:
        return None
    low = text.lower()
    if any(m in low for m in CRITERION_MARKERS):
        return None
    return {
        "id": "RankWithoutCriterion",
        "confidence": MAX_ENUM_CONFIDENCE,
        "exploratory": True,
        "evidence": (f"{len(ranked)} nummerierte Rangpositionen ohne ein "
                     "einziges Bewertungskriterium (kein Grund/Massstab/"
                     "Kriterium im Text)"),
        "keep_when": ("Rankings MIT Kriterium (Installationszahlen, Punkte, "
                      "genannte Massstaebe) feuern nicht; kurze Listen mit "
                      "< 3 Positionen nicht. EXPLORATIV — nur im Kontext "
                      "weiterer Signale werten, nie score-wirksam."),
    }


def _sentence_frames(sentences: list):
    """Anfangs-Frames je Satz: erstes Wort, erste zwei Woerter sowie
    (Stamm-Prefix + letztes Wort) — letzteres faengt Flexionsvarianten
    wie "Kein/Keine … mehr" ein."""
    one, two, stemlast = {}, {}, {}
    for s in sentences:
        words = s.strip().split()
        if not words:
            continue
        first = words[0].lower().strip(",;:!?«»\"'")
        one.setdefault(first, []).append(s)
        if len(words) >= 2:
            second = words[1].lower().strip(",;:!?«»\"'")
            two.setdefault(f"{first} {second}", []).append(s)
        if len(words) >= 3:
            last = words[-1].lower().strip(".,;:!?«»\"'")
            stemlast.setdefault((first[:4], last), []).append(s)
    return one, two, stemlast


def identical_enumeration(text: str):
    sentences = tokenizer.split_sentences(text)
    if len(sentences) < MIN_ENUM_ITEMS:
        return None
    one, two, stemlast = _sentence_frames(sentences)
    best_frame, best_group = None, []
    for frames in (two, one, stemlast):  # spezifischere Frames zuerst
        for frame, group in frames.items():
            if len(group) > len(best_group):
                best_frame, best_group = frame, group
    if len(best_group) < MIN_ENUM_ITEMS:
        return None
    label = best_frame if isinstance(best_frame, str) else \
        f"{best_frame[0]}… {best_frame[1]}"
    return {
        "id": "IdenticalEnumeration",
        "confidence": MAX_ENUM_CONFIDENCE,
        "exploratory": True,
        "evidence": (f"{len(best_group)} Saetze mit identischem Anfangs-"
                     f"Frame ('{label} …') — Aufzaehlung als "
                     "rhetorische Staffage statt Argument"),
        "keep_when": ("echte Aufzaehlungen mit variierendem Satzbau; "
                      "Wiederholungs-Stilmittel (Anapher) in Literatur/"
                      "Reden ist legitim. EXPLORATIV — nie score-wirksam, "
                      "nur als Kontext-Hinweis werten."),
    }


def find_discourse_findings(text: str) -> list:
    return [f for f in (rank_without_criterion(text),
                        identical_enumeration(text)) if f]
