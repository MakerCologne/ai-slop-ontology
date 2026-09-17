#!/usr/bin/env python3
"""
Circular Explanations (issue #122, detect-only).

Prosa-Signal aus dem PRISM-Kontext (bhanvinayer/PRISM: "hat ein Mensch es
wirklich gelesen?" — hier adaptiert fuer Prosa): die tautologische
Definition im Satz. "The auth module validates authentic user
authentication" — das Praedikat fuegt dem Subjekt keine Information hinzu,
weil es dessen Stamm-Woerter wiederholt.

Regel (messbar):
  Ein Satz feuert, wenn ALLES gilt:
    1. Laenge >= 5 Woerter.
    2. Enthaelt ein definitionales Verb (is/are/means/validates/ensures/
       provides/verifies/secures/defines/describes/refers to) — ohne
       solches Verb ist Wiederholung bloss Referenz, keine Definition.
    3. Mindestens ein Content-Wort-Stamm (Prefix >= 5 Zeichen, keine
       Stoppworte) erscheint BEIDSEITS des Verbs (Subjekt und Praedikat).
    4. Das Praedikat bringt <= 3 NEUE Content-Staemme hinzu — eine echte
       Definition fuehrt neuen Inhalt ein.

DETECT-ONLY: Konfidenz fest 0.45, niemals Teil des numerischen
Slop-Scores (ADR-0001). Score-Distripliniert wie alle Prosa-Struktursignale.

keep_when / Hard Negatives:
  - "The cache caches data" — Praedikat {data}, 0 Shared-Staemme: feuert
    nicht (Regel 3).
  - "The auth module handles authentication tokens" — 'handles' ist nicht
    definitional: feuert nicht (Regel 2). Technische Spec-Prosa, in der
    ein Modul seine Inputs benennt, ist legitim.
  - "Authentication is the process of verifying identity against stored
    credentials" — Praedikat bringt verifying/identity/stored/credentials
    (4 neue Staemme): feuert nicht (Regel 4, echte Definition).

Public surface:
    circular_explanation(text) -> finding | None
    find_circular_findings(text) -> list[finding]
"""

import re

# Tokenizer-Abhaengigkeit wie alle skill-Skripte (issue #68 SSOT).
try:
    import tokenizer
    _tokenize = tokenizer.tokenize_words
except ImportError:  # pragma: no cover - direct execution fallback
    def _tokenize(text):
        return re.findall(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß\-]*", text.lower())

# Definitionale Verben: nur diese machen aus Wiederholung eine Tautologie.
DEFINITIONAL_VERBS = {
    "is", "are", "means", "validates", "ensures", "provides", "verifies",
    "secures", "defines", "describes", "refers",
    "bedeutet", "heisst", "heißt", "definiert", "beschreibt",
}

STOPWORDS = {
    "the", "a", "an", "of", "to", "and", "or", "for", "in", "on", "with",
    "that", "this", "it", "its", "by", "as", "at", "be", "was", "were",
    "der", "die", "das", "den", "dem", "ein", "eine", "einer", "eines",
    "und", "oder", "fuer", "für", "in", "im", "auf", "mit", "von", "vom",
}


MIN_WORDS = 5
STEM_PREFIX = 4          # Stamm-Prefix-Laenge fuer Aehnlichkeit
MAX_NEW_PREDICATE_STEMS = 3
CONFIDENCE = 0.45        # detect-only, fest, nie score-wirksam


def _stems(words):
    """Content-Stamm-Prefixes (>= STEM_PREFIX Zeichen, keine Stoppworte)."""
    out = set()
    for w in words:
        if w in STOPWORDS or w in DEFINITIONAL_VERBS:
            continue
        if len(w) >= STEM_PREFIX:
            out.add(w[:STEM_PREFIX])
    return out


def circular_explanation(text: str):
    """Pruefe jeden Satz auf tautologische Definition; erster Treffer."""
    for sent in re.split(r"[.!?]+", text or ""):
        finding = _check_sentence(sent)
        if finding:
            return finding
    return None


def _check_sentence(sent: str):
    words = _tokenize(sent)
    if len(words) < MIN_WORDS:
        return None
    verb_idx = next((i for i, w in enumerate(words)
                     if w in DEFINITIONAL_VERBS), None)
    if verb_idx is None:
        return None
    subject_stems = _stems(words[:verb_idx])
    predicate_stems = _stems(words[verb_idx + 1:])
    shared = subject_stems & predicate_stems
    new_stems = predicate_stems - subject_stems
    if not shared:
        return None
    if len(new_stems) > MAX_NEW_PREDICATE_STEMS:
        return None
    return {
        "id": "CircularExplanation",
        "confidence": CONFIDENCE,
        "evidence": (f"tautologische Definition: {sent.strip()[:120]!r} "
                     f"(geteilte Staemme {sorted(shared)[:3]}, Praedikat "
                     f"bringt nur {len(new_stems)} neue Staemme)"),
        "keep_when": ("Echte Definitionen (Praedikat mit >3 neuen Staemmen), "
                      " technische Referenz ('the auth module handles "
                      "authentication tokens') und verb-lose Wiederholung "
                      "feuern nicht. DETECT-ONLY — nie score-wirksam."),
    }


def find_circular_findings(text: str):
    """Alle Zirkelschluss-Saetze eines Textes als Findings-Liste."""
    findings = []
    for sent in re.split(r"[.!?]+", text or ""):
        f = _check_sentence(sent)
        if f:
            findings.append(f)
    return findings
