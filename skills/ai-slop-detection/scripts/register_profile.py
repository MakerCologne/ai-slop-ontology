#!/usr/bin/env python3
"""
Register-Profile v2 (issue #74, detect-only).

Zwei Oberflächen:

1. ``register_profile(text) -> dict`` — JSON-Stilkarte:
   mode, deictic_center, address, distance, sentence_shape, word_level,
   paragraph_openers, particles, punctuation_affinity (+ meta).
   Reine Beschreibung des Stilkontexts; fließt NIEMALS in den numerischen
   Slop-Score. Der Scorer gibt die Karte unter ``context`` im Report aus.

2. ``register_drift_intern(text, genre=None) -> finding | None`` —
   detect-only Signal (Konfidenz 0.5): Register-Distanz ZWISCHEN
   Dokument-Hälften — positionssensibel, bewusst komplementär zu #81
   ``register_drift`` (Ganztext-Mischung formal/kolloquial).
   ``register_drift_intern`` feuert nur, wenn jede Hälfte für sich
   registerrein ist, die Hälften aber unterschiedliche Register tragen.
   Kollisionsdisziplin (#46): anderes Finding-Id, disjunkter Fallraum —
   der #81-Fall (beide Hälften gemischt) wird hier nie gemeldet.

Guardrails:
   - #42 Genre-Profile: für Ggenres mit register-konventioneller Formel
     (academic/legal/technical) wird kein Finding ausgegeben; Genre-
     ``exempt_terms`` werden vor der Marker-Zählung entfernt.
   - "Legitim gleichmäßig": durchgehend formaler (oder kolloquialer)
     Text ist ein Register, kein Drift → nie ein Finding.
   - Zitierte Dialoge zählen nicht (Quotes werden entfernt, wie #81/#23).

Marker-Listen: FORMAL_MARKERS/COLLOQUIAL_MARKERS werden aus
naturalness_guard (#81) importiert — keine zweite Kopie (SSOT-C3-
Disziplin). Alle weiteren Listen sind selbst abgeleitet (kein
Drittpartei-Pattern-Material).

Public surface:
    register_profile(text) -> dict
    register_drift_intern(text, genre=None) -> finding | None
    find_register_findings(text, genre=None) -> list[finding]
"""

import re
import statistics

import naturalness_guard
from naturalness_guard import COLLOQUIAL_MARKERS, FORMAL_MARKERS
import tokenizer

# --- closed lists (self-derived, EN+DE) ------------------------------------

# Imperativ-Starter für "instructive" mode detection.
IMPERATIVE_STARTERS = {
    "consider", "imagine", "note", "remember", "look", "listen", "try",
    "betrachten", "stellen", "denken", "beachten", "versuchen",
}

# Modalpartikel (DE) — Inventar bewusst klein (Rest folgt mit #76 M63).
MODAL_PARTICLES_DE = [
    "halt", "mal", "doch", "eben", "ja", "wohl", "eigentlich", "wohl",
]

# Hedge-Partikel (EN+DE).
HEDGE_PARTICLES = [
    "maybe", "perhaps", "sort of", "kind of", "possibly",
    "vielleicht", "möglicherweise", "eventuell", "irgendwie",
]

# Intensifier-Partikel (EN+DE, Kleinteilmenge von #24, nur Beschreibung).
INTENSIFIER_PARTICLES = [
    "really", "very", "extremely", "incredibly",
    "echt", "wirklich", "sehr", "extrem", "krass",
]

# Genre-Profile (#42), deren Register-Konventionen internen "Drift"
# legitim machen — hier wird suppressiert statt gemeldet.
REGISTER_DRIFT_EXEMPT_GENRES = {"academic", "legal", "technical"}

# Skalierung: Floskelraten pro 1000 Zeichen.
PUNCT_PER_CHARS = 1000

MIN_WORDS_DRIFT = 40       # kürzere Texte: keine Hälften-Aussagekraft
MIN_MARKERS_PER_HALF = 2   # einzelner Streifmarker bleibt unmarkiert

_QUOTE_RE = re.compile(r'[„"“][^„""“”]{1,300}[”“"]')


def _strip_quotes(text: str) -> str:
    return _QUOTE_RE.sub(" ", text)


def _strip_exempt_terms(text: str, genre: str) -> str:
    """#42-Guardrail: Genre-exempte Begriffe zählen nicht als Marker."""
    import genre_profiles
    try:
        profile = genre_profiles.get_profile(genre)
    except ValueError:
        return text
    for term in profile.get("exempt_terms", []):
        text = re.sub(re.escape(term), " ", text, flags=re.IGNORECASE)
    return text


# --- 1. Stilkarte -----------------------------------------------------------


def _words(text: str) -> list:
    return re.findall(r"[a-zA-ZäöüßÄÖÜ]+(?:-[a-zA-ZäöüßÄÖÜ]+)*", text)


def _guess_language(words: list) -> str:
    de_markers = {"der", "die", "das", "und", "ist", "nicht", "mit",
                  "für", "auch", "aber", "wird", "wurde"}
    en_markers = {"the", "and", "is", "not", "with", "for", "also",
                  "but", "was", "are", "this"}
    text_set = {w.lower() for w in words}
    de = len(text_set & de_markers)
    en = len(text_set & en_markers)
    if de > en:
        return "de"
    if en > de:
        return "en"
    return "mixed" if de else "en"


def _classify_mode(text: str, low: str) -> str:
    sentences = tokenizer.split_sentences(text)
    imperative = sum(
        1 for s in sentences
        if s.split() and s.split()[0].lower().strip(",;:") in IMPERATIVE_STARTERS
    )
    author = len(re.findall(r"\b(?:ich|wir|i|we)\b", low))
    reader = len(re.findall(r"\b(?:du|sie|you)\b", low))
    if imperative and imperative >= len(sentences) / 3:
        return "instructive"
    if reader >= 2 and reader > author:
        return "interactive"
    if author >= 2 and author > reader:
        return "narrative"
    return "expository"


def _classify_deictic_center(low: str) -> str:
    author = len(re.findall(r"\b(?:ich|wir|i|we)\b", low))
    reader = len(re.findall(r"\b(?:du|deiner|ihr|you|your)\b", low))
    subject = len(re.findall(r"\b(?:er|sie|es|he|she|it|they)\b", low))
    best = max(author, reader, subject)
    if best == 0:
        return "impersonal"
    if author == best:
        return "author"
    if reader == best:
        return "reader"
    return "subject"


def _classify_distance(low: str) -> str:
    formal = sum(1 for m in FORMAL_MARKERS if m in low)
    colloquial = sum(1 for m in COLLOQUIAL_MARKERS if m in low)
    if formal >= 2 and formal > colloquial:
        return "formal"
    if colloquial >= 2 and colloquial > formal:
        return "informal"
    return "neutral"


def register_profile(text: str) -> dict:
    words = _words(text)
    word_count = len(words)
    low = text.lower()
    sentences = tokenizer.split_sentences(text)
    lengths = [len(tokenizer.tokenize_words(s)) for s in sentences] or [0]

    formal = sum(1 for m in FORMAL_MARKERS if m in low)
    colloquial = sum(1 for m in COLLOQUIAL_MARKERS if m in low)
    _ = formal, colloquial  # distance reuses _classify_distance(low)

    paragraphs = [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    opener_words = []
    for p in paragraphs:
        toks = _words(p)
        if toks:
            opener_words.append(toks[0].lower())
    opener_counts = {}
    for w in opener_words:
        opener_counts[w] = opener_counts.get(w, 0) + 1
    repeated = sorted(w for w, c in opener_counts.items() if c >= 2)

    n_chars = max(len(text), 1)

    def _rate(charset_pattern: str) -> float:
        return round(len(re.findall(charset_pattern, text)) / n_chars
                     * PUNCT_PER_CHARS, 2)

    return {
        "mode": _classify_mode(text, low),
        "deictic_center": _classify_deictic_center(low),
        "address": "direct" if _classify_deictic_center(low) == "reader"
                   or _classify_mode(text, low) == "instructive" else "indirect",
        "distance": _classify_distance(low),
        "sentence_shape": {
            "sentences": len(sentences),
            "avg_length": round(statistics.mean(lengths), 1),
            "stdev": round(statistics.pstdev(lengths), 1) if len(lengths) > 1 else 0.0,
            "profile": "uniform" if (len(lengths) > 1
                                     and statistics.pstdev(lengths) < 3.0)
                       else "varied",
        },
        "word_level": {
            "avg_word_length": round(
                sum(len(w) for w in words) / word_count, 2) if words else 0.0,
            "long_word_rate": round(
                sum(1 for w in words if len(w) >= 12) / word_count, 3)
                if words else 0.0,
        },
        "paragraph_openers": {
            "first_words": opener_words,
            "repeated": repeated,
        },
        "particles": {
            "modal_particles": sorted({m for m in MODAL_PARTICLES_DE
                                       if re.search(r"\b" + m + r"\b", low)}),
            "hedges": sorted({h for h in HEDGE_PARTICLES if h in low}),
            "intensifiers": sorted({i for i in INTENSIFIER_PARTICLES if i in low}),
        },
        "punctuation_affinity": {
            "em_dash_rate": _rate(r"—|--"),
            "ellipsis_rate": _rate(r"\.\.\.|…"),
            "exclamation_rate": _rate(r"!"),
            "semicolon_rate": _rate(r";"),
        },
        "meta": {
            "word_count": word_count,
            "paragraphs": len(paragraphs),
            "language_guess": _guess_language(words),
            "detect_only": True,
        },
    }


# --- 2. register_drift_intern ------------------------------------------------


def _halves(text: str):
    """Dokument-Hälften: absatzweise (>=2 Absätze), sonst satzweise —
    eine Wort-Mitte würde Registergrenzen mitten im Satz zerschneiden."""
    paragraphs = [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    if len(paragraphs) >= 2:
        mid = len(paragraphs) // 2
        return "\n\n".join(paragraphs[:mid]), "\n\n".join(paragraphs[mid:])
    sentences = tokenizer.split_sentences(text)
    if len(sentences) >= 2:
        mid = len(sentences) // 2
        return " ".join(sentences[:mid]), " ".join(sentences[mid:])
    words = text.split()
    mid = len(words) // 2
    return " ".join(words[:mid]), " ".join(words[mid:])


def register_drift_intern(text: str, genre: str = None):
    if genre in REGISTER_DRIFT_EXEMPT_GENRES:
        return None
    body = _strip_quotes(text)
    if genre is not None:
        body = _strip_exempt_terms(body, genre)
    if len(body.split()) < MIN_WORDS_DRIFT:
        return None

    first, second = _halves(body)
    low1, low2 = first.lower(), second.lower()

    def _counts(low):
        return (sum(1 for m in FORMAL_MARKERS if m in low),
                sum(1 for m in COLLOQUIAL_MARKERS if m in low))

    f1, c1 = _counts(low1)
    f2, c2 = _counts(low2)

    def _pure_formal_then_colloquial():
        return (f1 >= MIN_MARKERS_PER_HALF and c1 == 0
                and c2 >= MIN_MARKERS_PER_HALF and f2 == 0)

    def _pure_colloquial_then_formal():
        return (c1 >= MIN_MARKERS_PER_HALF and f1 == 0
                and f2 >= MIN_MARKERS_PER_HALF and c2 == 0)

    if not (_pure_formal_then_colloquial() or _pure_colloquial_then_formal()):
        return None

    return {
        "id": "RegisterDriftIntern",
        "confidence": 0.5,
        "evidence": (f"Dokument-Hälften tragen unterschiedliche Register: "
                     f"Hälfte 1 formal={f1}/kolloquial={c1}, Hälfte 2 "
                     f"formal={f2}/kolloquial={c2} (je Hälfte registerrein)"),
        "keep_when": ("durchgehend einheitliches Register (legitim "
                      "gleichmäßig); zitierte Dialoge (Quotes entfernt); "
                      "Genre-Profile academic/legal/technical (#42-"
                      "Exemptions); Texte < "
                      f"{MIN_WORDS_DRIFT} Wörter; gleichmäßig gemischte "
                      "Texte gehören zu register_drift #81"),
    }


def find_register_findings(text: str, genre: str = None) -> list:
    findings = []
    f = register_drift_intern(text, genre=genre)
    if f:
        findings.append(f)
    return findings
