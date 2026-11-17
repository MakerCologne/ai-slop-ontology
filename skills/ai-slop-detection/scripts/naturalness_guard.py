#!/usr/bin/env python3
"""
Naturalness-Guard (issue #81, detect-only, low confidence).

Two advisory signals against the two failure modes of automated text
cleanup (humanizer register-profile idea, architecture reference deep/11;
marker lists self-derived, no third-party pattern material copied):

  register_drift      mixed register in one text: >= 2 formal markers AND
                      >= 2 colloquial markers outside quotes (>= 30 words).
                      keep_when: quoted dialogue/fiction (colloquial inside
                      quotation marks never counts); short chat snippets.

  over_sanitized      >= 3 distinct expanded full forms ("do not", "it
                      is", ...) with ZERO contractions (>= 60 words).
                      keep_when: formal genres — callers pass genre=
                      "academic"/"legal" to suppress; possessive 's is not
                      a contraction.

  modal_particle_anomaly  M63 (#76): DE modal particle inventory.
                      Humanized German sprinkles modal particles (ja,
                      halt, eben, doch, mal, ...) mechanically — as
                      uniform per-sentence seasoning rather than natural
                      discourse function. Two anomaly cues (detect-only,
                      outside quotes, >= 40 words):
                        density  >= 6 particle tokens AND >= 2.5 % of all
                                  words are inventory particles
                        stacking >= 2 sentences carrying >= 2 distinct
                                  particles each (particle cluster per
                                  sentence reads as decorative filler)
                      keep_when: spoken-word/dialogue/fiction genres
                      (colloquial particles inside quotes never count —
                      quotes are stripped first).

DETECT-ONLY: findings never feed the numeric slop score and are capped at
confidence 0.45. FP expectation (#64): formal writing triggers
over_sanitized by design — that is why the genre guard exists and the
finding is advisory with fixed low confidence.

Public surface:
    register_drift(text) -> finding | None
    over_sanitized(text) -> finding | None
    modal_particle_anomaly(text) -> finding | None   (M63, DE, detect-only)
    find_naturalness_findings(text, genre=None) -> list[finding]
"""

import re

# Closed marker lists (EN+DE), deliberately small.
FORMAL_MARKERS = {
    "furthermore", "moreover", "in addition", "hereby", "notwithstanding",
    "thus", "hence", "consequently",
    "ferner", "mithin", "gemäß", "hierauf", "folglich", "laut",
}
COLLOQUIAL_MARKERS = {
    "yeah", "kinda", "gonna", "hey", "okay", "honestly", "stuff", "wild",
    "na ja", "irgendwie", "halt", "krass", "echt",
}

# Expanded full forms whose contraction-free accumulation reads sanitized.
FULL_FORMS = [
    "do not", "does not", "did not", "cannot", "can not", "will not",
    "would not", "it is", "we are", "they are", "that is", "there is",
    "we have", "they have", "it has",
]
_CONTRACTION_RE = re.compile(r"\b\w+['’](?:t|s|re|ve|ll|d|m)\b")
_POSSESSIVE_OK = re.compile(r"\b\w+['’]s\b")
_QUOTE_RE = re.compile(r'[„"“][^„""“”]{1,300}[”“"]')

MIN_WORDS_REGISTER = 30
MIN_WORDS_SANITIZED = 25  # fixture-calibrated (pos1/pos3/possessive fixtures in tests)
MIN_FULL_FORMS = 3

# Genres where expanded full forms are register-correct, not sanitization.
FORMAL_GENRES = {"academic", "legal"}

# Genres where dense modal particles are register-correct (spoken word,
# dialogue, fiction). #63 M63 keep_when guard, symmetric to FORMAL_GENRES.
COLLOQUIAL_GENRES = {"dialogue", "fiction", "spoken"}

# --- M63: DE modal particle inventory (#76) ---------------------------
# Closed inventory, deliberately small: high-frequency German modal
# particles that humanizer output sprinkles decoratively. Matched as
# whole words only (word boundary), outside quotes, case-insensitive.
DE_MODAL_PARTICLES = {
    "ja", "halt", "eben", "doch", "mal", "wohl", "schon",
    "denn", "eigentlich", "einfach", "irgendwie", "quasi",
}
_PARTICLE_RES = {
    p: re.compile(rf"(?<![\wäöüß]){re.escape(p)}(?![\wäöüß])", re.IGNORECASE)
    for p in DE_MODAL_PARTICLES
}
MIN_WORDS_PARTICLES = 40
MIN_PARTICLE_TOKENS = 6
MAX_PARTICLE_DENSITY = 0.025  # 2.5 % of all words
MIN_STACKING_SENTENCES = 2
MIN_DISTINCT_PER_SENTENCE = 2


def _markers(text_lower: str, markers: set) -> list:
    return sorted(m for m in markers if m in text_lower)


def _strip_quotes(text: str) -> str:
    return _QUOTE_RE.sub(" ", text)


def register_drift(text: str):
    body = _strip_quotes(text)
    if len(body.split()) < MIN_WORDS_REGISTER:
        return None
    low = body.lower()
    formal = _markers(low, FORMAL_MARKERS)
    colloquial = _markers(low, COLLOQUIAL_MARKERS)
    if len(formal) >= 2 and len(colloquial) >= 2:
        return {
            "id": "RegisterDrift",
            "confidence": 0.45,
            "evidence": (f"formal {formal} vs colloquial {colloquial} "
                         "in one text (outside quotes)"),
            "keep_when": ("quoted dialogue/fiction (quotes stripped before "
                          "counting); short chat snippets < "
                          f"{MIN_WORDS_REGISTER} words"),
        }
    return None


def over_sanitized(text: str):
    if len(text.split()) < MIN_WORDS_SANITIZED:
        return None
    low = text.lower()
    full_hits = sorted({f for f in FULL_FORMS if f in low})
    has_contraction = bool(_CONTRACTION_RE.search(text) and
                           not _only_possessives(text))
    if len(full_hits) >= MIN_FULL_FORMS and not has_contraction:
        return {
            "id": "OverSanitized",
            "confidence": 0.45,
            "evidence": (f"{len(full_hits)} distinct expanded full forms "
                         f"({', '.join(full_hits[:5])}), zero contractions"),
            "keep_when": ("formal genres (pass genre='academic'/'legal' to "
                          "suppress); possessive 's is not a contraction"),
        }
    return None


def _only_possessives(text: str) -> bool:
    """True when every apostrophe token is a possessive 's (not a
    contraction) — those do not count as human-typed rhythm."""
    tokens = re.findall(r"\b\w+['’](?:t|s|re|ve|ll|d|m)\b", text)
    if not tokens:
        return True
    return all(_POSSESSIVE_OK.fullmatch(t) for t in tokens)


def modal_particle_anomaly(text: str):
    """M63 (#76): mechanical modal-particle sprinkling in German text.

    Detect-only, advisory, never score-relevant. Cues: particle density
    (>= 6 tokens and >= 2.5 % of words) or repeated per-sentence stacking
    (>= 2 sentences with >= 2 distinct particles each). Colloquial
    particles inside quotation marks never count (quotes stripped), and
    callers pass genre="dialogue"/"fiction"/"spoken" for legitimately
    colloquial material.
    """
    body = _strip_quotes(text)
    n_words = len(body.split())
    if n_words < MIN_WORDS_PARTICLES:
        return None
    low = body.lower()
    tokens = []
    for particle, rx in _PARTICLE_RES.items():
        tokens.extend((particle, m.start()) for m in rx.finditer(low))
    if not tokens:
        return None
    distinct = sorted({p for p, _ in tokens})
    density = len(tokens) / n_words
    density_hit = (len(tokens) >= MIN_PARTICLE_TOKENS and
                   density >= MAX_PARTICLE_DENSITY)

    # Stacking: count sentences carrying >= 2 distinct particles.
    sentences = re.split(r"[.!?]+", body)
    stacking_sentences = 0
    for sent in sentences:
        sent_low = sent.lower()
        hit = sum(1 for particle, rx in _PARTICLE_RES.items()
                  if rx.search(sent_low))
        if hit >= MIN_DISTINCT_PER_SENTENCE:
            stacking_sentences += 1
    stacking_hit = stacking_sentences >= MIN_STACKING_SENTENCES

    if not (density_hit or stacking_hit):
        return None
    cues = []
    if density_hit:
        cues.append(f"density {len(tokens)} particles = {density:.1%} of words")
    if stacking_hit:
        cues.append(f"{stacking_sentences} sentences with >= 2 distinct "
                    "particles each")
    return {
        "id": "ModalParticleAnomaly",
        "confidence": 0.45,
        "evidence": ("DE-Modalpartikel mechanisch gestreut: " + "; ".join(cues)
                     + f" (distinct: {', '.join(distinct[:6])})"),
        "keep_when": ("spoken-word/dialogue/fiction genres (pass "
                      "genre='dialogue'/'fiction'/'spoken' to suppress; "
                      "quoted speech is stripped before counting)"),
    }


def find_naturalness_findings(text: str, genre: str = None) -> list:
    findings = []
    rd = register_drift(text)
    if rd:
        findings.append(rd)
    if genre not in FORMAL_GENRES:
        os_ = over_sanitized(text)
        if os_:
            findings.append(os_)
    if genre not in COLLOQUIAL_GENRES:
        mp = modal_particle_anomaly(text)
        if mp:
            findings.append(mp)
    return findings
